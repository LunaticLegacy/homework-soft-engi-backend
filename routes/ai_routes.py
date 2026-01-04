from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Optional, Any, List, AsyncGenerator
import json

from core.database import get_db_manager
from core.llm_service import get_llm_fetcher

from core.utils.getters import get_ai_service, get_redis_manager, get_task_service
from core.utils.user_id_fetch import get_user_id_from_redis_by_token

from modules import LLMFetcher, DatabaseManager
from modules.redisman import RedisManager
from services import AITaskService, TaskService
from core.config import load_config

from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

from .models.ai_llm_models import (
    TaskDecomposeRequest, 
    TaskSuggestionRequest, 
    ChatRequest,
    TaskDecomposeResponse,
    TaskSuggestionResponse,
    ChatResponse,
    ChatData,
    LLMContext
)

router = APIRouter(prefix="/ai", tags=["ai"])


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

@router.get("/decompose/{ai_request_id}/", response_model=Dict[str, Any])
async def get_task_decomposition(
    ai_request_id: str,
    user_id: str,
    service: AITaskService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """
    获取已存储的任务分解结果
    
    Args:
        ai_request_id (str): AI请求ID
        user_id (str): 用户ID
        service (AITaskService): AI任务服务实例
        
    Returns:
        Dict[str, Any]: 存储的任务分解结果
    """
    try:
        result = await service.get_task_decomposition(user_id, ai_request_id)
        if result:
            return {
                "success": True,
                "data": result,
                "message": "获取任务分解结果成功"
            }
        else:
            raise HTTPException(status_code=404, detail="未找到对应的任务分解结果")
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
    redis_man: RedisManager = Depends(get_redis_manager),
    task_man: TaskService = Depends(get_task_service),
    database: DatabaseManager = Depends(get_db_manager)
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
        request.workspace_id
        request.project_id

        if not system_prompt:
            system_prompt = load_config()["prompts"]["task_decompose"]
        
        user_id: str = await get_user_id_from_redis_by_token(request.token)

        # 从数据库内获取上下文。现在这个东西仅仅是一个作用在内存系统中的东西。await service.get_context(request.workspace_id, request.project_id, user_id) or
        history: List[LLMContext] = await service.get_context(request.workspace_id, request.project_id, user_id) or []

        # 准备消息历史
        messages: List[LLMContext] = []
        for item in history:
            messages.append(LLMContext(item.role, item.content))
            
        # 添加当前用户消息
        messages.append(LLMContext("user", request.message))
        
        # 调用LLM流式方法
        async def generate():
            full_response = ""
            async for chunk in llm_fetcher.fetch_stream(
                msg=request.message,
                prev_messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=8192,
                output_reasoning=True
            ):
                full_response += chunk
                yield chunk
            
            # 将对话历史保存到数据库内。
            nonlocal history
            user_msg: LLMContext = LLMContext("user", request.message)
            llm_msg: LLMContext = LLMContext("assistant", full_response)
            history.append(user_msg)    
            history.append(llm_msg)

            print("Now hisotries:", len(history))

            json_msg: Optional[str] = service._extract_json_block(full_response)
            print(json_msg)

            # 如果可以出JSON，则将其解析并按照任务主表分解
            # 强化检查：确保json_msg不仅存在且去除空格后非空
            if json_msg and isinstance(json_msg, str) and json_msg.strip():
                nonlocal user_id
                # 进一步确保要解析的JSON内容有效
                cleaned_json_msg = json_msg.strip()
                if cleaned_json_msg:  # 再次确认非空
                    try:
                        await task_man.create_task_by_json(
                            project_id=request.project_id,
                            workspace_id=request.workspace_id,
                            creator_id=user_id,
                            json_message=cleaned_json_msg  # 使用清理后的JSON消息
                        )
                    except ValueError as e:
                        # 记录JSON解析错误但不中断流程
                        print(f"Warning: Failed to parse AI-generated JSON: {e}")
            # TODO: 当内容过期时，将上下文保存在数据库内。

            # 只保留最近10轮对话
            if len(history) > 20:  # 10轮对话包含用户和助手的消息
                history = history[-20:]
                
            await service.save_context(
                request.workspace_id, request.project_id, user_id, (history[-2], history[-1])
            )
        
        # 返回一个处理流式内容的handler。
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))