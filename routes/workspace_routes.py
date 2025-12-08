from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, Any, List
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from modules.redisman import RedisManager
from core.database import get_db_manager
from core.redis_cache import get_redis_manager
from services.workspace_service import WorkspaceService
from services.user_service import UserService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from datetime import datetime, timedelta, UTC
import jwt
from passlib.context import CryptContext
import os
from routes.models.workspace_models import (
    WorkspaceCreateRequest,
    WorkspaceUpdateRequest,
    WorkspaceDeleteRequest,
    WorkSpaceGetRequest,
    WorkSpaceQueryRequest,
    WorkspaceCreateResponse,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceUpdateResponse,
    WorkspaceDeleteResponse
)


JWT_SECRET = os.getenv("JWT_SECRET", "secret_key")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def get_workspace_service(db: DatabaseManager = Depends(get_db_manager)) -> WorkspaceService:
    return WorkspaceService(db)

def get_user_service(db: DatabaseManager = Depends(get_db_manager)) -> UserService:
    return UserService(db)

@router.post("/create/", response_model=WorkspaceCreateResponse)
async def create_workspace(
    request: WorkspaceCreateRequest,
    svc: WorkspaceService = Depends(get_workspace_service),
    user: UserService = Depends(get_user_service),
    db: DatabaseManager = Depends(get_db_manager),
    redisman: RedisManager = Depends(get_redis_manager),
):
    """创建工作空间。"""
    try:
        # redis检测头：获取用户ID
        token: Optional[str] = request.token
        if not token:
            raise HTTPException(status_code=403, detail="You are still not logged in, please login at first.")

        id_sets: Optional[Any] = await redisman.get(token, deserialize="json")
        if not id_sets:
            raise HTTPException(status_code=403, detail="Invalid User")

        user_id: str = dict(id_sets)["user_id"]
        # 检测头结束

        now = datetime.now(UTC)
        workspace = await svc.create_workspace(request.name, request.description, owner_user_id=user_id)
        return {"status": "success", "data": workspace, "message": "创建成功", "time": str(now)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))


@router.post("/list/", response_model=WorkspaceListResponse)
async def list_workspaces(
    request: WorkSpaceQueryRequest,
    svc: WorkspaceService = Depends(get_workspace_service),
    user: UserService = Depends(get_user_service),
    db: DatabaseManager = Depends(get_db_manager),
    redisman: RedisManager = Depends(get_redis_manager),
):
    """获取当前用户下的工作空间列表。"""
    try:
        # redis检测头：获取用户ID
        token: Optional[str] = request.token
        if not token:
            raise HTTPException(status_code=403, detail="You are still not logged in, please login at first.")
 
        user_data: Optional[Dict] = await redisman.get(key=token, deserialize="json")
        if not user_data:
            raise HTTPException(status_code=500, detail="Redis error when deleting workspace.")
        
        user_id: str = user_data["user_id"]
        # 检测头结束

        # 正式逻辑
        data: Optional[List[Dict[str, Any]]] | List = await svc.get_workspace_by_user_id(user_id)
        if not data:
            data = []
        data = list(data)

        now = datetime.now(UTC)
        return {"status": "success", "data": data, "count": len(data), "time": str(now)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))


@router.post("/{workspace_id}/", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str, 
    request: WorkSpaceGetRequest,
    svc: WorkspaceService = Depends(get_workspace_service),
    user: UserService = Depends(get_user_service),
    redisman: RedisManager = Depends(get_redis_manager),
):
    """获取指定工作空间。"""
    try:
        # 这个就不需要token头了。
        ws = await svc.get_workspace_by_id(workspace_id)
        
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace not found")
        now = datetime.now(UTC)
        return {"status": "success", "data": ws, "time": str(now)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))


@router.put("/{workspace_id}/", response_model=WorkspaceUpdateResponse)
async def update_workspace(
    workspace_id: str, 
    request: WorkspaceUpdateRequest, 
    svc: WorkspaceService = Depends(get_workspace_service),
    user: UserService = Depends(get_user_service),
    redisman: RedisManager = Depends(get_redis_manager),
):
    """更新工作空间。"""
    try:
        # redis检测头：获取用户ID
        token: Optional[str] = request.token
        if not token:
            raise HTTPException(status_code=403, detail="You are still not logged in, please login at first.")
 
        user_data: Optional[Dict] = await redisman.get(key=token, deserialize="json")
        if not user_data:
            raise HTTPException(status_code=500, detail="Redis error when deleting workspace.")
        
        user_id: str = user_data["user_id"]
        # 检测头结束

        # 检查工作空间所有者ID是否正确。
        result: Optional[List[Dict[str, Any]]] = await svc.get_workspace_by_user_id(user_id=user_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # 更新工作空间逻辑。
        updated = await svc.update_workspace(workspace_id, request.name, request.description)
        if not updated:
            raise HTTPException(status_code=404, detail="Workspace not found")
        now = datetime.now(UTC)
        return {"status": "success", "data": updated, "message": "更新成功", "time": str(now)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))


@router.delete("/{workspace_id}/", response_model=WorkspaceDeleteResponse)
async def delete_workspace(
    workspace_id: str, 
    request: WorkspaceDeleteRequest, 
    svc: WorkspaceService = Depends(get_workspace_service),
    user: UserService = Depends(get_user_service),
    redisman: RedisManager = Depends(get_redis_manager),
):
    """删除工作空间。"""
    try:
        # redis检测头：获取用户ID
        token: Optional[str] = request.token
        if not token:
            raise HTTPException(status_code=403, detail="You are still not logged in, please login at first.")
 
        user_data: Optional[Dict] = await redisman.get(key=token, deserialize="json")
        if not user_data:
            raise HTTPException(status_code=500, detail="Redis error when deleting workspace.")
        
        user_id: str = user_data["user_id"]
        # 检测头结束

        # 检查目标工作空间所属人是否为该ID持有者。
        target = await svc.get_workspace_by_id(workspace_id=workspace_id)

        if not target:
            # 不存在目标
            raise HTTPException(404, detail="Target workspace not found.")
        
        if str(target["owner_user_id"]) != user_id:
            # ID不对
            raise HTTPException(404, detail="Target workspace is not yours.")

        # 如果不是，直接返回HTTP错误，否则再继续向下走。
        ok = await svc.delete_workspace(workspace_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Workspace not found")
        now = datetime.now(UTC)
        return {"status": "success", "message": "删除成功", "time": str(now)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))
