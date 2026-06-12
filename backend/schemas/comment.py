from pydantic import BaseModel
from datetime import datetime
import uuid

class CommentCreate(BaseModel):
    content: str
    task_id: uuid.UUID

class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    task_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
