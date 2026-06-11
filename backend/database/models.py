import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="member")
    created_at = Column(DateTime, default=datetime.utcnow)

    teams_created = relationship("Team", back_populates="creator")
    team_memberships = relationship("TeamMember", back_populates="user")
    projects_managed = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")

class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", back_populates="teams_created")
    members = relationship("TeamMember", back_populates="team")
    projects = relationship("Project", back_populates="team")

class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(20), default="member")
    joined_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    team = relationship("Team", back_populates="projects")
    owner = relationship("User", back_populates="projects_managed")
    tasks = relationship("Task", back_populates="project")
    sprints = relationship("Sprint", back_populates="project")

class Sprint(Base):
    __tablename__ = "sprints"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="planned")
    ai_plan = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="todo")
    priority = Column(String(10), default="medium")
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(UUID(as_uuid=True), ForeignKey("sprints.id"), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    due_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by])
    comments = relationship("Comment", back_populates="task")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")
