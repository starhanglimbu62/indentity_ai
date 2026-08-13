import secrets
from datetime import timedelta
from django.utils import timezone


def generate_challenge(length: int = 48, ttl_seconds: int = 300):
    """Generate a URL-safe challenge and timezone-aware expiry timestamp."""
    token = secrets.token_urlsafe(length)
    expires_at = timezone.now() + timedelta(seconds=ttl_seconds)
    return token, expires_at


def is_challenge_valid(challenge: str, expected: str, expires_at) -> bool:
    if not challenge or not expected:
        return False
    if challenge != expected:
        return False
    if expires_at and timezone.now() > expires_at:
        return False
    return True
