from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Team, TeamMember, User
from schemas.team import TeamCreate, TeamResponse, TeamMemberAdd
from auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.post("/", response_model=TeamResponse)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = Team(name=team_data.name, description=team_data.description, created_by=current_user.id)
    db.add(team)
    db.commit()
    db.refresh(team)
    member = TeamMember(team_id=team.id, user_id=current_user.id, role="owner")
    db.add(member)
    db.commit()
    return team

@router.get("/", response_model=list[TeamResponse])
def get_my_teams(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    memberships = db.query(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    team_ids = [m.team_id for m in memberships]
    return db.query(Team).filter(Team.id.in_(team_ids)).all()

@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.post("/{team_id}/members")
def add_member(team_id: uuid.UUID, member_data: TeamMemberAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == member_data.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in team")
    member = TeamMember(team_id=team_id, user_id=member_data.user_id, role=member_data.role)
    db.add(member)
    db.commit()
    return {"message": "Member added successfully"}

@router.delete("/{team_id}")
def delete_team(team_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    team = db.query(Team).filter(Team.id == team_id, Team.created_by == current_user.id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found or not authorized")
    db.delete(team)
    db.commit()
    return {"message": "Team deleted"}
