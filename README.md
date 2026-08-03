# AI-Powered Opportunity Analysis & Sales Enablement Portal (Backend)

Welcome to the backend repository for the **AI-Powered Opportunity Analysis & Sales Enablement Portal**. This application provides robust APIs to manage users, track sales opportunities, generate AI-driven job summaries, and manage sales enablement resources (like outreach templates and suggested talking points).

## Tech Stack
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL with `asyncpg`
- **ORM:** SQLAlchemy (Async)
- **Migrations:** Alembic
- **Validation:** Pydantic
- **Authentication:** OAuth2 with JWT tokens

## Core Features
1. **Authentication & Authorization**: Secure login, session tracking, and role-based access control.
2. **Opportunity Management**: Complete CRUD operations for tracking job opportunities and parsing detailed job requirements.
3. **Sales Enablement**: Generate and store targeted outreach templates, talking points, and relevant projects tailored to specific opportunities.
4. **AI Integration**: Endpoints to intelligently summarize job descriptions and extract key insights.

## Project Structure
```
app/
├── api/          # FastAPI routers and endpoints
├── core/         # Core configuration (DB connections, security, settings)
├── exceptions/   # Custom exception handlers and error codes
├── models/       # SQLAlchemy database models
├── responses/    # Standardized API response models
├── schemas/      # Pydantic validation schemas
└── services/     # Business logic and database query layers
```

## Getting Started

### 1. Environment Setup
Make sure you have Python 3.11+ installed. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/macOS
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Configure your database connection and secret keys by setting up your `.env` file (if applicable) or ensuring your local PostgreSQL server is running and matches the connection strings in `app.core.connections.postgres`.

### 3. Database Migrations
We use Alembic for database schema migrations.

**Generate a new migration** (after changing SQLAlchemy models):
```bash
alembic revision --autogenerate -m "description of changes"
```

**Apply migrations to the database**:
```bash
alembic upgrade head
```

### 4. Running the Development Server
Start the FastAPI application using Uvicorn:
```bash
python -m uvicorn app.main:app --port 8001 --reload
```

The API will be available at `http://localhost:8001`.
You can view the interactive API documentation (Swagger UI) at `http://localhost:8001/docs`.