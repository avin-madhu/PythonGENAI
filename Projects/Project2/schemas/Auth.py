from pydantic import BaseModel, EmailStr
from typing import Optional

class AuthRequest(BaseModel):
    email: str
    password: str
    role: Optional[str] = "USER"