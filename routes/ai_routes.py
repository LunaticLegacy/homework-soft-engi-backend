from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional, Any
from modules.databaseman import DatabaseManager
from core.database import get_db_manager
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from services.ai_task_service import AITaskService
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from core.config import load_config

router = APIRouter(prefix="/ai", tags=["ai"])

def get_llm_fetcher() -> LLMFetcher:
    """
    获取LLM获取器实例的依赖注入函数
    
    Returns:
        LLMFetcher: LLM获取器实例
    """
    # 从配置中获取API密钥等信息
    config = load_config()
    llm_config = config.get("llm", {})
    
    return LLMFetcher(
        api_url=llm_config.get("api_url", "https://api.deepseek.com"),
        api_key=llm_config.get("api_key", "sk-your-api-key"),
        model=llm_config.get("model", "deepseek-reasoner")
    )

def get_ai_service(
    db_manager: DatabaseManager = Depends(get_db_manager),
    llm_fetcher: LLMFetcher = Depends(get_llm_fetcher)
) -> AITaskService:
    """
    获取AI任务服务实例的依赖注入函数
    
    Args:
        db_manager (DatabaseManager): 数据库管理器实例
        llm_fetcher (LLMFetcher): LLM获取器实例
        
    Returns:
        AITaskService: AI任务服务实例
    """
    return AITaskService(db_manager, llm_fetcher)

@router.post("/decompose", response_model=Dict[str, Any])
async def decompose_task(
    goal: str,
    user_id: str,
    workspace_id: Optional[str] = None,
    service: AITaskService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    使用AI将大目标分解为具体任务
    
    Args:
        goal (str): 用户的大目标
        user_id (str): 用户ID
        workspace_id (Optional[str]): 工作空间ID
        service (AITaskService): AI任务服务实例
        
    Returns:
        Dict[str, Any]: 分解后的任务结构
    """
    try:
        result = await service.decompose_task(user_id, goal, workspace_id)
        return result
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions/{task_id}", response_model=Dict[str, Any])
async def get_task_suggestions(
    task_id: str,
    user_id: str,
    service: AITaskService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    获取特定任务的AI建议
    
    Args:
        task_id (str): 任务ID
        user_id (str): 用户ID
        service (AITaskService): AI任务服务实例
        
    Returns:
        Dict[str, Any]: AI建议
    """
    try:
        suggestions = await service.get_task_suggestions(user_id, task_id)
        return suggestions
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_ai(
    message: str,
    user_id: str,
    system_prompt: Optional[str] = None,
    llm_fetcher: LLMFetcher = Depends(get_llm_fetcher)
) -> Dict[str, Any]:
    """
    与AI进行对话
    
    Args:
        message (str): 用户消息
        user_id (str): 用户ID
        system_prompt (Optional[str]): 系统提示词
        llm_fetcher (LLMFetcher): LLM获取器实例
        
    Returns:
        Dict[str, Any]: AI回复
    """
    try:
        # 默认系统提示词
        if not system_prompt:
            system_prompt = "你是一个专业的任务管理助手，帮助用户更好地规划和完成任务。"
        
        # 调用LLM
        response = llm_fetcher.fetch(
            msg=message,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        ai_response = response.choices[0].message.content
        
        return {
            "success": True,
            "data": {
                "response": ai_response
            },
            "message": "对话成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))