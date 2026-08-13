<div align="center">

# 🛡️ IdentityAI

### Privacy-Preserving Digital Identity Verification Infrastructure

**Verify identity once. Prove what matters. Reveal only what is necessary.**

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active%20Development-2563EB?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/Version-v0.2-0F172A?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
  <img src="https://img.shields.io/badge/Next.js-TypeScript-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js"/>
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,django,ts,nextjs,react,tailwind,postgres,redis,docker,kubernetes,kafka&perline=11" alt="Technology Stack"/>
</p>

<br/>

> **IdentityAI is being built as a privacy-first identity verification platform for banks and financial institutions.**

</div>

---

## ✦ The Problem

Traditional KYC workflows repeatedly move sensitive identity information between users, banks, and service providers.

A bank asking:

> "Is this customer over 18?"

should not necessarily need access to:

* the customer's citizenship document
* NID number
* date of birth
* address
* identity photograph
* the user's complete identity credential

IdentityAI is designed around **claim-based verification and minimum disclosure**.

---

# ◈ The Core Idea

```text
                     IDENTITYAI
                         │
                         ▼
                 ┌───────────────┐
                 │     USER      │
                 └───────┬───────┘
                         │
                   Identity Document
                         │
                         ▼
                 ┌───────────────┐
                 │      KYC      │
                 │   PROCESSING  │
                 └───────┬───────┘
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
            OCR      Verification  Validation
             │           │           │
             └───────────┼───────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   CREDENTIAL  │
                 │     ACTIVE    │
                 └───────┬───────┘
                         │
                  Bank requests claim
                         │
                         ▼
                 ┌───────────────┐
                 │ USER CONSENT  │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │  VERIFICATION │
                 └───────┬───────┘
                         │
                         ▼
                 ┌─────────────────┐
                 │ verified: true  │
                 │ timestamp       │
                 └─────────────────┘
```

The important distinction is:

```text
Traditional KYC
────────────────────────────────

Bank ← Full identity information


IdentityAI
────────────────────────────────

Bank ← Only the required verification result
```

---

# 🔐 Privacy by Design

Privacy is not an additional feature of IdentityAI.

It is the architectural constraint around which the system is being built.

### Minimum disclosure

A bank should receive only what its verification request requires.

Example:

```json
{
  "verified": true,
  "timestamp": "2026-08-13T18:00:00Z",
  "verification_id": "VER-8E12A1"
}
```

Not:

```json
{
  "verified": true,
  "nid": "...",
  "dob": "...",
  "address": "...",
  "document": "..."
}
```

### Explicit consent

Every bank verification request requires active user approval.

```text
PENDING
   │
   ▼
APPROVED
   │
   ▼
VERIFIED
```

This transition must never be bypassed.

### Temporary document processing

Identity documents are treated as processing data.

```text
UPLOAD
   ↓
PROCESS
   ↓
VERIFY
   ↓
DELETE RAW DOCUMENT
```

### Separation of identity and verification

Identity establishment and bank verification are separate operations.

```text
One-time KYC
     ↓
Reusable credential
     ↓
Repeated claim verification
```

---

# 🧠 System Architecture

IdentityAI currently uses a **modular Django monolith**.

This is deliberate.

The system is being designed with service boundaries first, while avoiding premature operational complexity from immediately deploying multiple independent microservices.

```text
                         ┌──────────────────────┐
                         │       Next.js        │
                         │       Frontend       │
                         └──────────┬───────────┘
                                    │
                              HTTPS / REST
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Django REST      │
                         │         API          │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │  Accounts   │       │  Identity   │       │ Verification│
       │    App      │       │    App      │       │    App      │
       └─────────────┘       └──────┬──────┘       └─────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Identity Layer    │
                         ├──────────────────────┤
                         │ Document             │
                         │ Preprocessing        │
                         │ OCR                  │
                         │ Extraction           │
                         │ Validation           │
                         │ NIDMC                │
                         │ Credential           │
                         └──────────────────────┘
```

---

# 🧩 Service Boundaries

The identity pipeline is deliberately split into replaceable services.

```text
DocumentService
      │
      ▼
PreprocessingService
      │
      ▼
OCRService
      │
      ▼
IdentityExtractionService
      │
      ▼
IdentityValidationService
      │
      ▼
NIDMCService
      │
      ▼
CredentialService
```

This allows development implementations to be replaced independently.

For example:

```text
Mock OCR
   ↓
EasyOCR
   ↓
Optimized production OCR
```

without changing the entire application.

---

# 📦 Repository Structure

