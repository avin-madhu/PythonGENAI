from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db
from models.user import User
from models.tool import Tool
from models.review import Review

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/summary")
async def get_counts(db: AsyncSession = Depends(get_db)):

    # Create the count statements
    user_count_stmt = select(func.count(User.id))
    tool_count_stmt = select(func.count(Tool.id))
    review_count_stmt = select(func.count(Review.id))

    user_res = await db.execute(user_count_stmt)
    tool_res = await db.execute(tool_count_stmt)
    review_res = await db.execute(review_count_stmt)

    return {
        "users": user_res.scalar(),
        "tools": tool_res.scalar(),
        "reviews": review_res.scalar()
    }