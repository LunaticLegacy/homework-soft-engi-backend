from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, Any, List
from modules.database import DatabaseManager
from core.database import get_db_manager
from services.user_service import UserService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db_manager: DatabaseManager = Depends(get_db_manager)) -> UserService:
    """
    获取用户服务实例的依赖注入函数
    
    Args:
        db_manager (DatabaseManager): 数据库管理器实例
        
    Returns:
        UserService: 用户服务实例
    """
    return UserService(db_manager)

@router.get("/", response_model=Dict[str, Any])
async def read_users(service: UserService = Depends(get_user_service)) -> Dict[str, Any]:
    """
    获取所有用户列表
    
    Args:
        service (UserService): 用户服务实例
        
    Returns:
        Dict[str, Any]: 用户列表响应
    """
    try:
        users = await service.get_all_users()
        return {
            "success": True,
            "data": users,
            "count": len(users)
        }
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=Dict[str, Any])
async def read_user(
    user_id: str, 
    service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    根据用户ID获取用户信息
    
    Args:
        user_id (str): 用户ID
        service (UserService): 用户服务实例
        
    Returns:
        Dict[str, Any]: 用户信息响应
    """
    try:
        user = await service.get_user_by_id(user_id)
        if user:
            return {
                "success": True,
                "data": user
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    email: str,
    full_name: str,
    password: str,
    service: UserService = Depends(get_user_service)
) -> Dict[str, Any]:
    """
    注册新用户
    
    Args:
        email (str): 用户邮箱
        full_name (str): 用户全名
        password (str): 用户密码
        service (UserService): 用户服务实例
        
    Returns:
        Dict[str, Any]: 新用户信息响应
    """
    try:
        # 简单的密码哈希模拟（实际应用中应使用更安全的方法）
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = await service.create_user(email, full_name, password_hash)
        return {
            "success": True,
            "data": user,
            "message": "User created successfully"
        }
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))