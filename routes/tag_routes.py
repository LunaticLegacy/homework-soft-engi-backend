from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.tag_service import TagService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/tags", tags=["tags"])


class TagCreateRequest(BaseModel):
    workspace_id: str
    user_id: str
    name: str
    color: Optional[str] = None


class TagAttachRequest(BaseModel):
    task_id: str
    tag_id: str


def get_tag_service(db: DatabaseManager = Depends(get_db_manager)) -> TagService:
    return TagService(db)


@router.post("/", response_model=Dict[str, Any])
async def create_tag(request: TagCreateRequest, svc: TagService = Depends(get_tag_service)):
    try:
        data = await svc.create_tag(request.workspace_id, request.name, request.color, request.user_id)
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


class TagListRequest(BaseModel):
    workspace_id: str


@router.post("/list", response_model=Dict[str, Any])
async def list_tags(request: TagListRequest, svc: TagService = Depends(get_tag_service)):
    try:
        data = await svc.list_tags(request.workspace_id)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/attach/", response_model=Dict[str, Any])
async def attach_tag(request: TagAttachRequest, svc: TagService = Depends(get_tag_service)):
    try:
        await svc.attach_tag(request.task_id, request.tag_id)
        return {"status": "success", "message": "标签已关联"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/detach/", response_model=Dict[str, Any])
async def detach_tag(request: TagAttachRequest, svc: TagService = Depends(get_tag_service)):
    try:
        await svc.detach_tag(request.task_id, request.tag_id)
        return {"status": "success", "message": "标签已移除"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
