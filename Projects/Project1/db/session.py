from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from Project1.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,  # shows the sql it executed in the cmd
    pool_pre_ping=True,  # just do a pre health check of the DB in case it time out or anything
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    # usually after saving SQLalchemy "expires" objects, this is to not let it do that so we can still access objects like users
)

Base = declarative_base()  # this is the parent to all your classes.


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
