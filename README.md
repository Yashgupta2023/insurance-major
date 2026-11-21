# ClaimIQ — Insurance Claim Intelligence Platform

## Phase 1
A full-stack Flask + PostgreSQL + React implementation with JWT roles, claim management, document upload, OCR-ready processing, verification, historical analysis, duplicate detection, and explainable fraud risk.

## Demo accounts
- Customer: `customer@demo.com` / `Demo@123`
- Investigator: `investigator@demo.com` / `Demo@123`
- Admin: `admin@demo.com` / `Demo@123`

## Run
### Backend
1. Install PostgreSQL and create a database named `insurance_claims`.
2. Copy `backend/.env.example` to `backend/.env` and set `DATABASE_URL`.
3. From the workspace: `.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt`
4. Seed: `.\.venv\Scripts\python.exe backend/seed.py`
5. Server: `cd backend; ..\.venv\Scripts\python.exe run.py`

### Frontend
- `cd frontend`
- `npm install`
- `npm run dev`

Open `http://localhost:5173`.

## Known setup condition
PostgreSQL must be running and the configured `postgres` password must match `DATABASE_URL`. The database and initial seed require local PostgreSQL administration privileges.
