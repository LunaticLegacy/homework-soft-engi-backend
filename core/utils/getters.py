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
from core.llm_service import get_llm_fetcher

# 对应的服务
from services import (
    AITaskService, ProjectService, TaskService, UserService, WorkspaceService
)


# 服务方法喵

def get_ai_service(
    db_manager: DatabaseManager = Depends(get_db_manager),
    llm_fetcher: LLMFetcher = Depends(get_llm_fetcher)
) -> AITaskService:
    """
    获取AI任务服务实例的依赖注入函数
    
    Args:
        db_manager (DatabaseManager): 数据库管理器实例
        llm_fetcher (LLMFetcher): LLM获取器实例
        
    Returns:
        AITaskService: AI任务服务实例
    """
    return AITaskService(db_manager, llm_fetcher)

def get_project_service(
        db: DatabaseManager = Depends(get_db_manager)
    ) -> ProjectService:
    return ProjectService(db)

def get_task_service(
        db: DatabaseManager = Depends(get_db_manager)
    ) -> TaskService:
    return TaskService(db)

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
    "get_db_manager", "get_llm_fetcher", "get_redis_manager",
    # 服务方法
    "get_ai_service", "get_project_service", "get_task_service", "get_user_service",
    "get_workspace_service",
]
