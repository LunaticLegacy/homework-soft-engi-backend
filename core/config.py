import json
from typing import Dict, Any

def load_config(json_config_path: str = "./config.json") -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        json_config_path (str): 配置文件路径
        
    Returns:
        Dict[str, Any]: 配置字典
    """
    try:
        with open(json_config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # 如果没有找到配置文件，返回默认配置
        return {
            "database": {
                "db_url": "127.0.0.1",
                "db_username": "postgres",
                "db_password": "lunamoon",
                "db_database_name": "postgres",
                "db_port": 5432,
                "minconn": 1,
                "maxconn": 20
            },
            "server": {
                "host": "127.0.0.1",
                "port": 8000,
                "reload": True
            }
        }