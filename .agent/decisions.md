# IdentityAI Decisions

## 001 - Django modular monolith

Decision:
Keep IdentityAI as one Django project with modular applications.

Reason:
The project is still in development. Immediate microservices would add operational complexity without solving a current problem.

Consequence:
apps/identity, apps/verification and apps/banks must maintain clear boundaries.

---

## 002 - Service layer

Decision:
Business operations live in service classes/modules.

Flow:

View
-> Serializer
-> Service
-> Model

Views must remain thin.

---

## 003 - External integrations are abstracted

External systems are represented by service boundaries:

- OCRService
- NIDMCService
- ZKPService
- BlockchainService
- NotificationService

Real implementations will replace mocks later.

---

## 004 - Minimal disclosure

Decision:
Banks receive verification results, not raw identity information.

---

## 005 - Consent is mandatory

Decision:
The user must explicitly approve every bank verification request.

Consequence:
VerificationRequest cannot transition directly from PENDING to VERIFIED.

---

## 006 - PostgreSQL later

Decision:
Development may use SQLite.

Production will use PostgreSQL.

Consequence:
Do not write code that depends on SQLite-specific behavior.
