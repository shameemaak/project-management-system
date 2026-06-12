from pydantic import BaseModel
from datetime import datetime, date
import uuid

class TaskCreate(BaseModel):
    title: str
    description: str = None
    priority: str = "medium"
    project_id: uuid.UUID
    sprint_id: uuid.UUID = None
    assigned_to: uuid.UUID = None
    due_date: date = None

class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    status: str = None
    priority: str = None
    assigned_to: uuid.UUID = None
    sprint_id: uuid.UUID = None
    due_date: date = None

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str = None
    status: str
    priority: str
    project_id: uuid.UUID
    sprint_id: uuid.UUID = None
    assigned_to: uuid.UUID = None
    created_by: uuid.UUID
    due_date: date = None
    created_at: datetime

    class Config:
        from_attributes = True
