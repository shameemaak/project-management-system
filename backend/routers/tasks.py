from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Task, User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse
from auth.dependencies import get_current_user
import uuid

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        project_id=task_data.project_id,
        sprint_id=task_data.sprint_id,
        assigned_to=task_data.assigned_to,
        due_date=task_data.due_date,
        created_by=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/project/{project_id}", response_model=list[TaskResponse])
def get_tasks_by_project(project_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.project_id == project_id).all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: uuid.UUID, task_data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_data.title: task.title = task_data.title
    if task_data.description: task.description = task_data.description
    if task_data.status: task.status = task_data.status
    if task_data.priority: task.priority = task_data.priority
    if task_data.assigned_to: task.assigned_to = task_data.assigned_to
    if task_data.sprint_id: task.sprint_id = task_data.sprint_id
    if task_data.due_date: task.due_date = task_data.due_date
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.created_by == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
