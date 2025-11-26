from modules.databaseman import DatabaseManager
from core.config import get_settings


settings = get_settings()
db_manager: DatabaseManager = DatabaseManager(**settings.database.__dict__)


def get_db_manager() -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Returns:
        DatabaseManager: 数据库管理器实例
    """
    return db_manager
