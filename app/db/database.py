from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
    
# Bazaga ulanish urlni olish - use the correct environment variable name
DATABASE_URL = "sqlite+aiosqlite:///./restaurant.db"


# Async engine yaratish
engine = create_async_engine(DATABASE_URL, echo=True)

# Bazaning asosiy klassi (model uchun)
Base = declarative_base()

# Async db sessiyasi olish uchun funksiya
async def get_db():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
        finally:
            await session.close()