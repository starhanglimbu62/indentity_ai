from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .services import BankCredentialService


class BankAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get("X-Bank-API-Key", "").strip()
        if not api_key:
            return None

        bank = BankCredentialService.authenticate_header(api_key)
        if bank is None:
            raise AuthenticationFailed("Invalid bank credentials.")
        return bank, None

    def authenticate_header(self, request):
        return "X-Bank-API-Key"
