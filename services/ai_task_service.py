from typing import Dict, List, Any, Optional
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError
import json
import uuid

class AITaskService:
    """AI任务分解服务类，处理基于AI的任务分解逻辑"""
    
    def __init__(self, db_manager: DatabaseManager, llm_fetcher: LLMFetcher):
        """
        初始化AI任务服务
        
        Args:
            db_manager (DatabaseManager): 数据库管理器实例
            llm_fetcher (LLMFetcher): LLM获取器实例
        """
        self.db_manager = db_manager
        self.llm_fetcher = llm_fetcher
    
    async def decompose_task(
        self, 
        user_id: str, 
        goal: str,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用AI将大目标分解为具体任务
        
        Args:
            user_id (str): 用户ID
            goal (str): 用户的大目标
            workspace_id (Optional[str]): 工作空间ID
            
        Returns:
            Dict[str, Any]: 分解后的任务结构
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        # 构造系统提示词
        system_prompt = """
        你是一个专业的任务分解助手，你的任务是将用户的大目标分解为具体可执行的子任务。
        请按照以下格式返回JSON结构：
        {
            "main_goal": "用户输入的原始目标",
            "tasks": [
                {
                    "title": "任务标题",
                    "description": "任务详细描述",
                    "estimated_minutes": 30, // 预估完成时间（分钟）
                    "priority": "medium", // 优先级：low/medium/high/critical
                    "subtasks": [
                        {
                            "title": "子任务标题",
                            "description": "子任务详细描述",
                            "estimated_minutes": 15
                        }
                    ]
                }
            ]
        }
        
        要求：
        1. 将大目标分解为3-7个主要任务
        2. 每个主要任务可以包含1-3个子任务
        3. 任务应该具体、可执行，避免过于宽泛
        4. 为每个任务提供合理的预估时间
        5. 只返回有效的JSON，不要包含其他文本
        """
        
        # 构造用户消息
        user_message = f"请将以下目标分解为具体任务：{goal}"
        
        try:
            # 调用LLM获取任务分解结果
            response = self.llm_fetcher.fetch(
                msg=user_message,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=4096
            )
            
            # 解析LLM返回的JSON
            ai_response_content = response.choices[0].message.content
            task_structure = json.loads(ai_response_content)
            
            # 保存AI请求记录到数据库
            await self._save_ai_request(user_id, goal, ai_response_content)
            
            return {
                "success": True,
                "data": task_structure,
                "message": "任务分解成功"
            }
            
        except json.JSONDecodeError as e:
            raise Exception(f"AI返回结果解析失败: {str(e)}")
        except Exception as e:
            raise Exception(f"任务分解失败: {str(e)}")
    
    async def _save_ai_request(
        self, 
        user_id: str, 
        prompt: str, 
        response: str
    ) -> None:
        """
        保存AI请求记录到数据库
        
        Args:
            user_id (str): 用户ID
            prompt (str): 用户输入
            response (str): AI响应
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                await conn.execute(
                    """
                    INSERT INTO ai_requests (id, user_id, prompt, response_text, status)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    str(uuid.uuid4()), user_id, prompt, response, "completed"
                )
            finally:
                await self.db_manager.release_connection(conn)
        except Exception as e:
            # 记录日志但不中断主流程
            print(f"保存AI请求记录失败: {str(e)}")
    
    async def get_task_suggestions(
        self, 
        user_id: str, 
        task_id: str
    ) -> Dict[str, Any]:
        """
        获取特定任务的AI建议
        
        Args:
            user_id (str): 用户ID
            task_id (str): 任务ID
            
        Returns:
            Dict[str, Any]: AI建议
        """
        try:
            # 获取任务信息
            task_info = await self._get_task_info(task_id)
            
            # 构造系统提示词
            system_prompt = """
            你是一个专业的任务规划助手，你的任务是为用户提供完成特定任务的建议和技巧。
            请按照以下格式返回JSON结构：
            {
                "task_title": "任务标题",
                "suggestions": [
                    {
                        "title": "建议标题",
                        "description": "建议详细描述",
                        "steps": ["步骤1", "步骤2", "步骤3"]
                    }
                ],
                "resources": [
                    {
                        "title": "资源标题",
                        "url": "资源链接"
                    }
                ],
                "tips": ["提示1", "提示2"]
            }
            
            要求：
            1. 提供3-5条具体建议
            2. 每条建议包含2-4个执行步骤
            3. 推荐1-3个相关资源
            4. 给出2-3个实用小贴士
            5. 只返回有效的JSON，不要包含其他文本
            """
            
            # 构造用户消息
            user_message = f"请为以下任务提供完成建议：{task_info['title']} - {task_info['description']}"
            
            # 调用LLM获取建议
            response = self.llm_fetcher.fetch(
                msg=user_message,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2048
            )
            
            # 解析响应
            ai_response_content = response.choices[0].message.content
            suggestions = json.loads(ai_response_content)
            
            # 保存AI请求记录
            await self._save_ai_request(user_id, user_message, ai_response_content)
            
            return {
                "success": True,
                "data": suggestions,
                "message": "建议获取成功"
            }
            
        except Exception as e:
            raise Exception(f"获取任务建议失败: {str(e)}")
    
    async def _get_task_info(self, task_id: str) -> Dict[str, str]:
        """
        从数据库获取任务信息
        
        Args:
            task_id (str): 任务ID
            
        Returns:
            Dict[str, str]: 任务信息
        """
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
        except Exception as e:
            raise Exception(f"获取任务信息失败: {str(e)}")