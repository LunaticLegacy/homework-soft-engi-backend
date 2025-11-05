from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["main"])
async def root():
    """
    根路径，返回欢迎信息
    
    Returns:
        dict: 包含欢迎信息的字典
    """
    return {"message": "Hello, FastAPI is running!"}

@router.get("/health", tags=["main"])
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 表示服务健康的响应
    """
    return {"status": "healthy", "message": "Service is running"}