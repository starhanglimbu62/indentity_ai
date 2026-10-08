# Manual End-to-End Journey Audit

**Assessment:** Browser journey exercised against local development servers  
**Environment:** Next.js on `127.0.0.1:3000`, Django on `127.0.0.1:8000`, isolated SQLite database in `%TEMP%`  
**Test data:** Synthetic account, provisioned QA bank, and a disposable 1x1 PNG; no production or personal data used  
**Readiness:** The user-and-bank demo journey completes, but the platform remains **NOT PRODUCTION READY**.

## Journey and observed results

| Step | Browser action | Result |
|---|---|---|
| Account | Register and then log in as a test user | Passed. A server restart changed the temporary signing key, so the browser session was re-authenticated before later checks. |
| Identity | Upload the disposable PNG | Passed in the mock KYC pipeline; the API issued a credential. This is not a real identity check. |
| Credentials | Open My credentials | Initially failed: the page always displayed an empty state. Fixed with an authenticated, owner-scoped list endpoint; it now displays the issued credential's ID, issuer, dates, and status without its hash or source document. |
| Bank login | Sign in with the provisioned QA bank | Login succeeded. The first bank API request failed its browser CORS preflight because `X-Bank-API-Key` was not allowed. After allowing that header for the existing explicit frontend origins, bank API requests succeeded. |
| Account selection | Search for the test account and select the result | Passed after aligning the UI with the minimal search response. The result displays an account ID rather than name or email. Search still reveals whether an account matches. |
| Request | Create an AGE_OVER_18 request | Passed. The bank dashboard displayed the persisted request as PENDING. |
| Notification and consent | Open the user notification and review the bank, claim, disclosure, and prototype warning; approve | Passed. The request moved to APPROVED only after the authenticated user's explicit decision. |
| Proof and result | Select “Generate and verify proof” | Passed for this demo credential. The server generated and cryptographically verified a proof using the existing Node/SnarkJS path and returned a minimal result. |
| Bank refresh | Reopen/reload the bank dashboard | Passed. The persisted request appeared as VERIFIED. The bank response contained status and verification metadata, not the user's document, DOB, or credential hash. |

The result and consent screens explicitly warn that the OCR/NIDMC path is mocked and the current circuit does not bind its private DOB to the verified credential. The demo result must not be interpreted as reliable age or identity evidence.

The bank request detail page initially expected bank metadata not present in its scoped response and rendered an empty bank label. The view now omits that unsupported field; the bank identity is already shown by the authenticated portal header.

## Known limits and untested manual cases

- This was a browser-driven manual run, not a repeatable Playwright/Cypress suite. No browser E2E framework is declared in the frontend project, and no dependencies were installed.
- The old credential created before the source-document relation was added has no source document. Proof generation correctly fails closed for it; existing credentials are not auto-associated because their provenance may be ambiguous.
- The user-denial and no-consent paths have backend regression tests, but denial was not separately exercised in this browser session.
- Expired access-token recovery, bank-key rotation, real OCR/NIDMC integrations, production storage, and production deployment behavior were not tested.
- The browser run used the prototype's mocked identity extraction. Passing this journey is not evidence of a trustworthy credential-bound age proof.

## Reproduction

Use the repository's existing Python virtual environment and installed frontend dependencies; do not install packages for this audit. Start Django with an isolated database and the Next.js frontend with `NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000`. Provision a disposable bank credential and use a synthetic test account. The browser actions above can then be repeated through the registered user and bank portals.
