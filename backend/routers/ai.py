from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Task, User, Sprint
from auth.dependencies import get_current_user
from pydantic import BaseModel
import anthropic
import os
import json
import uuid

router = APIRouter(prefix="/ai", tags=["AI Features"])

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class TaskBreakdownRequest(BaseModel):
    project_description: str
    project_id: uuid.UUID

class SprintPlanRequest(BaseModel):
    sprint_id: uuid.UUID
    team_size: int
    sprint_duration_days: int = 14

@router.post("/breakdown")
def ai_task_breakdown(
    request: TaskBreakdownRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    prompt = f"""You are a project management expert. Break down this project into specific tasks.

Project Description: {request.project_description}

Return ONLY a JSON array with no explanation, like this:
[
  {{"title": "task title", "description": "task details", "priority": "high/medium/low"}},
  {{"title": "task title", "description": "task details", "priority": "high/medium/low"}}
]

Generate 5 to 8 tasks."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    try:
        tasks_data = json.loads(response_text)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            tasks_data = json.loads(match.group())
        else:
            raise HTTPException(status_code=500, detail="AI response parsing failed")

    created_tasks = []
    for task_info in tasks_data:
        task = Task(
            title=task_info.get("title", "Untitled Task"),
            description=task_info.get("description", ""),
            priority=task_info.get("priority", "medium"),
            project_id=request.project_id,
            created_by=current_user.id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        created_tasks.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status
        })

    return {
        "message": f"AI created {len(created_tasks)} tasks successfully",
        "tasks": created_tasks
    }

@router.post("/sprint-plan")
def ai_sprint_plan(
    request: SprintPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sprint = db.query(Sprint).filter(Sprint.id == request.sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")

    tasks = db.query(Task).filter(Task.sprint_id == request.sprint_id).all()

    if not tasks:
        tasks = db.query(Task).filter(
            Task.project_id == sprint.project_id,
            Task.status == "todo"
        ).limit(10).all()

    task_list = "\n".join([
        f"- {t.title} (priority: {t.priority}, status: {t.status})"
        for t in tasks
    ])

    prompt = f"""You are an agile project manager. Create a sprint plan.

Sprint: {sprint.name}
Duration: {request.sprint_duration_days} days
Team Size: {request.team_size} members

Tasks to plan:
{task_list}

Return ONLY a JSON object like this:
{{
  "sprint_goal": "what this sprint achieves",
  "recommended_tasks": ["task1", "task2"],
  "daily_plan": {{
    "week1": "focus description",
    "week2": "focus description"
  }},
  "estimated_completion": "percentage as number",
  "risks": ["risk1", "risk2"],
  "recommendations": "brief advice"
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    try:
        plan = json.loads(response_text)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            plan = json.loads(match.group())
        else:
            plan = {"raw_plan": response_text}

    sprint.ai_plan = json.dumps(plan)
    db.commit()

    return {
        "message": "AI sprint plan generated successfully",
        "sprint": sprint.name,
        "plan": plan
    }

@router.get("/sprint-plan/{sprint_id}")
def get_sprint_plan(
    sprint_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    if not sprint.ai_plan:
        raise HTTPException(status_code=404, detail="No AI plan generated yet")
    return {
        "sprint": sprint.name,
        "plan": json.loads(sprint.ai_plan)
    }
