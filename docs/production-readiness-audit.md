# Production Readiness Audit

**Assessment date:** 2026-10-07  
**Status:** Prototype; not production-ready  
**Scope:** Repository source, configuration, tests, documentation, dependency manifests, frontend, and checked-in deployment/CI files. Local `.env` contents were not opened or copied. No dependencies were installed and no Python command was run during this audit.

## Executive summary

IdentityAI remains a prototype: it is a modular Django monolith with a Next.js frontend and an AGE_OVER_18 Circom/SnarkJS proof flow. Follow-up changes have removed verifier-success fallbacks, hardened bank credentials and authorization, required explicit consent, reduced identity disclosure, and eliminated NID from audit metadata. The full Django suite and an isolated real-proof smoke flow currently pass.

The platform is **not production-ready**. The circuit proves an age inequality for a supplied DOB but does not establish that the DOB belongs to the user's verified credential. OCR and NIDMC are mocks; consent is not recorded in an immutable, policy-versioned ledger; account search still reveals whether a matching account exists; and any secret previously committed in `.env` may remain in Git history. These are material assurance and privacy gaps, regardless of passing tests.

Validation uses the repository environment `env\\Scripts\\python.exe` (Python 3.14.6). No packages were installed. The end-to-end smoke test was run against an isolated in-memory database because the existing local `db.sqlite3` schema predates the current bank-key migration; that local database was left unmigrated.

## Hardening progress (2026-10-07)

The initial findings below describe the audited baseline. Follow-up changes in the current working tree address several of those issues:

- Removed file-based verifier success fallbacks. The Node prover/verifier now receive data over stdin, emit one JSON result, flush it, and exit; missing dependencies, invalid output, and timeouts do not produce success.
- Bank API keys are hashed at rest and disclosed only during privileged provisioning. Bank API-key principals and bank-linked operator JWTs are scoped to an active bank; bank request operations are queried within that bank.
- Consent input requires an explicit boolean. Request/claim/challenge public inputs are checked against persisted request state, sensitive transitions use row locks, and bank request/search responses no longer include user names, email addresses, or usernames.
- Removed NID from identity audit-event metadata. Verification responses disclose the requested claim and verification metadata only.
- Validation with `env\\Scripts\\python.exe`: all 36 Django tests pass; `manage.py check` and `makemigrations --check --dry-run` pass. The backend smoke flow passes 27/27 checks with real proof generation and verification, using an isolated in-memory SQLite database. No packages were installed.

These changes do **not** close all release blockers. The circuit still proves an age inequality for a supplied private DOB without binding that DOB to an issued credential or credential commitment. OCR and NIDMC remain mocks; there is no immutable, policy-versioned consent record; and user search still permits an authenticated bank to learn whether a matching account exists. Search results contain the current stable, sequential user ID rather than names or contact fields, so the ID itself is not a non-enumerable opaque identifier. Removing `.env` from the Git index does not remove any secret from Git history or rotate it. Keep the overall readiness status as **not production-ready**.

## Manual E2E reliability follow-up

The browser journey was exercised with synthetic data against local Django and Next.js servers and an isolated temporary SQLite database. Credential listing, bank CORS, account selection, request creation, notification review, explicit consent, proof generation, and bank-dashboard refresh are now wired. The full manual result and test matrix are documented in [manual-e2e-audit.md](./manual-e2e-audit.md) and [e2e-test-matrix.md](./e2e-test-matrix.md).

The follow-up adds a nullable source-document relation for new credentials and a holder-authenticated proof-generation endpoint. It requires approved consent and an active credential linked to a verified source document with a DOB; historical credentials without established provenance fail closed. The browser demo completed through the existing SnarkJS verifier, but this does not close the DOB-to-credential binding issue or replace mocked OCR/NIDMC. The system remains **not production-ready**. Bank search currently returns stable sequential user IDs and still reveals match existence; consent remains mutable request state rather than an immutable, policy-versioned record.

## Audited baseline architecture and technology

