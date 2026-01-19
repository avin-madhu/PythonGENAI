from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from langgraph_sdk.auth.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from project1.core.security import create_access_token
from project1.db.repositories import get_user_by_username, create_user
from project1.db.session import get_db
from project1.schemas.auth import UserCreate, TokenResponse, UserLogin
from project1.utils.hashing import hash_password, verify_password

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


@router.post("/register")
async def register_user(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="user already exists"
        )

    await create_user(
        db=db,
        username=user.username,
        hashedPassword=hash_password(user.password)
    )

    return {"message": "user created successfully"}


@router.post("/login", response_model=TokenResponse)
async def login_user(
        user: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    db_user = await get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": db_user.username})
    return TokenResponse(access_token=token)


@router.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {"message": "You are authenticated"}
