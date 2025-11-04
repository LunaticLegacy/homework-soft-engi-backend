from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union

class DatabaseConnectionError(Exception):
    """数据库连接异常"""
    def __init__(self, message: str = "Database connection failed"):
        self.message = message
        super().__init__(self.message)

class DatabaseTimeoutError(Exception):
    """数据库超时异常"""
    def __init__(self, message: str = "Database operation timed out"):
        self.message = message
        super().__init__(self.message)

class ResourceNotFoundError(Exception):
    """资源未找到异常"""
    def __init__(self, resource: str = "Resource", message: str = "not found"):
        self.message = f"{resource} {message}"
        super().__init__(self.message)

def register_exception_handlers(app):
    """
    注册全局异常处理器
    
    Args:
        app (FastAPI): FastAPI应用实例
    """
    
    @app.exception_handler(DatabaseConnectionError)
    async def database_connection_exception_handler(request, exc):
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "Database Connection Error",
                "message": exc.message
            }
        )
    
    @app.exception_handler(DatabaseTimeoutError)
    async def database_timeout_exception_handler(request, exc):
        return JSONResponse(
            status_code=408,
            content={
                "success": False,
                "error": "Database Timeout Error",
                "message": exc.message
            }
        )
    
    @app.exception_handler(ResourceNotFoundError)
    async def resource_not_found_exception_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Resource Not Found",
                "message": exc.message
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": "HTTP Error",
                "message": exc.detail
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation Error",
                "message": "Input validation failed",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            }
        )