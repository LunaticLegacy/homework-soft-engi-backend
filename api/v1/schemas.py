from datetime import date, datetime
from typing import List, Optional
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


class TagCreate(BaseModel):
    workspace_id: str
    name: str
    color: Optional[str] = None
    created_by: Optional[str] = None


class CommentCreate(BaseModel):
    resource_type: str
    resource_id: str
    user_id: Optional[str] = None
    content: str
    content_html: Optional[str] = None
    reply_to_comment_id: Optional[str] = None


class AttachmentCreate(BaseModel):
    owner_user_id: Optional[str] = None
    attached_to_type: Optional[str] = None
    attached_to_id: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    storage_key: Optional[str] = None
    attachment_type: Optional[str] = None
    metadata: Optional[dict] = Field(default_factory=dict)


class NotificationCreate(BaseModel):
    user_id: str
    level: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    data: Optional[dict] = Field(default_factory=dict)
    is_read: Optional[bool] = False
    channel: Optional[str] = None


class NotificationReadUpdate(BaseModel):
    is_read: bool = True


class SearchQuery(BaseModel):
    query: str
    workspace_id: Optional[str] = None


class TagIds(BaseModel):
    tag_ids: List[str]
