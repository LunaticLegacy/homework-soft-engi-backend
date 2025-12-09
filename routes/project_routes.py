from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, UTC

from typing import Any, Dict, Optional
from dataclasses import dataclass

# 自己写的东西喵
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services import ProjectService, WorkspaceService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

# 核心依赖
from core.utils.getters import get_project_service, get_workspace_service
from core.utils.user_id_fetch import get_user_id_from_redis_by_token

from routes.models.project_models import (  # 路由
    ProjectCreateRequest,
    ProjectListRequest,
    ProjectGetRequest,
    ProjectUpdateRequest,
    ProjectDeleteRequest,
    ProjectCreateResponse,
    ProjectListResponse,
)


router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/create/", response_model=ProjectCreateResponse)
async def create_project(
    request: ProjectCreateRequest, 
    svc: ProjectService = Depends(get_project_service),
    workspace: WorkspaceService = Depends(get_workspace_service)
):
    try:
        # 获得用户ID，并检查目标工作空间是否属于该用户。
        user_id: str = await get_user_id_from_redis_by_token(request.token)
        workspace_data: Optional[Dict[str, Any]] = \
            await workspace.get_workspace_by_id(request.workspace_id)

        if not workspace_data:
            raise HTTPException(404, "Not Found")

        if workspace_data["owner_user_id"] != user_id:
            raise HTTPException(404, "Not Found")

        data = await svc.create_project(
            request.workspace_id,
            request.owner_id,
            request.title,
            request.description,
            request.start_date,
            request.due_date,
        )

        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "message": "创建成功", "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))

@router.post("/list/", response_model=ProjectListResponse)
async def list_projects(
    request: ProjectListRequest, 
    svc: ProjectService = Depends(get_project_service)
):
    try:
        # 需要获得用户ID以及该用户对应的权限组，但现在暂时设置为“只有持有者可编辑”。
        data = await svc.list_projects(request.workspace_id)

        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "count": len(data), "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{project_id}/get/", response_model=Dict[str, Any])
async def get_project(
    project_id: str, 
    svc: ProjectService = Depends(get_project_service)
):
    try:
        data = await svc.get_project(project_id)
        if not data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{project_id}/update/", response_model=Dict[str, Any])
async def update_project(
    project_id: str, 
    request: ProjectUpdateRequest, 
    svc: ProjectService = Depends(get_project_service)
):
    try:
        payload: Dict[str, Any] = {k: v for k, v in dict(request).items() if v is not None}
        data = await svc.update_project(project_id, payload)
        if not data:
            raise HTTPException(status_code=404, detail="Project not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "data": data, 
            "message": "更新成功", "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{project_id}/delete/", response_model=Dict[str, Any])
async def delete_project(
    project_id: str, 
    svc: ProjectService = Depends(get_project_service)
):
    try:
        ok = await svc.delete_project(project_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Project not found")
        
        now: datetime = datetime.now(UTC)
        return {
            "status": "success", "message": "删除成功",
             "time": str(now)
        }
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
