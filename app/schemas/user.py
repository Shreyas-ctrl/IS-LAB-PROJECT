from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str  # Plain password for registration (will be handled securely)

class UserLogin(BaseModel):
    username: str
    password: str  # Plain password for login (used in PAKE)

class UserRead(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True