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
    
class CredentialStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    REVOKED = "REVOKED", "Revoked"


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

    # Compatibility field kept for previous code paths.
    is_active = models.BooleanField(
        default=True
    )

    # New explicit status field for credential lifecycle
    status = models.CharField(
        max_length=20,
        choices=CredentialStatus.choices,
        default=CredentialStatus.ACTIVE,
    )

    blockchain_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return str(self.id)


class ZKProof(models.Model):
    """Minimal metadata for a generated ZK proof.

    Do NOT store private witness material here.
    Store only metadata needed for audit and replay protection.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    verification_request_id = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Proof status: REQUESTED, GENERATED, VERIFIED, FAILED, EXPIRED
    status = models.CharField(max_length=20, default="REQUESTED")

    # Optional: a small digest of the proof bundle (not the private witness)
    proof_digest = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["verification_request_id"])]

    def __str__(self):
        return str(self.id)