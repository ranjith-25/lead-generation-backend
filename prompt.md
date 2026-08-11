MASTER REFERENCE MODULE — EXACT REPLICA RULE

TARGET MODULE / INPUT

I will provide exactly ONE new SQLAlchemy model file.

Example:

app/models/<new_model_file_name>.py

This SQLAlchemy model is the TARGET MODEL for which the CRUD module
must be generated.

The provided SQLAlchemy model is READ-ONLY.

DO NOT modify the provided model file.

DO NOT rename the model.

DO NOT rename any model fields.

DO NOT modify:
- Columns
- Relationships
- Foreign keys
- Constraints
- Defaults
- UUID fields
- Timestamp fields
- is_active
- Any existing model configuration


TARGET MODULE NAME

The generated module name must be derived from the provided model.

Example:

Provided model:

app/models/customer_project.py

Model:

class CustomerProject(Base):
    ...


Generated files:

app/api/customer_project.py
app/schemas/customer_project.py
app/services/db/customer_project.py
app/services/customer_project.py
app/responses/customer_project.py


TARGET ENTITY NAMING

Derive all names from the SQLAlchemy model.

Example:

SQLAlchemy Model:
CustomerProject

Module:
customer_project

Schema:
CustomerProjectBase
CustomerProjectDTO
CustomerProjectCreate
CustomerProjectUpdate

Service functions:
handle_get_all_customer_project()
handle_get_by_id_customer_project()
handle_create_customer_project()
handle_update_customer_project()
handle_delete_customer_project()

DB functions:
get_all_customer_project()
get_customer_project_by_id()
create_customer_project()
update_customer_project()
delete_customer_project()

Router:
customer_project_router

Response models:
GetCustomerProjectResponse
CreateCustomerProjectResponse
UpdateCustomerProjectResponse
DeleteCustomerProjectResponse

The exact naming must follow the naming convention used by:

pipeline_opportunity_project

Do NOT blindly use the example names above if the reference module
uses a different naming convention.

The reference module takes precedence.


TARGET MODEL IS THE ONLY NEW SOURCE OF TRUTH

The provided SQLAlchemy model determines:

- Available fields
- Field names
- Field types
- Nullable fields
- Default values
- Relationships
- Foreign keys
- Primary key
- is_active
- Model-specific filtering requirements

Do NOT invent fields that do not exist in the provided model.

Do NOT remove model fields unless the reference implementation
demonstrates that such fields are intentionally excluded from a
specific schema.

Do NOT invent relationships.

Do NOT invent foreign keys.

Do NOT assume fields based only on the entity name.

Use the actual provided SQLAlchemy model.

The existing module:

pipeline_opportunity_project

must be treated as the PRIMARY SOURCE OF TRUTH and MASTER REFERENCE
for generating the new CRUD module.

Use the corresponding existing files:

app/api/pipeline_opportunity_project.py
app/schemas/pipeline_opportunity_project.py
app/services/db/pipeline_opportunity_project.py
app/services/pipeline_opportunity_project.py
app/responses/pipeline_opportunity_project.py

as the exact implementation references.

The generated module must follow the existing
pipeline_opportunity_project module as closely as possible.

DO NOT independently design or infer a new implementation.

DO NOT redesign the architecture.

DO NOT refactor the reference implementation.

DO NOT optimize the reference implementation.

DO NOT introduce new patterns.

DO NOT "improve" existing code.

DO NOT simplify existing logic.

Treat the reference module as if it were a template that is being
copied and adapted for the new SQLAlchemy model.


EXACT REPLICA REQUIREMENT

For EVERY generated file, preserve the same:

- Overall file structure
- Import structure
- Import ordering
- Naming conventions
- Class structure
- Function structure
- Function ordering
- Parameters
- Return types
- Async/await pattern
- SQLAlchemy query patterns
- AsyncSession usage
- Validation approach
- DTO conversion approach
- Error handling
- Exception handling
- Logging
- JSONResponse usage
- Permission handling
- Status codes
- Response structure
- Database transaction handling
- commit()
- refresh()
- rollback()
- update logic
- is_active handling
- ID handling
- None handling
- model_dump() usage
- model_validate() usage
- Coding style
- Formatting style


