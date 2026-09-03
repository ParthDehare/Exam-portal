from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserRegister(BaseModel):
    fullname: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters long")
    role: Optional[UserRole] = UserRole.candidate

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserOut(BaseModel):
    id: int
    fullname: str
    email: str
    role: UserRole
    created_at: datetime
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut
