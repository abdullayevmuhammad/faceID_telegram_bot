# src/database/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# DATABASE_URL = os.getenv("DB_URL", "postgresql+asyncpg://postgres:root@localhost/faceid")
DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/faceid"


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
