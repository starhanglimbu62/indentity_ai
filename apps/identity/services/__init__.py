from django.db import transaction
from django.utils import timezone

from apps.audit.services import AuditService
from apps.identity.models import IdentityDocument, VerifiableCredential, VerificationStatus

from .credential import CredentialService
from .document_handling import DocumentHandlingService
from .extraction import IdentityExtractionService
from .nidmc import NIDMCService
from .ocr import OCRService
from .preprocessing import ImagePreprocessingService
from .validation import IdentityValidationService


class IdentityService:
    @staticmethod
    @transaction.atomic
    def process_document(document: IdentityDocument) -> VerifiableCredential:
        DocumentHandlingService.validate_document(document)

        document.status = VerificationStatus.PROCESSING
        document.save(update_fields=["status"])

        AuditService.record_event(
            user=document.user,
            event_type="DOCUMENT_UPLOADED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"document_type": document.document_type},
        )
        AuditService.record_event(
            user=document.user,
            event_type="OCR_STARTED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"document_type": document.document_type},
        )

        prepared_path = ImagePreprocessingService.preprocess(document)
        ocr_data = OCRService.extract(document, prepared_path)
        extracted = IdentityExtractionService.extract(ocr_data)
        validated = IdentityValidationService.validate(extracted)

        AuditService.record_event(
            user=document.user,
            event_type="OCR_COMPLETED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"confidence": validated.get("confidence", 0.0)},
        )

        AuditService.record_event(
            user=document.user,
            event_type="IDENTITY_CHECK_STARTED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"nid": validated["nid"]},
        )

        if not NIDMCService.verify_identity(validated["nid"]):
            document.status = VerificationStatus.FAILED
            document.extracted_nid = validated["nid"]
            document.extracted_name = validated["name"]
            document.extracted_dob = validated["dob"]
            document.processed_at = timezone.now()
            document.save(
                update_fields=[
                    "status",
                    "extracted_nid",
                    "extracted_name",
                    "extracted_dob",
                    "processed_at",
                ]
            )
            AuditService.record_event(
                user=document.user,
                event_type="IDENTITY_VERIFICATION_FAILED",
                entity_type="identity_document",
                entity_id=document.id,
                metadata={"reason": "NIDMC verification failed"},
            )
            DocumentHandlingService.delete_raw_document(document)
            raise ValueError("Identity verification failed.")

        document.extracted_nid = validated["nid"]
        document.extracted_name = validated["name"]
        document.extracted_dob = validated["dob"]
        document.save(update_fields=["extracted_nid", "extracted_name", "extracted_dob"])

        credential = CredentialService.create_credential(document.user, validated["nid"])

        document.status = VerificationStatus.VERIFIED
        document.processed_at = timezone.now()
        document.save(
            update_fields=[
                "status",
                "extracted_nid",
                "extracted_name",
                "extracted_dob",
                "processed_at",
            ]
        )

        document.user.is_identity_verified = True
        document.user.save(update_fields=["is_identity_verified"])

        AuditService.record_event(
            user=document.user,
            event_type="IDENTITY_CHECK_COMPLETED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"credential_id": str(credential.id)},
        )
        AuditService.record_event(
            user=document.user,
            event_type="CREDENTIAL_CREATED",
            entity_type="credential",
            entity_id=credential.id,
            metadata={"credential_hash": credential.credential_hash},
        )
        DocumentHandlingService.delete_raw_document(document)

        return credential
