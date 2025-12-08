from typing import Any, Dict, Optional
from pydantic import BaseModel
from dataclasses import dataclass

from .base_models import BaseRequest, BaseResponse


@dataclass
class ProjectListRequest(BaseRequest):
    workspace_id: str

@dataclass
class ProjectGetRequest(BaseRequest):
    pass

@dataclass
class ProjectCreateRequest(BaseRequest):
    workspace_id: str
    owner_id: str
    title: str
    description: str
    start_date: Optional[str] = None
    due_date: Optional[str] = None


@dataclass
class ProjectUpdateRequest(BaseRequest):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    archived: Optional[bool] = None

@dataclass
class ProjectDeleteRequest(BaseRequest):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    archived: Optional[bool] = None