from fastapi import HTTPException
from typing import Optional, Dict

from .getters import get_redis_manager
from modules import RedisManager

async def get_user_id_from_redis_by_token(
        token: Optional[str]
    ) -> str:
    """
    基于用户token，在redis上获得用户ID。

    Args:
        token (str): 用户token。
    
    Returns:
        (str): 用户ID。
    """
    if not token:
        raise HTTPException(status_code=403, detail="You are still not logged in, please login at first.")
    
    redisman: RedisManager = get_redis_manager()

    user_data: Optional[Dict] = await redisman.get(key=token, deserialize="json")
    if not user_data:
        raise HTTPException(status_code=500, detail="Redis error when deleting workspace.")
    
    user_id: str = user_data["user_id"]
    return user_id
