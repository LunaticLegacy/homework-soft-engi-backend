from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, Any, List
from pydantic import BaseModel
from modules.databaseman import DatabaseManager
from modules.redisman import RedisManager
from core.database import get_db_manager
from core.redis_cache import get_redis_manager
from services.workspace_service import WorkspaceService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError
import uuid

# 定义请求模型
class BaseRequest(BaseModel):
    time: str
    token: str

class WorkspaceCreateRequest(BaseModel):
    time: str
    token: str
    name: str
    description: Optional[str] = None

class WorkspaceUpdateRequest(BaseModel):
    time: str
    token: str
    name: Optional[str] = None
    description: Optional[str] = None

class WorkspaceDeleteRequest(BaseModel):
    time: str
    token: str

# 定义响应模型
class BaseResponse(BaseModel):
    status: str
    message: str

class WorkspaceCreateResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str

class WorkspaceListResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
    count: int

class WorkspaceResponse(BaseModel):
    status: str
    data: Dict[str, Any]

class WorkspaceUpdateResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    message: str

class WorkspaceDeleteResponse(BaseModel):
    status: str
    message: str


router = APIRouter(prefix="/workspaces", tags=["workspaces"])

def get_workspace_service(db: DatabaseManager = Depends(get_db_manager)) -> WorkspaceService:
    return WorkspaceService(db)

@router.post("/create/", response_model=WorkspaceCreateResponse)
async def create_workspace(
    request: WorkspaceCreateRequest, 
    svc: WorkspaceService = Depends(get_workspace_service),
    db: DatabaseManager = Depends(get_db_manager),
    redisman: RedisManager = Depends(get_redis_manager)
    ):
    try:
        token: str = request.token
        id_sets: Optional[Any] = await redisman.get(token, deserialize="json")
        if id_sets:
            user_id: str = dict(id_sets)["user_id"]
            workspace = await svc.create_workspace(request.name, request.description, owner_user_id=user_id)
            return {"status": "success", "data": workspace, "message": "创建成功"}
        else:
            raise HTTPException(status_code=403, detail="Invalid User")
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))

@router.post("/", response_model=WorkspaceListResponse)
async def list_workspaces(request: BaseRequest, svc: WorkspaceService = Depends(get_workspace_service)):
    """
    获取当前用户下的工作空间。
    """
    try:
        data = await svc.get_all_workspaces()
        return {"status": "success", "data": data, "count": len(data)}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))

@router.post("/{workspace_id}/", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, svc: WorkspaceService = Depends(get_workspace_service)):
    try:
        ws = await svc.get_workspace_by_id(workspace_id)
        if not ws:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"status": "success", "data": ws}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))

@router.put("/{workspace_id}/", response_model=WorkspaceUpdateResponse)
async def update_workspace(workspace_id: str, request: WorkspaceUpdateRequest, svc: WorkspaceService = Depends(get_workspace_service)):
    """
    更新工作空间。
    """
    try:
        updated = await svc.update_workspace(workspace_id, request.name, request.description)
        if not updated:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"status": "success", "data": updated, "message": "更新成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))

@router.delete("/{workspace_id}/", response_model=WorkspaceDeleteResponse)
async def delete_workspace(workspace_id: str, request: WorkspaceDeleteRequest, svc: WorkspaceService = Depends(get_workspace_service)):
    try:
        ok = await svc.delete_workspace(workspace_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return {"status": "success", "message": "删除成功"}
    except (DatabaseConnectionError, DatabaseTimeoutError) as e:
        raise HTTPException(status_code=503 if isinstance(e, DatabaseConnectionError) else 408, detail=str(e))
