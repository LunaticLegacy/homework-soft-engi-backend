# -*- coding: utf-8 -*-

# 库
from fastapi import Depends
from typing import Optional, Any, Dict, List

# 管理器类
from modules.databaseman import DatabaseManager
from modules.redisman import RedisManager
from modules.llm_fetcher import LLMFetcher

# 对应的调度方法，这些也需要被导出
from core.database import get_db_manager
from core.redis_cache import get_redis_manager

# 对应的服务
from services import (
    ProjectService, UserService, WorkspaceService
)


# 服务方法喵
def get_project_service(
        db: DatabaseManager = Depends(get_db_manager)
    ) -> ProjectService:
    return ProjectService(db)

def get_user_service(
        db: DatabaseManager = Depends(get_db_manager)
    ) -> UserService:
    return UserService(db)

def get_workspace_service(
        db: DatabaseManager = Depends(get_db_manager)
    ) -> WorkspaceService:
    return WorkspaceService(db)



# 导出符号表
__all__ = [
    # 调度方法
    "get_db_manager", "get_redis_manager",
    # 服务方法
    "get_project_service", "get_user_service",
    "get_workspace_service",
]
