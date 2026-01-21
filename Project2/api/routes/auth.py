from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.deps import get_db, get_current_user
from core.security import verify_password, hash_password, create_access_token
from models.user import User
from schemas.Auth import AuthRequest

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/me")
async def get_me(user = Depends(get_current_user)):
    return user

@router.post("/register")
async def register(payload: AuthRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role
    )

    db.add(new_user)
    await db.commit()
    return {"message": "Registered successfully"}


@router.post("/login")
async def login(payload: AuthRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    # Return structure should match what React expects (res.data.user)
    return {
        "token": token,
        "user": {"email": user.email, "role": user.role.value}
    }