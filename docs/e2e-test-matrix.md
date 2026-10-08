# End-to-End Test Matrix

**Scope:** User registration, identity upload, bank request, consent, proof verification, and bank result refresh.  
**Overall result:** Demo flow passes locally; assurance gaps keep the platform **NOT PRODUCTION READY**.

| ID | Scenario | Validation | Expected behavior | Result |
|---|---|---|---|---|
| E2E-01 | Register and log in | Manual browser | Authenticated user workspace opens | PASS |
| E2E-02 | Upload an accepted document | Manual browser; identity API tests | Mock KYC pipeline issues a credential | PASS — mock only |
| E2E-03 | List credentials | Manual browser; `apps.identity.tests` | Authenticated user sees their own credential metadata; no hash/source document; no cross-user records | PASS |
| E2E-04 | Bank portal authenticated API call | Manual browser; `apps.banks.tests` CORS preflight case | Explicitly allowed `X-Bank-API-Key` header passes CORS; bank API remains authenticated | PASS |
| E2E-05 | Bank searches and selects an account | Manual browser; `apps.verification.tests_security` | Bank receives only the user identifier, not name/email fields | PASS — account-existence disclosure remains |
| E2E-06 | Create verification request | Manual browser; verification API/security tests | Bank-scoped request starts PENDING and creates user notification | PASS |
| E2E-07 | Approve consent | Manual browser; verification security tests | Only request owner can approve; state becomes APPROVED | PASS |
| E2E-08 | Deny consent | Verification security tests | Denial is recorded; proof cannot advance a denied request | PASS — API/service coverage; not separately browser-tested |
| E2E-09 | Generate proof without consent | `apps.verification.tests_zkp` | Request is rejected and does not become VERIFIED | PASS |
| E2E-10 | Generate and verify after consent | Manual browser; real SnarkJS integration test in `apps.verification.tests_zkp` | Owner-authenticated operation verifies proof and returns minimal result | PASS — prototype assurance only |
| E2E-11 | Refresh bank result | Manual browser | Bank dashboard reload reads persisted VERIFIED state | PASS |
| E2E-12 | Generate proof without a linked verified source DOB | `apps.verification.tests_zkp` | Fail closed with an explicit error; no successful result | PASS |
| E2E-13 | Proof request/claim/challenge mismatch | `apps.verification.tests_zkp` | Reject proof and preserve non-verified state | PASS |
| E2E-14 | Expired login session recovery | Not exercised | Refresh or explicit re-login behaves safely and predictably | NOT TESTED |

The proof-flow tests use the repository's existing proof helper and local SnarkJS artifacts. They do not resolve the missing cryptographic binding between private DOB and issued credential, nor replace mock OCR/NIDMC services with trusted sources.

