from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
	register_url = reverse("register")
	login_url = reverse("login")
	protected_url = reverse("identity-document-upload")

	def registration_payload(self, **overrides):
		payload = {
			"legal_name": "John Doe",
			"username": "johndoe",
			"email": "john@example.com",
			"password": "Strong-password-123",
		}
		payload.update(overrides)
		return payload

	def test_valid_registration_returns_jwt_and_stores_legal_name(self):
		response = self.client.post(
			self.register_url,
			self.registration_payload(),
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)
		user = User.objects.get(username="johndoe")
		self.assertEqual(user.first_name, "John Doe")
		self.assertNotIn("password", response.data)

	def test_registration_requires_legal_name(self):
		payload = self.registration_payload()
		del payload["legal_name"]

		response = self.client.post(self.register_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("legal_name", response.data)

	def test_duplicate_registration_is_rejected(self):
		payload = self.registration_payload()
		self.client.post(self.register_url, payload, format="json")

		response = self.client.post(self.register_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("username", response.data)

	def test_login_by_username_returns_jwt(self):
		User.objects.create_user(
			username="johndoe",
			email="john@example.com",
			password="Strong-password-123",
		)

		response = self.client.post(
			self.login_url,
			{"username": "johndoe", "password": "Strong-password-123"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data["access"])
		self.assertTrue(response.data["refresh"])

	def test_login_by_email_returns_jwt(self):
		User.objects.create_user(
			username="johndoe",
			email="john@example.com",
			password="Strong-password-123",
		)

		response = self.client.post(
			self.login_url,
			{"username": "john@example.com", "password": "Strong-password-123"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data["access"])

	def test_invalid_login_is_rejected(self):
		User.objects.create_user(
			username="johndoe",
			email="john@example.com",
			password="Strong-password-123",
		)

		response = self.client.post(
			self.login_url,
			{"username": "johndoe", "password": "wrong-password"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_protected_endpoint_rejects_missing_jwt(self):
		document = SimpleUploadedFile(
			"identity.png", b"image data", content_type="image/png"
		)

		response = self.client.post(
			self.protected_url,
			{"document_file": document},
			format="multipart",
		)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_protected_endpoint_accepts_valid_jwt(self):
		registration = self.client.post(
			self.register_url,
			self.registration_payload(),
			format="json",
		)
		self.client.credentials(
			HTTP_AUTHORIZATION=f"Bearer {registration.data['access']}"
		)
		document = SimpleUploadedFile(
			"identity.png", b"image data", content_type="image/png"
		)

		response = self.client.post(
			self.protected_url,
			{"document_file": document},
			format="multipart",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
