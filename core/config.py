import json
import os
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
                "db_url": os.environ.get("DATABASE_HOST", "127.0.0.1"),
                "db_username": os.environ.get("DATABASE_USER", "postgres"),
                "db_password": os.environ.get("DATABASE_PASSWORD", "lunamoon"),
                "db_database_name": os.environ.get("DATABASE_NAME", "postgres"),
                "db_port": int(os.environ.get("DATABASE_PORT", 5432)),
                "minconn": 1,
                "maxconn": 20
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": False
            },
            "llm": {
                "api_url": "https://api.deepseek.com",
                "api_key": "key",
                "model": "deepseek-reasoner"
            }
        }