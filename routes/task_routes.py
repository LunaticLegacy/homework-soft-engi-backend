from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC

from modules.databaseman import DatabaseManager

from core.database import get_db_manager
from core.utils.getters import (
    get_task_service, get_workspace_service, get_project_service
)
from core.utils.user_id_fetch import get_user_id_from_redis_by_token

from services import TaskService, WorkspaceService, ProjectService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from routes.models.task_models import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskListRequest,
    TaskGetRequest,
    TaskDeleteRequest,
    TaskCreateResponse,
    TaskUpdateResponse,
    TaskListResponse,
    TaskGetResponse,
    TaskDeleteResponse,
)


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/create/", response_model=TaskCreateResponse)
async def create_task(
    request: TaskCreateRequest, 
    svc: TaskService = Depends(get_task_service),
    workspace: WorkspaceService = Depends(get_workspace_service),
    project: ProjectService = Depends(get_project_service)
):
    try:
        # 保证用户ID和用户空间ID的处理
        user_id: str = await get_user_id_from_redis_by_token(request.token)

        if request.creator_id != user_id:
            raise HTTPException(405, "Invalid User ID.")

        data = await svc.create_task(
            request.project_id,
            request.workspace_id,
            user_id,
            request.title,
            request.description,
            request.assignee_id,
            request.priority,
            request.estimated_minutes,
            request.due_at,
        )

        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "message": "创建成功", "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/list/", response_model=TaskListResponse)
async def list_tasks(
    request: TaskListRequest, 
    svc: TaskService = Depends(get_task_service)
):
    try:
        data = await svc.list_tasks(request.workspace_id, request.project_id)

        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "count": len(data), "time": str(now)
            }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{task_id}/get", response_model=TaskGetResponse)
async def get_task(
    task_id: str, 
    svc: TaskService = Depends(get_task_service)
):
    try:
        data = await svc.get_task(task_id)
        if not data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "time": str(now)
            }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.put("/{task_id}/", response_model=Dict[str, Any])
async def update_task(
    task_id: str, 
    request: TaskUpdateRequest, 
    svc: TaskService = Depends(get_task_service)
):
    try:
        payload: Dict[str, Any] = {k: v for k, v in dict(request).items() if v is not None}
        data = await svc.update_task(task_id, payload)
        if not data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "message": "更新成功", "time": str(now)
            }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{task_id}/", response_model=Dict[str, Any])
async def delete_task(
    task_id: str, 
    svc: TaskService = Depends(get_task_service)
):
    try:
        ok = await svc.delete_task(task_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Task not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "message": "删除成功", 
            "time": str(now)
            }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
