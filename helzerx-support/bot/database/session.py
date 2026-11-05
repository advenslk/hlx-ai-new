"""
HELZERX AI Support - Database Session Management
Handles async connection pools, reconnection retries, and automatic schema initialization.
"""
from __future__ import annotations

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from bot.config import config
from bot.database.models import Base
from bot.utils.logger import logger

# Determine connection URL and driver
raw_url = config.DATABASE_URL

# Normalize URL for asyncpg / aiosqlite
if raw_url.startswith("postgresql://"):
    ASYNC_DATABASE_URL = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("sqlite://"):
    ASYNC_DATABASE_URL = raw_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
else:
    ASYNC_DATABASE_URL = raw_url

try:
    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
except Exception as e:
    logger.warning(f"Failed to create engine with {ASYNC_DATABASE_URL}: {e}. Falling back to SQLite.")
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///helzerx_support.db"
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def init_db() -> None:
    """Creates database tables if they do not exist."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized successfully with URL: {ASYNC_DATABASE_URL.split('@')[-1]}")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        # Fallback to local SQLite if postgres was not reachable
        if "postgresql" in ASYNC_DATABASE_URL and config.SQLITE_FALLBACK:
            logger.warning("Attempting emergency fallback to local SQLite...")
            global engine, AsyncSessionLocal
            engine = create_async_engine("sqlite+aiosqlite:///helzerx_support.db", echo=False)
            AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Emergency SQLite fallback database initialized.")
        else:
            raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency helper providing an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
