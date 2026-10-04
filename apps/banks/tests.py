from django.test import TestCase
from rest_framework.test import APIClient

from apps.banks.models import Bank


class BankAuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_bank_registration_and_login(self):
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
        self.assertTrue(response.data["api_key"])

        bank = Bank.objects.get(bank_code="ALPHA")
        login_response = self.client.post(
            "/api/banks/login/",
            {"bank_code": "ALPHA", "api_key": bank.api_key},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.data["bank_code"], "ALPHA")
        self.assertEqual(login_response.data["name"], "Alpha Bank")
