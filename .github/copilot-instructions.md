# IdentityAI Backend - Copilot Instructions

## Project purpose

IdentityAI is a privacy-preserving digital identity verification platform for banks.

The core product flow is:

User
-> identity document submission
-> OCR extraction
-> external identity verification
-> credential issuance
-> bank verification request
-> explicit user consent
-> privacy-preserving verification
-> bank receives only the minimum required verification result.

The platform must NOT unnecessarily expose the user's raw identity information to banks.

## Current architecture

This project is currently a modular Django monolith.

Current applications:

- apps.accounts
- apps.identity
- apps.verification
- apps.banks

Do NOT convert these into independent microservices unless explicitly instructed.

## Architecture rules

Use this dependency direction:

API/View
-> Serializer
-> Service
-> Model

Views must remain thin.

Business logic belongs in service modules.

Do not put substantial business logic inside serializers or views.

Do not make database queries from unrelated modules when a service layer is appropriate.

Do not introduce circular imports.

## Identity architecture

Identity processing is separated into:

- OCRService
- NIDMCService
- ZKPService
- BlockchainService
- NotificationService

These are abstraction boundaries.

Current implementations may be mocks.

Do not remove these boundaries merely to simplify the implementation.

Real infrastructure will eventually replace these implementations.

## Privacy requirements

Never return raw identity documents to banks.

Never expose:

- raw citizenship documents
- raw document images
- NID numbers
- dates of birth
- addresses
- internal credential data

unless the feature explicitly requires them and the request is authorized.

The bank verification API should return the minimum required information.

Example:

{
    "verified": true,
    "timestamp": "...",
    "verification_id": "..."
}

## Consent requirement

Every bank verification request requires explicit user consent.

The valid state transition is:

PENDING
-> APPROVED
-> VERIFIED

A request must NOT become VERIFIED without user consent.

Never bypass the consent state.

## Credential architecture

Credentials represent a verified identity state.

Do not store unnecessary raw identity information inside the credential model.

Credential hashes, identifiers, timestamps, status and blockchain references are acceptable.

## Security requirements

Never hard-code:

- API keys
- passwords
- JWT secrets
- database passwords
- private keys
- encryption keys
- external service credentials

Use environment variables.

Never commit .env files.

Never disable authentication or permission checks just to make a test pass.

Never expose sensitive data in API responses or logs.

## Database requirements

Use Django ORM.

Do not use raw SQL unless explicitly required.

Use transactions for identity and verification state changes.

Use UUIDs for externally exposed identity and verification identifiers where appropriate.

Use migrations for all schema changes.

Never manually edit an existing migration that has already been committed unless explicitly instructed.

## API requirements

Use Django REST Framework.

Use serializers for input validation and response serialization.

Use explicit permission classes.

Do not trust user_id values supplied by clients when the authenticated user should determine ownership.

## Testing requirements

Every meaningful business rule must have a test.

At minimum test:

- user registration
- identity verification
- failed identity verification
- credential creation
- bank verification request
- consent
- denial
- verification without consent
- unauthorized access
- expired credentials

Run:

python manage.py check
python manage.py test

before considering a change complete.

## Change policy

Before modifying code:

1. Inspect the relevant files.
2. Identify existing architecture.
3. Preserve existing working behavior.
4. Explain what will change.
5. Make the smallest required change.

Do NOT rewrite unrelated files.

Do NOT rename existing models, APIs, modules or fields without explicit instruction.

Do NOT replace working implementations with hypothetical architecture.

Do NOT add dependencies unless they are required.

## Important rule

If existing code contradicts a proposed change, stop and inspect the existing implementation.

Do not assume the existing code is wrong.

Preserve backward compatibility unless explicitly told otherwise.

Before finishing a task, inspect the git diff and identify every changed file.
