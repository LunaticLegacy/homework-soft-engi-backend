from typing import Any, Dict

from .unified_io import UnifiedDatabaseIO 

__version__ = "0.1.0"  # 定义包版本号

async def create_io(
    db_config: Dict[str, Any],
    redis_config: Dict[str, Any],
    serialization_format: str = "pickle",
) -> UnifiedDatabaseIO:  # 返回初始化完成的接口实例
    return await UnifiedDatabaseIO.create(
        db_config=db_config,
        redis_config=redis_config,
        serialization_format=serialization_format,
    )

__all__ = ["UnifiedDatabaseIO", "create_io", "__version__"]