---
applyTo: "apps/identity/**/*.py,apps/verification/**/*.py,apps/banks/**/*.py"
---

# IdentityAI security rules

This system handles identity verification.

Treat identity information as sensitive.

## Never log

- NID numbers
- identity document contents
- passwords
- access tokens
- refresh tokens
- private keys

## Never expose

Never return raw identity data to banks unless explicitly required by an authorized feature.

## Consent

Verification requests must require explicit user consent.

Never allow:

PENDING -> VERIFIED

The valid transition is:

PENDING -> APPROVED -> VERIFIED

## Verification requirements

Any credential verification must check:

- credential exists
- credential is active
- credential belongs to the intended user
- verification request is valid
- user consent exists

Use atomic transactions for state transitions.

All security-sensitive changes should be covered by tests.
