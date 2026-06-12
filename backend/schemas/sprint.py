from pydantic import BaseModel
from datetime import datetime, date
import uuid

class SprintCreate(BaseModel):
    name: str
    project_id: uuid.UUID
    start_date: date = None
    end_date: date = None

class SprintResponse(BaseModel):
    id: uuid.UUID
    name: str
    project_id: uuid.UUID
    start_date: date = None
    end_date: date = None
    status: str
    ai_plan: str = None
    created_at: datetime

    class Config:
        from_attributes = True
