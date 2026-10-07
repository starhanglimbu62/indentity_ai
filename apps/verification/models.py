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


class NotificationType(models.TextChoices):
    VERIFICATION_REQUEST = "VERIFICATION_REQUEST", "Verification Request"
    VERIFICATION_APPROVED = "VERIFICATION_APPROVED", "Verification Approved"
    VERIFICATION_DENIED = "VERIFICATION_DENIED", "Verification Denied"
    VERIFICATION_RESULT = "VERIFICATION_RESULT", "Verification Result"


class Notification(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.VERIFICATION_REQUEST
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    verification_request = models.ForeignKey(
        'VerificationRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"


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

    # Challenge/nonce issued by verifier and bound to the proof
    challenge = models.CharField(max_length=128, null=True, blank=True)
    challenge_expires_at = models.DateTimeField(null=True, blank=True)

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