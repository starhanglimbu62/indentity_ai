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
        verification_request,
        proof: dict,
        public_signals: dict,
    ):

        # Require explicit user consent first
        if (
            verification_request.status
            != VerificationRequestStatus.APPROVED
        ):
            raise ValueError(
                "User consent is required."
            )

        # Ensure credential is ACTIVE
        credential = verification_request.credential
        if hasattr(credential, 'status'):
            if credential.status != 'ACTIVE':
                raise ValueError('Credential is not active.')
        else:
            if not credential.is_active:
                raise ValueError('Credential is not active.')

        # Ensure challenge present and matches public_signals
        challenge = verification_request.challenge
        expires_at = verification_request.challenge_expires_at
        if not isinstance(public_signals, dict):
            raise ValueError('Public signals must be a mapping.')

        sent_challenge = public_signals.get('challenge')
        if not challenge or not sent_challenge:
            raise ValueError('Challenge is missing.')
        if challenge != sent_challenge:
            raise ValueError('Challenge does not match verification request.')
        if expires_at and timezone.now() > expires_at:
            raise ValueError('Challenge expired.')

        # current_ts must be trusted and server-issued.
        current_ts = public_signals.get('current_ts')
        if current_ts is None:
            raise ValueError('Current timestamp is missing from public signals.')
        try:
            current_ts_value = int(current_ts)
        except (TypeError, ValueError):
            raise ValueError('Current timestamp is invalid.')
        now_ts = int(timezone.now().timestamp())
        if abs(current_ts_value - now_ts) > 300:
            raise ValueError('Current timestamp is not trusted or is outside the allowed verification window.')

        # Verify proof cryptographically using the ZK verifier boundary
        from apps.identity.services.zk_verifier import Verifier

        verified = False
        try:
            verified = Verifier.verify_age_proof(
                str(verification_request.id),
                proof,
                public_signals,
            )
        except Exception as exc:
            raise ValueError(f'Cryptographic verification failed: {exc}') from exc

        if not verified:
            raise ValueError('Proof verification failed.')

        # Mark as verified, record time, and clear/consume the challenge to prevent replay
        verification_request.status = VerificationRequestStatus.VERIFIED
        verification_request.verified_at = timezone.now()
        verification_request.challenge = None
        verification_request.challenge_expires_at = None
        verification_request.save(
            update_fields=[
                'status',
                'verified_at',
                'challenge',
                'challenge_expires_at',
            ]
        )

        return verification_request