# IdentityAI Roadmap

## Phase 1 - Stable Django Core

- [x] Django project
- [x] Accounts
- [x] Identity model
- [x] Verification request
- [x] Consent flow
- [ ] Comprehensive automated tests
- [ ] API documentation
- [ ] Proper permissions
- [ ] Temporary document handling

## Phase 2 - Real KYC Pipeline

- [x] Real document upload validation (V0.2 service boundary)
- [ ] OpenCV preprocessing
- [ ] EasyOCR
- [ ] OCR confidence scoring
- [ ] NIDMC integration interface
- [ ] NIDMC client
- [ ] Identity verification errors
- [ ] Secure document deletion

## Phase 3 - Real Cryptographic Credential (V0.4)

- [x] Define credential schema (added credential status)
- [x] Define ZKP claims (AGE_OVER_18)
- [x] Implement real proving circuit (circom placeholder in docs)
- [x] Implement verifier (Node/snarkjs helper + Django boundary)
- [x] Proof expiration (proof model + challenge expiry implemented)
- [x] Replay protection (challenge consumed after verification)
- [ ] Credential revocation (status supported, revocation plumbing remains)

Notes:
- V0.4 implements AGE_OVER_18 using Circom + snarkjs (PLONK) with a server-side prover prototype. The Django app orchestrates challenge generation, consent, credential status checks, and verification state updates.
- The production-ready circuit should replace the illustrative circuit in docs/ with a robust comparator and proper R1CS design.

## Phase 4 - Bank Integration

- [ ] Bank authentication
- [ ] Bank onboarding
- [ ] Verification API
- [ ] Webhooks / notifications
- [ ] Request expiration
- [ ] Audit logging

## Phase 5 - Production Infrastructure

- [ ] PostgreSQL
- [ ] Redis
- [ ] Celery
- [ ] Kafka
- [ ] MinIO
- [ ] Observability
- [ ] Docker
- [ ] Kubernetes

## Phase 6 - Distributed Trust

- [ ] Hyperledger Fabric
- [ ] Credential anchoring
- [ ] Bank peer architecture
- [ ] Multi-bank isolation
- [ ] Disaster recovery

## Phase 7 - AML

- [ ] AML service
- [ ] Risk scoring
- [ ] Screening pipeline
- [ ] Suspicious activity workflow
