import hashlib
import hmac
import secrets

from django.db import transaction

from .models import Bank


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


class BankCredentialService:
    @staticmethod
    @transaction.atomic
    def provision_bank(*, name: str, bank_code: str, webhook_url: str = ""):
        if Bank.objects.filter(bank_code__iexact=bank_code).exists():
            raise ValueError("A bank with this code already exists.")

        api_key = secrets.token_urlsafe(32)
        bank = Bank.objects.create(
            name=name,
            bank_code=bank_code,
            webhook_url=webhook_url or None,
            api_key_hash=hash_api_key(api_key),
        )
        return bank, api_key

    @staticmethod
    def authenticate(*, bank_code: str, api_key: str):
        bank = Bank.objects.filter(
            bank_code__iexact=bank_code,
            is_active=True,
        ).first()
        if bank is None or not hmac.compare_digest(
            bank.api_key_hash,
            hash_api_key(api_key),
        ):
            return None
        return bank

    @staticmethod
    def authenticate_header(api_key: str):
        if not api_key:
            return None

        key_hash = hash_api_key(api_key)
        return Bank.objects.filter(
            api_key_hash=key_hash,
            is_active=True,
        ).first()