- **Backend:** Django modular monolith; apps include accounts, identity, verification, banks, audit, and common. HTTP routes use Django REST Framework.
- **Authentication:** SimpleJWT for Django users. Registration and login are custom API views. At the initial audit, bank authentication used a plaintext API key and was not consistently enforced. Follow-up changes introduce hashed per-bank keys and linked-bank operator JWTs; see hardening progress above.
- **Frontend:** Next.js 13.4.12, React 18.2, TypeScript 5.1+, client-side pages, a shared fetch wrapper, and browser `sessionStorage` for access tokens and bank data.
- **Persistence:** SQLite is the default. Settings accept a database engine and connection parameters from environment variables, including PostgreSQL configuration, but no production database operations or recovery configuration are present.
- **Cryptography:** Circom AGE_OVER_18 circuit and Node/SnarkJS PLONK prover/verifier scripts. The Python integration passes data to Node subprocesses. At the initial audit, development/test artifact fallbacks existed; they have since been removed from the verification path.
- **Dependencies:** Python requirements are pinned; root and frontend npm lockfiles are present. No dependency vulnerability or provenance scan was run.
- **Operations:** No tracked Docker/Compose deployment, CI workflow, production server configuration, health/readiness endpoint, or observability configuration was found.

## Audited baseline data model and lifecycle

- `User` extends Django `AbstractUser`, with unique email, optional unique phone number, and an identity-verified flag.
- `IdentityDocument` stores an uploaded file, extracted NID, name, DOB, status, and processing timestamps. Raw file deletion is attempted after processing, but extracted sensitive fields remain persisted.
- `VerifiableCredential` stores a user, hash, issuer, issue/expiry timestamps, status, active flag, and optional blockchain reference.
- `VerificationRequest` relates a bank, user, and credential; it records claim, status, challenge, consent timestamp, verification timestamp, and expiry. Consent has no separate immutable record, policy version, or explicit denial timestamp.
- At the initial audit, `Bank` stored an API key in plaintext. Follow-up changes replace it with a hashed key field, while retaining bank metadata, webhook URL, and active status.
- `Notification` and `AuditEvent` store application metadata. Audit metadata accepts arbitrary JSON without a sensitive-field policy or append-only database enforcement.
- The intended verification state machine is PENDING → APPROVED → VERIFIED, or PENDING → DENIED. Follow-up changes lock rows during sensitive transitions; database-level transition constraints and a separate immutable consent record remain outstanding.

## Audited baseline authentication and authorization

### Behavior at initial audit

- User routes use JWT authentication by default and several views specify `IsAuthenticated`.
- Bank registration, login, and info endpoints use `AllowAny`. Bank registration creates a bank and returns its API key; login and info also return that key.
- Verification request creation accepts a client-supplied `bank_code`. Staff can select any target user; ordinary users can create a request for themselves.
- Bank-facing request list/detail queries are globally visible to every staff user rather than scoped to the authenticated bank.
- `IsRequestOwnerOrStaff` authorizes any staff member for any verification request.
- Search-users is available to any authenticated account and returns names, usernames, and email addresses.

### Assessment

Bank identity is not securely established or associated with an authorization scope. An API key is stored and returned as plaintext, bank portal authentication is not enforced by the bank-request APIs, and global staff access enables cross-bank access. User and bank workflows therefore lack robust object-level authorization and isolation.

## Audited baseline: identity and credential lifecycle

- Identity upload validates extension, declared MIME type, and size. These values are supplied by the client; file signatures/content are not independently verified and no malware-scanning boundary is implemented.
- The OCR and NIDMC integrations are mocks. Current OCR fixture data returns synthetic identity attributes; no real authority response is obtained.
- Extracted NID, name, and DOB are persisted on `IdentityDocument`. An audit event records the NID in metadata.
- A credential hash is issued and the source file is deleted after processing. The service does not bind the AGE_OVER_18 proof to an authenticated, active credential commitment.
- Credential validity is checked during verification, but database constraints and revocation workflows are not established.
- Processing and external proof calls run synchronously in the request path. Prover/verifier subprocesses have no timeout. Temporary preprocessing files and failed-processing retention require explicit lifecycle controls.

