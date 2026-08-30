import hashlib
import secrets
from datetime import timedelta
from django.utils import timezone

FIELD_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617


def encode_challenge(challenge: str) -> str:
    """Match the SnarkJS field encoding used by the AGE_OVER_18 circuit."""
    if challenge is None:
        return ""

    if isinstance(challenge, (int, float)):
        return str(int(challenge))

    text = str(challenge)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return str(int(digest, 16) % FIELD_PRIME)


def generate_challenge(length: int = 48, ttl_seconds: int = 300):
    """Generate a URL-safe challenge and timezone-aware expiry timestamp."""
    token = secrets.token_urlsafe(length)
    expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
    return token, expires_at


def is_challenge_valid(challenge: str, expected: str, expires_at) -> bool:
    if not challenge or not expected:
        return False
    if challenge == expected:
        return not (expires_at and timezone.now() > expires_at)

    if encode_challenge(challenge) == str(expected):
        return not (expires_at and timezone.now() > expires_at)

    if encode_challenge(expected) == str(challenge):
        return not (expires_at and timezone.now() > expires_at)

    return False
