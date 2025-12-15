from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.middleware import log_requests, error_handler
from core.exceptions import register_exception_handlers
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    
    Yields:
        ...（虽然我也不知道这个在yield什么）
    """
    # 启动前：初始化连接池
    try:
        from core.database import db_manager
        from core.redis_cache import redis_manager
        await db_manager.init_pool()
        await redis_manager.init_pool()
        redis_connection: bool = await redis_manager.ping()
        if redis_connection: 
            print("Redis connection successfully.")

    except Exception as e:
        print(f"Warning: Database or Redis connection failed: {e}")

    try:
        yield
    finally:
        # 关闭时：释放连接池
        try:
            from core.database import db_manager
            from core.redis_cache import redis_manager
            
            # 在关闭前显示活跃连接数
            active_connections = db_manager.get_active_connections_count()
            print(f"Active database connections before shutdown: {active_connections}")
            
            # 使用超时机制关闭数据库连接池
            try:
                await asyncio.wait_for(db_manager.close_all_connections(), timeout=30.0)
                print("Database connections closed successfully.")
            except asyncio.TimeoutError:
                print("WARNING: Database connection pool closing timed out!")
                
            await redis_manager.close_pool()
            print("Redis connections closed successfully.")

        except Exception as e:
            pass

def create_app() -> FastAPI:
    """
    创建并配置FastAPI应用实例
    
    Returns:
        FastAPI: 配置好的FastAPI应用实例
    """
    app = FastAPI(
        title="任务管理系统API",
        description="这是一个任务管理系统的后端API",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 添加中间件
    app.middleware("http")(log_requests)
    app.middleware("http")(error_handler)
    
    # 导入并注册路由
    from routes.main_routes import router as main_router
    from routes.user_routes import router as user_router
    from routes.ai_routes import router as ai_router
    from routes.workspace_routes import router as workspace_router
    from routes.project_routes import router as project_router
    from routes.task_routes import router as task_router
    from routes.tag_routes import router as tag_router
    from routes.comment_routes import router as comment_router
    from routes.attachment_routes import router as attachment_router
    from routes.notification_routes import router as notification_router
    from routes.search_routes import router as search_router
    from api.v1.routes import router as api_v1_router
    
    app.include_router(main_router)
    app.include_router(user_router)
    app.include_router(ai_router)
    app.include_router(workspace_router)
    app.include_router(project_router)
    app.include_router(task_router)
    app.include_router(tag_router)
    app.include_router(comment_router)
    app.include_router(attachment_router)
    app.include_router(notification_router)
    app.include_router(search_router)
    app.include_router(api_v1_router)
    
    return app