from typing import Literal, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 以后得用到这两个Enum了。
class TimeUnit(Enum):
    "minute"
    "hour"
    "day"
    "week"
    "month"

class PriorityUnit(Enum):
    "low"
    "medium"
    "high"
    "critical"

@dataclass
class TaskListInfo:
    # 来自JSON的原始信息。
    main_goal: str
    summary: str
    tasks: List["TaskInfo"]

@dataclass
class TaskInfo:
    # 来自JSON的任务信息。
    title: str
    description: str
    estimated_time: int
    estimated_time_unit: str
    priority: str
    subtasks: List["TaskInfo"]

@dataclass
class Task:
    # 实际从数据库里扒出来的任务信息
    id: str
    project_id: str
    workspace_id: str
    creator_id: str
    assignee_id: Optional[str]
    parent_task_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    status: str                                 # 需要开个enum解决该问题。
    priority: str                               # 需要开个enum解决该问题。
    estimated_minutes: int
    actual_minutes: Optional[int]
    due_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    is_recurring: Optional[str]
    recurrence_rule: Optional[str]
    recurrence_frequency: Optional[str]
    recurrence_meta: Optional[str]
    metadata: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    deleted_at: Optional[str]

@dataclass
class TaskTree:
    # 任务树，容器。
    task: Task
    subtasks: List["TaskTree"]

@dataclass
class TaskResponse:
    # 加任务时的回答内容
    id: str
    project_id: str
    workspace_id: str
    creator_id: str
    assignee_id: Optional[str]
    parent_task_id: Optional[str]
    title: str
    description: Optional[str]
    status: str 
    priority: str
    estimated_minutes: int
    actual_minutes: Optional[int]
    started_at: str
    due_at: str 
    created_at: str 
    updated_at: str



