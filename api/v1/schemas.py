from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: Optional[str] = None
    owner_user_id: Optional[str] = None
    settings: Optional[dict] = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[dict] = None


class ProjectCreate(BaseModel):
    workspace_id: Optional[str] = None
    owner_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    archived: Optional[bool] = None
    metadata: Optional[dict] = None


class TaskCreate(BaseModel):
    project_id: Optional[str] = None
    workspace_id: Optional[str] = None
    creator_id: Optional[str] = None
    assignee_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    due_at: Optional[datetime] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[str] = None
    estimated_minutes: Optional[int] = None
    due_at: Optional[datetime] = None


