import hashlib
from datetime import timedelta

from django.utils import timezone

from apps.identity.models import VerifiableCredential


class CredentialService:
    @staticmethod
    def list_for_user(user):
        return VerifiableCredential.objects.filter(user=user).order_by("-issued_at")

    @staticmethod
    def create_credential(
        user,
        nid: str,
        source_document=None,
    ) -> VerifiableCredential:
        if source_document is not None and source_document.user_id != user.pk:
            raise ValueError("Source document does not belong to the credential owner.")

        payload = f"{user.id}:{nid}:{timezone.now().isoformat()}"
        credential_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        credential = VerifiableCredential.objects.create(
            user=user,
            source_document=source_document,
            credential_hash=credential_hash,
            issuer="Identity Platform",
            expires_at=timezone.now() + timedelta(days=365),
        )

        return credential
