import json

from django.db import transaction
from django.utils import timezone

from .models import (
    VerificationRequest,
    VerificationRequestStatus,
)

from apps.common.exceptions import InvalidStateTransition
from apps.identity.services.zk_challenge import encode_challenge


def _normalize_public_signals(public_signals):
    """Accept both dict-shaped and SnarkJS array-shaped publicSignals payloads."""
    if isinstance(public_signals, dict):
        return public_signals

    if isinstance(public_signals, list):
        if len(public_signals) < 4:
            raise ValueError('Public signals list must include current_ts, verification_request_id, claim_id, and challenge.')

        return {
            'current_ts': public_signals[0],
            'verification_request_id': public_signals[1],
            'claim_id': public_signals[2],
            'challenge': public_signals[3],
        }

    if isinstance(public_signals, str):
        try:
            parsed = json.loads(public_signals)
            return _normalize_public_signals(parsed)
        except (TypeError, ValueError):
            pass

    raise ValueError('Public signals must be a mapping or a list.')


class VerificationService:

    @staticmethod
    @transaction.atomic
    def create_request(bank, user, credential, claim):
        """Create a verification request. Caller must ensure caller identity/permissions."""
        request = VerificationRequest.objects.create(bank=bank, user=user, credential=credential, claim=claim)
        return request

    @staticmethod
    @transaction.atomic
    def approve_request(verification_request):
        """Approve a pending verification request (user consent).

        Allowed: PENDING -> APPROVED
        """
        if verification_request.status != VerificationRequestStatus.PENDING:
            raise InvalidStateTransition("Verification request is no longer pending and cannot be approved.")

        verification_request.status = VerificationRequestStatus.APPROVED
        verification_request.user_consented_at = timezone.now()
        verification_request.save(update_fields=["status", "user_consented_at"])  # atomic
        return verification_request

    @staticmethod
    @transaction.atomic
    def deny_request(verification_request):
        """Deny a pending verification request.

        Allowed: PENDING -> DENIED
        """
        if verification_request.status != VerificationRequestStatus.PENDING:
            raise InvalidStateTransition("Only pending requests can be denied.")

        verification_request.status = VerificationRequestStatus.DENIED
        verification_request.save(update_fields=["status"])  # atomic
        return verification_request

    @staticmethod
    @transaction.atomic
    def verify_request(verification_request, proof: dict, public_signals: dict):
        """Verify a request using provided proof/public signals.

        Allowed: APPROVED -> VERIFIED
        """
        # Require explicit user consent first
        if verification_request.status != VerificationRequestStatus.APPROVED:
            raise InvalidStateTransition("User consent is required before verification.")

        # Ensure credential is active and not expired.
        credential = verification_request.credential
        if hasattr(credential, 'status'):
            if credential.status == 'EXPIRED':
                raise InvalidStateTransition('Credential is expired.')
            if credential.status != 'ACTIVE':
                raise InvalidStateTransition('Credential is not active.')
        else:
            if not credential.is_active:
                raise InvalidStateTransition('Credential is not active.')

        expires_at = getattr(credential, 'expires_at', None)
        if expires_at is not None and timezone.now() >= expires_at:
            if hasattr(credential, 'status'):
                credential.status = 'EXPIRED'
                credential.save(update_fields=['status'])
            raise InvalidStateTransition('Credential is expired.')

        # Ensure challenge present and matches public_signals
        challenge = verification_request.challenge
        expires_at = verification_request.challenge_expires_at
        public_signals = _normalize_public_signals(public_signals)

        sent_challenge = public_signals.get('challenge')
        if not challenge or not sent_challenge:
            raise ValueError('Challenge is missing.')

        expected_challenges = {str(challenge), str(encode_challenge(challenge))}
        if str(sent_challenge) not in expected_challenges:
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

        # Verify proof cryptographically using the ZK verifier boundary.
        # Keep the list-shaped public signals for the snarkjs verifier, while using the dict form
        # only for challenge/current_ts validation above.
        from apps.identity.services.zk_verifier import Verifier

        verified = False
        try:
            verifier_payload = public_signals if isinstance(public_signals, list) else [
                str(public_signals.get('current_ts', '')),
                str(public_signals.get('verification_request_id', '')),
                str(public_signals.get('claim_id', '')),
                str(public_signals.get('challenge', '')),
            ]
            verified = Verifier.verify_age_proof(str(verification_request.id), proof, verifier_payload)
        except Exception as exc:
            raise ValueError(f'Cryptographic verification failed: {exc}') from exc

        if not verified:
            raise ValueError('Proof verification failed.')

        # Mark as verified, record time, and clear/consume the challenge to prevent replay
        verification_request.status = VerificationRequestStatus.VERIFIED
        verification_request.verified_at = timezone.now()
        verification_request.challenge = None
        verification_request.challenge_expires_at = None
        verification_request.save(update_fields=['status', 'verified_at', 'challenge', 'challenge_expires_at'])

        return verification_request
