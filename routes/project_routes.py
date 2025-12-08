from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from dataclasses import dataclass

from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.project_service import ProjectService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from routes.models.project_models import (
    ProjectListRequest,
    ProjectCreateRequest,
    ProjectUpdateRequest
)


router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_service(db: DatabaseManager = Depends(get_db_manager)) -> ProjectService:
    return ProjectService(db)

@router.post("/", response_model=Dict[str, Any])
async def create_project(request: ProjectCreateRequest, svc: ProjectService = Depends(get_project_service)):
    try:
        data = await svc.create_project(
            request.workspace_id,
            request.owner_id,
            request.title,
            request.description,
            request.start_date,
            request.due_date,
        )
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))

@router.post("/list/", response_model=Dict[str, Any])
async def list_projects(request: ProjectListRequest, svc: ProjectService = Depends(get_project_service)):
    try:
        data = await svc.list_projects(request.workspace_id)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{project_id}/get/", response_model=Dict[str, Any])
async def get_project(project_id: str, svc: ProjectService = Depends(get_project_service)):
    try:
        data = await svc.get_project(project_id)
        if not data:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"status": "success", "data": data}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{project_id}/update/", response_model=Dict[str, Any])
async def update_project(project_id: str, request: ProjectUpdateRequest, svc: ProjectService = Depends(get_project_service)):
    try:
        payload: Dict[str, Any] = {k: v for k, v in request.dict().items() if v is not None}
        data = await svc.update_project(project_id, payload)
        if not data:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"status": "success", "data": data, "message": "更新成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{project_id}/delete/", response_model=Dict[str, Any])
async def delete_project(project_id: str, svc: ProjectService = Depends(get_project_service)):
    try:
        ok = await svc.delete_project(project_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"status": "success", "message": "删除成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
