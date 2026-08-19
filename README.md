# AI-Powered Opportunity Analysis & Sales Enablement Portal (Backend)

Welcome to the backend repository for the **AI-Powered Opportunity Analysis & Sales Enablement Portal**. This application provides an enterprise-grade asynchronous FastAPI platform designed to manage sales opportunities, orchestrate lead pipeline workflows, generate AI-driven job summaries and talking points, manage enablement resources, and dispatch real-time in-app and Firebase push notifications.

---

## 🏗️ Core Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) with Asynchronous ASGI execution (`uvicorn`)
- **Database:** PostgreSQL (Aiven Cloud) via `asyncpg` (Asynchronous Driver)
- **ORM & Migrations:** [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation & Settings:** [Pydantic v2](https://docs.pydantic.dev/latest/) & `pydantic-settings`
- **Push Notification Engine:** Firebase Cloud Messaging (FCM HTTP v1 via `firebase-admin`) + Real-time SSE (Server-Sent Events)
- **Cloud Object Storage:** AWS S3 (via `aioboto3` / `boto3`)
- **Authentication & Security:** OAuth2 with JWT tokens, password hashing with `passlib[bcrypt]`

---

## 📁 Project Architecture & Module Structure

The project follows a clean, layered architecture separating routing, business logic, data models, and database access layers:

```
lead-generation-backend/
├── app/
│   ├── api/                  # Thin FastAPI router endpoints
│   │   ├── ai.py             # AI summarization & intelligence endpoints
│   │   ├── auth.py           # OAuth2, JWT login, registration & OTP password reset
│   │   ├── branch.py         # Organization branch management
│   │   ├── dashboard.py      # Analytics & dashboard metrics
│   │   ├── feature.py        # Feature toggle & permissions
│   │   ├── firebase_token.py # FCM device token registration & lifecycle
│   │   ├── job_role.py       # Job role definitions
│   │   ├── notification.py   # In-app notifications & SSE real-time streaming
│   │   ├── opportunity.py    # Opportunity tracking & parsing
│   │   ├── opportunity_status.py
│   │   ├── permissions.py    # System permissions management
│   │   ├── pipeline_*.py     # Opportunity pipeline executions & resource matching
│   │   ├── profile_variant.py# Profile variant CRUD
│   │   ├── project.py        # Sales enablement project catalog
│   │   ├── role.py           # System role definitions
│   │   ├── role_permissions.py
│   │   ├── sales_enablement.py
│   │   ├── settings.py       # Global app settings management
│   │   ├── techstack.py      # Technology stack catalog
│   │   ├── user.py           # Current user endpoints
│   │   ├── user_invitation.py# Team invitation management & token validation
│   │   ├── user_management.py# Admin user management operations
│   │   ├── user_personal_info.py
│   │   └── user_project.py   # User project associations
│   ├── core/                 # Core infrastructure configuration
│   │   ├── connections/      # Connection managers (PostgreSQL, Firebase, AWS S3, AI Service, SSE Listener)
│   │   ├── security.py       # JWT token generation, verification & password hashing
│   │   ├── settings.py       # Pydantic BaseSettings environment loader
│   │   └── storage.py        # AWS S3 & file storage utilities
│   ├── exceptions/           # Custom domain exceptions & global exception handlers
│   ├── models/               # SQLAlchemy 2.0 declarative async models
│   ├── responses/            # Standardized HTTP API response wrappers
│   ├── schemas/              # Pydantic v2 request/response validation schemas
│   ├── services/             # Core business logic, DB access layer & external dispatchers
│   └── utils/                # Helper utilities (email formatting, date parsing, etc.)
├── alembic/                  # Database migration scripts & environment configuration
├── scripts/                  # Data cleanup & administrative utility scripts
├── .env                      # Local environment configuration file (git-ignored)
├── alembic.ini               # Alembic configuration file
├── requirements.txt          # Production dependencies
└── README.md                 # Project documentation
```

---

## ⚙️ Environment Configuration

Create a `.env` file in the root directory. All configuration options are loaded dynamically via `app.core.settings.Settings`:

```env
# Environment & Server
ENVIRONMENT=development
FRONTEND_BASE_URL=http://localhost:3000

# Database Configuration (PostgreSQL / Aiven Cloud)
DATABASE_URL=postgresql+asyncpg://avnadmin:<password>@<host>:<port>/defaultdb?ssl=require
DATABASE_URL_SYNC=postgresql://avnadmin:<password>@<host>:<port>/defaultdb?ssl=require
DB_LOGS=false
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

# Security & Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
OTP_EXPIRE_MINUTES=10

# AI Service Integration
AI_BASE_URL=http://localhost:8002

# AWS S3 Storage
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=lead-generation-assets
MAX_CASE_STUDY_SIZE_MB=10
CASE_STUDY_DIR=uploads/case_studies

# Firebase Cloud Messaging (FCM)
FIREBASE_CREDENTIALS_PATH=serviceaccount.json

# SMTP Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true
EMAIL_FROM=your-email@example.com

# Real-time Event Streaming (SSE)
STREAM_TOKEN_EXPIRE_SECONDS=60
STREAM_KEEPALIVE_SECONDS=25
STREAM_SESSION_RECHECK_SECONDS=300
```

---

## 🚀 Getting Started

### 1. Prerequisites & Environment Setup

Ensure you have Python 3.11+ installed. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup & Alembic Migrations

Ensure your PostgreSQL database is reachable. Apply all pending schema migrations:

```bash
# Apply migrations to head
alembic upgrade head

# Generate a new migration script after updating SQLAlchemy models
alembic revision --autogenerate -m "describe_your_model_changes"
```

To directly query or inspect the Aiven PostgreSQL database:
```bash
psql -h <aiven-host> -p <port> -U avnadmin -d defaultdb
```

### 3. Running the Application

Start the FastAPI ASGI server with hot reloading enabled:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

- **Base API URL:** `http://localhost:8001`
- **Swagger Interactive API Docs:** `http://localhost:8001/docs`
- **ReDoc API Documentation:** `http://localhost:8001/redoc`

---

## 🔔 FCM Push Notification Engine Protocol

The platform integrates dual-channel notification delivery (In-App notifications + Firebase Cloud Messaging push notifications):

1. **Idempotent Device Token Registration:**
   - Tokens are registered via `POST /firebase/tokens`. Device tokens are upserted dynamically for the authenticated user.
2. **Error Handling & Automatic Token Pruning:**
   - When FCM dispatch returns `registration-token-not-registered` or `invalid-argument` error codes, the notification service automatically deactivates (`is_active = FALSE`) or prunes stale tokens to avoid quota drain.
3. **PII Security in Push Payloads:**
   - Push notification payloads do not transmit unauthenticated PII. Metadata and IDs are transmitted to trigger secure, client-authenticated fetch calls.

---

## 🧪 API Endpoints & cURL Testing Examples

### 1. Health Check
```bash
curl -X GET "http://localhost:8001/health"
```

### 2. User Authentication (Login)
```bash
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "YourSecurePassword123!"
  }'
```

### 3. Register FCM Device Token
```bash
curl -X POST "http://localhost:8001/firebase/tokens" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "fcm_device_token_string_here",
    "device_type": "web"
  }'
```

### 4. Fetch User Notifications
```bash
curl -X GET "http://localhost:8001/notification/get_all_notifications" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

### 5. Fetch Opportunities List
```bash
curl -X GET "http://localhost:8001/opportunities/" \
  -H "Authorization: Bearer <YOUR_JWT_TOKEN>"
```

---

## 🛡️ Coding Standards & Guidelines

- **Strict Async I/O:** Always use `async`/`await` for database operations (`AsyncSession`) and external service calls.
- **Thin Routers:** Keep FastAPI endpoint handlers concise and move logic to `app/services/`.
- **Database Indexing:** Ensure foreign key relationships and frequent lookup columns (`user_id`, `is_active`) use explicit indices.
- **Documentation Synchronization:** Whenever models, endpoints, or environment options change, ensure `README.md` and `SYSTEM_DESIGN.md` are updated accordingly.