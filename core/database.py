from modules.databaseman import DatabaseManager
from core.config import load_config
from typing import Dict

# 全局配置和数据库管理器实例
config: Dict = load_config()
db_manager: DatabaseManager = DatabaseManager(**config["database"])

def get_db_manager() -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Returns:
        DatabaseManager: 数据库管理器实例
    """
    return db_manager