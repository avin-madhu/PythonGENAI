from pydantic import BaseModel, Field, field_validator
from typing import Optional

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)  # Rating between 1 and 5
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    tool_id: int
    user_id: int
    approved: bool

    class Config:
        from_attributes = True