from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, Optional
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from services.notification_service import NotificationService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationCreateRequest(BaseModel):
    user_id: str
    level: str = "info"
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    channel: str = "in_app"


def get_notification_service(db: DatabaseManager = Depends(get_db_manager)) -> NotificationService:
    return NotificationService(db)


@router.post("/", response_model=Dict[str, Any])
async def create_notification(request: NotificationCreateRequest, svc: NotificationService = Depends(get_notification_service)):
    try:
        data = await svc.create_notification(
            request.user_id,
            request.level,
            request.title,
            request.body,
            request.data,
            request.channel,
        )
        return {"status": "success", "data": data, "message": "创建成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


class NotificationListRequest(BaseModel):
    user_id: str
    unread_only: bool = False


@router.post("/list", response_model=Dict[str, Any])
async def list_notifications(request: NotificationListRequest, svc: NotificationService = Depends(get_notification_service)):
    try:
        data = await svc.list_notifications(request.user_id, request.unread_only)
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))


@router.post("/{notification_id}/read/", response_model=Dict[str, Any])
async def mark_notification_read(notification_id: str, svc: NotificationService = Depends(get_notification_service)):
    try:
        ok = await svc.mark_read(notification_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"status": "success", "message": "已标记为已读"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(status_code=503 if isinstance(exc, DatabaseConnectionError) else 408, detail=str(exc))
