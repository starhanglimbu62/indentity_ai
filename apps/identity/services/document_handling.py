import os

from django.utils import timezone

from apps.audit.services import AuditService
from apps.identity.models import IdentityDocument

from .validation import DocumentValidationService


class DocumentHandlingService:
    @staticmethod
    def validate_document(document: IdentityDocument) -> IdentityDocument:
        if document.document_file is None or not document.document_file.name:
            raise ValueError("Document file is required.")

        DocumentValidationService.validate_file(document.document_file)
        return document

    @staticmethod
    def delete_raw_document(document: IdentityDocument) -> None:
        if document.document_file and document.document_file.name:
            try:
                document.document_file.delete(save=False)
            except FileNotFoundError:
                pass
            document.document_file.name = ""

        document.processed_at = timezone.now()
        document.save(update_fields=["document_file", "processed_at"])

        AuditService.record_event(
            user=document.user,
            event_type="DOCUMENT_DELETED",
            entity_type="identity_document",
            entity_id=document.id,
            metadata={"document_type": document.document_type},
        )
