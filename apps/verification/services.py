import json
import subprocess
from datetime import datetime, timedelta, timezone as datetime_timezone

from django.db import transaction
from django.utils import timezone

from apps.identity.models import CredentialStatus, VerificationStatus
from apps.identity.services.zk_claims import CLAIM_AGE_OVER_18

from .models import (
    VerificationRequest,
    VerificationRequestStatus,
)

from apps.audit.services import AuditService
from apps.common.exceptions import InvalidStateTransition
from apps.identity.services.zk_challenge import encode_challenge
from apps.identity.services.zk_challenge import generate_challenge


def _normalize_public_signals(public_signals):
    """Accept both dict-shaped and SnarkJS array-shaped publicSignals payloads."""
    if isinstance(public_signals, dict):
        return public_signals

    if isinstance(public_signals, list):
        if len(public_signals) != 4:
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
    def issue_challenge(verification_request):
        with transaction.atomic():
            locked_request = VerificationRequest.objects.select_for_update().get(
                pk=verification_request.pk
            )
            if locked_request.status != VerificationRequestStatus.PENDING:
                raise InvalidStateTransition(
                    "A challenge can only be issued for a pending request."
                )
            if (
                locked_request.expires_at
                and timezone.now() >= locked_request.expires_at
            ):
                locked_request.status = VerificationRequestStatus.EXPIRED
                locked_request.save(update_fields=["status"])
                expired = True
            else:
                token, expires_at = generate_challenge()
                locked_request.challenge = token
                locked_request.challenge_expires_at = expires_at
                locked_request.save(
                    update_fields=["challenge", "challenge_expires_at"]
                )
                expired = False

        if expired:
            raise InvalidStateTransition("Verification request has expired.")
        return token, expires_at

    @staticmethod
    @transaction.atomic
    def create_request(bank, user, credential, claim):
        """Create a verification request. Caller must ensure caller identity/permissions."""
        if claim != CLAIM_AGE_OVER_18:
            raise InvalidStateTransition("Unsupported verification claim.")
        if credential.user_id != user.pk:
            raise InvalidStateTransition("Credential does not belong to the requested user.")
        if (
            credential.status != CredentialStatus.ACTIVE
            or not credential.is_active
            or (credential.expires_at and timezone.now() >= credential.expires_at)
        ):
            raise InvalidStateTransition("An active credential is required.")

        request = VerificationRequest.objects.create(
            bank=bank,
            user=user,
            credential=credential,
            claim=claim,
            expires_at=timezone.now() + timedelta(days=7),
        )
        AuditService.record_event(
            user=user,
            event_type="VERIFICATION_REQUEST_CREATED",
            entity_type="verification_request",
            entity_id=request.id,
            metadata={"bank_code": bank.bank_code, "claim": claim},
        )
        
        # Create notification for the user
        from .models import Notification, NotificationType
        Notification.objects.create(
            user=user,
            notification_type=NotificationType.VERIFICATION_REQUEST,
            title="Identity verification request",
            message=f"{bank.name} is requesting verification that you are over 18.",
            verification_request=request,
        )
        
        return request

    @staticmethod
    def approve_request(verification_request):
        """Approve a pending verification request (user consent).

        Allowed: PENDING -> APPROVED
        """
        expired = False
        with transaction.atomic():
            verification_request = VerificationRequest.objects.select_for_update().get(
                pk=verification_request.pk
            )
            if verification_request.expires_at and timezone.now() >= verification_request.expires_at:
                verification_request.status = VerificationRequestStatus.EXPIRED
                verification_request.save(update_fields=["status"])
                expired = True
            elif verification_request.status != VerificationRequestStatus.PENDING:
                raise InvalidStateTransition(
                    "Verification request is no longer pending and cannot be approved."
                )
            else:
                verification_request.status = VerificationRequestStatus.APPROVED
                verification_request.user_consented_at = timezone.now()
                update_fields = ["status", "user_consented_at"]
                if (
                    not verification_request.challenge
                    or not verification_request.challenge_expires_at
                    or timezone.now() >= verification_request.challenge_expires_at
                ):
                    (
                        verification_request.challenge,
                        verification_request.challenge_expires_at,
                    ) = generate_challenge()
                    update_fields.extend(
                        ["challenge", "challenge_expires_at"]
                    )
                verification_request.save(update_fields=update_fields)
                AuditService.record_event(
                    user=verification_request.user,
                    event_type="VERIFICATION_REQUEST_APPROVED",
                    entity_type="verification_request",
                    entity_id=verification_request.id,
                    metadata={"claim": verification_request.claim},
                )
        if expired:
            raise InvalidStateTransition("Verification request has expired.")
        return verification_request

    @staticmethod
    def generate_and_verify_proof(verification_request):
        verification_request = (
            VerificationRequest.objects.select_related(
                "credential__source_document",
                "user",
            )
            .get(pk=verification_request.pk)
        )
        if verification_request.status != VerificationRequestStatus.APPROVED:
            raise InvalidStateTransition(
                "User consent is required before proof generation."
            )
        if verification_request.user_consented_at is None:
            raise InvalidStateTransition(
                "An explicit user consent record is required."
            )
        if (
            verification_request.expires_at
            and timezone.now() >= verification_request.expires_at
        ):
            raise InvalidStateTransition("Verification request has expired.")

        credential = verification_request.credential
        document = credential.source_document
        if (
            credential.user_id != verification_request.user_id
            or credential.status != CredentialStatus.ACTIVE
            or not credential.is_active
            or (credential.expires_at and timezone.now() >= credential.expires_at)
        ):
            raise InvalidStateTransition("Credential is not active for this user.")
        if (
            document is None
            or document.user_id != verification_request.user_id
            or document.status != VerificationStatus.VERIFIED
            or document.extracted_dob is None
        ):
            raise InvalidStateTransition(
                "A verified source document with a date of birth is required."
            )

        now = timezone.now()
        challenge, challenge_expires_at = verification_request.challenge, (
            verification_request.challenge_expires_at
        )
        if (
            not challenge
            or not challenge_expires_at
            or now >= challenge_expires_at
        ):
            challenge, challenge_expires_at = generate_challenge()
            with transaction.atomic():
                locked_request = VerificationRequest.objects.select_for_update().get(
                    pk=verification_request.pk
                )
                if (
                    locked_request.status != VerificationRequestStatus.APPROVED
                    or locked_request.user_consented_at is None
                ):
                    raise InvalidStateTransition(
                        "User consent is required before proof generation."
                    )
                locked_request.challenge = challenge
                locked_request.challenge_expires_at = challenge_expires_at
                locked_request.save(
                    update_fields=["challenge", "challenge_expires_at"]
                )

        dob_ts = int(
            datetime.combine(
                document.extracted_dob,
                datetime.min.time(),
                tzinfo=datetime_timezone.utc,
            ).timestamp()
        )
        current_ts = int(now.timestamp())
        from apps.identity.services.zk_prover import Prover

        try:
            proof_bundle = Prover.generate_age_proof(
                credential_id=str(credential.id),
                dob_ts=dob_ts,
                verification_request_id=str(verification_request.id),
                challenge=challenge,
                current_ts=current_ts,
            )
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            raise InvalidStateTransition(
                "Cryptographic proof generation is unavailable."
            ) from exc

        if (
            not isinstance(proof_bundle, dict)
            or "proof" not in proof_bundle
            or "publicSignals" not in proof_bundle
        ):
            raise InvalidStateTransition(
                "Cryptographic proof generation returned invalid data."
            )

        return VerificationService.verify_request(
            verification_request,
            proof=proof_bundle["proof"],
            public_signals=proof_bundle["publicSignals"],
        )

    @staticmethod
    def deny_request(verification_request):
        """Deny a pending verification request.

        Allowed: PENDING -> DENIED
        """
        expired = False
        with transaction.atomic():
            verification_request = VerificationRequest.objects.select_for_update().get(
                pk=verification_request.pk
            )
            if verification_request.expires_at and timezone.now() >= verification_request.expires_at:
                verification_request.status = VerificationRequestStatus.EXPIRED
                verification_request.save(update_fields=["status"])
                expired = True
            elif verification_request.status != VerificationRequestStatus.PENDING:
                raise InvalidStateTransition("Only pending requests can be denied.")
            else:
                verification_request.status = VerificationRequestStatus.DENIED
                verification_request.save(update_fields=["status"])
                AuditService.record_event(
                    user=verification_request.user,
                    event_type="VERIFICATION_REQUEST_DENIED",
                    entity_type="verification_request",
                    entity_id=verification_request.id,
                    metadata={"claim": verification_request.claim},
                )
        if expired:
            raise InvalidStateTransition("Verification request has expired.")
        return verification_request

    @staticmethod
    def verify_request(verification_request, proof: dict, public_signals: dict):
        """Verify a request using provided proof/public signals.

        Allowed: APPROVED -> VERIFIED
        """
        expired = False
        with transaction.atomic():
            current_request = VerificationRequest.objects.select_for_update().get(
                pk=verification_request.pk
            )
            if (
                current_request.expires_at
                and timezone.now() >= current_request.expires_at
            ):
                current_request.status = VerificationRequestStatus.EXPIRED
                current_request.save(update_fields=["status"])
                expired = True
        if expired:
            raise InvalidStateTransition("Verification request has expired.")

        with transaction.atomic():
            verification_request = (
                VerificationRequest.objects.select_for_update()
                .select_related("credential", "user")
                .get(pk=verification_request.pk)
            )
            if (
                verification_request.expires_at
                and timezone.now() >= verification_request.expires_at
            ):
                raise InvalidStateTransition("Verification request has expired.")

            if verification_request.status != VerificationRequestStatus.APPROVED:
                raise InvalidStateTransition("User consent is required before verification.")
            if verification_request.user_consented_at is None:
                raise InvalidStateTransition("An explicit user consent record is required.")
            if verification_request.claim != CLAIM_AGE_OVER_18:
                raise InvalidStateTransition("Unsupported verification claim.")

            credential = verification_request.credential
            if (
                credential.user_id != verification_request.user_id
                or credential.status != CredentialStatus.ACTIVE
                or not credential.is_active
            ):
                raise InvalidStateTransition("Credential is not active for this user.")
            if credential.expires_at and timezone.now() >= credential.expires_at:
                raise InvalidStateTransition("Credential is expired.")

            public_signals = _normalize_public_signals(public_signals)
            challenge = verification_request.challenge
            challenge_expires_at = verification_request.challenge_expires_at
            sent_challenge = public_signals.get("challenge")
            if not challenge or not sent_challenge:
                raise ValueError("Challenge is missing.")
            if str(sent_challenge) not in {
                str(challenge),
                str(encode_challenge(challenge)),
            }:
                raise ValueError("Challenge does not match verification request.")
            if challenge_expires_at and timezone.now() >= challenge_expires_at:
                raise ValueError("Challenge expired.")

            sent_request_id = public_signals.get("verification_request_id")
            expected_request_ids = {
                str(verification_request.id),
                str(encode_challenge(str(verification_request.id))),
            }
            if str(sent_request_id) not in expected_request_ids:
                raise ValueError("Proof is bound to a different verification request.")
            if str(public_signals.get("claim_id")) != "1":
                raise ValueError("Proof is bound to an unsupported claim.")

            current_ts = public_signals.get("current_ts")
            if current_ts is None:
                raise ValueError("Current timestamp is missing from public signals.")
            try:
                current_ts_value = int(current_ts)
            except (TypeError, ValueError) as exc:
                raise ValueError("Current timestamp is invalid.") from exc
            now_ts = int(timezone.now().timestamp())
            if abs(current_ts_value - now_ts) > 300:
                raise ValueError(
                    "Current timestamp is outside the allowed verification window."
                )

            from apps.identity.services.zk_verifier import Verifier

            verifier_payload = [
                str(public_signals.get("current_ts", "")),
                str(public_signals.get("verification_request_id", "")),
                str(public_signals.get("claim_id", "")),
                str(public_signals.get("challenge", "")),
            ]
            try:
                verified = Verifier.verify_age_proof(
                    str(verification_request.id),
                    proof,
                    verifier_payload,
                )
            except (OSError, subprocess.SubprocessError, ValueError) as exc:
                raise InvalidStateTransition(
                    "Cryptographic proof verification is unavailable."
                ) from exc
            if not verified:
                raise ValueError("Proof verification failed.")

            verification_request.status = VerificationRequestStatus.VERIFIED
            verification_request.verified_at = timezone.now()
            verification_request.challenge = None
            verification_request.challenge_expires_at = None
            verification_request.save(
                update_fields=[
                    "status",
                    "verified_at",
                    "challenge",
                    "challenge_expires_at",
                ]
            )
            AuditService.record_event(
                user=verification_request.user,
                event_type="VERIFICATION_REQUEST_VERIFIED",
                entity_type="verification_request",
                entity_id=verification_request.id,
                metadata={
                    "claim": verification_request.claim,
                    "verification_id": str(verification_request.id),
                },
            )
        return verification_request
