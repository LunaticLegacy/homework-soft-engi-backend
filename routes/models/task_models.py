from typing import Any, Dict, Optional
from pydantic import BaseModel

from .base_models import BaseRequest, BaseResponse

class TaskCreateRequest(BaseRequest):
    workspace_id: str
    creator_id: str
    title: str
    project_id: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: str = "medium"
    estimated_minutes: Optional[int] = None
    due_at: Optional[str] = None


class TaskUpdateRequest(BaseRequest):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    status: Optional[str] = None
    due_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class TaskListRequest(BaseRequest):
    workspace_id: str
    project_id: Optional[str] = None