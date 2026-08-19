# SYSTEM DESIGN — AI-Powered Opportunity Analysis & Sales Enablement Portal (Backend)

## 1. System Overview & Architecture

The backend of the **AI-Powered Opportunity Analysis & Sales Enablement Portal** is built using asynchronous Python 3.11+ with **FastAPI**, **SQLAlchemy 2.0 (Async)**, **PostgreSQL (Asyncpg)**, **Firebase Cloud Messaging (FCM HTTP v1)**, and **AWS S3**.

```
 +-------------------------------------------------------------------------------+
 |                               Client Layer                                    |
 |                   (Web Frontend / Mobile Applications)                        |
 +-------------------------------------------------------------------------------+
       |                                |                             |
       | REST APIs                      | SSE Stream                  | FCM Push
       v                                v                             v
+------------------+          +-------------------+        +--------------------+
|  FastAPI Routers |          | SSE Notification  |        | Firebase Cloud     |
|  (`app/api/`)    |          | Listener Service  |        | Messaging (FCM)    |
+------------------+          +-------------------+        +--------------------+
       |                                |                             |
       v                                v                             v
+--------------------------------------------------------------------------------+
|                             Service Layer (`app/services/`)                    |
|       - Business Logic & Orchestration         - Notification Dispatcher       |
|       - AI Summarization Pipelines             - Token Lifecyle / Pruner       |
|       - S3 File Storage Integration            - DB Access & Query Layer       |
+--------------------------------------------------------------------------------+
       |                                                              |
       v                                                              v
+------------------------------------+              +----------------------------+
|   PostgreSQL DB (Aiven Cloud)      |              |   AWS S3 Storage Bucket    |
|   Asyncpg / SQLAlchemy 2.0         |              |   (Case Studies & Assets)  |
+------------------------------------+              +----------------------------+
```

---

## 2. Core Architectural Layers

1. **API Router Layer (`app/api/`)**
   - Implements thin FastAPI routers.
   - Responsible for validating request bodies via Pydantic schemas, extracting auth tokens via security dependencies (`app/api/deps.py`), and forwarding parameters to services.

2. **Service & Domain Layer (`app/services/`)**
   - Houses all domain business logic, async database access queries (`AsyncSession`), external HTTP calls (AI microservices), S3 file uploads, and notification dispatch loops.

3. **Data Model Layer (`app/models/`)**
   - Declarative async SQLAlchemy 2.0 models with explicit foreign keys, composite indexes (`(user_id, is_active)`), and cascading relationships.

4. **Schema Layer (`app/schemas/`)**
   - Strict Pydantic v2 schemas providing input serialization, response filtering, and type safety across all API interfaces.

5. **Infrastructure & Security Layer (`app/core/`)**
   - `settings.py`: Centralized environment configuration via Pydantic `BaseSettings`.
   - `security.py`: JWT token generation, verification, and bcrypt password hashing.
   - `connections/`: Asynchronous connection singletons for PostgreSQL, Firebase Admin SDK, AWS S3, AI Service, and notification listeners.

---

## 3. Real-Time & Push Notification Architecture

### Dual-Delivery Pipeline
When a system event occurs (e.g., opportunity status update, resource assignment, system alert), notifications are dispatched via a dual path:
1. **In-App Notification Record:** Persisted to PostgreSQL (`notifications` table).
2. **Server-Sent Events (SSE):** Streamed in real-time to active browser sessions.
3. **Firebase Push Notifications (FCM HTTP v1):** Dispatched via `firebase-admin` to active user device tokens.

```
                  +--------------------------------+
                  |    Notification Event Trigger  |
                  +--------------------------------+
                                  |
            +---------------------+---------------------+
            v                                           v
  +--------------------+                     +--------------------+
  |  In-App DB Record  |                     |  FCM Dispatcher    |
  |  (`notifications`) |                     |  (`firebase_admin`)|
  +--------------------+                     +--------------------+
            |                                           |
            v                                           v
  +--------------------+                     +--------------------+
  | SSE Stream Feed    |                     | User Device Tokens |
  | (Real-time Web UI) |                     | (Mobile / Web Push)|
  +--------------------+                     +--------------------+
```

### FCM Token Lifecycle & Auto-Pruning Rule
- Device tokens are registered via `POST /firebase/tokens` and stored in `user_device_tokens`.
- Every push attempt catches FCM-specific failure codes (`registration-token-not-registered`, `invalid-argument`).
- Unregistered or invalid tokens are automatically set to `is_active = FALSE` or pruned, eliminating unnecessary FCM API call overhead.
- Payloads omit unauthenticated PII, passing resource metadata/IDs to require authenticated client fetches.

---

## 4. Security & Authentication Flow

1. **Authentication:**
   - OAuth2 Password Bearer flow.
   - Passwords hashed using Bcrypt with salt.
   - JWT tokens signed with `HS256` and configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
2. **Authorization (RBAC):**
   - System permissions linked to roles (`roles`, `permissions`, `role_permissions`).
   - Dynamic permission checks evaluated in `app/api/deps.py`.

---

## 5. Storage Architecture (AWS S3)

- **Bucket:** Managed via `AWS_S3_BUCKET` in S3 connection manager (`app/core/connections/s3.py`).
- **File Uploads:** Asynchronous uploads and presigned URL generation for sales enablement assets and case studies.
- **Quota Enforcements:** File size limits validated prior to storage streaming (`MAX_CASE_STUDY_SIZE_MB`).

---

## 6. Migration Protocol

- **Schema Evolution:** All model changes require Alembic migration scripts (`alembic revision --autogenerate`).
- **Index Optimization:** Lookup and FK columns maintain explicit compound indices (`(user_id, is_active)`) for high-throughput query optimization.
