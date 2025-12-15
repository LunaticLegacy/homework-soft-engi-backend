from typing import Dict, List, Any, Optional
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
from settings import get_settings
import json
import uuid
from datetime import datetime


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
        begin = "<<<JSON_BEGIN>>>"
        end = "<<<JSON_END>>>"

        b = text.find(begin)
        if b == -1:
            return

        e = text.find(end, b + len(begin))
        if e == -1:
            return

        return text[b + len(begin): e].strip()
