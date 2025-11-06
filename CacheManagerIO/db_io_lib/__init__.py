from typing import Any, Dict  # 导入类型提示：任意类型与字典类型

from .unified_io import UnifiedDatabaseIO  # 从同包模块导入核心类

__version__ = "0.1.0"  # 定义包版本号

async def create_io(
    db_config: Dict[str, Any],  # 数据库连接配置（asyncpg 连接池参数）
    redis_config: Dict[str, Any],  # Redis 连接配置（aioredis 地址或参数）
    serialization_format: str = "pickle",  # 序列化格式（支持 pickle 或 json）
) -> UnifiedDatabaseIO:  # 返回初始化完成的接口实例
    return await UnifiedDatabaseIO.create(  # 调用类的异步工厂方法创建实例
        db_config=db_config,  # 传入数据库配置字典
        redis_config=redis_config,  # 传入 Redis 配置字典
        serialization_format=serialization_format,  # 指定序列化格式
    )  # 返回创建的实例

__all__ = ["UnifiedDatabaseIO", "create_io", "__version__"]  # 对外导出名称列表