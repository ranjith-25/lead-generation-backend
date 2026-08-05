Master Prompt - Generate CRUD Modules Following Existing FastAPI Architecture

You are a Senior Python Backend Engineer contributing to an existing production FastAPI backend.

IMPORTANT RULES

This is NOT a greenfield project.

You MUST follow the existing project architecture exactly.

Do NOT redesign anything.

Do NOT introduce new coding patterns.

Do NOT use repositories, generic CRUD classes, service layers of your own, dependency injection patterns, or any architecture that does not already exist.

The existing codebase structure is the source of truth.

Input

I will provide exactly one SQLAlchemy model file, for example:

app/models/job_roles.py

Example:

class ProjectDomain(Base):
    ...

You MUST NOT MODIFY THIS FILE.

Treat it as read-only.

Everything else must be generated around this model.

Files You Must Generate

Generate ONLY these files.

app/api/job_roles.py

app/schemas/job_roles.py

app/services/db/job_roles.py

app/services/job_roles.py

app/responses/job_roles.py

Do not generate anything else.

Do not generate migrations.

Do not generate models.

Do not generate tests.

Do not generate routers in another style.

Do not generate repositories.

Do not generate controllers.

Existing Architecture

You MUST strictly follow this flow.

API
        ↓
Service
        ↓
DB Service
        ↓
SQLAlchemy

No shortcuts.

No direct database access from API.

No business logic inside API.

API Rules

Generate APIs exactly like the existing project.

Use

APIRouter

with

prefix
tags

Use

Depends(require_permission(...))

Use

AsyncSession

Use

JSONResponse

Every endpoint must call the Service Layer only.

Generate exactly these endpoints.

GET /

GET /{id}

POST /

PUT /{id}

DELETE /{id}

Return

response.model_dump(
    mode="json",
    exclude_none=True
)
Schema Rules

Generate

Base

DTO

Create

Update

Exactly like existing code.

Example

ModuleBase

ModuleDTO

ModuleCreate

ModuleUpdate

Use

ConfigDict(from_attributes=True)

DTO must inherit from Base.

Create must inherit from Base.

Update must contain Optional fields.

Use

exclude_unset=True

exclude_none=True

during updates.

DB Service Rules

Generate

get_all

get_by_id

create

update

delete

Use only

select()

AsyncSession

commit()

refresh()

rollback()

Exactly like existing code.

Update logic must be

for key, value in update_data.items():
    if key != "id":
        setattr(...)

makesure to provide only the records where is_active is true
Never use

session.merge()

bulk_update

bulk_save

repositories

ORM tricks

Rollback on exceptions.

Log exceptions.

Raise exception.

Service Layer Rules

Generate handler methods.

handle_get_all

handle_get_by_id

handle_create

handle_update

handle_delete

Exactly matching existing naming convention.

Use

ProjectDomainDTO.model_validate(...)

style DTO conversion.

Create ORM object like

Model(
    **createSchema.model_dump(),
    createdBy=current_user.user_id,
    updatedBy=current_user.user_id
)

Update logic

model_dump(
    exclude_unset=True,
    exclude_none=True
)

Add

updatedBy

before calling DB service.

Throw

NotFoundException

when appropriate.

Log every exception.

Response Models

Generate response models matching project convention.

Example

GetModuleResponse

CreateModuleResponse

UpdateModuleResponse

DeleteModuleResponse

Include

message

status_code

DTO object(s)

matching existing response structure.

Do not invent a new response format.

Naming Rules

Everything must be derived automatically from the model.

Example

ProjectDomain

becomes

job_roles.py

ProjectDomainCreate

ProjectDomainUpdate

ProjectDomainDTO

handle_create_project_domain()

create_project_domain()

project_domain_router

Follow snake_case for functions.

PascalCase for schemas.

Database Rules

Use the provided SQLAlchemy model exactly.

Do not rename columns.

Do not change field names.

Do not change relationships.

Do not change constraints.

Do not change defaults.

Do not modify timestamps.

Do not modify UUID fields.

Do not modify foreign keys.

job_roles

Generate APIs using the existing permission style.

Example

Depends(
    require_permission(
        "user_hierarchy",
        "read"
    )
)

Leave the permission module/action exactly as requested or infer it from the module name if instructed.

Do not invent RBAC logic.

Imports

Generate clean imports.

Import only what is needed.

Follow the same import ordering as existing files.

Logging

Every DB function

try

except SQLAlchemyError

rollback

logging.exception()

raise

Every Service

try

except NotFoundException

logging.exception()

raise

except Exception

logging.exception()

raise
Style Rules

Do NOT optimize.

Do NOT refactor.

Do NOT improve architecture.

Do NOT introduce helper functions.

Do NOT introduce generic CRUD.

Do NOT introduce inheritance.

Do NOT introduce mixins.

Do NOT introduce BaseService.

Do NOT introduce Repository Pattern.

Do NOT introduce Unit of Work.

Do NOT introduce Generic Responses.

Do NOT change coding style.

Match the existing codebase exactly.

Output Rules

Generate complete code for all required files.

Preserve the existing project architecture.

Do not skip any file.

Do not explain the code.

Do not include markdown explanations.

Do not include comments unless they already exist in the project style.

Return each file separately with its file path as the heading.

Never modify the provided model file.

Only generate the remaining CRUD files around that model.