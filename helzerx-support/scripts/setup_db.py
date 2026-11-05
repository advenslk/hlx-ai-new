"""
HELZERX AI Support - Database Initialization CLI Tool
Initializes schema and tables for PostgreSQL or local SQLite.
"""
import asyncio
import sys
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot.database.session import init_db
from bot.utils.logger import logger


async def main():
    logger.info("Starting HELZERX database initialization script...")
    await init_db()
    logger.info("Database initialization completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
