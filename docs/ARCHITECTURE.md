# IdentityAI Architecture

## Current state

IdentityAI is a Django modular monolith.

## Applications

### accounts

Responsible for:
- user registration
- authentication
- user profile
- identity verification status

### identity

Responsible for:
- identity document lifecycle
- OCR abstraction
- NIDMC abstraction
- credential issuance
- identity verification
- temporary file handling and cleanup

### verification

Responsible for:
- bank verification requests
- user consent
- verification state transitions
- verification results

### banks

Responsible for:
- bank registration
- bank integration metadata
- bank authentication

### audit

Responsible for:
- sanitized audit trails
- event logging for KYC processing steps
- metadata-only records without raw sensitive identity data

## Core state machine

Identity document:

PENDING
-> PROCESSING
-> VERIFIED

or:

PENDING
-> PROCESSING
-> FAILED

Verification request:

PENDING
-> APPROVED
-> VERIFIED

or:

PENDING
-> DENIED

## Core service boundaries

OCRService
NIDMCService
ZKPService
BlockchainService
NotificationService

### V0.2 KYC service modules

`apps/identity/services/`
- `document_handling.py` - file validation and raw-document cleanup
- `preprocessing.py` - image preparation for OCR
- `ocr.py` - structured OCR extraction mock
- `extraction.py` - normalization of OCR output
- `validation.py` - field, format, and confidence validation
- `nidmc.py` - mock identity authority verification boundary
- `credential.py` - credential creation logic

## V0.4 ZKP (AGE_OVER_18)

V0.4 introduces a real zero-knowledge proof flow for the single claim AGE_OVER_18. The architecture follows a strict service boundary, with the cryptographic proving/verification performed via Circom + snarkjs (PLONK). Key points:

- A new ZKP boundary is added in the codebase (apps.identity.services.zk_*) to orchestrate challenge generation and call out to a prover/verifier.
- The actual cryptographic work is performed by a Node/snarkjs helper (docs/prover.js and docs/verifier.js). Django remains responsible for authentication, consent, request state, challenge lifecycle, credential status checks, and returning the minimal verification result to banks.
- The circom circuit (docs/age_over_18.circom) models the comparison "current_ts - dob_ts >= 18 years" and binds the proof to the verification_request via a challenge public input.
- Pinned toolchain for this prototype: circom compiler v2.2.3 (official GitHub release), circomlib 2.0.5, snarkjs 0.7.6. The comparator uses the standard circomlib Num2Bits template, then constrains the signed-age difference to an unsigned bit width without field-wraparound.
- Private witness material (DOB, credential randomness) is never persisted nor written to logs. The prover runs server-side for the prototype and only holds private witness in-memory during proof generation.
- Proof lifecycle: REQUESTED -> GENERATED -> VERIFIED (or FAILED/EXPIRED)
- Verification request lifecycle: PENDING -> APPROVED -> VERIFIED (consent mandatory)

Notes on operational setup:
- Developer environment / CI must have Node.js and snarkjs installed to generate/verify real proofs; test artifacts with precomputed proofs are included under docs/ for CI fallback.
- The implementation aims to separate cryptography (Node/snarkjs) from Django orchestration to make it easier to migrate prover to a holder-controlled environment in future versions.

## Current implementations

OCR:
Mock

NIDMC:
Mock abstraction with validation rules

ZKP:
Placeholder hash implementation

Blockchain:
Not implemented

Kafka:
Not implemented

Redis:
Not implemented

## Future architecture

When scale requires it:

Django API
    |
Kafka
    |
+-----------+-----------+-----------+
| Identity  | KYC       | AML       |
| Service   | Service   | Service   |
+-----------+-----------+-----------+

The modular boundaries must remain stable so extraction into services is possible.
