from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.task_service import TaskService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreateRequest(BaseModel):
    workspace_id: str
    creator_id: str
    title: str
    project_id: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: str = "medium"
    estimated_minutes: Optional[int] = None
    due_at: Optional[str] = None


class TaskUpdateRequest(BaseModel):
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


def get_task_service(db: DatabaseManager = Depends(get_db_manager)) -> TaskService:
    return TaskService(db)


@router.post("/", response_model=Dict[str, Any])
async def create_task(request: TaskCreateRequest, svc: TaskService = Depends(get_task_service)):
    try:
        data = await svc.create_task(
            request.project_id,
            request.workspace_id,
            request.creator_id,
            request.title,
            request.description,
            request.assignee_id,
            request.priority,
            request.estimated_minutes,
            request.due_at,
        )
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


class TaskListRequest(BaseModel):
    workspace_id: str
    project_id: Optional[str] = None


@router.post("/list", response_model=Dict[str, Any])
async def list_tasks(request: TaskListRequest, svc: TaskService = Depends(get_task_service)):
    try:
        data = await svc.list_tasks(request.workspace_id, request.project_id)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.get("/{task_id}/", response_model=Dict[str, Any])
async def get_task(task_id: str, svc: TaskService = Depends(get_task_service)):
    try:
        data = await svc.get_task(task_id)
        if not data:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success", "data": data}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.put("/{task_id}/", response_model=Dict[str, Any])
async def update_task(task_id: str, request: TaskUpdateRequest, svc: TaskService = Depends(get_task_service)):
    try:
        payload: Dict[str, Any] = {k: v for k, v in request.dict().items() if v is not None}
        data = await svc.update_task(task_id, payload)
        if not data:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success", "data": data, "message": "更新成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{task_id}/", response_model=Dict[str, Any])
async def delete_task(task_id: str, svc: TaskService = Depends(get_task_service)):
    try:
        ok = await svc.delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success", "message": "删除成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
