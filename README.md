- 顶层导出： UnifiedDatabaseIO
- 便捷工厂： create_io
- 版本号： version_1.0.0

示例用法

- 安装（对方在库根目录执行）: pip install -e .
- 导入与初始化:
  - from db_io_lib import UnifiedDatabaseIO, create_io
  - io = await create_io(db_config, redis_config, serialization_format="json")
  - rows = await io.fetch_with_cache("SELECT * FROM users;")

函数
create 创建实例
fetch_with_cache 读取缓存记录
fetch_one_with_cache 读取单条缓存记录
execute_and_invalidate 执行写操作并失效缓存
transaction 执行事务操作
close 关闭实例

程序框图
/************************ create ************************/
[create(db_config, redis_config, serialization_format)]
        |
        v
[实例化 UnifiedDatabaseIO]
        |
        v
[asyncpg.create_pool]
        |
        v
[aioredis.from_url]
        |
        v
[检查 serialization_format] --json--> [设为 json] --\
                  \--pickle/默认--> [设为 pickle] ----> [返回实例]

/************************ fetch_with_cache ************************/
[fetch_with_cache(query, *params, ttl)]
        |
        v
[生成 cache_key]
        |
        v
{Redis 读取} --命中--> [loads(cached_data)] --> [返回]
        \--未命中/异常--> [DB acquire] -> [conn.fetch] -> [转为字典列表]
                                    |
                                    v
                              {写入 Redis} --成功--> [set(key, data, ex=ttl)]
                                           \--异常--> [仅打印错误]
                                    |
                                    v
                                  [返回]

/************************ fetch_one_with_cache ************************/
[fetch_one_with_cache]
        |
        v
[调用 fetch_with_cache]
        |
        v
{结果列表} --非空--> [返回第一条]
           \--空--> [返回 None]

/************************ execute_and_invalidate ************************/
[execute_and_invalidate(command, *params, patterns)]
        |
        v
[DB acquire] -> [conn.execute]
        |
        v
{patterns?} --否--> [返回 status]
           \--是--> [Redis 客户端] -> [遍历 pattern] -> [scan_iter 收集键]
                                     |
                                     v
                               {有键?} --是--> [delete(*keys)] --> [返回]
                                        \--否--> [返回]

/************************ transaction ************************/
[transaction(*operations)]
        |
        v
[DB acquire] -> [开启事务]
        |
        v
[遍历 (command, params)] -> [conn.execute]
        |
        v
{全部成功?} --是--> [提交并返回]
           \--否(异常)--> [抛出异常(自动回滚)]

/************************ close ************************/
[close()]
  |
  v
{db_pool?} --是--> [db_pool.close()]
          \--否--> (跳过)
  |
  v
{redis_pool?} --是--> [redis_pool.close()]
            \--否--> (跳过)
  |
  v
[完成]


注意事项

- db_config 是 asyncpg 连接池参数，示例： {"user": "...", "password": "...", "database": "...", "host": "localhost"}
- redis_config 需要包含地址字段，示例： {"address": "redis://localhost"}