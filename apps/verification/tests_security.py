from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone

from apps.accounts.models import User
from apps.banks.models import Bank
from apps.identity.models import VerifiableCredential
from apps.verification.models import VerificationRequest, VerificationRequestStatus
from apps.verification.services import VerificationService
from apps.common.exceptions import InvalidStateTransition


class VerificationSecurityTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='alice', email='alice@example.com', password='pass')
        self.user_b = User.objects.create_user(username='bob', email='bob@example.com', password='pass')
        self.staff = User.objects.create_user(username='staff', email='staff@example.com', password='pass', is_staff=True)
        self.bank = Bank.objects.create(name='Test Bank', bank_code='TEST', api_key='APIKEY')
        # credential for user_b
        self.cred_b = VerifiableCredential.objects.create(user=self.user_b, credential_hash='hash-b')

        self.client = APIClient()

    def test_non_staff_cannot_create_verification_request(self):
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.post('/api/verification/request/', data={
            'bank_code': 'TEST',
            'user_id': str(self.user_b.id),
            'claim': 'AGE_OVER_18',
        }, format='json')
        # non-staff must be forbidden from creating bank verification requests
        self.assertEqual(resp.status_code, 403)

    def test_staff_can_create_request_for_user(self):
        self.client.force_authenticate(user=self.staff)
        resp = self.client.post('/api/verification/request/', data={
            'bank_code': 'TEST',
            'user_id': str(self.user_b.id),
            'claim': 'AGE_OVER_18',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('id', resp.data)

    def test_user_cannot_approve_other_users_request(self):
        # staff creates request for user_b
        req = VerificationService.create_request(bank=self.bank, user=self.user_b, credential=self.cred_b, claim='AGE_OVER_18')
        self.client.force_authenticate(user=self.user_a)
        resp = self.client.post(f'/api/verification/{req.id}/consent/')
        # Should not be allowed / should not find a request for this user
        self.assertEqual(resp.status_code, 404)

    def test_pending_cannot_transition_to_verified_via_service(self):
        req = VerificationService.create_request(bank=self.bank, user=self.user_b, credential=self.cred_b, claim='AGE_OVER_18')
        # Attempt to verify while still PENDING should raise InvalidStateTransition
        with self.assertRaises(InvalidStateTransition):
            VerificationService.verify_request(req, proof={}, public_signals={})

    def test_denied_cannot_transition_to_verified(self):
        req = VerificationService.create_request(bank=self.bank, user=self.user_b, credential=self.cred_b, claim='AGE_OVER_18')
        # Deny the request
        VerificationService.deny_request(req)
        self.assertEqual(req.status, VerificationRequestStatus.DENIED)
        # Attempt to verify should raise InvalidStateTransition
        with self.assertRaises(InvalidStateTransition):
            VerificationService.verify_request(req, proof={}, public_signals={})
