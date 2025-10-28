import asyncio  # 导入异步事件循环库，用于运行异步代码
import asyncpg  # 导入 asyncpg，用于异步连接和操作 PostgreSQL 数据库
import aioredis  # 导入 aioredis，用于异步连接和操作 Redis 缓存
import json  # 导入 JSON 序列化模块，用于以 JSON 格式存储数据
import pickle  # 导入 pickle 序列化模块，用于以二进制格式存储数据
from typing import Any, Dict, List, Optional, Tuple, Union  # 导入类型提示，提升代码可读性与可靠性

class UnifiedDatabaseIO:  # 统一的数据库与缓存 I/O 封装类
    def __init__(self):  # 初始化实例属性
        self.db_pool = None  # PostgreSQL 连接池，占位等待异步创建
        self.redis_pool = None  # Redis 连接池，占位等待异步创建
        self.serializer = pickle  # 默认使用 pickle 进行序列化
        self.deserializer = pickle  # 默认使用 pickle 进行反序列化

    @classmethod  # 声明类方法，便于通过类直接创建实例
    async def create(
        cls,  # 类本身，用于构造实例
        db_config: Dict[str, Any],  # 数据库连接配置，传入 asyncpg.create_pool 的参数
        redis_config: Dict[str, Any],  # Redis 连接配置，传入 aioredis.from_url 的参数
        serialization_format: str = "pickle",  # 序列化格式，支持 "pickle" 或 "json"
    ) -> "UnifiedDatabaseIO":  # 返回创建好的 UnifiedDatabaseIO 实例
        instance = cls()  # 创建类实例
        try:  # 尝试初始化数据库和缓存连接池
            instance.db_pool = await asyncpg.create_pool(**db_config)  # 创建 PostgreSQL 连接池
            instance.redis_pool = aioredis.from_url(**redis_config)  # 创建 Redis 连接对象
        except Exception as e:  # 捕获连接初始化过程中可能的异常
            print(f"Error during pool creation: {e}")  # 打印错误信息，便于定位问题
            raise  # 抛出异常，让上层调用方处理

        if serialization_format == "json":  # 如果选择 JSON 序列化
            instance.serializer = json  # 设置序列化器为 json
            instance.deserializer = json  # 设置反序列化器为 json
        elif serialization_format != "pickle":  # 如果不是支持的格式
            raise ValueError("Serialization format must be 'pickle' or 'json'")  # 抛出参数错误

        return instance  # 返回初始化完成的实例

    async def close(self):  # 关闭数据库和缓存连接，进行资源清理
        if self.db_pool:  # 如果数据库连接池已创建
            await self.db_pool.close()  # 关闭数据库连接池
        if self.redis_pool:  # 如果 Redis 连接已创建
            await self.redis_pool.close()  # 关闭 Redis 连接

    def _generate_cache_key(self, query: str, *params: Any) -> str:  # 生成缓存键，基于查询语句与参数
        return f"cache:{hash((query, params))}"  # 使用 hash 构造稳定的缓存键前缀

    async def fetch_with_cache(
        self,  # 实例自身
        query: str,  # SQL 查询语句（SELECT）
        *params: Any,  # 查询参数，可变长度
        ttl: int = 300,  # 缓存有效期（秒），默认 300 秒
    ) -> List[Dict[str, Any]]:  # 返回记录列表，每条记录为字典
        cache_key = self._generate_cache_key(query, *params)  # 根据查询与参数生成缓存键
        try:  # 优先尝试从 Redis 读取缓存
            async with self.redis_pool.client() as redis:  # 获取 Redis 客户端上下文
                cached_data = await redis.get(cache_key)  # 读取缓存数据
                if cached_data:  # 若存在缓存
                    return self.deserializer.loads(cached_data)  # 反序列化后返回结果
        except Exception as e:  # 读取缓存失败时只打印错误，不中断流程
            print(f"Redis cache read error: {e}")  # 打印 Redis 读取错误信息

        async with self.db_pool.acquire() as conn:  # 若无缓存则访问数据库
            records = await conn.fetch(query, *params)  # 执行查询语句并获取记录
            result = [dict(record) for record in records]  # 将 Record 转换为字典列表

        try:  # 将查询结果写入 Redis 缓存
            async with self.redis_pool.client() as redis:  # 获取 Redis 客户端上下文
                serialized_data = self.serializer.dumps(result)  # 序列化结果数据
                await redis.set(cache_key, serialized_data, ex=ttl)  # 设置缓存并指定过期时间
        except Exception as e:  # 写入缓存失败时只打印错误，不影响查询结果返回
            print(f"Redis cache write error: {e}")  # 打印 Redis 写入错误信息

        return result  # 返回最终的查询结果

    async def fetch_one_with_cache(
        self,  # 实例自身
        query: str,  # SQL 查询语句（期望返回单条记录）
        *params: Any,  # 查询参数
        ttl: int = 300,  # 缓存有效期（秒）
    ) -> Optional[Dict[str, Any]]:  # 返回单条记录的字典或 None
        results = await self.fetch_with_cache(query, *params, ttl=ttl)  # 调用带缓存的查询
        return results[0] if results else None  # 返回第一条记录，若为空则返回 None

    async def execute_and_invalidate(
        self,  # 实例自身
        command: str,  # 写入型 SQL 语句（INSERT/UPDATE/DELETE）
        *params: Any,  # SQL 参数
        invalidate_patterns: List[str] = None,  # 需要失效的缓存键模式列表
    ) -> str:  # 返回数据库执行状态字符串
        async with self.db_pool.acquire() as conn:  # 获取数据库连接
            status = await conn.execute(command, *params)  # 执行写操作并获取状态

        if invalidate_patterns:  # 如果提供了缓存失效模式
            try:  # 扫描匹配的键并删除
                async with self.redis_pool.client() as redis:  # 获取 Redis 客户端上下文
                    for pattern in invalidate_patterns:  # 遍历所有模式
                        keys_to_delete = [key async for key in redis.scan_iter(pattern)]  # 异步扫描匹配键
                        if keys_to_delete:  # 若有匹配键
                            await redis.delete(*keys_to_delete)  # 批量删除这些键
            except Exception as e:  # 缓存失效过程中若出错则打印日志
                print(f"Redis cache invalidation error: {e}")  # 打印缓存失效错误信息

        return status  # 返回数据库执行状态

    async def transaction(self, *operations: Tuple[str, Tuple]):  # 在单个事务中执行多条写入语句
        async with self.db_pool.acquire() as conn:  # 获取数据库连接
            async with conn.transaction():  # 开启事务上下文
                for command, params in operations:  # 逐条执行传入的 SQL 命令与参数
                    await conn.execute(command, *params)  # 执行写操作