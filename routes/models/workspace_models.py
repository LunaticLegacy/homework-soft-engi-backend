from typing import Dict, Optional, Any, List
from pydantic import BaseModel

from .base_models import BaseRequest, BaseResponse

# 请求模型
class WorkspaceCreateRequest(BaseRequest):
    # 创建工作空间
    name: str
    description: Optional[str] = None


class WorkspaceUpdateRequest(BaseRequest):
    # 更新工作空间
    name: Optional[str] = None
    description: Optional[str] = None


class WorkspaceDeleteRequest(BaseRequest):
    # 删除工作空间
    pass

class WorkSpaceGetRequest(BaseRequest):
    # 获取工作空间内项目
    pass

class WorkSpaceQueryRequest(BaseRequest):
    # 获取用户名下工作空间
    pass

# 响应模型
class WorkspaceCreateResponse(BaseResponse):
    status: str
    data: Dict[str, Any]
    message: str


class WorkspaceListResponse(BaseResponse):
    status: str
    data: List[Dict[str, Any]]
    count: int


class WorkspaceResponse(BaseResponse):
    status: str
    data: Dict[str, Any]


class WorkspaceUpdateResponse(BaseResponse):
    status: str
    data: Dict[str, Any]
    message: str


class WorkspaceDeleteResponse(BaseResponse):
    status: str
    message: str