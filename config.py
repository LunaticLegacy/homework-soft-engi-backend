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
    with open(json_config_path, "r") as f:
        config = json.load(f)
    return config