ONLY ADAPT ENTITY-SPECIFIC INFORMATION

When copying the reference implementation, change ONLY information that
must change because the target SQLAlchemy model is different.

This includes, where applicable:

- Model name
- Entity name
- File name
- Schema names
- DTO names
- Create schema names
- Update schema names
- Response names
- Router names
- Function names
- SQLAlchemy model references
- Model-specific fields
- Model-specific IDs
- Model-specific foreign keys
- Model-specific filters
- Model-specific relationships

Do NOT change the implementation pattern merely because another approach
is possible.


REFERENCE FILE MAPPING

Use the following reference file for each generated file:

API:
app/api/pipeline_opportunity_project.py

Schema:
app/schemas/pipeline_opportunity_project.py

DB Service:
app/services/db/pipeline_opportunity_project.py

Service:
app/services/pipeline_opportunity_project.py

Response:
app/responses/pipeline_opportunity_project.py


FILE-BY-FILE REPLICATION

1. API

Copy the structure and implementation style of:

app/api/pipeline_opportunity_project.py

Preserve:
- APIRouter configuration
- prefix
- tags
- Depends(...)
- permission handling
- AsyncSession handling
- endpoint structure
- parameter ordering
- service invocation
- JSONResponse construction
- status codes
- exception handling
- response serialization

Only adapt entity-specific names and fields.


2. SCHEMAS

Copy the structure and implementation style of:

app/schemas/pipeline_opportunity_project.py

Preserve:
- Base schema structure
- DTO structure
- Create schema structure
- Update schema structure
- ConfigDict configuration
- inheritance
- Optional field handling
- field naming
- validation patterns

Only adapt fields according to the provided SQLAlchemy model.


3. DB SERVICE

Copy the structure and implementation style of:

app/services/db/pipeline_opportunity_project.py

Preserve:
- all existing functions
- function ordering
- AsyncSession usage
- select() usage
- filtering
- is_active handling
- create logic
- update logic
- delete logic
- commit()
- refresh()
- rollback()
- SQLAlchemyError handling
- logging
- return values

Do not independently decide how database operations should be
implemented.


4. SERVICE

Copy the structure and implementation style of:

app/services/pipeline_opportunity_project.py

Preserve:
- handler naming pattern
- handler ordering
- DB service invocation
- DTO conversion
- model_validate(...)
- model_dump(...)
- current_user handling
- createdBy
- updatedBy
- NotFoundException handling
- generic exception handling
- logging
- return values

Only adapt entity-specific names and fields.


5. RESPONSES

Copy the structure and implementation style of:

app/responses/pipeline_opportunity_project.py

Preserve:
- response class structure
- field ordering
- DTO usage
- message handling
- status_code handling
- response object structure
- naming conventions

Do not invent a new response format.


REFERENCE PRIORITY

If the general instructions in this prompt and the existing
pipeline_opportunity_project implementation appear to conflict:

1. Follow the existing project implementation.
2. Follow the pipeline_opportunity_project reference pattern.
3. Adapt only what is required by the new SQLAlchemy model.

The existing project code is the ultimate source of truth.

The goal is NOT to create an equivalent implementation.

The goal is to create an implementation that looks and behaves as if
pipeline_opportunity_project was copied and then adapted for the new
model.


NO NEW ARCHITECTURE

Under no circumstances introduce:

- Repository Pattern
- Generic CRUD
- Generic Services
- BaseService
- Repository classes
- Unit of Work
- Mixins
- Generic Responses
- New dependency injection patterns
- New helper utilities
- New abstractions
- New architectural layers
- New coding patterns


FINAL VALIDATION

Before generating the output, compare every generated file against its
corresponding pipeline_opportunity_project reference file.

Verify that:

- The architecture is identical.
- The implementation pattern is identical.
- The function ordering follows the reference.
- The error handling follows the reference.
- The logging follows the reference.
- The response structure follows the reference.
- The database access pattern follows the reference.
- The service flow follows the reference.
- No new patterns were introduced.
- No existing patterns were removed unnecessarily.
- Only model/entity-specific information was changed.

The generated module should be an exact replica of the reference module,
adapted to the new SQLAlchemy model.