from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError


class ManagementService:
    """Service layer for workspace, project, and task management."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def _fetchrow(self, query: str, *params: Any) -> Optional[Dict[str, Any]]:
        try:
            async with self.db_manager.acquire() as conn:
                row = await conn.fetchrow(query, *params)
                return dict(row) if row else None
        except ConnectionError as exc:
            raise DatabaseConnectionError(str(exc))
        except DBTimeoutError as exc:
            raise DatabaseTimeoutError(str(exc))

    async def _fetch(self, query: str, *params: Any) -> List[Dict[str, Any]]:
        try:
            async with self.db_manager.acquire() as conn:
                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except ConnectionError as exc:
            raise DatabaseConnectionError(str(exc))
        except DBTimeoutError as exc:
            raise DatabaseTimeoutError(str(exc))

    async def _execute(self, query: str, *params: Any) -> str:
        try:
            async with self.db_manager.acquire() as conn:
                return await conn.execute(query, *params)
        except ConnectionError as exc:
            raise DatabaseConnectionError(str(exc))
        except DBTimeoutError as exc:
            raise DatabaseTimeoutError(str(exc))

    # Workspace operations
    async def create_workspace(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO workspaces (organization_id, owner_user_id, name, description, settings)
            VALUES ($1, $2, $3, $4, COALESCE($5, '{}'::jsonb))
            RETURNING id, organization_id, owner_user_id, name, description, settings, created_at, updated_at
            """,
            payload.get("organization_id"),
            payload.get("owner_user_id"),
            payload["name"],
            payload.get("description"),
            payload.get("settings"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to create workspace")
        return row

    async def list_workspaces(self) -> List[Dict[str, Any]]:
        return await self._fetch(
            """
            SELECT id, organization_id, owner_user_id, name, description, settings, created_at, updated_at
            FROM workspaces
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC
            """
        )

    async def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            SELECT id, organization_id, owner_user_id, name, description, settings, created_at, updated_at
            FROM workspaces
            WHERE id = $1 AND deleted_at IS NULL
            """,
            workspace_id,
        )
        if row is None:
            raise ResourceNotFoundError("Workspace not found")
        return row

    async def update_workspace(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields: List[str] = []
        values: List[Any] = []
        for key in ["name", "description", "settings"]:
            if key in payload and payload[key] is not None:
                values.append(payload[key])
                fields.append(f"{key} = ${len(values)}")
        if not fields:
            return await self.get_workspace(workspace_id)
        values.append(workspace_id)
        row = await self._fetchrow(
            f"""
            UPDATE workspaces
            SET {', '.join(fields)}, updated_at = now()
            WHERE id = ${len(values)} AND deleted_at IS NULL
            RETURNING id, organization_id, owner_user_id, name, description, settings, created_at, updated_at
            """,
            *values,
        )
        if row is None:
            raise ResourceNotFoundError("Workspace not found")
        return row

    async def delete_workspace(self, workspace_id: str) -> str:
        result = await self._execute(
            """
            UPDATE workspaces SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL
            """,
            workspace_id,
        )
        return result

    # Project operations
    async def create_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO projects (workspace_id, owner_id, title, description, start_date, due_date, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, COALESCE($7, '{}'::jsonb))
            RETURNING id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
            """,
            payload.get("workspace_id"),
            payload.get("owner_id"),
            payload["title"],
            payload.get("description"),
            payload.get("start_date"),
            payload.get("due_date"),
            payload.get("metadata"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to create project")
        return row

    async def list_projects(self, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if workspace_id:
            return await self._fetch(
                """
                SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
                FROM projects
                WHERE deleted_at IS NULL AND workspace_id = $1
                ORDER BY created_at DESC
                """,
                workspace_id,
            )
        return await self._fetch(
            """
            SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
            FROM projects
            WHERE deleted_at IS NULL
            ORDER BY created_at DESC
            """
        )

    async def get_project(self, project_id: str) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
            FROM projects
            WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )
        if row is None:
            raise ResourceNotFoundError("Project not found")
        return row

    async def update_project(self, project_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields: List[str] = []
        values: List[Any] = []
        for key in ["title", "description", "start_date", "due_date", "archived", "metadata"]:
            if key in payload and payload[key] is not None:
                values.append(payload[key])
                fields.append(f"{key} = ${len(values)}")
        if not fields:
            return await self.get_project(project_id)
        values.append(project_id)
        row = await self._fetchrow(
            f"""
            UPDATE projects
            SET {', '.join(fields)}, updated_at = now()
            WHERE id = ${len(values)} AND deleted_at IS NULL
            RETURNING id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
            """,
            *values,
        )
        if row is None:
            raise ResourceNotFoundError("Project not found")
        return row

    async def delete_project(self, project_id: str) -> str:
        return await self._execute(
            """
            UPDATE projects SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL
            """,
            project_id,
        )

    # Task operations
    async def create_task(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO tasks (project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, COALESCE($7, 'backlog'), COALESCE($8, 'medium'), $9, $10, COALESCE($11, '{}'::jsonb))
            RETURNING id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
            """,
            payload.get("project_id"),
            payload.get("workspace_id"),
            payload.get("creator_id"),
            payload.get("assignee_id"),
            payload["title"],
            payload.get("description"),
            payload.get("status"),
            payload.get("priority"),
            payload.get("estimated_minutes"),
            payload.get("due_at"),
            payload.get("metadata"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to create task")
        return row

    async def list_tasks(
        self,
        workspace_id: Optional[str] = None,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        conditions: List[str] = ["deleted_at IS NULL"]
        values: List[Any] = []
        if workspace_id:
            values.append(workspace_id)
            conditions.append(f"workspace_id = ${len(values)}")
        if status:
            values.append(status)
            conditions.append(f"status = ${len(values)}")
        if assignee_id:
            values.append(assignee_id)
            conditions.append(f"assignee_id = ${len(values)}")
        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
            FROM tasks
            WHERE {where_clause}
            ORDER BY created_at DESC
        """
        return await self._fetch(query, *values)

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            SELECT id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
            FROM tasks
            WHERE id = $1 AND deleted_at IS NULL
            """,
            task_id,
        )
        if row is None:
            raise ResourceNotFoundError("Task not found")
        return row

    async def update_task(self, task_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields: List[str] = []
        values: List[Any] = []
        for key in [
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "estimated_minutes",
            "due_at",
        ]:
            if key in payload and payload[key] is not None:
                values.append(payload[key])
                fields.append(f"{key} = ${len(values)}")
        if not fields:
            return await self.get_task(task_id)
        values.append(task_id)
        row = await self._fetchrow(
            f"""
            UPDATE tasks
            SET {', '.join(fields)}, updated_at = now()
            WHERE id = ${len(values)} AND deleted_at IS NULL
            RETURNING id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
            """,
            *values,
        )
        if row is None:
            raise ResourceNotFoundError("Task not found")
        return row

    async def delete_task(self, task_id: str) -> str:
        return await self._execute(
            """
            UPDATE tasks SET deleted_at = now() WHERE id = $1 AND deleted_at IS NULL
            """,
            task_id,
        )

