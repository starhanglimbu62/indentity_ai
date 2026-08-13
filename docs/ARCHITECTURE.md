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

## Current implementations

OCR:
Mock

NIDMC:
Mock

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
