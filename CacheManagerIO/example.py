import asyncio  # 导入异步事件循环模块
from db_io_lib import UnifiedDatabaseIO  # 从封装库导入统一 I/O 接口类

DB_CONFIG = {  # PostgreSQL 数据库连接配置（示例）
    "user": "postgres",  # 数据库用户名
    "password": "123456",  # 数据库密码
    "database": "postgres",  # 数据库名称
    "host": "localhost",  # 数据库主机地址（本机）
}

REDIS_CONFIG = {  # Redis 连接配置（示例）
    "address": "redis://localhost"  # Redis 地址（本机）
}

async def main():  # 主函数，演示库的用法
    io_interface = await UnifiedDatabaseIO.create(  # 初始化 I/O 接口实例
        db_config=DB_CONFIG,  # 传入数据库配置
        redis_config=REDIS_CONFIG,  # 传入 Redis 配置
        serialization_format="json"  # 指定使用 JSON 序列化
    )

    try:  # 异常捕获块开始
        print("--- 正在创建用户表 (如果不存在) ---")  # 提示建表操作
        await io_interface.execute_and_invalidate(  # 创建用户表（如果不存在）
            """CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );"""
        )  # 执行建表语句
        print("用户表已准备就绪。")  # 输出建表完成提示

        print("\n--- 正在创建新用户 ---")  # 提示创建用户操作
        username = "test_user_1"  # 示例用户名
        email = "test1@example.com"  # 示例邮箱
        await io_interface.execute_and_invalidate(  # 插入用户记录并使缓存失效
            "INSERT INTO users (username, email) VALUES ($1, $2) ON CONFLICT (username) DO NOTHING;",  # 插入语句（避免重复）
            username, email,  # 传入用户名与邮箱参数
            invalidate_patterns=["cache:users:*"]  # 使所有用户列表相关缓存失效
        )  # 执行插入语句
        print(f"用户 '{username}' 已创建或已存在。")  # 输出插入结果提示

        print("\n--- 第一次获取所有用户 (从数据库) ---")  # 提示首次查询（命中数据库）
        users = await io_interface.fetch_with_cache("SELECT id, username, email FROM users ORDER BY id;")  # 执行查询并写入缓存
        print("获取到的用户:", users)  # 打印查询结果

        print("\n--- 第二次获取所有用户 (应从缓存中获取) ---")  # 提示再次查询（命中缓存）
        users_from_cache = await io_interface.fetch_with_cache("SELECT id, username, email FROM users ORDER BY id;")  # 再次查询，读取缓存
        print("从缓存中获取的用户:", users_from_cache)  # 打印缓存结果

        print("\n--- 获取单个用户 (ID=1) ---")  # 提示单条查询
        user = await io_interface.fetch_one_with_cache("SELECT id, username, email FROM users WHERE id = $1;", 1)  # 查询指定 ID 的用户
        print("获取到的用户:", user)  # 打印单条查询结果

    except Exception as e:  # 捕获并处理运行过程中的异常
        print(f"发生错误: {e}")  # 打印错误信息
    finally:  # 无论是否发生异常都执行的清理操作
        print("\n--- 正在关闭连接 ---")  # 提示关闭连接
        await io_interface.close()  # 关闭数据库与缓存连接
        print("连接已关闭。")  # 提示清理完成

if __name__ == "__main__":  # 脚本入口
    if asyncio.get_event_loop_policy()._loop_factory is None:  # Windows 环境下的事件循环兼容处理
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 设置选择器事件循环策略

    asyncio.run(main())  # 运行异步主函数