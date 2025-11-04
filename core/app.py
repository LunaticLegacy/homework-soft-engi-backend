from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import db_manager
from core.middleware import log_requests, error_handler
from core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    
    Yields:
        ...（虽然我也不知道这个在yield什么）
    """
    # 启动前：初始化连接池
    await db_manager.init_pool()
    print(" -------- Hello server! -------- ")
    try:
        yield
    finally:
        # 关闭时：释放连接池
        await db_manager.close_all_connections()

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
        lifespan=lifespan
    )
    
    # 注册异常处理器
    register_exception_handlers(app)
    
    # 添加中间件
    app.middleware("http")(log_requests)
    app.middleware("http")(error_handler)
    
    # 导入并注册路由
    from main_routes import router as main_router
    from routes.user_routes import router as user_router
    from api.v1.routes import router as api_v1_router
    
    app.include_router(main_router)
    app.include_router(user_router)
    app.include_router(api_v1_router)
    
    return app