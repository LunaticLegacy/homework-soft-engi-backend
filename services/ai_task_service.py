from typing import Dict, List, Any, Optional
from modules import LLMFetcher, DatabaseManager, DBTimeoutError
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
            await db.execute("")

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
            json_text: str = self._extract_json_block(full_text)
            task_structure = json.loads(json_text)

            await self._save_ai_request(user_id, goal, json_text)

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
        response: str,
        prompt: Optional[str] = None,
        status: str = "backlog"
    ) -> None:
        """
        保存AI请求记录到数据库。
        Args:
            user_id (str): 用户ID。
            prompt (str): 用户自定义提示词。（系统提示词全部都是一致的）
            response (str): 来自LLM的回答。
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                await conn.execute(
                    """
                    INSERT INTO ai_requests (id, user_id, prompt, response_text, status)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    str(uuid.uuid4()), user_id, prompt, response, status
                )
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as exc:
            # 记录日志但不中断主流程
            print(f"保存AI请求记录失败: {str(exc)}")

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

    def _extract_json_block(
            self, 
            text: str
        ) -> str:
        """从流式文本中提取首个JSON块。"""
        start: int = text.find("{")
        end: int = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise json.JSONDecodeError("未找到有效的JSON边界", text, 0)
        return text[start:end + 1]