## Audited baseline: verification, consent, and API behavior

- Consent lookup checks the authenticated user owns the request, but missing `approved` input defaults to `True`; an empty POST therefore approves a request.
- Consent is represented by request status and a timestamp rather than a separate auditable, claim/policy-versioned consent record.
- Verification checks status, expiry, credential status, challenge, and a timestamp window. State updates are atomic at the transaction level but do not lock the request row; duplicate concurrent requests can race.
- Request claims are accepted as arbitrary strings. Verification does not enforce that the persisted claim and proof claim match, and the successful response always returns `AGE_OVER_18`.
- Public signals include a verification request identifier, but the service does not compare that signal to the current request ID. Challenge matching provides partial request binding, not complete domain separation.
- APIs are not versioned, most list responses are unpaginated, and error formats vary. Several views return raw exception text to clients.
- The successful verification response is relatively small, but bank request listing/detail and user search disclose identity attributes before proof completion.

## Audited baseline: ZKP and cryptographic boundary

The project contains a real Circom/SnarkJS proof path, but the current API/test path is not a reliable cryptographic acceptance boundary:

1. `apps/identity/services/zk_verifier.py` accepts a precomputed `verified_<request-id>.json` result if the Node verifier cannot run.
2. `docs/verifier.js` can return a precomputed success file before invoking SnarkJS.
3. `apps/verification/tests_zkp.py` writes such files containing `{"verified": true}`, so tests can pass without cryptographic verification.
4. The circuit proves an age inequality for a supplied private DOB; it does not bind that DOB to the issued credential or a credential commitment. The `credential_id` is passed to the prover wrapper but is not a circuit input.
5. Verification does not check that public request ID and claim signals equal the current persisted request and requested claim.
6. Prover/verifier scripts write shared proof/public files and use relative paths; concurrent requests can race or overwrite artifacts. Node subprocesses have no timeout.

Consequently, the system must not claim that a bank result proves a claim about the user's verified identity. Preserve real proof verification; remove all success-shaped fallback behavior from production acceptance paths, and rework/test credential binding and public-input validation before relying on the claim.

## Audited baseline: frontend assessment

- A shared API wrapper exists and TypeScript strict mode is enabled, but many pages use `any` and response types are incomplete.
- User access tokens and bank data/keys are stored in `sessionStorage`; this is session-scoped but remains readable by same-origin JavaScript.
- Client-side route checks are UX controls only. Backend authorization must remain authoritative.
- Bank login stores returned bank data and key, but the shared API client only attaches the user JWT. Protected bank pages call global staff/JWT APIs; the bank credential is not attached to those requests. This makes bank frontend authentication inconsistent with the backend contract.
- The result page invokes verification with null proof and public signals, rather than obtaining/generating a valid proof. The current backend smoke script is not equivalent to a working browser end-to-end flow.
- No `dangerouslySetInnerHTML` or `innerHTML` use was found in the inspected frontend source. No CSP, browser security-header policy, frontend automated E2E suite, or privacy-preserving bank UI contract exists.

## Audited baseline: security, privacy, and configuration

- The root `.env` is currently tracked by Git despite `.gitignore` patterns that would ignore an untracked environment file. Its contents were not inspected. Treat any credential in it as potentially exposed; removing it from the latest tree does not erase Git history.
- Production settings require a secret when DEBUG is false and set several secure-cookie/HSTS defaults, but the configuration is mixed in one settings module. `check --deploy` behavior is altered by inspecting command-line arguments inside settings.
- `ALLOWED_HOSTS` has permissive local defaults; CORS is hard-coded for local origins. No explicit CSRF trusted-origin or CSP policy is configured.
- Password validators are limited to similarity and minimum length; no application-level authentication throttling or rate limiting is configured. JWT refresh rotation/revocation is not configured.
- Logging is not structured or correlated. Audit metadata is caller-controlled and currently includes NID. Audit rows are not protected from updates/deletion at the database layer.
- SQLite and local `MEDIA_ROOT` are development defaults. No private object storage, backup/restore procedure, retention schedule, or production serving policy is configured.

