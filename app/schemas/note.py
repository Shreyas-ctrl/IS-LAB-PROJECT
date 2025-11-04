from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NoteCreate(BaseModel):
    content: str
    keywords: str
    title: str
    drawing: Optional[str] = None  

class NoteRead(BaseModel):
    id: int
    encrypted_title: str
    encrypted_content: str
    encrypted_keywords: str
    signature: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
