from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
from uuid import UUID
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

from dataclasses import asdict
from asyncpg import Record
import json

from .models.task_data_model import *

class TaskService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_task(
            self, 
            project_id: str, 
            workspace_id: str, 
            creator_id: str, 
            title: str, 
            parent_task_id: Optional[str],
            description: Optional[str], 
            assignee_id: Optional[str], 
            priority: str, 
            estimated_minutes: Optional[int], 
            due_at: Optional[str]
        ) -> Optional[Task]:
        """
        创建单个任务。
        Args:
            project_id: 项目ID。
            workspace_id: 工作空间ID。
            creator_id: 用户ID。
            title: 任务标题。
            parent_task_id: 上级任务ID，可选。
            description: 任务描述。
            assignee_id: 任务分配人。（是否要实现这个？）
            priority: 优先级。
            estimated_minutes: 预估分钟。
            due_at: 结束时间。
        """
        try:
            conn = await self.db.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO tasks 
                    (project_id, workspace_id, creator_id, assignee_id, title, description, priority, estimated_minutes, due_at, parent_task_id)
                    VALUES 
                    ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                    RETURNING 
                    id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
                    """,
                    project_id, workspace_id, creator_id, assignee_id, title, description, priority, estimated_minutes, due_at, parent_task_id
                )
                if row is None:
                    return None
                return self._build_task_from_row(row, parent_task_id)
            finally:
                await self.db.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(str(e))
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(str(e))
        
    async def create_task_by_json(
            self,
            project_id: str, 
            workspace_id: str, 
            creator_id: str,
            json_message: str
    ) -> Optional[Task]:
        """
        基于JSON创建任务。
        - 最开始写这个函数是为了解析来自LLM的JSON文件，但现在看上去，我需要用这个函数解决来自用户的任务JSON。

        Args:
            project_id (str): 当前工程ID。
            workspace_id (str): 当前工作空间ID
            creator_id (str): 任务创建者ID
            json_message (str): 创建JSON任务。

        Notes:
            输入的JSON格式见提示词部分。
        """
        # 增加对json_message的严格检查
        if not json_message:
            print("Warning: Empty JSON message provided to create_task_by_json")
            return None
            
        if not isinstance(json_message, str):
            print(f"Warning: Invalid JSON message type provided to create_task_by_json: {type(json_message)}")
            return None
            
        cleaned_message = self._normalize_json_message(json_message)
        if not cleaned_message or not cleaned_message.strip():
            # 没有可解析的内容，直接跳过。
            print("Warning: No valid content found in JSON message after normalization")
            return None
            
        # 确保清理后的消息是非空的
        cleaned_message = cleaned_message.strip()
        if not cleaned_message:
            print("Warning: Cleaned JSON message is empty")
            return None
        
        # 开始在JSON中加入内容。
        try:
            payload: Dict[str, Any] = json.loads(cleaned_message)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON format for tasks: {exc}") from exc

        tasks_block = payload.get("tasks")
        if not isinstance(tasks_block, list) or not tasks_block:
            raise ValueError("Invalid task information format: 'tasks' must be a non-empty list.")

        tasks: List[TaskInfo] = [self._parse_task_info(item) for item in tasks_block]
        if len(tasks) != 1:
            # 只能有1个主任务。
            raise ValueError("Invalid task information format: Only ONE main task expected.")

        maintask: TaskInfo = tasks[0]

        try:
            conn = await self.db.get_connection(5.0)
            try:
                async with conn.transaction():
                    created_tree: Optional[TaskTree] = await self._recursive_create_tasks(
                        task_info=maintask,
                        project_id=project_id,
                        workspace_id=workspace_id,
                        creator_id=creator_id,
                        parent_task_id=None,
                        conn=conn
                    )
                return created_tree.task if created_tree else None  # 返回TaskTree中的Task对象
            
            finally:
                await self.db.release_connection(conn)
        except ConnectionError as exc:
            raise DatabaseConnectionError(str(exc))
        except DBTimeoutError as exc:
            raise DatabaseTimeoutError(str(exc))

    def _normalize_json_message(self, json_message: Any) -> Optional[str]:
        if json_message is None:
            return None
        content = str(json_message).strip()
        if not content:
            return None

        begin = "<<<JSON_BEGIN>>>"
        end = "<<<JSON_END>>>"
        if begin in content and end in content:
            start = content.find(begin)
            finish = content.find(end, start + len(begin))
            if finish != -1:
                content = content[start + len(begin):finish].strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        content = content.lstrip("\ufeff").strip()
        if not content:
            return None

        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            pass

        if "{" not in content or "}" not in content:
            return content

        opens = [i for i, ch in enumerate(content) if ch == "{"]
        closes = [i for i, ch in enumerate(content) if ch == "}"]
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

        return content

    
    async def _recursive_create_tasks(
            self,
            task_info: TaskInfo,
            project_id: str,
            workspace_id: str,
            creator_id: str,
            parent_task_id: Optional[str],
            conn: Any   # <- 必须有一个被创建了的连接实例
    ) -> TaskTree:
        """
        输入任务信息，然后递归解析子任务。通过多条SQL创建任务并合并发送。
        - 该内容必须要引入来自外界的链接实例——递归解析子任务时不能创建更多的连接实例。
        - 返回任务树结构。
        
        Args:
            task_info (TaskInfo): 来自JSON的任务信息。
            project_id (str): 目标项目ID。
            workspace_id (str): 目标工作空间ID。
            creator_id (str): 任务创建者ID。
            parent_task_id (Optional[str]): 上级任务ID。对主任务而言，可以无需该部分。
            conn (any): 来自外界的、被创建的连接实例。
        """
        if not task_info.title:
            raise ValueError("Task title is required.")
        
        # 换算时间。
        estimated_minutes: Optional[int] = self._convert_to_minutes(
            task_info.estimated_time,
            task_info.estimated_time_unit
        )

        if conn is None:
            # 如果没实例则重新进行本步骤
            created = await self.create_task(
                project_id=project_id,
                workspace_id=workspace_id,
                creator_id=creator_id,
                title=task_info.title,
                parent_task_id=parent_task_id,
                description=task_info.description,
                assignee_id=None,
                priority=task_info.priority,
                estimated_minutes=estimated_minutes,
                due_at=None
            )
        else:
            # 开始执行步骤，返回：
            # id, project_id, workspace_id, creator_id, assignee_id,
            # title, description, status, priority, estimated_minutes, 
            # due_at, created_at, updated_at
            # 共计13条属性
            row = await conn.fetchrow(
                """
                INSERT INTO tasks (project_id, workspace_id, creator_id, assignee_id, title, description, priority, estimated_minutes, due_at, parent_task_id)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
                RETURNING 
                id, project_id, workspace_id, creator_id, assignee_id,
                title, description, status, priority, estimated_minutes, 
                due_at, created_at, updated_at
                """,
                project_id, workspace_id, creator_id, None, task_info.title, task_info.description,
                task_info.priority, estimated_minutes, None, parent_task_id
            )
            created = self._build_task_from_row(row, parent_task_id) if row else None

        if created is None:
            # 保证上述SQL事务必须返回一个东西
            raise DatabaseConnectionError("Failed to create task from decomposition result.")
        
        # 随后对每一个task_info的子任务，递归创建子任务。
        children: List[Task] = []   # <-- 储存子任务的位置
        for subtask in task_info.subtasks:
            result = await self._recursive_create_tasks(
                task_info=subtask,
                project_id=project_id,
                workspace_id=workspace_id,
                creator_id=creator_id,
                parent_task_id=created.id,
                conn=conn
            )
            children.append(result)
        
        # 返回任务树结构
        return TaskTree(created, children)

    def _parse_task_info(self, payload: TaskInfo) -> TaskInfo:
        """
        将原始字典转换为 TaskInfo，顺便做一些基本校验。
        """
        if not isinstance(payload, dict):
            raise ValueError("Task item must be an object.")

        subtasks_raw: List[TaskInfo] = payload.get("subtasks") or []
        if not isinstance(subtasks_raw, list):
            raise ValueError("Subtasks must be provided as a list.")

        priority: str = str(payload.get("priority", "medium")).lower()
        allowed_priority = {"low", "medium", "high", "critical"}
        if priority not in allowed_priority:
            raise ValueError(f"Invalid priority: {priority}")

        unit: str = str(payload.get("estimated_time_unit", "minute")).lower()
        allowed_units = {"minute", "hour", "day", "week", "month"}
        if unit not in allowed_units:
            raise ValueError(f"Invalid estimated_time_unit: {unit}")

        estimated_time_val: int = payload.get("estimated_time", 0)
        try:
            estimated_time = float(estimated_time_val)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid estimated_time: {estimated_time_val}")

        return TaskInfo(
            title=str(payload.get("title", "")).strip(),
            description=str(payload.get("description", "")).strip(),
            estimated_time=estimated_time_val,
            estimated_time_unit=unit,
            priority=priority,
            subtasks=[self._parse_task_info(item) for item in subtasks_raw]
        )

    def _build_task_from_row(
            self,
            row: Any,
            parent_task_id: Optional[str] = None
    ) -> Task:
        data = {key: self._normalize_db_value(value) for key, value in dict(row).items()}
        if "parent_task_id" not in data:
            data["parent_task_id"] = self._normalize_db_value(parent_task_id)

        defaults = {
            "actual_minutes": None,
            "started_at": None,
            "completed_at": None,
            "is_recurring": None,
            "recurrence_rule": None,
            "recurrence_frequency": None,
            "recurrence_meta": None,
            "metadata": None,
            "deleted_at": None,
        }
        for key, val in defaults.items():
            data.setdefault(key, val)

        return Task(**data)

    def _normalize_db_value(self, value: Any) -> Any:
        """
        辅助函数：将Record里的UUID全部转为str，并将时间转为iso格式的函数。
        - 请自动解析每一项内容，并对每一项使用。
        """
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _convert_to_minutes(
            self, 
            estimated_time: Optional[float], 
            unit: str
        ) -> Optional[int]:
        """
        将时间估算转换为分钟。
        """
        if estimated_time is None:
            return None

        unit = unit.lower()
        multiplier = {
            "minute": 1,
            "hour": 60,
            "day": 60 * 24,
            "week": 60 * 24 * 7,
            "month": 60 * 24 * 30
        }.get(unit)

        if multiplier is None:
            raise ValueError(f"Unsupported time unit: {unit}")

        return int(round(estimated_time * multiplier))
    
    def _convert_minute_to_time(
            self,
            estimated_minute: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        将分钟估算回时间，和对应单位。
        """
        if estimated_minute is None:
            return None

        units = [
            ("month", 60 * 24 * 30),
            ("week", 60 * 24 * 7),
            ("day", 60 * 24),
            ("hour", 60),
            ("minute", 1),
        ]

        for unit, divisor in units:
            if estimated_minute >= divisor:
                value = estimated_minute / divisor
                if estimated_minute % divisor == 0:
                    value = estimated_minute // divisor
                else:
                    value = round(value, 2)
                return {"time": value, "unit": unit}

        return {"time": estimated_minute, "unit": "minute"}


    async def list_tasks(
            self, 
            workspace_id: str, 
            project_id: Optional[str] = None
        ) -> List[Task]:
        """
        列出特定工作空间、特定工程下的所有任务。

        Deprecated:
            这个API已废弃，并在2个版本迭代后被删除。
            请使用list_root_tasks() + get_task_tree()，获取全部任务。
            我并不需要获取某个工作空间内的全部的、未被保留依赖关系的任务。
            
        TODO: 我需要将这个地方改为列出全部的子任务的版本，参考ai_task_service.py。
        """
        conn = await self.db.get_connection(5.0)
        try:
            if project_id:
                rows = await conn.fetch(
                    "SELECT * FROM tasks WHERE project_id=$1 AND deleted_at IS NULL ORDER BY created_at DESC",
                    project_id
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM tasks WHERE workspace_id=$1 AND deleted_at IS NULL ORDER BY created_at DESC",
                    workspace_id
                )
            return [self._build_task_from_row(r) for r in rows]
        finally:
            await self.db.release_connection(conn)
    
    async def list_root_tasks(
            self, 
            workspace_id: str, 
            project_id: Optional[str] = None
        ) -> List[Task]:
        """
        列出特定工作空间、特定工程下的主任务。
        - 主任务为任务树的最上级任务，其上级任务为空白。

        Returns:
            (List[Task]): 任务列表。
        """
        conn = await self.db.get_connection(5.0)
        try:
            if project_id:
                rows = await conn.fetch(
                    """
                    SELECT * FROM tasks 
                    WHERE project_id=$1 AND deleted_at IS NULL AND parent_task_id IS NULL
                    ORDER BY created_at DESC
                    """,
                    project_id
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM tasks 
                    WHERE workspace_id=$1 AND deleted_at IS NULL AND parent_task_id IS NULL
                    ORDER BY created_at DESC
                    """,
                    workspace_id
                )
            return [self._build_task_from_row(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def get_task(
            self, 
            task_id: str
        ) -> Optional[Task]:
        """
        根据任务ID，获取任务。
        """
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow("SELECT * FROM tasks WHERE id=$1 AND deleted_at IS NULL", task_id)
            return self._build_task_from_row(row) if row else None
        finally:
            await self.db.release_connection(conn)
    
    async def get_task_tree(
            self,
            task_id: str
    ) -> Optional[TaskTree]:
        """
        根据任务ID，获取任务，及其所有的子任务。
        - 该过程是一个递归过程，并会返回任务树结构。

        Returns:
            (Optional[TaskTree]): 任务树。
        """
        conn = await self.db.get_connection(5.0)
        try:
            now_task = await self._task_tree_getter(task_id, conn)
            return now_task
        finally:
            await self.db.release_connection(conn)
    
    async def _task_tree_getter(
            self,
            task_id: str,
            conn: Any
    ) -> Optional[TaskTree]:
        """
        私有函数：递归获取任务和其他所有子任务。
        """
        row: Record = await conn.fetchrow("SELECT * FROM tasks WHERE id=$1 AND deleted_at IS NULL", task_id)

        now_task: Task = self._build_task_from_row(row)

        # 建立任务树。
        now_tree: TaskTree = TaskTree(now_task, [])
        
        # 用这个获取子任务数量
        else_ids: List[Record] = await conn.fetch(
            "SELECT id FROM tasks WHERE parent_task_id=$1 AND deleted_at IS NULL", now_task.id
        )

        # 如果还有子任务
        if else_ids is not None:
            child_ids = [self._normalize_db_value(q["id"]) for q in else_ids]
            for child_id in child_ids:
                # 获取全部子任务，并返回。
                sub_tasktree: Optional[TaskTree] = await self._task_tree_getter(child_id, conn)
                if sub_tasktree is not None:
                    now_tree.subtasks.append(sub_tasktree)

        # 返回被构造好的树。
        return now_tree

    async def update_task(
            self, 
            task_id: str, 
            fields: Dict[str, Any]
        ) -> Optional[Task]:
        if not fields:
            return await self.get_task(task_id)
        updates, params = [], [task_id]
        for key, val in fields.items():
            updates.append(f"{key} = ${len(params)+1}")
            params.append(val)
        updates.append("updated_at = now()")
        conn = await self.db.get_connection(5.0)
        try:
            row: Optional[Record] = await conn.fetchrow(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id=$1 AND deleted_at IS NULL RETURNING *",
                *params
            )
            return self._build_task_from_row(row) if row else None
        finally:
            await self.db.release_connection(conn)

    async def delete_task(
            self, 
            task_id: str
        ) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE tasks SET deleted_at=now() WHERE id=$1 AND deleted_at IS NULL", task_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)


