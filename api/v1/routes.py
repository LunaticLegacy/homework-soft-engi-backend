from fastapi import APIRouter, Depends
from typing import Dict, List
from modules.databaseman import DatabaseManager
from core.database import get_db_manager

router = APIRouter(prefix="/api/v1", tags=["api-v1"])

@router.get("/status")
async def api_status():
    """
    API状态检查
    
    Returns:
        dict: API状态信息
    """
    return {
        "version": "1.0.0",
        "status": "active",
        "message": "API v1 is running"
    }

@router.get("/users")
async def list_users(db: DatabaseManager = Depends(get_db_manager)) -> Dict:
    """
    获取用户列表
    
    Args:
        db (DatabaseManager): 数据库管理器实例
        
    Returns:
        Dict: 用户列表
    """
    try:
        print("Fetching...")
        conn = await db.get_connection(5.0)
        rows = await conn.fetch("SELECT id, email, full_name FROM users")
        users = [dict(row) for row in rows]
        return {
            "success": True,
            "data": users
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }