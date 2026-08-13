from django.db import transaction
from django.utils import timezone

from .models import (
    VerificationRequest,
    VerificationRequestStatus,
)


class VerificationService:

    @staticmethod
    @transaction.atomic
    def create_request(
        bank,
        user,
        credential,
        claim
    ):

        request = VerificationRequest.objects.create(
            bank=bank,
            user=user,
            credential=credential,
            claim=claim,
        )

        return request


    @staticmethod
    @transaction.atomic
    def approve_request(
        verification_request
    ):

        if (
            verification_request.status
            != VerificationRequestStatus.PENDING
        ):
            raise ValueError(
                "Verification request is no longer pending."
            )

        verification_request.status = (
            VerificationRequestStatus.APPROVED
        )

        verification_request.user_consented_at = (
            timezone.now()
        )

        verification_request.save(
            update_fields=[
                "status",
                "user_consented_at",
            ]
        )

        return verification_request


    @staticmethod
    @transaction.atomic
    def verify_request(
        verification_request
    ):

        if (
            verification_request.status
            != VerificationRequestStatus.APPROVED
        ):
            raise ValueError(
                "User consent is required."
            )

        # Future:
        # ZKPService.verify(...)
        #
        # For now, the credential itself
        # represents a successful prototype proof.

        verification_request.status = (
            VerificationRequestStatus.VERIFIED
        )

        verification_request.verified_at = (
            timezone.now()
        )

        verification_request.save(
            update_fields=[
                "status",
                "verified_at",
            ]
        )

        return verification_request