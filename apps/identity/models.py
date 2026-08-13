import uuid

from django.conf import settings
from django.db import models


class VerificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    VERIFIED = "VERIFIED", "Verified"
    FAILED = "FAILED", "Failed"


class IdentityDocument(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="identity_documents"
    )

    document_type = models.CharField(
        max_length=50,
        default="CITIZENSHIP"
    )

    document_file = models.FileField(
        upload_to="identity_documents/"
    )

    status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    extracted_nid = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    extracted_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    extracted_dob = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.document_type}"
    
class VerifiableCredential(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="credentials"
    )

    credential_hash = models.CharField(
        max_length=128,
        unique=True
    )

    issuer = models.CharField(
        max_length=255,
        default="Identity Platform"
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    blockchain_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.id)