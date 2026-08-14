"""
IdentityAI Core Backend Smoke Test

Run from project root:

    python smoke-test.py

Tests the core backend flow without the frontend:

    Registration
        ↓
    Authentication
        ↓
    Identity document upload
        ↓
    Credential creation
        ↓
    Bank creation
        ↓
    Verification request
        ↓
    User consent
        ↓
    ZKP proof generation
        ↓
    Proof submission
        ↓
    Cryptographic verification
        ↓
    Minimal disclosure
        ↓
    Ownership security check
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


# ================================================================
# Django setup
# ================================================================

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()


# ================================================================
# Imports after Django initialization
# ================================================================

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.banks.models import Bank
from apps.identity.models import (
    IdentityDocument,
    VerifiableCredential,
)
from apps.verification.models import (
    VerificationRequest,
)


# ================================================================
# Test state
# ================================================================

PASSED = 0
FAILED = 0

TEST_USERNAME = "smoke_test_user"
TEST_EMAIL = "smoke@test.local"
TEST_PHONE = "9800000001"

ATTACKER_USERNAME = "smoke_attacker"
ATTACKER_EMAIL = "attacker@test.local"
ATTACKER_PHONE = "9800000002"

BANK_CODE = "SMOKE_BANK"


# ================================================================
# Helpers
# ================================================================

def record_test(
    name: str,
    condition: bool,
    details: str = "",
) -> None:
    global PASSED, FAILED

    if condition:
        PASSED += 1
        print(f"[PASS] {name}")
    else:
        FAILED += 1
        print(f"[FAIL] {name}")

        if details:
            print(f"       {details}")


def assert_status(
    response,
    expected: int,
    name: str,
) -> None:
    actual = response.status_code

    try:
        data = response.data
    except AttributeError:
        data = response.content[:500]

    record_test(
        name,
        actual == expected,
        (
            f"Expected HTTP {expected}, "
            f"got HTTP {actual}. "
            f"Response: {data}"
        ),
    )


def response_data(response) -> dict:
    data = getattr(response, "data", {})

    if isinstance(data, dict):
        return data

    return {}


# ================================================================
# Cleanup
# ================================================================

def cleanup() -> None:
    """
    Remove only records created by this smoke test.
    """

    # Delete dependent objects first to avoid ProtectedError.
    VerificationRequest.objects.filter(
        user__username__in=[
            TEST_USERNAME,
            ATTACKER_USERNAME,
            f"{ATTACKER_USERNAME}_2",
        ]
    ).delete()

    IdentityDocument.objects.filter(
        user__username__in=[
            TEST_USERNAME,
            ATTACKER_USERNAME,
            f"{ATTACKER_USERNAME}_2",
        ]
    ).delete()

    VerifiableCredential.objects.filter(
        user__username__in=[
            TEST_USERNAME,
            ATTACKER_USERNAME,
            f"{ATTACKER_USERNAME}_2",
        ]
    ).delete()

    Bank.objects.filter(
        bank_code=BANK_CODE
    ).delete()

    User.objects.filter(
        username__in=[
            TEST_USERNAME,
            ATTACKER_USERNAME,
            f"{ATTACKER_USERNAME}_2",
            'smoke_bankstaff'
        ]
    ).delete()


# ================================================================
# Main
# ================================================================

def main() -> int:

    global PASSED, FAILED

    print()
    print("=" * 70)
    print("IdentityAI Backend Smoke Test")
    print("=" * 70)
    print()

    cleanup()

    # DRF API client.
    # Using APIClient allows:
    #     client.credentials(...)
    # for JWT authentication.
    client = APIClient()

    # Avoid Django's default testserver host.
    client.defaults["HTTP_HOST"] = "127.0.0.1"

    # ============================================================
    # 1. REGISTRATION
    # ============================================================

    print("1. Registration")
    print("-" * 70)

    response = client.post(
        "/api/accounts/register/",
        {
            "username": TEST_USERNAME,
            "email": TEST_EMAIL,
            "password": "StrongPassword123!",
            "phone_number": TEST_PHONE,
        },
        format="json",
    )

    assert_status(
        response,
        201,
        "User registration",
    )

    user = User.objects.filter(
        username=TEST_USERNAME
    ).first()

    record_test(
        "User created in database",
        user is not None,
    )

    if user is None:
        print()
        print("Registration failed.")
        cleanup()
        return 1

    # ============================================================
    # 2. AUTHENTICATION
    # ============================================================

    print()
    print("2. Authentication")
    print("-" * 70)

    data = response_data(response)

    access_token = data.get("access")

    record_test(
        "Registration returns access token",
        bool(access_token),
        f"Response keys: {list(data.keys())}",
    )

    if not access_token:
        print()
        print("No access token returned.")
        cleanup()
        return 1

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # ============================================================
    # 3. IDENTITY DOCUMENT UPLOAD
    # ============================================================

    print()
    print("3. Identity Document")
    print("-" * 70)

    fake_document = SimpleUploadedFile(
        "smoke_test.jpg",
        b"fake-image-content",
        content_type="image/jpeg",
    )

    response = client.post(
        "/api/identity/documents/",
        {
            "document_type": "CITIZENSHIP",
            "document_file": fake_document,
        },
        format="multipart",
    )

    assert_status(
        response,
        201,
        "Identity document upload",
    )

    document = (
        IdentityDocument.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    record_test(
        "Identity document created",
        document is not None,
    )

    # ============================================================
    # 4. CREDENTIAL
    # ============================================================

    print()
    print("4. Credential")
    print("-" * 70)

    credential = (
        VerifiableCredential.objects
        .filter(user=user)
        .order_by("-issued_at")
        .first()
    )

    record_test(
        "Credential created",
        credential is not None,
    )

    user.refresh_from_db()

    record_test(
        "User marked identity verified",
        user.is_identity_verified is True,
    )

    if credential is None:
        print()
        print(
            "Credential creation failed. "
            "Stopping dependent tests."
        )
        cleanup()
        return 1

    # ============================================================
    # 5. BANK
    # ============================================================

    print()
    print("5. Bank")
    print("-" * 70)

    bank = Bank.objects.create(
        name="IdentityAI Smoke Bank",
        bank_code=BANK_CODE,
        api_key="smoke-test-api-key",
    )

    record_test(
        "Bank created",
        bank.pk is not None,
    )

    # ============================================================
    # 6. VERIFICATION REQUEST
    # ============================================================

    print()
    print("6. Verification Request")
    print("-" * 70)

    response = client.post(
        "/api/verification/request/",
        {
            "bank_code": BANK_CODE,

            # Intentionally included because the current API
            # exposes this field. The security test later checks
            # whether it can be abused.
            "user_id": user.id,

            "claim": "AGE_OVER_18",
        },
        format="json",
    )

    assert_status(
        response,
        201,
        "Verification request creation",
    )

    verification_request = (
        VerificationRequest.objects
        .filter(
            bank=bank,
            user=user,
        )
        .order_by("-created_at")
        .first()
    )

    record_test(
        "Verification request created",
        verification_request is not None,
    )

    if verification_request is None:
        cleanup()
        return 1

    # ============================================================
    # 6a. CHALLENGE (bank/staff)
    # ============================================================

    print()
    print("6a. Challenge issuance (bank/staff)")
    print("-" * 70)

    # Create a bank staff user and request a challenge
    staff = User.objects.create_user(username='smoke_bankstaff', email='staff@test.local', password='pass', is_staff=True)
    client.force_authenticate(user=staff)

    ch_resp = client.post(f"/api/verification/{verification_request.id}/challenge/")
    assert_status(ch_resp, 200, "Challenge issuance")

    challenge = response_data(ch_resp).get("challenge")

    record_test(
        "Challenge provided",
        bool(challenge),
    )

    # ============================================================
    # 7. CONSENT
    # ============================================================

    print()
    print("7. User Consent")
    print("-" * 70)

    # Switch back to holder (user) and give consent
    client.force_authenticate(user=None)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    response = client.post(
        f"/api/verification/"
        f"{verification_request.id}/consent/"
    )

    assert_status(
        response,
        200,
        "User consent",
    )

    verification_request.refresh_from_db()

    record_test(
        "Request moved to APPROVED",
        verification_request.status == "APPROVED",
        f"Actual status: {verification_request.status}",
    )

    # ============================================================
    # 8. VERIFICATION (real prover)
    # ============================================================

    print()
    print("8. Verification (using real V0.4 prover)")
    print("-" * 70)

    # Generate a proof using the project's prover implementation.
    # Ensure the challenge issued by the bank is used and the prover
    # runs the node/snarkjs path by removing any fallback artifacts.
    from django.utils import timezone
    from datetime import datetime
    from apps.identity.services.zk_prover import Prover

    # Ensure we have the matching credential and DOB
    identity_doc = (
        IdentityDocument.objects
        .filter(user=user)
        .order_by("-created_at")
        .first()
    )

    record_test(
        "Identity doc available for proof generation",
        identity_doc is not None,
    )

    dob = getattr(identity_doc, "extracted_dob", None)

    record_test(
        "Document contains extracted DOB",
        dob is not None,
    )

    if dob is None:
        print()
        print("Cannot generate proof without DOB on identity document.")
        cleanup()
        return 1

    dob_ts = int(datetime.combine(dob, datetime.min.time()).timestamp())
    current_ts = int(timezone.now().timestamp())

    # Ensure the zkey is in the expected location so the Node prover can run snarkjs.
    # The build artifacts are stored under docs/zk_build; copy the zkey into docs/ if needed.
    try:
        zkey_src = PROJECT_ROOT / 'docs' / 'zk_build' / 'age_over_18.zkey'
        zkey_dst = PROJECT_ROOT / 'docs' / 'age_over_18.zkey'
        if zkey_src.exists() and not zkey_dst.exists():
            import shutil

            shutil.copyfile(str(zkey_src), str(zkey_dst))
            record_test('ZKey copied to prover path', True)
        elif zkey_dst.exists():
            record_test('ZKey already present', True)
        else:
            record_test('ZKey missing (no copy available)', False, f"Checked {zkey_src}")
    except Exception as exc:
        record_test('ZKey presence check', False, str(exc))

    # Remove any precomputed artifact for this request so prover cannot fallback
    artifact_path = PROJECT_ROOT / 'docs' / f'proof_{verification_request.id}.json'
    verified_artifact = PROJECT_ROOT / 'docs' / f'verified_{verification_request.id}.json'
    try:
        if artifact_path.exists():
            artifact_path.unlink()
    except Exception:
        pass
    try:
        if verified_artifact.exists():
            verified_artifact.unlink()
    except Exception:
        pass

    # Call the prover to create proof + publicSignals
    try:
        proof_bundle = Prover.generate_age_proof(
            credential_id=str(credential.id),
            dob_ts=dob_ts,
            verification_request_id=str(verification_request.id),
            challenge=challenge,
            current_ts=current_ts,
        )
    except Exception as exc:
        record_test(
            "Prover executed successfully",
            False,
            f"Prover failed: {exc}",
        )
        cleanup()
        return 1

    proof = proof_bundle.get("proof")
    public_signals = proof_bundle.get("publicSignals")

    record_test(
        "Proof generated",
        proof is not None,
    )

    record_test(
        "Public signals generated",
        public_signals is not None,
    )

    if proof is None or public_signals is None:
        print()
        print("Proof generation failed or returned incomplete bundle.")
        cleanup()
        return 1

    # Submit proof as the bank/staff (verifier)
    client.force_authenticate(user=staff)
    verify_resp = client.post(
        f"/api/verification/{verification_request.id}/verify/",
        data={
            "proof": proof,
            "publicSignals": public_signals,
        },
        format='json',
    )

    assert_status(
        verify_resp,
        200,
        "Identity verification",
    )

    verification_request.refresh_from_db()

    record_test(
        "Request moved to VERIFIED",
        verification_request.status == "VERIFIED",
        f"Actual status: {verification_request.status}",
    )

    # ============================================================
    # 9. MINIMAL DISCLOSURE
    # ============================================================

    print()
    print("9. Minimal Disclosure")
    print("-" * 70)

    data = response_data(verify_resp)

    forbidden_fields = {
        "nid",
        "NID",
        "dob",
        "DOB",
        "date_of_birth",
        "address",
        "document",
        "document_file",
        "identity_document",
        "credential_hash",
    }

    leaked_fields = forbidden_fields.intersection(
        data.keys()
    )

    record_test(
        "Bank response uses minimal disclosure",
        not leaked_fields,
        f"Forbidden fields: {sorted(leaked_fields)}",
    )

    record_test(
        "Verification result contains verified=true",
        data.get("verified") is True,
        f"Response: {data}",
    )

    record_test(
        "Verification result contains verification_id",
        bool(data.get("verification_id")),
        f"Response: {data}",
    )

    record_test(
        "Verification result contains timestamp",
        bool(data.get("timestamp")),
        f"Response: {data}",
    )

    # ============================================================
    # 10. SECURITY: IMPERSONATION
    # ============================================================

    print()
    print("10. Ownership Security")
    print("-" * 70)

    attacker_client = APIClient()
    attacker_client.defaults["HTTP_HOST"] = "127.0.0.1"

    attacker_response = attacker_client.post(
        "/api/accounts/register/",
        {
            "username": ATTACKER_USERNAME,
            "email": ATTACKER_EMAIL,
            "password": "StrongPassword123!",
            "phone_number": ATTACKER_PHONE,
        },
        format="json",
    )

    assert_status(
        attacker_response,
        201,
        "Attacker test user registration",
    )

    attacker_data = response_data(
        attacker_response
    )

    attacker_token = attacker_data.get("access")

    record_test(
        "Attacker receives authentication token",
        bool(attacker_token),
        f"Response keys: {list(attacker_data.keys())}",
    )

    if attacker_token:

        attacker_client.credentials(HTTP_AUTHORIZATION=(f"Bearer {attacker_token}"))

    # Attempt to create a verification request for another user.
    response = attacker_client.post(
        "/api/verification/request/",
        {
            "bank_code": BANK_CODE,
            "user_id": user.id,
            "claim": "AGE_OVER_18",
        },
        format="json",
    )

    record_test(
        "Client cannot impersonate another user",
        response.status_code in {
            400,
            403,
            404,
        },
        (
            f"Expected denial. "
            f"Got HTTP {response.status_code}. "
            f"Response: {getattr(response, 'data', None)}"
        ),
    )

    # ============================================================
    # 11. FINAL RESULT
    # ============================================================

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(f"Passed: {PASSED}")
    print(f"Failed: {FAILED}")
    print()

    if FAILED == 0:

        print("ALL SMOKE TESTS PASSED")

        cleanup()
        return 0

    print("SMOKE TEST FAILED")

    cleanup()
    return 1


# ============================================================
# Entry point
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())
