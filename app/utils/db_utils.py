from app.database import AsyncSessionLocal  # Import session maker from database.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

# Dependency to get the database session for FastAPI routes
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an asynchronous database session."""
    async with AsyncSessionLocal() as db:
        yield db  # Yield the session to be used in route handlers
