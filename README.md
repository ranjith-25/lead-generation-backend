# lead-generation-backend

Command to run migrations : 
alembic revision --autogenerate -m "message"


Migrating the database changes 
alembic upgrade head


Running Development Server
python -m uvicorn app.main:app --port 8001 --reload