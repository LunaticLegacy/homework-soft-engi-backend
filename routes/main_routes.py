from fastapi import APIRouter
from pydantic import BaseModel


class SimpleRequest(BaseModel):
    time: str | None = None
    token: str | None = None

router = APIRouter()

@router.post("/", tags=["main"])
async def root(_: SimpleRequest | None = None):
    """
    根路径，返回欢迎信息
    
    Returns:
        dict: 包含欢迎信息的字典
    """
    return {"message": "Hello, FastAPI is running!"}

@router.post("/health", tags=["main"])
async def health_check(_: SimpleRequest | None = None):
    """
    健康检查端点
    
    Returns:
        dict: 表示服务健康的响应
    """
    return {"status": "healthy", "message": "Service is running."}
