from typing import Any, List, Dict, Optional
from pydantic import BaseModel
from dataclasses import dataclass

from .base_models import BaseRequest, BaseResponse


@dataclass
class TaskCreateRequest(BaseRequest):
    workspace_id: str
    creator_id: str
    title: str
    project_id: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: str = "medium"
    estimated_minutes: Optional[int] = None
    due_at: Optional[str] = None


@dataclass
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


@dataclass
class TaskListRequest(BaseRequest):
    workspace_id: str
    project_id: str

@dataclass
class TaskGetRequest(BaseRequest):
    pass

@dataclass
class TaskDeleteRequest(BaseRequest):
    pass

@dataclass
class TaskCreateResponse(BaseResponse):
    task_id: str
    message: str
    time: str

@dataclass
class TaskListResponse(BaseResponse):
    status: str
    data: List[Dict[str, Any]]
    count: int

@dataclass
class TaskGetResponse(BaseResponse):
    status: str
    data: Dict[str, Any]

@dataclass
class TaskUpdateResponse(BaseResponse):
    message: str
    time: str
    data: Dict[str, Any]

@dataclass
class TaskDeleteResponse(BaseResponse):
    message: str
    time: str