## Audited baseline: deployment, CI/CD, dependencies, and observability

- No Docker/Compose, production WSGI/ASGI process definition, deployment manifests, reverse-proxy/HTTPS configuration, or rollback/backups documentation was found.
- No tracked GitHub Actions workflow was found. Existing scripts and documented test commands are not enforced on pull requests.
- No health/readiness routes, request correlation IDs, metrics, tracing, or structured log configuration was found.
- Dependency versions are pinned in manifests and npm lockfiles exist. A vulnerability audit, upgrade compatibility review, and automated dependency-update policy remain outstanding.
- Redis, Celery, Kafka, Kubernetes, and other infrastructure are not present. Their absence is not itself a defect; introduce them only when operational requirements justify them.

## Findings by priority

### P0 — Critical security or data-integrity issues

| ID | Finding | Evidence | Required outcome |
|---|---|---|---|
| P0-1 | Verification can succeed without cryptographic verification through precomputed success files; tests create `verified: true` fixtures. | `apps/identity/services/zk_verifier.py`, `docs/verifier.js`, `apps/verification/tests_zkp.py` | No fallback may authorize a bank result. Tests must assert cryptographic verification or explicitly test verifier-unavailable failure. |
| P0-2 | Public bank registration and key-returning endpoints permit untrusted bank creation and disclose reusable bank secrets. Keys are stored plaintext. | `apps/banks/views.py`, `apps/banks/models.py` | Provision banks through a trusted administrative process; store only a verifier/hash for secrets and never return them after issuance. |
| P0-3 | Bank request, challenge, and result access is not scoped to an authenticated bank; any staff user can access all banks' requests. | `apps/verification/views.py` | Every bank operation must derive bank identity from verified credentials and query only that bank's objects. |
| P0-4 | An empty consent request defaults to approval, and no immutable, claim-scoped consent decision is recorded. | `apps/verification/views.py`, `apps/verification/models.py` | Require explicit validated decision and record user, request, bank, claim, decision, timestamp, and policy version. |
| P0-5 | The age proof is not bound to an issued credential, and request/claim public signals are not validated against persisted request context. Any claim string can be created while success returns AGE_OVER_18. | `docs/age_over_18.circom`, `apps/verification/services.py`, `apps/verification/views.py` | Threat-model and redesign proof/credential binding; enforce supported claims and exact public-input/request equality before acceptance. |
| P0-6 | Highly sensitive NID is written into audit metadata. | `apps/identity/services/__init__.py` | Remove direct identifiers from events and add metadata allowlisting/redaction tests. |
| P0-7 | Root `.env` is tracked. Contents were intentionally not read; current Git history may retain any secrets. | Git tracked-file inventory; `.gitignore` | Stop tracking it while preserving the local file, provide a safe example file, rotate any exposed secrets, and assess history cleanup. |

### P1 — Production blockers

