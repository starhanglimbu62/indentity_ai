# Production Architecture (Target)

**Status:** Proposed target; not implemented or production-ready.

## Principles

- Keep the existing Django modular monolith. Do not introduce microservices or infrastructure without measured need.
- Preserve the dependency direction: API/view → serializer and validation → application service → domain rules → Django ORM → external integration.
- Keep identity attributes inside the identity boundary. Bank-facing responses disclose only the requested claim and verification metadata.
- Treat consent and verified proof acceptance as separate, explicit security boundaries.
- Every claim proof must be tied to a current, active credential and the specific bank request, challenge, claim, and proof-verification key.
- Fail closed when proof verification, credential validation, authorization, or persistence fails.
- Keep operational configuration external to source control; no secrets in Git, logs, responses, or browser URLs.

## Logical modules

| Module | Owns | Public responsibilities |
|---|---|---|
| `apps.accounts` | User account and user authentication | Registration, login/token lifecycle, user-owned identity access |
| `apps.identity` | Document processing and credential lifecycle | Validated upload, OCR/NIDMC integration boundaries, credential issuance/status/revocation, private claim material |
| `apps.banks` | Institution records and bank-principal authentication | Trusted onboarding, bank identity, status and scoped authorization |
| `apps.verification` | Request, consent, challenge and result lifecycle | Request creation, user decision, proof checks, request-scoped result |
| `apps.audit` | Security event records | Append-oriented, allowlisted metadata events without PII/secrets |
| `apps.common` | Cross-cutting API/security utilities | Safe exception contracts and shared permissions; no domain ownership |

## Trust boundaries and data ownership

- **User principal:** authenticated through the existing Django user/JWT boundary; owns their documents, credentials, and consent decisions.
- **Bank principal:** must be authenticated independently of client-supplied `bank_code`, `user_id`, or `bank_id`; all request/result reads and writes are scoped to that principal.
- **Proof verifier:** accepts only a cryptographically valid proof under the configured verification key and exact persisted request context. Missing Node/key/configuration is an error, never a success fallback.
- **Identity processing:** owns HIGHLY_SENSITIVE document and identity fields. These are not serialized into bank APIs or emitted to logs/audit metadata.
- **Audit store:** records identifiers and enumerated operational metadata only. Ordinary users and bank principals cannot edit/delete audit records.

The selected bank-principal contract supports both workflows without making them interchangeable:

- Human bank operators use the existing Django user/JWT system and are explicitly linked to one bank.
- Server-to-server integrations use per-bank API keys stored as SHA-256 digests and scoped to one bank. Trusted administrators provision banks; the generated key is disclosed once at provisioning and is not returned by login or info endpoints.
- Bank endpoints accept either principal but always resolve and scope to exactly one active bank. A global `is_staff` flag alone does not authorize bank access.

## Intended request flows

### Identity establishment

Authenticated user → validated private upload → identity application service → OCR/NIDMC provider boundaries → validated identity state → credential issuance → raw-file deletion according to retention policy.

### Bank claim verification

Authenticated bank principal creates a request for a supported claim → request and notification persist atomically → user sees the bank, claim, and purpose → explicit, request-scoped consent or denial is recorded → fresh challenge is issued → proof is checked against active credential and exact request context → request transitions once to VERIFIED → bank receives only `{verified, claim, verification_id, timestamp}`.

Any failed dependency or invalid transition leaves the request unverified. Duplicate submissions return the existing terminal result only when the request's idempotency policy permits it.

## Data and transaction boundaries

- Use Django ORM and migrations; use database constraints for uniqueness and valid ranges where possible.
- Use atomic transactions for multi-row state changes.
- Lock the request row when deciding consent, consuming challenges, or accepting a proof.
- Keep proof generation and verification work isolated per operation; impose a finite timeout/resource budget.
- External notification delivery must not be represented as successful unless the defined delivery/queue contract is satisfied. Introduce asynchronous infrastructure only after workload evidence and an operational design exist.

## API contracts

- Keep the existing REST framework and explicit input/output serializers.
- Authenticate before object lookup where practical and scope querysets by the authenticated principal.
- Use stable, versioned contracts when introducing breaking changes; preserve existing URLs until compatibility is planned.
- Use one safe error envelope and never return internal exceptions, stack traces, raw database errors, proof witness data, or identity attributes.
- Paginate potentially unbounded lists and enforce request-size limits.
- Make sensitive operations rate-limited based on abuse risk and idempotent where retries are expected.

## Deployment and operations (future work)

Production must use explicit production settings, a supported production WSGI/ASGI server, TLS termination, restricted hosts/origins, secure cookies/headers, a production database, private document storage, backups with tested restore, and external secret management. Health and readiness endpoints must return no sensitive configuration. Structured logs need request correlation IDs and an allowlisted field policy.

This target does not claim any of those capabilities currently exist. PostgreSQL, Redis, Celery, object storage, metrics/tracing, containers, or orchestration are introduced only with a specific requirement, threat model, deployment owner, and tested operational plan.
