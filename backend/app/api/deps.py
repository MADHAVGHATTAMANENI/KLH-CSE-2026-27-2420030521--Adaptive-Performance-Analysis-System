from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides an asynchronous database session to API route handlers."""
    async for session in get_db_session():
        yield session
