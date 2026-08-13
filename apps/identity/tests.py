from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.identity.models import IdentityDocument, VerificationStatus, VerifiableCredential
from apps.identity.services import IdentityService
from apps.identity.services.credential import CredentialService
from apps.identity.services.nidmc import NIDMCService
from apps.identity.services.ocr import OCRService
from apps.identity.services.validation import IdentityValidationService


class IdentityPipelineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass!123",
        )

    def test_valid_upload(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/identity/documents/",
            {
                "document_file": SimpleUploadedFile("citizen.png", b"validpng", content_type="image/png"),
                "document_type": "CITIZENSHIP",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(VerifiableCredential.objects.filter(user=self.user).exists())

        document = IdentityDocument.objects.get(user=self.user)
        self.assertEqual(document.status, VerificationStatus.VERIFIED)
        self.assertTrue(document.user.is_identity_verified)
        self.assertFalse(document.document_file.name)

    def test_invalid_extension(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/identity/documents/",
            {
                "document_file": SimpleUploadedFile("citizen.txt", b"not-an-image", content_type="text/plain"),
                "document_type": "CITIZENSHIP",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_mime_type(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/identity/documents/",
            {
                "document_file": SimpleUploadedFile("citizen.png", b"payload", content_type="application/octet-stream"),
                "document_type": "CITIZENSHIP",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_oversized_file(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.post(
            "/api/identity/documents/",
            {
                "document_file": SimpleUploadedFile(
                    "large.png",
                    b"a" * (10 * 1024 * 1024 + 1),
                    content_type="image/png",
                ),
                "document_type": "CITIZENSHIP",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)

    def test_ocr_extraction(self):
        document = IdentityDocument.objects.create(
            user=self.user,
            document_file=SimpleUploadedFile("citizen.png", b"image-bytes", content_type="image/png"),
            document_type="CITIZENSHIP",
        )

        data = OCRService.extract(document)
        self.assertIn("name", data)
        self.assertIn("nid", data)
        self.assertIn("dob", data)

    def test_missing_required_field(self):
        with self.assertRaises(ValueError):
            IdentityValidationService.validate({"name": "Alice", "nid": "1234567890"})

    def test_invalid_nid(self):
        with self.assertRaises(ValueError):
            IdentityValidationService.validate({
                "name": "Alice",
                "nid": "INVALIDNID",
                "dob": "1990-01-01",
                "confidence": 0.90,
            })

    def test_failed_nidmc_verification(self):
        self.assertFalse(NIDMCService.verify_identity("INVALIDNID"))
        self.assertFalse(NIDMCService.verify_identity("0000000000"))

    def test_successful_identity_verification(self):
        document = IdentityDocument.objects.create(
            user=self.user,
            document_file=SimpleUploadedFile("citizen.png", b"image-bytes", content_type="image/png"),
            document_type="CITIZENSHIP",
        )

        credential = IdentityService.process_document(document)

        self.assertIsNotNone(credential)
        self.assertEqual(document.status, VerificationStatus.VERIFIED)
        self.assertTrue(document.user.is_identity_verified)

    def test_credential_creation(self):
        credential = CredentialService.create_credential(self.user, "1234567890")

        self.assertIsNotNone(credential)
        self.assertEqual(credential.user, self.user)

    def test_document_deletion(self):
        document = IdentityDocument.objects.create(
            user=self.user,
            document_file=SimpleUploadedFile("citizen.png", b"image-bytes", content_type="image/png"),
            document_type="CITIZENSHIP",
        )

        IdentityService.process_document(document)

        document.refresh_from_db()
        self.assertFalse(document.document_file.name)

    def test_audit_event_creation(self):
        document = IdentityDocument.objects.create(
            user=self.user,
            document_file=SimpleUploadedFile("citizen.png", b"image-bytes", content_type="image/png"),
            document_type="CITIZENSHIP",
        )

        IdentityService.process_document(document)

        self.assertTrue(AuditEvent.objects.filter(event_type="DOCUMENT_DELETED").exists())
        self.assertTrue(AuditEvent.objects.filter(event_type="CREDENTIAL_CREATED").exists())
