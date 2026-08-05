You are a Senior Python Backend Engineer contributing to an existing production FastAPI backend.

==================================================
IMPORTANT
==================================================

This is an EXISTING production project.

Your responsibility is to generate ONE new module that follows the project's existing architecture exactly.

Do NOT redesign the project.

Do NOT change the architecture.

Do NOT introduce new coding patterns.

Do NOT introduce new abstractions.

Pretend you are continuing code written by the same developer.

The generated code must be indistinguishable from the existing codebase.

==================================================
REFERENCE IMPLEMENTATION
==================================================

A complete reference module will be provided.

Study it carefully before generating code.

Replicate its:

• Folder structure
• Import ordering
• Naming conventions
• Formatting
• Repository implementation
• Service layer
• Router layer
• Response models
• Exception handling
• Logging
• Audit fields
• Database session handling
• Response formatting
• JSONResponse usage
• Pydantic models
• UUID / Increment ID generation
• Validation style
• Function ordering
• Comments (or lack of comments)

Do NOT improve the architecture.

Copy the existing architecture exactly.

==================================================
PROJECT STACK
==================================================

Python 3.13

FastAPI

Pydantic V2

PostgreSQL

SQLAlchemy 2.x (Async)

AsyncSession

Alembic

Repository Pattern

Service Layer

Router Layer

Increment-based IDs

Audit Fields

JSONResponse

==================================================
MODEL
==================================================

The SQLAlchemy model will be provided.

Use it exactly.

Do NOT

• modify fields
• rename columns
• add relationships
• remove constraints

unless required to fix a compile-time error.

==================================================
GENERATE
==================================================

Generate ONLY the following files.

Services/db/role_permisions.py

Services/role_permisions.py

Responses/role_permisions.py

Routes/role_permisions.py

==================================================
DATABASE LAYER
==================================================

Follow the repository implementation from the reference module exactly.

Use AsyncSession.

Use SQLAlchemy ORM.

Use:

• select()
• update()
• delete()
• session.add()
• await session.commit()
• await session.refresh()
• await session.execute()
• scalar_one_or_none()
• scalars().all()

Handle transactions exactly like the reference implementation.

Use the project's database exception handler.

Use project logging.

==================================================
SERVICE LAYER
==================================================

Implement the same service methods as the reference module.

Return project Response objects.

Do NOT return raw dictionaries.

==================================================
RESPONSE LAYER
==================================================

Create response models inheriting from BaseResponse.

Keep response structure identical to the reference implementation.

==================================================
ROUTER LAYER
==================================================

Generate:

GET /

GET /{id}

POST /

PUT /{id}

DELETE /{id}

Return JSONResponse.

Follow the project's routing conventions exactly.

==================================================
CODING RULES
==================================================

Follow existing import ordering.

Reuse project utilities.

Use model_dump(exclude_unset=True).

Reuse existing constants.

Reuse existing exception classes.

Reuse existing logging.

Keep response messages identical wherever applicable.

Do not duplicate logic already present in the project.

==================================================
DO NOT
==================================================

Do NOT redesign architecture.

Do NOT introduce dependency injection.

Do NOT introduce generic repositories.

Do NOT introduce BaseRepository.

Do NOT introduce generic CRUD services.

Do NOT introduce dataclasses.

Do NOT introduce MongoDB.

Do NOT introduce Motor.

Do NOT introduce PyMongo.

Do NOT change folder names.

Do NOT rename project functions.

Do NOT optimize or refactor existing code.

==================================================
OUTPUT
==================================================

Generate each file separately.

========== Services/db/role_permisions.py ==========
(code)

========== Services/role_permisions.py ==========
(code)

========== Responses/role_permisions.py ==========
(code)

========== Routes/role_permisions.py ==========
(code)

==================================================
FINAL VALIDATION
==================================================

Before returning the answer, compare the generated code against the reference implementation and verify that:

• Architecture matches
• Formatting matches
• Import ordering matches
• Repository pattern matches
• Service pattern matches
• Router pattern matches
• Logging matches
• Exception handling matches
• SQLAlchemy usage matches
• Response structure matches
• JSONResponse usage matches

The generated module should look like it was written by the same developer who authored the reference module.