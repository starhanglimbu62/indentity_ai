# IdentityAI Agent Context

## Project

IdentityAI is a privacy-preserving identity verification platform for banks.

The core mechanism is:

1. User submits identity document.
2. Document is temporarily processed.
3. OCR extracts identity information.
4. External identity authority verifies identity.
5. Platform issues a privacy-preserving credential.
6. Bank requests a verification claim.
7. User explicitly approves the request.
8. Platform verifies the claim.
9. Bank receives only the minimum verification result.

## Current architecture

The project is currently a modular Django monolith.

Applications:

- accounts
- identity
- verification
- banks

Do not convert these into independent microservices unless explicitly requested.

## Current implementation status

### Accounts

Implemented:
- custom User model
- email
- phone number
- identity verification status
- JWT authentication

### Identity

Implemented:
- IdentityDocument
- VerifiableCredential
- IdentityService
- OCRService mock
- NIDMCService mock
- ZKPService placeholder

### Verification

Implemented:
- VerificationRequest
- bank verification request
- user consent
- verification state transition

### Banks

Implemented:
- Bank model

## Explicitly not production-ready

OCR is currently mocked.

NIDMC integration is currently mocked.

ZKP implementation is currently a placeholder.

Blockchain integration does not exist yet.

Kafka does not exist yet.

Redis does not exist yet.

Do not claim these systems are implemented.

## Non-negotiable business rule

A verification request cannot go directly from:

PENDING -> VERIFIED

It must go:

PENDING -> APPROVED -> VERIFIED

User consent is mandatory.

## Privacy rule

Banks must not receive raw identity documents or unnecessary identity attributes.

Default successful response:

{
    "verified": true,
    "timestamp": "...",
    "verification_id": "..."
}
