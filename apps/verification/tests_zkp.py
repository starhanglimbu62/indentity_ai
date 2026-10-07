from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.banks.models import Bank
from apps.banks.services import hash_api_key
from apps.identity.models import VerifiableCredential
from apps.identity.services.zk_prover import Prover
from apps.identity.services.zk_verifier import Verifier
from apps.verification.models import VerificationRequestStatus


AGE_THRESHOLD_SECONDS = 567648000


class ZKPIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="proof-user",
            email="proof-user@example.com",
            password="pass",
        )
        self.bank = Bank.objects.create(
            name="Proof Test Bank",
            bank_code="PROOF",
            api_key_hash=hash_api_key("proof-test-api-key"),
        )
        self.credential = VerifiableCredential.objects.create(
            user=self.user,
            credential_hash="proof-credential-hash",
            expires_at=timezone.now() + timedelta(days=30),
        )
        self.client = APIClient()

    def create_request(self):
        self.client.credentials(HTTP_X_BANK_API_KEY="proof-test-api-key")
        response = self.client.post(
            "/api/verification/request/",
            {
                "bank_code": self.bank.bank_code,
                "user_id": self.user.pk,
                "claim": "AGE_OVER_18",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        request_id = response.data["id"]

        challenge_response = self.client.post(
            f"/api/verification/{request_id}/challenge/"
        )
        self.assertEqual(challenge_response.status_code, 200)
        return request_id, challenge_response.data["challenge"]

    def generate_age_proof(self, request_id, challenge):
        current_ts = int(timezone.now().timestamp())
        proof = Prover.generate_age_proof(
            credential_id=str(self.credential.id),
            dob_ts=current_ts - AGE_THRESHOLD_SECONDS - 1000,
            verification_request_id=str(request_id),
            challenge=challenge,
            current_ts=current_ts,
        )
        return proof

    def approve_request(self, request_id):
        self.client.credentials()
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/verification/{request_id}/consent/",
            {"approved": True},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

    def submit_proof(self, request_id, proof):
        self.client.force_authenticate(user=None)
        self.client.credentials(HTTP_X_BANK_API_KEY="proof-test-api-key")
        return self.client.post(
            f"/api/verification/{request_id}/verify/",
            {
                "proof": proof["proof"],
                "publicSignals": proof["publicSignals"],
            },
            format="json",
        )

    def test_valid_age_proof_is_cryptographically_verified(self):
        request_id, challenge = self.create_request()
        self.approve_request(request_id)
        proof = self.generate_age_proof(request_id, challenge)

        response = self.submit_proof(request_id, proof)

        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data["verified"])
        self.assertIsNotNone(response.data["timestamp"])

    def test_wrong_challenge_is_rejected_before_proof_verification(self):
        request_id, challenge = self.create_request()
        self.approve_request(request_id)
        proof = self.generate_age_proof(request_id, challenge)
        proof["publicSignals"][3] = "wrong-challenge"

        response = self.submit_proof(request_id, proof)

        self.assertEqual(response.status_code, 400)

    def test_verification_without_consent_is_rejected(self):
        request_id, challenge = self.create_request()
        proof = self.generate_age_proof(request_id, challenge)

        response = self.submit_proof(request_id, proof)

        self.assertEqual(response.status_code, 400)

    def test_changed_request_signal_is_rejected(self):
        request_id, challenge = self.create_request()
        self.approve_request(request_id)
        proof = self.generate_age_proof(request_id, challenge)
        proof["publicSignals"][1] = "1"

        response = self.submit_proof(request_id, proof)

        self.assertEqual(response.status_code, 400)

    def test_verifier_failure_does_not_use_precomputed_success(self):
        with patch(
            "apps.identity.services.zk_verifier._call_node_verifier",
            side_effect=FileNotFoundError("verifier unavailable"),
        ):
            with self.assertRaises(FileNotFoundError):
                Verifier.verify_age_proof("test-request", {}, [])

    def test_request_transitions_only_after_successful_proof(self):
        request_id, challenge = self.create_request()
        self.approve_request(request_id)
        proof = self.generate_age_proof(request_id, challenge)
        self.submit_proof(request_id, proof)

        from apps.verification.models import VerificationRequest

        verification_request = VerificationRequest.objects.get(pk=request_id)
        self.assertEqual(
            verification_request.status,
            VerificationRequestStatus.VERIFIED,
        )
        self.assertIsNone(verification_request.challenge)
