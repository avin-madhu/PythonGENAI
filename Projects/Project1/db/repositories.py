from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Project1.db.models import User


async def get_user_by_username(
        db: AsyncSession,
        username: str
):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()


async def create_user(
        db: AsyncSession,
        username: str,
        hashedPassword: str
):
    user = User(
        username=username,
        hashed_password=hashedPassword
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