```text
IdentityAI/
│
├── apps/
│   │
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── identity/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services/
│   │       ├── document.py
│   │       ├── preprocessing.py
│   │       ├── ocr.py
│   │       ├── extraction.py
│   │       ├── validation.py
│   │       ├── nidmc.py
│   │       └── credential.py
│   │
│   ├── verification/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   │
│   ├── banks/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py
│   │
│   └── audit/
│       ├── models.py
│       └── services.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── frontend/
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# 🛠️ Technology Stack

<div align="center">

| Layer                     | Technology                                                                                                                                                                                                                                                           |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**               | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python\&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?logo=django\&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-A30000?logo=django\&logoColor=white)                   |
| **Frontend**              | ![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js\&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?logo=react\&logoColor=black) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?logo=typescript\&logoColor=white) |
| **Styling**               | ![Tailwind](https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss\&logoColor=white)                                                                                                                                                                      |
| **Database**              | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql\&logoColor=white)                                                                                                                                                                       |
| **OCR**                   | OpenCV · Pillow · EasyOCR                                                                                                                                                                                                                                            |
| **Authentication**        | JWT · SimpleJWT                                                                                                                                                                                                                                                      |
| **Future Infrastructure** | Kafka · Redis · Celery · MinIO · Kubernetes                                                                                                                                                                                                                          |
| **Future Trust Layer**    | Hyperledger Fabric · ZKP                                                                                                                                                                                                                                             |

</div>

---

# 🚀 Current Release

<div align="center">

## V0.2 — KYC Document Processing

`ACTIVE DEVELOPMENT`

</div>

### V0.1

* Authentication
* Registration
* Login
* User dashboard
* Identity verification UI
* Consent flow
* Bank verification prototype
* Verification result

### V0.2

* Secure document upload
* File validation
* Temporary document processing
* Image preprocessing
* OCR
* Identity extraction
* Extracted-data validation
* NIDMC abstraction
* Credential creation
* Document deletion
* Audit events

---

# 🗺️ Roadmap

```text
                    IDENTITYAI ROADMAP

 V0.1 ────────────────► V0.2
  │                      │
  │                      ├── Document Upload
  ├── Authentication     ├── OCR
  ├── Dashboard          ├── Extraction
  ├── Consent            ├── Validation
  └── Basic Flow         ├── KYC Pipeline
                         └── Audit
                                │
                                ▼
                         V0.3
                         Real Identity
                         Verification
                                │
                                ▼
                         V0.4
                         ZKP + Verifiable
                         Credentials
                                │
                                ▼
                         V0.5
                         Bank Integration
                         + SDK
                                │
                                ▼
                         V0.6
                         PostgreSQL
                         Redis
                         Celery
                                │
                                ▼
                         V0.7
                         Kafka
                         Fabric
                         Multi-Bank
                         Infrastructure
```

### Version roadmap

| Version | Focus                           | Status |
| ------- | ------------------------------- | ------ |
| `V0.1`  | Core UI + verification flow     | ✅      |
| `V0.2`  | KYC document processing         | 🚧     |
| `V0.3`  | External identity verification  | ⏳      |
| `V0.4`  | ZKP + credentials               | ⏳      |
| `V0.5`  | Bank integration + SDK          | ⏳      |
| `V0.6`  | Production infrastructure       | ⏳      |
| `V0.7`  | Distributed multi-bank platform | ⏳      |

---

# ⚙️ Local Development

## Requirements

* Python 3.12+
* Node.js 20+
* npm
* Git

---

## Backend

```powershell
git clone https://github.com/YOUR_USERNAME/identity-ai.git

cd identity-ai

python -m venv env

.\env\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

---

## Frontend

Open another terminal:

```powershell
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 🧪 Testing

### Django

```powershell
python manage.py check
python manage.py test
```

### Frontend

```powershell
cd frontend
npm run build
```

A feature is not considered complete until the relevant tests pass.

---

# 🔌 API Flow

### Register

```http
POST /api/accounts/register/
```

### Upload identity document

```http
POST /api/identity/documents/
```

### Create bank verification request

```http
POST /api/verification/request/
```

### User consent

```http
POST /api/verification/{id}/consent/
```

### Verify

```http
POST /api/verification/{id}/verify/
```

The intended lifecycle is:

```text
REGISTER
   ↓
IDENTITY VERIFICATION
   ↓
CREDENTIAL ACTIVE
   ↓
BANK REQUEST
   ↓
USER CONSENT
   ↓
VERIFICATION
   ↓
RESULT
```

---

# 🔭 Target Production Architecture

The current Django monolith is an intentional starting point.

As scale and operational requirements increase, the target architecture evolves toward:

```text
                           ┌─────────────────┐
                           │   API Gateway   │
                           └────────┬────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
             Identity            KYC              AML
             Service            Service          Service
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    │
                                  Kafka
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
         PostgreSQL              Redis                Fabric
              │
              ▼
            MinIO
```

The eventual system is intended to support:

* independent service scaling
* multiple bank deployments
* fault tolerance
* auditability
* privacy-preserving verification
* decentralized trust
* regional data controls

---

# 🔒 Security Status

> **⚠️ Development Prototype**

IdentityAI is not currently a production identity-verification system.

Do **not** use this repository with real:

* citizenship documents
* NID numbers
* banking credentials
* government identity data
* production secrets

Current limitations include:

* mocked external identity verification
* placeholder credential generation
* incomplete ZKP implementation
* incomplete production access control
* local development storage
* incomplete compliance controls
* incomplete production-grade document protection

Use synthetic test data during development.

---

# 🧱 Engineering Principles

### 01 · Privacy first

Sensitive information should not be disclosed simply because it is available.

### 02 · Consent is mandatory

A bank cannot silently verify a user.

### 03 · Services over spaghetti

Business logic belongs in explicit service boundaries.

```text
View
 ↓
Serializer
 ↓
Service
 ↓
Model
```

### 04 · Infrastructure follows need

Kafka, Kubernetes and blockchain are not introduced just because they look impressive in an architecture diagram.

### 05 · Replaceable integrations

OCR, identity verification, ZKP and blockchain implementations must remain replaceable.

### 06 · Small releases

IdentityAI is developed incrementally.

```text
V0.1 → V0.2 → V0.3 → V0.4 → ...
```

Each version must have a clearly defined scope.

---

# 🌐 Project Vision

IdentityAI aims to move identity verification from:

```text
"Give me all your information."
```

toward:

```text
"Prove only what I need to know."
```

The long-term goal is infrastructure where identity becomes **verifiable without becoming unnecessarily exposed**.

---

<div align="center">

### Built for privacy. Designed for verification.

<br/>

<img src="https://skillicons.dev/icons?i=python,django,nextjs,react,ts,tailwind,postgres,docker,kubernetes&perline=9" alt="Built With"/>

<br/><br/>

**IdentityAI**

`Privacy-Preserving Identity Infrastructure`

</div>
