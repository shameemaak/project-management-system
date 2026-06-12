from pydantic import BaseModel
from datetime import datetime
import uuid

class TeamCreate(BaseModel):
    name: str
    description: str = None

class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str = None
    created_by: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TeamMemberAdd(BaseModel):
    user_id: uuid.UUID
    role: str = "member"
