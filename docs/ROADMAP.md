# IdentityAI Roadmap

## Current State

IdentityAI is currently in a working V0.4 prototype stage for privacy-preserving age verification using a modular Django monolith and a Circom + SnarkJS PLONK proof flow. The system has already implemented the core consent-driven verification lifecycle, a clear service boundary for identity processing, and the initial cryptographic proof architecture needed to demonstrate minimal disclosure.

## Phase 1 - Stable Django Core (Completed)

- [x] Django project bootstrap
- [x] Accounts and authentication
- [x] Custom User model
- [x] Identity document model
- [x] Verifiable credential model
- [x] Verification request lifecycle model
- [x] User consent flow
- [x] Explicit verification state constraints
- [x] Basic API permissions and ownership checks
- [x] Environment-based configuration and secret loading
- [x] Automated Django validation and test execution
- [x] API endpoint coverage for core identity and verification flows
- [x] Audit event logging for major lifecycle actions

## Phase 2 - KYC and Identity Processing (Completed)

- [x] Document upload validation
- [x] Identity credential creation flow
- [x] Mock OCR abstraction boundary
- [x] Mock NID verification boundary
- [x] Credential status tracking
- [x] Image preprocessing pipeline (PIL-based with graceful fallback)
- [x] OCR confidence scoring and validation
- [x] NIDMC verification boundary with validation rules
- [x] Secure document lifecycle cleanup and raw document deletion
- [x] Full identity failure analysis and remediation workflow with actionable recommendations

## Phase 3 - Privacy-Preserving Verification (V0.4) (Completed)

- [x] Define claim model for AGE_OVER_18
- [x] Implement ZKP boundary in Django service layer
- [x] Implement Circom circuit for age threshold verification
- [x] Implement Node-based prover helper using SnarkJS PLONK
- [x] Implement Node-based verifier helper using SnarkJS verification key
- [x] Bind proof to verification request and challenge
- [x] Enforce proof freshness and challenge expiration
- [x] Prevent replay by consuming challenge after successful verification
- [x] Return minimal-disclosure verification result to banks
- [x] Require explicit consent before VERIFIED state is reached
- [x] Validate active/expired credential status before proof acceptance
- [x] Implement the current V4 bank and request lifecycle hardening around the ZKP flow
- [x] Establish the working AGE_OVER_18 proof pipeline in the repository
- [x] Validate the proof lifecycle with automated Django tests

Notes:
- The repository already demonstrates the key cryptographic workflow for AGE_OVER_18 using Circom + SnarkJS (PLONK).
- Django remains the orchestration layer for user auth, consent, request lifecycle, challenge validation, and minimal-response generation.
- Private witness material such as DOB is not persisted in the application database; it remains ephemeral during proof generation.

## Phase 4 - Bank Integration and Operational Readiness (Completed)

- [x] Bank request creation flow
- [x] Verification request issuance
- [x] Consent approval API
- [x] Proof submission and verification API
- [x] Bank registration and login API
- [x] Bank onboarding metadata support (bank_code, webhook_url, API key generation)
- [x] Request expiry enforcement for stale verification requests
- [x] Verification audit event logging for created, approved, and verified requests
- [x] Bank-facing verification lifecycle coverage for the current V4 workflow
- [x] Core bank-side operational validation and state enforcement
- [x] Completion of the current bank integration baseline in the repository

## Phase 5 - Production Infrastructure

- [ ] PostgreSQL migration from local SQLite for production
- [ ] Redis for caching and async tasks
- [ ] Celery background job processing
- [ ] Kafka event bus for identity and verification pipelines
- [ ] MinIO or equivalent object storage for document handling
- [ ] Observability and metrics stack
- [ ] Dockerized deployment
- [ ] Kubernetes orchestration
- [ ] Secret rotation and secure secret management automation

## Phase 6 - Distributed Trust and Credential Layer

- [ ] Hyperledger Fabric or equivalent trust anchor
- [ ] Credential anchoring and revocation support
- [ ] Multi-bank trust isolation
- [ ] Cross-organization verification federation
- [ ] Recovery and disaster planning
- [ ] Advanced policy enforcement for credential issuance and expiry

## Phase 7 - AML and Risk Services

- [ ] AML screening integration
- [ ] Risk scoring workflow
- [ ] Suspicious transaction or identity review pipeline
- [ ] Case management for flagged users or institutions
- [ ] Compliance reporting and audit retention policies

## Strategic Priority for the Next Milestone

The next major milestone is to move beyond the V4 baseline and make the platform production-ready by improving:

1. real OCR/NIDMC integration,
2. stronger credential lifecycle controls and revocation,
3. bank webhook delivery and notification workflows,
4. operational security and bank-specific permission isolation,
5. containerized deployment infrastructure, and
6. enterprise-grade monitoring and compliance tooling.
