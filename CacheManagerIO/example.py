import asyncio
from db_io_lib import UnifiedDatabaseIO

DB_CONFIG = {
    "user": "postgres",
    "password": "123456",
    "database": "postgres",
    "host": "localhost",
}

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0
}

async def main():
    """主函数，演示库的用法
    
    演示UnifiedDatabaseIO库的基本功能，包括：
    - 数据库连接和缓存配置
    - 表的创建
    - 数据的插入和查询
    - 缓存的使用和失效
    """
    io_interface = await UnifiedDatabaseIO.create(
        db_config=DB_CONFIG,
        redis_config=REDIS_CONFIG,
        serialization_format="json"
    )

    try:
        print("--- 正在创建用户表 (如果不存在) ---")
        await io_interface.execute_and_invalidate(
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );"""
        )
        print("用户表已准备就绪。")

        print("\n--- 正在创建新用户 ---")
        username = "test_user_1"
        email = "test1@example.com"
        await io_interface.execute_and_invalidate(
            "INSERT INTO users (username, email) VALUES ($1, $2) ON CONFLICT (username) DO NOTHING;",
            username, email,
            invalidate_patterns=["cache:users:*"]
        )
        print(f"用户 '{username}' 已创建或已存在。")

        print("\n--- 第一次获取所有用户 (从数据库) ---")
        users = await io_interface.fetch_with_cache("SELECT id, username, email FROM users ORDER BY id;")
        print("获取到的用户:", users)

        print("\n--- 第二次获取所有用户 (应从缓存中获取) ---")
        users_from_cache = await io_interface.fetch_with_cache("SELECT id, username, email FROM users ORDER BY id;")
        print("从缓存中获取的用户:", users_from_cache)

        print("\n--- 获取单个用户 (ID=1) ---")
        user = await io_interface.fetch_one_with_cache("SELECT id, username, email FROM users WHERE id = $1;", 1)
        print("获取到的用户:", user)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("\n--- 正在关闭连接 ---")
        await io_interface.close()
        print("连接已关闭。")

if __name__ == "__main__":
    """脚本入口点
    
    配置Windows环境下的异步事件循环并运行主函数
    """
    if asyncio.get_event_loop_policy()._loop_factory is None:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())