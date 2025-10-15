from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/faceid"

Base = declarative_base()

# Asinxron engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Asinxron session
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
