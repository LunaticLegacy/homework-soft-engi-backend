from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError


class ManagementService:
    """Service layer for workspace, project, task, tag, comment, attachment and notification management."""

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

    # Tag operations
    async def create_tag(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO tags (workspace_id, name, color, created_by)
            VALUES ($1, $2, $3, $4)
            RETURNING id, workspace_id, name, color, created_by, created_at
            """,
            payload["workspace_id"],
            payload["name"],
            payload.get("color"),
            payload.get("created_by"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to create tag")
        return row

    async def list_tags(self, workspace_id: str) -> List[Dict[str, Any]]:
        return await self._fetch(
            """
            SELECT id, workspace_id, name, color, created_by, created_at
            FROM tags
            WHERE workspace_id = $1
            ORDER BY created_at DESC
            """,
            workspace_id,
        )

    async def attach_tag_to_task(self, task_id: str, tag_id: str) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO task_tags (task_id, tag_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            RETURNING task_id, tag_id
            """,
            task_id,
            tag_id,
        )
        return row or {"task_id": task_id, "tag_id": tag_id}

    async def detach_tag_from_task(self, task_id: str, tag_id: str) -> str:
        return await self._execute(
            """
            DELETE FROM task_tags WHERE task_id = $1 AND tag_id = $2
            """,
            task_id,
            tag_id,
        )

    # Comment operations
    async def add_comment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO comments (resource_type, resource_id, user_id, content, content_html, reply_to_comment_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, resource_type, resource_id, user_id, content, content_html, reply_to_comment_id, created_at, updated_at
            """,
            payload["resource_type"],
            payload["resource_id"],
            payload.get("user_id"),
            payload["content"],
            payload.get("content_html"),
            payload.get("reply_to_comment_id"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to add comment")
        return row

    async def list_comments(self, resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
        return await self._fetch(
            """
            SELECT id, resource_type, resource_id, user_id, content, content_html, reply_to_comment_id, created_at, updated_at
            FROM comments
            WHERE resource_type = $1 AND resource_id = $2 AND deleted_at IS NULL
            ORDER BY created_at ASC
            """,
            resource_type,
            resource_id,
        )

    # Attachment operations
    async def add_attachment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO attachments (owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, COALESCE($8, 'file'), COALESCE($9, '{}'::jsonb))
            RETURNING id, owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata, created_at
            """,
            payload.get("owner_user_id"),
            payload.get("attached_to_type"),
            payload.get("attached_to_id"),
            payload["file_name"],
            payload.get("file_size"),
            payload.get("content_type"),
            payload.get("storage_key"),
            payload.get("attachment_type"),
            payload.get("metadata"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to add attachment")
        return row

    async def list_attachments(self, attached_to_type: str, attached_to_id: str) -> List[Dict[str, Any]]:
        return await self._fetch(
            """
            SELECT id, owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata, created_at
            FROM attachments
            WHERE attached_to_type = $1 AND attached_to_id = $2 AND deleted_at IS NULL
            ORDER BY created_at DESC
            """,
            attached_to_type,
            attached_to_id,
        )

    # Notification operations
    async def create_notification(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            INSERT INTO notifications (user_id, level, title, body, data, is_read, channel)
            VALUES ($1, COALESCE($2, 'info'), $3, $4, COALESCE($5, '{}'::jsonb), COALESCE($6, FALSE), COALESCE($7, 'in_app'))
            RETURNING id, user_id, level, title, body, data, is_read, channel, created_at, delivered_at
            """,
            payload["user_id"],
            payload.get("level"),
            payload.get("title"),
            payload.get("body"),
            payload.get("data"),
            payload.get("is_read"),
            payload.get("channel"),
        )
        if row is None:
            raise DatabaseConnectionError("Failed to create notification")
        return row

    async def list_notifications(self, user_id: str, only_unread: bool = False) -> List[Dict[str, Any]]:
        if only_unread:
            return await self._fetch(
                """
                SELECT id, user_id, level, title, body, data, is_read, channel, created_at, delivered_at
                FROM notifications
                WHERE user_id = $1 AND is_read = FALSE
                ORDER BY created_at DESC
                """,
                user_id,
            )
        return await self._fetch(
            """
            SELECT id, user_id, level, title, body, data, is_read, channel, created_at, delivered_at
            FROM notifications
            WHERE user_id = $1
            ORDER BY created_at DESC
            """,
            user_id,
        )

    async def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        row = await self._fetchrow(
            """
            UPDATE notifications
            SET is_read = TRUE, delivered_at = COALESCE(delivered_at, now())
            WHERE id = $1
            RETURNING id, user_id, level, title, body, data, is_read, channel, created_at, delivered_at
            """,
            notification_id,
        )
        if row is None:
            raise ResourceNotFoundError("Notification not found")
        return row

    # Search operations
    async def search(self, query: str, workspace_id: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        like_query = f"%{query}%"
        project_conditions = ["deleted_at IS NULL", "(title ILIKE $1 OR description ILIKE $1)"]
        task_conditions = ["deleted_at IS NULL", "(title ILIKE $1 OR description ILIKE $1)"]
        params_projects: List[Any] = [like_query]
        params_tasks: List[Any] = [like_query]
        if workspace_id:
            params_projects.append(workspace_id)
            params_tasks.append(workspace_id)
            project_conditions.append(f"workspace_id = ${len(params_projects)}")
            task_conditions.append(f"workspace_id = ${len(params_tasks)}")
        projects = await self._fetch(
            f"""
            SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, metadata, created_at, updated_at
            FROM projects
            WHERE {' AND '.join(project_conditions)}
            ORDER BY created_at DESC
            LIMIT 50
            """,
            *params_projects,
        )
        tasks = await self._fetch(
            f"""
            SELECT id, project_id, workspace_id, creator_id, assignee_id, title, description, status, priority, estimated_minutes, due_at, created_at, updated_at
            FROM tasks
            WHERE {' AND '.join(task_conditions)}
            ORDER BY created_at DESC
            LIMIT 50
            """,
            *params_tasks,
        )
        return {"projects": projects, "tasks": tasks}
