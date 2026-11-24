
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.database.models import Base


DATABASE_URL = "sqlite+aiosqlite:///student.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("Database initialized successfully!")


async def close_db():
    await engine.dispose()
