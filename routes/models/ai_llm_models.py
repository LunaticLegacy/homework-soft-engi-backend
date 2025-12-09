from typing import Any, List, Dict, Optional
from pydantic import BaseModel
from dataclasses import dataclass

from .base_models import BaseRequest, BaseResponse


@dataclass
class TaskDecomposeRequest(BaseRequest):
    """任务分解请求模型"""
    goal: str
    user_id: str
    project_id: str
    workspace_id: str


@dataclass
class TaskSuggestionRequest(BaseRequest):
    """任务建议请求模型"""
    task_id: str
    user_id: str
    workspace_id: str
    project_id: str


@dataclass
class ChatRequest(BaseRequest):
    """AI聊天请求模型"""
    message: str
    user_id: str
    workspace_id: str
    project_id: str
    system_prompt: Optional[str] = None


@dataclass
class TaskItem:
    """任务项模型"""
    id: str
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    estimated_time: Optional[int] = None
    dependencies: Optional[List[str]] = None
    subtasks: Optional[List['TaskItem']] = None


@dataclass
class TaskDecomposeData:
    """任务分解数据模型"""
    goal: str
    tasks: List[TaskItem]


@dataclass
class TaskSuggestionData:
    """任务建议数据模型"""
    task_id: str
    suggestions: List[str]
    resources: Optional[List[str]] = None


@dataclass
class ChatData:
    """聊天数据模型"""
    response: Optional[str]


@dataclass
class TaskDecomposeResponse(BaseResponse):
    """任务分解响应模型"""
    success: bool
    data: Dict[str, Any]  # 这里保持Dict以兼容现有服务实现
    message: str


@dataclass
class TaskSuggestionResponse(BaseResponse):
    """任务建议响应模型"""
    success: bool
    data: Dict[str, Any]  # 这里保持Dict以兼容现有服务实现
    message: str


@dataclass
class ChatResponse(BaseResponse):
    """聊天响应模型"""
    success: bool
    data: ChatData
    message: str


@dataclass
class AIModelInfo:
    """AI模型信息"""
    id: str
    name: str
    provider: str
    model_identifier: str
    created_at: str


@dataclass
class AIRequestRecord:
    """AI请求记录"""
    id: str
    user_id: str
    prompt: str
    response_text: str
    status: str
    created_at: str


@dataclass
class AITaskSuggestionRecord:
    """AI任务建议记录"""
    id: str
    user_id: str
    task_id: str
    suggestion: Dict[str, Any]
    accepted: bool
    rejected: bool
    created_at: str