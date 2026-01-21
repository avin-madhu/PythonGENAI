from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ToolBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    category: str

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None

class Tool(ToolBase):
    id: int
    avg_rating: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True