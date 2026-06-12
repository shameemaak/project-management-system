from pydantic import BaseModel
from datetime import datetime, date
import uuid

class ProjectCreate(BaseModel):
    name: str
    description: str = None
    team_id: uuid.UUID
    start_date: date = None
    end_date: date = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str = None
    status: str
    team_id: uuid.UUID
    owner_id: uuid.UUID
    start_date: date = None
    end_date: date = None
    created_at: datetime

    class Config:
        from_attributes = True
