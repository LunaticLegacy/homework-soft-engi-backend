from typing import Dict, List, Any, Optional, Tuple
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from settings import get_settings
import json
import uuid
from datetime import datetime
from routes.models.ai_llm_models import LLMContext  # 上下文内容

class AITaskService:
    """AI任务分解服务类，处理基于AI的任务分解逻辑（流式收集JSON后解析）。"""

    def __init__(self, db_manager: DatabaseManager, llm_fetcher: LLMFetcher):
        self.db_manager = db_manager
        self.llm_fetcher = llm_fetcher
        prompts = get_settings().prompts
        # 提取提示词对象。
        self.prompt_task_decompose: str = prompts.task_decompose
        self.prompt_task_suggestion: str = prompts.task_suggestion

    async def decompose_task(
        self,
        user_id: str,
        goal: str,
        workspace_id: str,
        project_id: str
    ) -> Dict[str, Any]:
        """
        使用AI将大目标分解为具体任务；流式拉取直到完整JSON生成后再解析。
        - 该函数会创建一个主任务，主任务为用户子任务的解析。
        - 在创建任务完毕后，任务将会被储存到数据库内。

        Args:
            user_id (str): 用户ID。
            goal (str): 用户目标。
            workspace_id (str): 目标工作空间ID。
            project_id (str): 目标工程ID。
        """
        system_prompt = self.prompt_task_decompose

        user_message = f"请将以下目标分解为具体任务：{goal}"

        full_text: str = ""
        try:
            db = await self.db_manager.get_connection(5.0)

            # 获取当前模型上下文。
            # 然后，将模型上下文内容拼接. 

            chunks: List[str] = []
            async for chunk in self.llm_fetcher.fetch_stream(
                msg=user_message,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=4096
            ):
                if chunk:
                    chunks.append(chunk)

            full_text = "".join(chunks)
            json_text: Optional[str] = self._extract_json_block(full_text)
            if not json_text:
                raise ValueError("JSON分解失败：未产生任务。")
            task_structure = json.loads(json_text)

            ai_request_id = await self._save_ai_request(user_id, goal, json_text)
            
            # 保存任务分解结果和上下文
            await self._save_task_decomposition(ai_request_id, user_id, task_structure, workspace_id, project_id)

            # 随后保存当前上下文
            await self.db_manager.release_connection(db)

            return {
                "success": True,
                "data": task_structure,
                "message": "任务分解成功",
                "timestamp": datetime.now().isoformat()
            }
        except json.JSONDecodeError as exc:
            raise Exception(f"AI返回结果解析失败: {str(exc)} | 片段: {full_text[:200]}")
        except Exception as exc:
            raise Exception(f"任务分解失败: {str(exc)}")

    async def _save_ai_request(
        self,
        user_id: str,
        prompt: str,
        response: str,
        status: str = "done"
    ) -> str:
        """
        保存AI请求记录到数据库。
        Args:
            user_id (str): 用户ID。
            prompt (str): 用户输入的提示词。
            response (str): 来自LLM的回答。
            status (str): 请求状态，默认为'done'
        
        Returns:
            str: 生成的ai_request_id
        """
        try:
            ai_request_id = str(uuid.uuid4())
            conn = await self.db_manager.get_connection(5.0)
            try:
                await conn.execute(
                    """
                    INSERT INTO ai_requests (id, user_id, prompt, response_text, status)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    ai_request_id, user_id, prompt, response, status
                )
                return ai_request_id
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            # 记录日志但不中断主流程
            print(f"保存AI请求记录失败: {str(exc)}")
            return ""

    async def _save_task_decomposition(
        self,
        ai_request_id: str,
        user_id: str,
        task_structure: Dict[str, Any],
        workspace_id: str,
        project_id: str
    ) -> None:
        """
        保存任务分解结果到数据库。
        Args:
            ai_request_id (str): 关联的AI请求ID。
            user_id (str): 用户ID。
            task_structure (Dict[str, Any]): 任务分解结构。
            workspace_id (str): 工作空间ID。
            project_id (str): 项目ID。
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                # 保存任务分解结果
                await conn.execute(
                    """
                    INSERT INTO ai_task_suggestions 
                    (ai_request_id, user_id, suggestion, metadata)
                    VALUES ($1, $2, $3, $4)
                    """,
                    ai_request_id, user_id, json.dumps(task_structure), 
                    json.dumps({
                        "workspace_id": workspace_id,
                        "project_id": project_id
                    })
                )
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            # 记录日志但不中断主流程
            print(f"保存任务分解结果失败: {str(exc)}")

    async def get_task_decomposition(
        self,
        user_id: str,
        ai_request_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        从数据库获取任务分解结果。
        Args:
            user_id (str): 用户ID。
            ai_request_id (str): AI请求ID。
        
        Returns:
            Optional[Dict[str, Any]]: 任务分解结果，如果找不到则返回None。
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    SELECT id, ai_request_id, suggestion, metadata, created_at
                    FROM ai_task_suggestions 
                    WHERE ai_request_id = $1 AND user_id = $2
                    """,
                    ai_request_id, user_id
                )
                
                if row:
                    return {
                        "id": row["id"],
                        "ai_request_id": row["ai_request_id"],
                        "suggestion": json.loads(row["suggestion"]) if isinstance(row["suggestion"], str) else row["suggestion"],
                        "metadata": json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None
                    }
                return None
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            print(f"获取任务分解结果失败: {str(exc)}")
            return None

    async def get_task_suggestions(
        self,
        user_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取特定任务的AI建议。
        
        """
        try:
            task_info = await self._get_task_info(task_id)
            system_prompt = self.prompt_task_suggestion

            user_message = f"请为以下任务提供完成建议：{task_info['title']} - {task_info['description']}"

            response = self.llm_fetcher.fetch(
                msg=user_message,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2048
            )

            ai_response_content = response.choices[0].message.content
            if ai_response_content is None:
                raise Exception("AI返回内容为空")

            suggestions = json.loads(ai_response_content)

            await self._save_ai_request(user_id, user_message, ai_response_content)

            return {
                "success": True,
                "data": suggestions,
                "message": "建议获取成功",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as exc:
            raise Exception(f"获取任务建议失败: {str(exc)}")

    async def _get_task_info(self, task_id: str) -> Dict[str, str]:
        """从数据库获取任务信息。"""
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    "SELECT title, description FROM tasks WHERE id = $1",
                    task_id
                )
                if row:
                    return {
                        "title": row["title"],
                        "description": row["description"]
                    }
                else:
                    raise Exception("任务未找到")
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            raise Exception(f"获取任务信息失败: {str(exc)}")

    def _extract_json_block(self, text: str) -> Optional[str]:
        """
        提取出JSON任务块内容，优先使用标记，否则回退到大括号匹配。
        返回原始JSON字符串；若找不到有效JSON则返回None。
        """
        begin = "<<<JSON_BEGIN>>>"
        end = "<<<JSON_END>>>"

        b = text.find(begin)
        if b != -1:
            e = text.find(end, b + len(begin))
            if e != -1:
                candidate = text[b + len(begin): e].strip()
                if candidate:
                    return candidate

        # 回退：尝试寻找第一个左大括号到匹配的右大括号组成的合法JSON
        content = text.strip()
        if "{" not in content or "}" not in content:
            return None

        # 粗暴地寻找一个可解析的JSON片段
        opens: List[int] = [i for i, ch in enumerate(content) if ch == "{"]
        closes: List[int] = [i for i, ch in enumerate(content) if ch == "}"]
        if not opens or not closes:
            return None

        for start in opens:
            for end_idx in reversed(closes):
                if end_idx <= start:
                    continue
                candidate = content[start:end_idx + 1].strip()
                try:
                    json.loads(candidate)
                    return candidate
                except Exception:
                    continue
        return None
    
    async def save_context(
        self,
        workspace_id: str,
        project_id: str,
        user_id: str,
        context_msg: Tuple[LLMContext, LLMContext],  # 用户消息和AI回复
        previous_msg_id: Optional[str] = None
    ) -> Optional[str]:
        """
        储存特定工作空间、特定项目、特定用户的AI LLM上下文。
        Args:
            workspace_id: 工作空间ID。
            project_id: 项目ID。
            user_id: 用户ID。
            context_msg: 本片段内容。这个Tuple的长度为2，为保存用户输入和LLM输出。
            previous_msg_id: 上一段对话的ID。
        Returns:
            str: 返回新创建的对话ID
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                # 创建对话记录
                conversation_row = await conn.fetchrow(
                    """
                    INSERT INTO ai_conversations 
                    (project_id, workspace_id, creator_id, previous_conversation_id, model_name) 
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                    """,
                    project_id, workspace_id, user_id, previous_msg_id, self.llm_fetcher.model
                )
                
                if not conversation_row:
                    raise Exception("创建对话记录失败")

                # 保存对话ID内容，用于创建子内容。
                conversation_id = conversation_row['id']
                
                # 保存用户消息 - 暂时将token写为0，作为占位符。
                user_msg = context_msg[0]
                await conn.execute(
                    """
                    INSERT INTO ai_messages 
                    (conversation_id, role, content, tokens, sequence_number) 
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    conversation_id, user_msg.role, user_msg.content, 0, 1
                )
                
                # 保存AI回复
                ai_msg = context_msg[1]
                await conn.execute(
                    """
                    INSERT INTO ai_messages 
                    (conversation_id, role, content, tokens, sequence_number) 
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    conversation_id, ai_msg.role, ai_msg.content, 0, 2
                )
                
                return str(conversation_id)

            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            raise Exception(f"存储AI对话上下文失败: {str(exc)}")

    async def get_context(
        self,
        workspace_id: str,
        project_id: str,
        user_id: str
    ) -> List[LLMContext]:
        """
        获取特定工作空间、特定项目、特定用户的AI LLM上下文全文内容。
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                # 获取与指定用户、项目和工作空间相关的所有对话及消息
                rows = await conn.fetch(
                    """
                    SELECT am.role, am.content, am.tokens
                    FROM ai_messages am
                    JOIN ai_conversations ac ON am.conversation_id = ac.id
                    WHERE ac.project_id = $1 
                      AND ac.workspace_id = $2 
                      AND ac.creator_id = $3
                      AND ac.deleted_at IS NULL
                    ORDER BY ac.created_at, am.sequence_number
                    """,
                    project_id, workspace_id, user_id
                )
                
                # 将查询结果转换为 LLMContext 列表
                context_list: List[LLMContext] = []
                for row in rows:
                    context_list.append(LLMContext(
                        role=row['role'],
                        content=row['content'],
                    ))
                
                return context_list

            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            raise Exception(f"读取AI对话上下文失败: {str(exc)}")

