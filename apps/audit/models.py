import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    EVENT_TYPES = [
        ("DOCUMENT_UPLOADED", "Document uploaded"),
        ("OCR_STARTED", "OCR started"),
        ("OCR_COMPLETED", "OCR completed"),
        ("IDENTITY_CHECK_STARTED", "Identity check started"),
        ("IDENTITY_CHECK_COMPLETED", "Identity check completed"),
        ("IDENTITY_VERIFICATION_FAILED", "Identity verification failed"),
        ("CREDENTIAL_CREATED", "Credential created"),
        ("DOCUMENT_DELETED", "Document deleted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="audit_events",
        null=True,
        blank=True,
    )
    event_type = models.CharField(max_length=60, choices=EVENT_TYPES)
    entity_type = models.CharField(max_length=50, blank=True, default="")
    entity_id = models.UUIDField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} ({self.created_at})"
