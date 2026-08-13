import hashlib
import secrets

from django.db import transaction

from apps.identity.models import (
    IdentityDocument,
    VerifiableCredential,
    VerificationStatus,
)


class OCRService:
    """
    Placeholder for the real OCR pipeline.

    Later:
        EasyOCR
        OpenCV
        PyTorch
    """

    @staticmethod
    def extract(document: IdentityDocument) -> dict:

        # This is intentionally fake for the MVP.
        return {
            "nid": "MOCK-NID-123456",
            "name": document.user.get_full_name(),
            "dob": None,
        }


class NIDMCService:
    """
    Boundary for Nepal identity verification.

    Replace this class with the actual external API integration.
    """

    @staticmethod
    def verify(nid: str) -> bool:

        if not nid:
            return False

        # Mock successful verification.
        return True


class ZKPService:
    """
    Temporary ZKP abstraction.

    This is NOT a real zero-knowledge proof implementation.
    Replace this service with a real circuit/proving system.
    """

    @staticmethod
    def generate_credential_hash(
        user_id: int,
        nid: str
    ) -> str:

        nonce = secrets.token_hex(32)

        payload = (
            f"{user_id}:"
            f"{nid}:"
            f"{nonce}"
        )

        return hashlib.sha256(
            payload.encode()
        ).hexdigest()


class IdentityService:

    @staticmethod
    @transaction.atomic
    def process_document(
        document: IdentityDocument
    ) -> VerifiableCredential:

        document.status = VerificationStatus.PROCESSING
        document.save(
            update_fields=["status"]
        )

        extracted = OCRService.extract(document)

        document.extracted_nid = extracted["nid"]
        document.extracted_name = extracted["name"]
        document.extracted_dob = extracted["dob"]

        verified = NIDMCService.verify(
            extracted["nid"]
        )

        if not verified:

            document.status = VerificationStatus.FAILED

            document.save(
                update_fields=[
                    "status",
                    "extracted_nid",
                    "extracted_name",
                    "extracted_dob",
                ]
            )

            raise ValueError(
                "Identity verification failed."
            )

        credential_hash = (
            ZKPService.generate_credential_hash(
                user_id=document.user.id,
                nid=extracted["nid"]
            )
        )

        credential = VerifiableCredential.objects.create(
            user=document.user,
            credential_hash=credential_hash,
        )

        document.status = VerificationStatus.VERIFIED

        document.save(
            update_fields=[
                "status",
                "extracted_nid",
                "extracted_name",
                "extracted_dob",
            ]
        )

        document.user.is_identity_verified = True

        document.user.save(
            update_fields=["is_identity_verified"]
        )

        return credential