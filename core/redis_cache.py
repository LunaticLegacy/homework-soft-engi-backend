from modules.redisman import RedisManager
from core.config import get_settings


settings = get_settings()
redis_manager: RedisManager = RedisManager(**settings.redis.__dict__)


def get_redis_manager() -> RedisManager:
    """
    获取redis管理器实例
    
    Returns:
        RedisManager: redis管理器实例
    """
    return redis_manager
