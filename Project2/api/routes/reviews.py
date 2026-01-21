from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from models.user import User

from api.deps import get_db, get_current_user, admin_only
from models.review import Review
from models.tool import Tool
from schemas.review import ReviewCreate

router = APIRouter(tags=["Reviews"])


@router.post("/tools/{tool_id}/reviews")
async def add_review(
    tool_id: int,
    payload: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tool = await db.get(Tool, tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    review = Review(
        tool_id=tool_id,
        user_id=user.id,
        rating=payload.rating,
        comment=payload.comment,
    )

    db.add(review)
    await db.commit()
    return {"message": "Review submitted for approval"}


@router.get("/tools/{tool_id}/reviews")
async def get_reviews(tool_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(
            Review.tool_id == tool_id,
            Review.approved == True
        )
    )
    return result.scalars().all()

@router.get("/reviews/{tool_id}/pending")
async def get_pending_reviews(tool_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(
            and_(
                Review.approved == False,
                Review.tool_id == tool_id
            )
        )
    )
    return result.scalars().all()

@router.get("/reviews/pending")
async def get_pending_reviews(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(
            Review.approved == False
        )
    )
    return result.scalars().all()

@router.put("/reviews/{review_id}/approve", dependencies=[Depends(admin_only)])
async def approve_review(review_id: int, db: AsyncSession = Depends(get_db)):
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.approved = True
    await db.commit()

    # Recalculate avg rating
    avg_stmt = select(func.avg(Review.rating)).where(
        Review.tool_id == review.tool_id,
        Review.approved == True
    )

    result = await db.execute(avg_stmt)
    avg_rating = result.scalar()

    tool = await db.get(Tool, review.tool_id)
    tool.avg_rating = round(avg_rating or 0, 2)

    await db.commit()
    return {"message": "Review approved"}
