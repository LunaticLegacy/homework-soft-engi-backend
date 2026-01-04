from typing import Any, List, Dict, Optional
from pydantic import BaseModel
from dataclasses import dataclass

from .base_models import BaseRequest, BaseResponse
from .ai_llm_models import LLMContext

@dataclass
class ProjectCreateRequest(BaseRequest):
    workspace_id: str
    owner_id: str
    title: str
    description: str
    start_date: Optional[str] = None
    due_date: Optional[str] = None

@dataclass
class ProjectListRequest(BaseRequest):
    workspace_id: str

@dataclass
class ProjectGetRequest(BaseRequest):
    pass

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

@dataclass
class ProjectLLMContextRequest(BaseRequest):
    workspace_id: str
    project_id: str

@dataclass
class ProjectCreateResponse(BaseResponse):
    status: str
    data: Dict[str, Any]
    message: str

@dataclass
class ProjectListResponse(BaseResponse):
    status: str
    data: List[Dict[str, Any]]
    count: int

@dataclass
class ProjectGetResponse(BaseResponse):
    status: str
    data: Dict[str, Any]

@dataclass
class ProjectUpdateResponse(BaseResponse):
    status: str
    data: Dict[str, Any]
    message: str

@dataclass
class ProjectDeleteResponse(BaseResponse):
    status: str
    message: str

@dataclass
class ProjectLLMContextResponse(BaseResponse):
    contexts: List[LLMContext]

