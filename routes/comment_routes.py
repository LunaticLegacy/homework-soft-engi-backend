from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.comment_service import CommentService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/comments", tags=["comments"])


class CommentCreateRequest(BaseModel):
    resource_type: str
    resource_id: str
    user_id: str
    content: str
    reply_to_comment_id: Optional[str] = None


def get_comment_service(db: DatabaseManager = Depends(get_db_manager)) -> CommentService:
    return CommentService(db)


@router.post("/", response_model=Dict[str, Any])
async def add_comment(request: CommentCreateRequest, svc: CommentService = Depends(get_comment_service)):
    try:
        data = await svc.add_comment(
            request.resource_type,
            request.resource_id,
            request.user_id,
            request.content,
            request.reply_to_comment_id,
        )
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


class CommentListRequest(BaseModel):
    resource_type: str
    resource_id: str


@router.post("/list", response_model=Dict[str, Any])
async def list_comments(request: CommentListRequest, svc: CommentService = Depends(get_comment_service)):
    try:
        data = await svc.list_comments(request.resource_type, request.resource_id)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{comment_id}/", response_model=Dict[str, Any])
async def delete_comment(comment_id: str, svc: CommentService = Depends(get_comment_service)):
    try:
        ok = await svc.delete_comment(comment_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Comment not found")
        return {"status": "success", "message": "删除成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
