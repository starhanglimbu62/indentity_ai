from django.test import TestCase
from django.test import Client
from rest_framework.test import APIClient

from apps.accounts.models import User

from apps.banks.models import Bank
from apps.banks.services import hash_api_key


class BankAuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="StrongPassword123!",
        )

    def test_bank_registration_is_privileged_and_key_is_only_returned_once(self):
        response = self.client.post(
            "/api/banks/register/",
            {
                "name": "Untrusted Bank",
                "bank_code": "UNTRUSTED",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            "/api/banks/register/",
            {
                "name": "Alpha Bank",
                "bank_code": "ALPHA",
                "webhook_url": "https://example.com/webhook",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        api_key = response.data["api_key"]
        self.assertTrue(api_key)

        bank = Bank.objects.get(bank_code="ALPHA")
        self.assertEqual(bank.api_key_hash, hash_api_key(api_key))
        self.assertNotEqual(bank.api_key_hash, api_key)

        login_response = self.client.post(
            "/api/banks/login/",
            {"bank_code": "ALPHA", "api_key": api_key},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.data["bank_code"], "ALPHA")
        self.assertEqual(login_response.data["name"], "Alpha Bank")
        self.assertNotIn("api_key", login_response.data)

        self.client.force_authenticate(user=None)
        info_response = self.client.get(
            "/api/banks/info/",
            HTTP_X_BANK_API_KEY=api_key,
        )
        self.assertEqual(info_response.status_code, 200)
        self.assertNotIn("api_key", info_response.data)

    def test_bank_api_key_header_is_allowed_by_browser_cors_preflight(self):
        response = Client().options(
            "/api/verification/bank-requests/",
            HTTP_ORIGIN="http://127.0.0.1:3000",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="x-bank-api-key",
        )

        self.assertEqual(response.status_code, 200)
        allowed_headers = response["access-control-allow-headers"].lower()
        self.assertIn("x-bank-api-key", allowed_headers)
