from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from project1.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,  # shows the sql it executed in the cmd
    pool_pre_ping=True,  # just do a pre health check of the DB in case it time out or anything
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # usually after saving SQLalchemy "expires" objects, this is to not let it do that so we can still access objects like users
)

Base = declarative_base()  # this is the parent to all your classes.


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
