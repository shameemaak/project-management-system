from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Sprint, User
from schemas.sprint import SprintCreate, SprintResponse
from auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/sprints", tags=["Sprints"])

@router.post("/", response_model=SprintResponse)
def create_sprint(sprint_data: SprintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = Sprint(
        name=sprint_data.name,
        project_id=sprint_data.project_id,
        start_date=sprint_data.start_date,
        end_date=sprint_data.end_date
    )
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint

@router.get("/project/{project_id}", response_model=list[SprintResponse])
def get_sprints(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Sprint).filter(Sprint.project_id == project_id).all()

@router.get("/{sprint_id}", response_model=SprintResponse)
def get_sprint(sprint_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint

@router.delete("/{sprint_id}")
def delete_sprint(sprint_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    db.delete(sprint)
    db.commit()
    return {"message": "Sprint deleted"}
