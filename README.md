# ClaimIQ — Insurance Claim Intelligence Platform

A Phase 1 full-stack insurance claim management and fraud-risk demonstration platform built with React, Flask, PostgreSQL, JWT, OCR-ready document processing, and explainable risk scoring.

## Features

- JWT authentication for Customer, Investigator, and Admin roles
- Customer claim submission and document upload
- Investigator claim review, notes, decisions, and fraud-risk analysis
- Admin user, policy, provider, and analytics management
- PostgreSQL database models and seeded demonstration data
- PDF/image OCR processing using PyMuPDF and Tesseract
- Document classification, field extraction, and rule-based risk services
- Recharts analytics and responsive enterprise UI

## Technology

- Frontend: React 19, Vite, TypeScript, Recharts, Lucide React
- Backend: Python, Flask, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Migrate
- Database: PostgreSQL
- AI baseline: PyMuPDF, Tesseract, OpenCV, Pillow, ImageHash, scikit-learn

## Prerequisites

Install:

- Git
- Node.js 20 or newer
- npm
- Python 3.12
- PostgreSQL 17 or 18
- Tesseract OCR for image/OCR processing

## 1. Clone the repository

```bash
git clone https://github.com/Yashgupta2023/insurance-major.git
cd insurance-major
```

## 2. Create the PostgreSQL database

Create a database named `insurance_claims`:

```sql
CREATE DATABASE insurance_claims;
```

Set a known password for the PostgreSQL `postgres` user:

```sql
ALTER USER postgres WITH PASSWORD 'postgres';
```

Default local connection:

```text
postgresql+psycopg://postgres:postgres@localhost:5432/insurance_claims
```

## 3. Backend setup

### Windows PowerShell

From the project root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
copy backend\.env.example backend\.env
python backend\seed.py
cd backend
..\.venv\Scripts\python.exe run.py
```

### Linux/macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python backend/seed.py
cd backend
../.venv/bin/python run.py
```

Backend: `http://localhost:5000`

## 4. Configure environment variables

Edit `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/insurance_claims
JWT_SECRET_KEY=replace-with-a-long-random-secret
SECRET_KEY=replace-with-another-long-random-secret
UPLOAD_FOLDER=./app/uploads
```

Generate secure random secrets:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit `.env` or real database credentials.

## 5. Frontend setup

Open a second terminal at the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

Keep PostgreSQL, Flask, and Vite running simultaneously.

## 6. Demo accounts

| Role | Email | Password |
|---|---|---|
| Customer | `customer@demo.com` | `Demo@123` |
| Investigator | `investigator@demo.com` | `Demo@123` |
| Admin | `admin@demo.com` | `Demo@123` |

## Database seeding

The seed script creates tables and demonstration users, policies, providers, and claims:

```bash
python backend/seed.py
```

Warning: the seed script drops existing application tables. Use it only with a development database.

## Frontend production build

```bash
cd frontend
npm run build
```

## Troubleshooting

### PostgreSQL is not running

Windows:

```powershell
net start postgresql-x64-18
```

Or start `postgresql-x64-18` in Windows Services.

### Database authentication fails

Verify PostgreSQL is running, the `postgres` password matches `DATABASE_URL`, and the `insurance_claims` database exists.

### Backend login fails

Open `http://localhost:5000/api/health`. It should report PostgreSQL as the database.

### CORS browser error

Use `http://localhost:5173` consistently. The local Vite origins `localhost` and `127.0.0.1` are allowed.

### Tesseract is not detected

Install Tesseract OCR and ensure `tesseract` is available in `PATH`. PDF text extraction works independently; scanned image OCR requires Tesseract.

## Security note

Demo credentials and local secrets are for development and demonstration only. Replace secrets and database credentials before production deployment.
