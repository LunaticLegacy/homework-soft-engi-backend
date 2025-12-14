from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Optional, Any, List, AsyncGenerator
import json

from core.database import get_db_manager
from core.llm_service import get_llm_fetcher

from core.utils.getters import get_ai_service, get_redis_manager
from core.utils.user_id_fetch import get_user_id_from_redis_by_token

from modules import LLMFetcher, DatabaseManager
from modules.redisman import RedisManager
from services import AITaskService
from core.config import load_config

from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

from .models.ai_llm_models import (
    TaskDecomposeRequest, 
    TaskSuggestionRequest, 
    ChatRequest,
    TaskDecomposeResponse,
    TaskSuggestionResponse,
    ChatResponse,
    ChatData
)

router = APIRouter(prefix="/ai", tags=["ai"])

"""
TODO:
- 获取任务的AI建议时，必须附带工作空间信息和项目信息（其中，工作空间用于管理项目）。
- 完成请求模型。
"""

@router.post("/decompose/", response_model=Dict[str, Any])
async def decompose_task(
    request: TaskDecomposeRequest,
    service: AITaskService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    使用AI将大目标分解为具体任务
    - TODO: 这个东西的底层方法已经是流式方法，但尚未具有存储用户认为的方案。
    
    Args:
        request (TaskDecomposeRequest): 任务分解请求
        service (AITaskService): AI任务服务实例
        
    Returns:
        Dict[str, Any]: 分解后的任务结构
    """
    try:
        result = await service.decompose_task(
            request.user_id, 
            request.goal, 
            request.workspace_id,
            request.project_id
        )
        return result
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions/{task_id}/", response_model=Dict[str, Any])
async def get_task_suggestions(
    task_id: str,
    request: TaskSuggestionRequest,
    service: AITaskService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    获取特定任务的AI建议
    - TODO: 这个东西的底层方法需要被改为流式方法。
    
    Args:
        task_id (str): 任务ID
        request (TaskSuggestionRequest): 任务建议请求
        service (AITaskService): AI任务服务实例
        
    Returns:
        Dict[str, Any]: AI建议
    """
    try:
        suggestions = await service.get_task_suggestions(request.user_id, task_id)
        return suggestions
    except DatabaseConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except DatabaseTimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    llm_fetcher: LLMFetcher = Depends(get_llm_fetcher)
) -> ChatResponse:
    """
    与AI进行对话
    - 我实际上不想使用这个。
    
    Args:
        request (ChatRequest): 聊天请求
        llm_fetcher (LLMFetcher): LLM获取器实例
        
    Returns:
        ChatResponse: AI回复
    """
    try:
        # 默认系统提示词
        system_prompt = request.system_prompt
        if not system_prompt:
            system_prompt = load_config()["llm"]["task_decompose"]
        
        # 调用LLM
        response = llm_fetcher.fetch(
            msg=request.message,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2048
        )
        
        ai_response: Optional[str] = response.choices[0].message.content
        
        return ChatResponse(
            time="",
            success=True,
            data=ChatData(response=ai_response),
            message="对话成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat-stream/")
async def chat_with_ai_stream(
    request: ChatRequest,
    llm_fetcher: LLMFetcher = Depends(get_llm_fetcher),
    service: AITaskService = Depends(get_ai_service),
    redis_man: RedisManager = Depends(get_redis_manager)
):
    """
    与AI进行流式对话
    
    Args:
        request (ChatRequest): 聊天请求
        llm_fetcher (LLMFetcher): LLM获取器实例
        redis_man (RedisManager): Redis管理器实例
        
    Returns:
        StreamingResponse: 流式响应
    """
    try:
        # 默认系统提示词
        system_prompt = request.system_prompt
        if not system_prompt:
            system_prompt = load_config()["prompts"]["task_decompose"]
#             system_prompt = """
# 你是一只说话带一点机械感的猫娘，你需要在每一句话后面都加上“喵”，并且以句号结尾。
# 如果用户没有主动说话，你就先打招呼介绍自己。输出要尽可能长一点。
# """
        
        # 构建历史对话上下文
        history_key = f"chat_history:{request.user_id}"
        history: List = await redis_man.get(history_key) or []
        await redis_man.delete(history_key)
        
        # 准备消息历史
        messages = []
        for item in history:
            messages.append({"role": item["role"], "content": item["content"]})
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": request.message})
        
        # 调用LLM流式方法
        async def generate():
            full_response = ""
            async for chunk in llm_fetcher.fetch_stream(
                msg=request.message,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2048
            ):
                full_response += chunk
                yield chunk
            
            # 将对话历史保存到Redis
            nonlocal history
            history.append({"role": "user", "content": request.message})
            history.append({"role": "assistant", "content": full_response})
            
            # 只保留最近10轮对话
            if len(history) > 20:  # 10轮对话包含用户和助手的消息
                history = history[-20:]
                
            await redis_man.set(history_key, history, expire=3600)  # 保存1小时
        
        # 返回一个处理流式内容的handler。
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
