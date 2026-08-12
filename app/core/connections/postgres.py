from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_LOGS,
    pool_pre_ping=True,
    # Bounded on purpose: this process can never open more than
    # DB_POOL_SIZE + DB_MAX_OVERFLOW backends. Leaving these at SQLAlchemy's
    # defaults (5 + 10) lets a single process eat 15 of the server's 20 slots.
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    connect_args={"server_settings": {"timezone": "UTC"}}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,    
    autocommit=False,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session