from fastapi import Request
import time
import uuid
from typing import Callable
from fastapi.responses import JSONResponse

async def log_requests(request: Request, call_next: Callable):
    """
    记录请求日志的中间件
    
    Args:
        request (Request): HTTP请求对象
        call_next (Callable): 下一个处理函数
        
    Returns:
        Response: HTTP响应对象
    """
    # 生成请求ID
    request_id = str(uuid.uuid4())
    
    # 记录请求开始时间
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录日志信息
    print(f"Request ID: {request_id} | "
          f"Method: {request.method} | "
          f"URL: {request.url} | "
          f"Time: {process_time:.4f}s | "
          f"Status: {response.status_code}")
    
    # 在响应头中添加请求ID和处理时间
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

async def error_handler(request: Request, call_next: Callable):
    """
    统一错误处理中间件
    
    Args:
        request (Request): HTTP请求对象
        call_next (Callable): 下一个处理函数
        
    Returns:
        Response: HTTP响应对象
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # 记录错误日志
        print(f"Error processing request {request.url}: {str(e)}")
        
        # 返回统一错误响应
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }
        )