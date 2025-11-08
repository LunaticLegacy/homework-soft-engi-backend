import asyncio
import asyncpg
import redis
import redis.asyncio as ario
import json
import pickle
from typing import Any, Dict, List, Optional, Tuple, Literal

from databaseman import DatabaseManager
from redisman import RedisManager

class UnifiedDatabaseIO:
    """
    统一数据库IO类，整合了PostgreSQL和Redis的操作
    提供缓存查询、数据操作和事务处理功能
    """
    def __init__(self):
        # 初始化连接池和序列化器
        self.db_pool: Optional[DatabaseManager] = None
        self.redis_pool: Optional[RedisManager] = None
        self.serializer = pickle
        self.deserializer = pickle

    @classmethod
    async def create(
        cls,
        db_config: Dict[str, Any],
        redis_config: Dict[str, Any],
        serialization_format: Literal["pickle", "json"] = "pickle",
    ) -> "UnifiedDatabaseIO":
        """
        创建UnifiedDatabaseIO实例
        
        Args:
            db_config: 数据库配置
            redis_config: Redis配置
            serialization_format: 序列化格式 ('pickle' 或 'json')
        """
        instance = cls()
        try:
            # 创建数据库和Redis连接池
            instance.db_pool = None
            instance.redis_pool = None
        except Exception as e:
            print(f"Error during pool creation: {e}")
            raise
        
        # 设置序列化方式
        if serialization_format == "json":
            instance.serializer = json
            instance.deserializer = json
        elif serialization_format == "pickle":
            instance.serializer = pickle
            instance.deserializer = pickle
        else:
            raise ValueError("Serialization format must be 'pickle' or 'json'")

        return instance

    async def close(self):
        """关闭数据库和Redis连接池"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_pool:
            await self.redis_pool.close()

    def _generate_cache_key(self, query: str, *params: Any) -> str:
        """生成缓存键"""
        return f"cache:{hash((query, params))}"

    async def fetch_with_cache(
        self,
        query: str,
        *params: Any,
        ttl: int = 300,
    ) -> List[Dict[str, Any]]:
        """
        带缓存的查询方法
        
        Args:
            query: SQL查询语句
            params: 查询参数
            ttl: 缓存过期时间(秒)
        """
        cache_key = self._generate_cache_key(query, *params)
        try:
            # 尝试从缓存获取数据
            async with self.redis_pool.client() as redis:
                cached_data = await redis.get(cache_key)
                if cached_data:
                    return self.deserializer.loads(cached_data)
        except Exception as e:
            print(f"Redis cache read error: {e}")

        # 缓存未命中，从数据库查询
        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            result = [dict(record) for record in records]

        # 将结果存入缓存
        try:
            async with self.redis_pool.client() as redis:
                serialized_data = self.serializer.dumps(result)
                await redis.set(cache_key, serialized_data, ex=ttl)
        except Exception as e:
            print(f"Redis cache write error: {e}")

        return result

    async def fetch_one_with_cache(
        self,
        query: str,
        *params: Any,
        ttl: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        Args:
            query: SQL查询语句
            params: 查询参数
            ttl: 缓存过期时间(秒)
        """
        results = await self.fetch_with_cache(query, *params, ttl=ttl)
        return results[0] if results else None

    async def execute_and_invalidate(
        self,
        command: str,
        *params: Any,
        invalidate_patterns: List[str] = None,
    ) -> str:
        """
        执行SQL命令并清除相关缓存
        
        Args:
            command: SQL命令
            params: 命令参数
            invalidate_patterns: 需要清除的缓存键模式
        """
        async with self.db_pool.acquire() as conn:
            status = await conn.execute(command, *params)

        # 清除相关缓存
        if invalidate_patterns:
            try:
                async with self.redis_pool.client() as redis:
                    for pattern in invalidate_patterns:
                        keys_to_delete = [key async for key in redis.scan_iter(pattern)]
                        if keys_to_delete:
                            await redis.delete(*keys_to_delete)
            except Exception as e:
                print(f"Redis cache invalidation error: {e}")

        return status

    async def transaction(
            self, 
            *operations: Tuple[str, Tuple]
        ) -> None:
        """
        执行数据库事务
        
        Args:
            operations: SQL命令和参数的元组列表
        """
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for command, params in operations:
                    await conn.execute(command, *params)