| ID | Finding | Evidence | Required outcome |
|---|---|---|---|
| P1-1 | Bank APIs expose user name/email through search and request list/detail before minimal claim disclosure. | `apps/verification/views.py` | Return only claim/result/request identifiers and data required for explicit bank workflow. |
| P1-2 | No bank-aware authentication is wired through the frontend; browser storage is treated as route state and backend bank endpoints use global staff JWTs. | `frontend/pages/bank/*`, `frontend/src/api/api.ts`, `apps/verification/views.py` | Select one supported bank-principal contract and enforce it on every bank endpoint. |
| P1-3 | Verification/consent/challenge updates have no row locking or idempotency; state transitions can race. | `apps/verification/services.py`, `apps/verification/views.py` | Serialize state transitions, define retries/idempotency, and test competing operations. |
| P1-4 | File checks rely on client-declared MIME type and file extension; no signature inspection or malware-scanning boundary exists. | `apps/identity/services/validation.py` | Validate content, size, storage isolation, authorization, cleanup, and retention; define a malware-scanning integration boundary. |
| P1-5 | Sensitive identity attributes remain stored; document retention/deletion and credential revocation policies are unspecified. | `apps/identity/models.py`, `apps/identity/services/__init__.py` | Define necessity, access, retention, deletion/anonymization, and revocation before production use. |
| P1-6 | Node proof calls have no timeout and write fixed shared artifact paths; synchronous proof generation can block or race. | `apps/identity/services/zk_prover.py`, `apps/identity/services/zk_verifier.py`, `docs/prover.js`, `docs/verifier.js` | Isolate workspaces per invocation, apply resource/time limits, and preserve explicit verifier failure. |
| P1-7 | SQLite is the default and no production database migration, backup, restore, or least-privilege connection plan is implemented. | `config/settings.py` | Make environment-specific production DB configuration explicit and validate backup/restore operations. |
| P1-8 | Login, registration, and proof endpoints lack targeted rate limits; JWT refresh revocation/rotation is not configured. | `config/settings.py`, account views | Add limits based on abuse risk and an explicit token lifecycle. |
| P1-9 | Errors are inconsistent and broad exception handlers expose internal exception messages. APIs lack versioning and pagination. | `apps/verification/views.py`, `apps/identity/views.py` | Standardize safe error contracts; paginate potentially unbounded collections. |
| P1-10 | No enforced CI, production runtime/deployment, health checks, or operational recovery documentation exists. | Repository inventory | Add the smallest supportable CI and deployment controls before production deployment. |

### P2 — Important engineering improvements

| ID | Finding | Required outcome |
|---|---|---|
| P2-1 | The frontend has incomplete API types and many `any` casts; user-visible consent and result flows are not an end-to-end functioning proof journey. | Establish explicit shared contracts and browser-level tests for actual flows. |
| P2-2 | Audit records are not append-only and metadata has no schema/allowlist; logs lack correlation identifiers. | Define event schemas, access controls, correlation, and retention. |
| P2-3 | Documentation conflicts: current architecture describes both a real V0.4 proof path and a placeholder; current-task notes prohibit implementing V0.4 despite its presence. | Keep docs aligned with the inspected implementation and mark mocks/prototypes explicitly. |
| P2-4 | Automated dependency security review and a safe update process are absent. | Add scheduled/PR dependency review without blind upgrades. |

### P3 — Lower-priority enhancements

- Add metrics/tracing integration points after request correlation and stable operational contracts exist.
- Add query optimization and caching only after measurements identify a bottleneck.
- Consider asynchronous processing only if measured OCR/proof/notification workloads require it; do not add Redis/Celery/Kafka/Kubernetes by default.

## Recommended change order

1. **Phase A — Audit and architecture:** Complete this audit, document target modular boundaries, identify decisions that need owner approval.
2. **Phase B — Critical trust boundaries:** Remove verifier success fallbacks; correct proof/credential/claim binding design; secure bank provisioning and bank-scoped authorization; require explicit consent; remove PII from audit.
3. **Phase C — Data integrity and privacy:** Add locked state transitions/idempotency, constraints, explicit serializers, retention and private-file controls.
4. **Phase D — Authentication and API hardening:** Set a bank identity contract, rate limits, token lifecycle, consistent safe errors, pagination, and scoped permissions.
5. **Phase E — Identity and credential assurance:** Replace mock integrations only with approved real providers; bind credential claims to proof; formalize revocation/expiry.
6. **Phase F — Frontend:** Align bank/user flows to backend contracts, reduce sensitive browser state, add real browser E2E coverage and accessibility checks.
7. **Phase G — Testing and delivery:** Separate cryptographic integration tests from unit tests, remove artifact-success fixtures, add CI and dependency checks.
8. **Phase H — Deployment and operations:** Establish production settings, server, database, private storage, backups/restore, health/readiness, structured logs, and incident/rollback procedures.

## Readiness conclusion

The repository is a useful prototype, not a production system. It must not be used to make real identity, age, banking, or compliance decisions until all P0 findings are closed, P1 controls are implemented and tested, mock KYC boundaries are replaced by approved integrations, and deployment/privacy operations are independently reviewed. No numeric production-readiness score is assigned before resolving the critical correctness and authorization failures.
