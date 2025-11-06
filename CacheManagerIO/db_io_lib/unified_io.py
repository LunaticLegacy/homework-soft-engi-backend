import asyncio
import asyncpg
import redis.asyncio as aioredis
import json
import pickle
from typing import Any, Dict, List, Optional, Tuple, Union

class UnifiedDatabaseIO:
    """统一的数据库与缓存 I/O 封装类
    
    提供PostgreSQL数据库和Redis缓存的统一异步操作接口
    """
    
    def __init__(self):
        """初始化实例属性"""
        self.db_pool = None
        self.redis_pool = None
        self.serializer = pickle
        self.deserializer = pickle

    @classmethod
    async def create(
        cls,
        db_config: Dict[str, Any],
        redis_config: Dict[str, Any],
        serialization_format: str = "pickle",
    ) -> "UnifiedDatabaseIO":
        """创建 UnifiedDatabaseIO 实例
        
        Args:
            db_config: 数据库连接配置，传入 asyncpg.create_pool 的参数
            redis_config: Redis 连接配置，包含 host, port, db 等参数
            serialization_format: 序列化格式，支持 "pickle" 或 "json"
            
        Returns:
            UnifiedDatabaseIO: 返回创建好的 UnifiedDatabaseIO 实例
            
        Raises:
            ValueError: 如果序列化格式不支持
            Exception: 如果连接池创建失败
        """
        instance = cls()
        try:
            instance.db_pool = await asyncpg.create_pool(**db_config)
            
            # 尝试创建Redis连接池，如果失败则降级为无缓存模式
            try:
                redis_url = f"redis://{redis_config.get('host', 'localhost')}:{redis_config.get('port', 6379)}"
                if 'db' in redis_config:
                    redis_url += f"/{redis_config['db']}"
                instance.redis_pool = aioredis.from_url(redis_url)
                instance.redis_available = True
                print("Redis缓存已启用")
            except Exception as e:
                instance.redis_pool = None
                instance.redis_available = False
                print(f"Redis缓存不可用，降级为仅数据库模式: {e}")
        except Exception as e:
            print(f"Error during pool creation: {e}")
            raise

        if serialization_format == "json":
            instance.serializer = json
            instance.deserializer = json
        elif serialization_format != "pickle":
            raise ValueError("Serialization format must be 'pickle' or 'json'")

        return instance

    async def close(self):
        """关闭数据库和缓存连接，进行资源清理"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_pool:
            await self.redis_pool.close()

    def _generate_cache_key(self, query: str, *params: Any) -> str:
        """生成缓存键，基于查询语句与参数
        
        Args:
            query: SQL查询语句
            *params: 查询参数
            
        Returns:
            str: 生成的缓存键
        """
        return f"cache:{hash((query, params))}"

    async def fetch_with_cache(
        self,
        query: str,
        *params: Any,
        ttl: int = 300,
    ) -> List[Dict[str, Any]]:
        """执行带缓存的查询操作
        
        Args:
            query: SQL 查询语句（SELECT）
            *params: 查询参数，可变长度
            ttl: 缓存有效期（秒），默认 300 秒
            
        Returns:
            List[Dict[str, Any]]: 返回记录列表，每条记录为字典
        """
        # 如果Redis不可用，直接查询数据库
        if not self.redis_available:
            async with self.db_pool.acquire() as conn:
                records = await conn.fetch(query, *params)
                if records:
                    columns = list(records[0].keys())
                    result = [dict(zip(columns, record)) for record in records]
                else:
                    result = []
                return result
        
        cache_key = self._generate_cache_key(query, *params)
        try:
            cached_data = await self.redis_pool.get(cache_key)
            if cached_data:
                return self.deserializer.loads(cached_data)
        except Exception as e:
            print(f"Redis cache read error: {e}")

        async with self.db_pool.acquire() as conn:
            records = await conn.fetch(query, *params)
            if records:
                columns = list(records[0].keys())
                result = [dict(zip(columns, record)) for record in records]
            else:
                result = []

        try:
            serialized_data = self.serializer.dumps(result)
            await self.redis_pool.set(cache_key, serialized_data, ex=ttl)
        except Exception as e:
            print(f"Redis cache write error: {e}")

        return result

    async def fetch_one_with_cache(
        self,
        query: str,
        *params: Any,
        ttl: int = 300,
    ) -> Optional[Dict[str, Any]]:
        """执行带缓存的单条记录查询
        
        Args:
            query: SQL 查询语句（期望返回单条记录）
            *params: 查询参数
            ttl: 缓存有效期（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 返回单条记录的字典或 None
        """
        # 如果Redis不可用，直接查询数据库
        if not self.redis_available:
            async with self.db_pool.acquire() as conn:
                record = await conn.fetchrow(query, *params)
                if record:
                    columns = list(record.keys())
                    return dict(zip(columns, record))
                return None
        
        cache_key = self._generate_cache_key(query, *params)
        
        # 尝试从缓存读取
        try:
            cached_data = await self.redis_pool.get(cache_key)
            if cached_data:
                return self.deserializer.loads(cached_data)
        except Exception as e:
            print(f"Redis cache read error: {e}")
        
        # 从数据库查询
        async with self.db_pool.acquire() as conn:
            record = await conn.fetchrow(query, *params)
            result = None
            if record:
                # 获取列名
                column_names = list(record.keys())
                result = dict(zip(column_names, record))
        
        # 尝试写入缓存
        try:
            if result:
                serialized_data = self.serializer.dumps(result)
                await self.redis_pool.set(cache_key, serialized_data, ex=ttl)
        except Exception as e:
            print(f"Redis cache write error: {e}")
        
        return result

    async def execute_and_invalidate(
        self,
        command: str,
        *params: Any,
        invalidate_patterns: List[str] = None,
    ) -> str:
        """执行写入操作并失效相关缓存
        
        Args:
            command: 写入型 SQL 语句（INSERT/UPDATE/DELETE）
            *params: SQL 参数
            invalidate_patterns: 需要失效的缓存键模式列表
            
        Returns:
            str: 返回数据库执行状态字符串
        """
        async with self.db_pool.acquire() as conn:
            status = await conn.execute(command, *params)

        if invalidate_patterns:
            try:
                for pattern in invalidate_patterns:
                    keys_to_delete = [key async for key in self.redis_pool.scan_iter(pattern)]
                    if keys_to_delete:
                        await self.redis_pool.delete(*keys_to_delete)
            except Exception as e:
                print(f"Redis cache invalidation error: {e}")

        return status

    async def transaction(self, *operations: Tuple[str, Tuple]):
        """在单个事务中执行多条写入语句
        
        Args:
            *operations: 可变数量的操作元组，每个元组包含SQL命令和参数
        
        Raises:
            Exception: 如果事务执行过程中出现错误
        """
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                for command, params in operations:
                    await conn.execute(command, *params)