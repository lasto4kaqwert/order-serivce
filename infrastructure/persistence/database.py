from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import Settings

settings = Settings()

database_url = make_url(settings.database_url).set(
    drivername="postgresql+asyncpg",
)

engine = create_async_engine(str(database_url))


async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
