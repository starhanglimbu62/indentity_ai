import hashlib
from datetime import timedelta

from django.utils import timezone

from apps.identity.models import VerifiableCredential


class CredentialService:
    @staticmethod
    def create_credential(user, nid: str) -> VerifiableCredential:
        payload = f"{user.id}:{nid}:{timezone.now().isoformat()}"
        credential_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        credential = VerifiableCredential.objects.create(
            user=user,
            credential_hash=credential_hash,
            issuer="Identity Platform",
            expires_at=timezone.now() + timedelta(days=365),
        )

        return credential
