# Current Task

## Version

V0.1 - IdentityAI Web UI

## Goal

Build the first usable frontend for the IdentityAI core identity verification flow.

## Technology

- Next.js
- TypeScript
- Tailwind CSS
- Axios
- React Hook Form
- Zod

## Screens

Implement:

1. Landing page
2. Registration
3. Login
4. User dashboard
5. Identity document upload
6. Identity processing state
7. Identity verified state
8. Verification request
9. Consent screen
10. Verification result
11. Bank dashboard

## Core user journey

Registration
-> Dashboard
-> Identity Verification
-> Document Upload
-> Processing
-> Identity Verified
-> Credential Active
-> Bank Verification Request
-> User Consent
-> Verification
-> Result

## UI requirements

The interface must communicate:

- privacy
- consent
- minimal disclosure
- verification status
- security

Bank verification requests must clearly show:

What the bank requested.

What the bank will receive.

What the bank will NOT receive.

## Architecture

Use:

components
-> hooks
-> API client
-> Django backend

Do not put API calls directly into visual components.

## Backend integration

Base API:

NEXT_PUBLIC_API_URL

Existing endpoints:

POST /api/accounts/register/
POST /api/identity/documents/
POST /api/verification/request/
POST /api/verification/<id>/consent/
POST /api/verification/<id>/verify/

## Constraints

Do not modify the Django backend.

Do not implement ZKP.

Do not implement OCR.

Do not implement blockchain.

Do not introduce Kafka.

Do not introduce Redis.

Use mock data only where an existing backend endpoint cannot provide the required UI state.

## Quality

Responsive desktop and mobile layouts.

Reusable components.

Loading states.

Error states.

Empty states.

Accessible buttons and form fields.

Do not create one giant page component.

Run the frontend build before completing the task.

## Acceptance criteria

A user should be able to visually complete:

Register
-> Dashboard
-> Upload identity document
-> See processing
-> See verified status
-> Receive a bank request
-> Review consent
-> Approve
-> See verification result