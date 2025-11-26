from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

class TaskService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_task(self, project_id: Optional[str], workspace_id: str, creator_id: str, title: str, description: Optional[str], assignee_id: Optional[str], priority: str, estimated_minutes: Optional[int], due_at: Optional[str]) -> Dict[str, Any]:
        try:
            conn = await self.db.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO tasks (project_id, workspace_id, creator_id, assignee_id, title, description, priority, estimated_minutes, due_at)
                    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                    RETURNING id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
                    """,
                    project_id, workspace_id, creator_id, assignee_id, title, description, priority, estimated_minutes, due_at
                )
                if row is None:
                    raise DatabaseConnectionError("Failed to create task")
                return dict(row)
            finally:
                await self.db.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(str(e))
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(str(e))

    async def list_tasks(self, workspace_id: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
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
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow("SELECT * FROM tasks WHERE id=$1 AND deleted_at IS NULL", task_id)
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)

    async def update_task(self, task_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not fields:
            return await self.get_task(task_id)
        updates, params = [], [task_id]
        for key, val in fields.items():
            updates.append(f"{key} = ${len(params)+1}")
            params.append(val)
        updates.append("updated_at = now()")
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                f"UPDATE tasks SET {', '.join(updates)} WHERE id=$1 AND deleted_at IS NULL RETURNING *",
                *params
            )
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)

    async def delete_task(self, task_id: str) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE tasks SET deleted_at=now() WHERE id=$1 AND deleted_at IS NULL", task_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)
