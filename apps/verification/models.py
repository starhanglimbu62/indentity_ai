import uuid

from django.conf import settings
from django.db import models

from apps.banks.models import Bank
from apps.identity.models import VerifiableCredential


class VerificationRequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    DENIED = "DENIED", "Denied"
    VERIFIED = "VERIFIED", "Verified"
    EXPIRED = "EXPIRED", "Expired"


class VerificationRequest(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="verification_requests"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_requests"
    )

    credential = models.ForeignKey(
        VerifiableCredential,
        on_delete=models.PROTECT
    )

    claim = models.CharField(
        max_length=100
    )

    status = models.CharField(
        max_length=20,
        choices=VerificationRequestStatus.choices,
        default=VerificationRequestStatus.PENDING
    )

    user_consented_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.bank.name} -> {self.user.username}"