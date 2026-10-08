# User and Bank Journey Reliability Report

**Assessment:** Local browser E2E follow-up  
**Disposition:** **NOT PRODUCTION READY**. The demo journey is now traversable, but current proof and identity assurance are insufficient for a real banking decision.

## Reliability changes completed

- Replaced the credentials screen's fabricated empty state with an authenticated, user-scoped credential API and a loading/error/empty/data UI. The serializer excludes credential hashes and source-document data.
- Added the credential's source verified document relation for newly issued credentials. Existing credentials remain unlinked when provenance cannot be established safely.
- Added an owner-authenticated proof-generation endpoint that requires an approved request, explicit consent, an active credential, and its linked verified source document with a DOB. It fails closed if these prerequisites or the prover are unavailable.
- Routed consent approval to a result/status screen with a deliberate proof-generation action. The result reflects persisted request state and never treats APPROVED as VERIFIED.
- Allowed the bank API's custom authentication header through CORS for the already configured frontend origins. The browser can now make its authenticated bank API calls.
- Aligned bank account selection with the API's reduced response and display only the account identifier. Bank dashboards and detail pages provide explicit status refresh controls.
- Removed a bank-detail label that expected fields absent from the intentionally minimal bank-scoped response.
- Removed copy claiming that proof generation is automatically in progress. Consent/result UI now calls out the mock identity integrations and missing proof-to-credential binding before the user approves.
- Added regression coverage for credential ownership/minimal fields, CORS preflight, consent-gated proof generation, source-DOB requirements, and the proof-to-bank-result API path.

## Remaining material risks

| Priority | Finding | Impact / required follow-up |
|---|---|---|
| Critical | AGE_OVER_18 proves an inequality for a supplied DOB but does not prove that DOB belongs to the issued credential. OCR and NIDMC are mocks. | A VERIFIED prototype result is not trustworthy identity or age evidence. Bind the proof to a cryptographically verifiable credential commitment and replace mocks before any real decision. |
| High | Bank account search reveals whether a query matches, and the current user IDs are stable sequential database IDs. | Enables account discovery and cross-request correlation. Replace search with a consented, scoped, non-enumerable onboarding/identifier design before production. |
| High | Existing credentials have no source-document relation after the additive migration. | They remain usable for existing request paths but cannot use the new holder proof path; generation fails closed. Establish provenance before issuing/relinking historical credentials. |
| High | Consent is stored as mutable request state and a timestamp, not an immutable, policy-versioned decision record. | Insufficient auditability and revocation/policy evidence for regulated consent. Add a durable consent-decision record before production. |
| Medium | User access tokens and bank API keys are held in browser `sessionStorage`; access-token refresh/recovery was not exercised. | XSS can expose browser-held credentials, and expired sessions may fail without a smooth recovery path. Review token custody and implement/test expiry handling. |
| Medium | No automated browser E2E runner is declared. | Manual browser results are not repeatable in CI. Add a supported browser test framework only when the project adopts one and its dependency/tooling policy is agreed. |

## Decision

The full demo workflow now completes in a real browser and persists its result across bank-dashboard reload. This validates wiring and usability only. Do not market or deploy the result as a production-grade proof of a verified user's age until the critical credential-binding and real-identity-source gaps are closed.
