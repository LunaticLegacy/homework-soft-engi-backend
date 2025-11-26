from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.attachment_service import AttachmentService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/attachments", tags=["attachments"])


class AttachmentCreateRequest(BaseModel):
    owner_id: str
    attached_to_type: str
    attached_to_id: str
    file_name: str
    storage_key: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    attachment_type: str = "file"
    metadata: Optional[Dict[str, Any]] = None


def get_attachment_service(db: DatabaseManager = Depends(get_db_manager)) -> AttachmentService:
    return AttachmentService(db)


@router.post("/", response_model=Dict[str, Any])
async def create_attachment(request: AttachmentCreateRequest, svc: AttachmentService = Depends(get_attachment_service)):
    try:
        data = await svc.create_attachment(
            request.owner_id,
            request.attached_to_type,
            request.attached_to_id,
            request.file_name,
            request.file_size,
            request.content_type,
            request.storage_key,
            request.attachment_type,
            request.metadata,
        )
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


class AttachmentListRequest(BaseModel):
    attached_to_type: str
    attached_to_id: str


@router.post("/list", response_model=Dict[str, Any])
async def list_attachments(request: AttachmentListRequest, svc: AttachmentService = Depends(get_attachment_service)):
    try:
        data = await svc.list_attachments(request.attached_to_type, request.attached_to_id)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.delete("/{attachment_id}/", response_model=Dict[str, Any])
async def delete_attachment(attachment_id: str, svc: AttachmentService = Depends(get_attachment_service)):
    try:
        ok = await svc.delete_attachment(attachment_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Attachment not found")
        return {"status": "success", "message": "删除成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
