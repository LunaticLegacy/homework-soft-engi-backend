from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError

class ProjectService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_project(
            self, 
            workspace_id: str, 
            owner_id: str, 
            title: str, 
            description: Optional[str], 
            start_date: Optional[str], 
            due_date: Optional[str]
        ) -> Dict[str, Any]:
        try:
            conn = await self.db.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO projects (workspace_id, owner_id, title, description, start_date, due_date)
                    VALUES ($1,$2,$3,$4,$5,$6)
                    RETURNING id, workspace_id, owner_id, title, description, start_date, due_date, archived, created_at, updated_at
                    """,
                    workspace_id, owner_id, title, description, start_date, due_date
                )
                if row is None:
                    raise DatabaseConnectionError("Failed to create project")
                return dict(row)
            finally:
                await self.db.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(str(e))
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(str(e))

    async def list_projects(
            self, 
            workspace_id: str
        ) -> List[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            rows = await conn.fetch(
                "SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, created_at, updated_at FROM projects WHERE workspace_id=$1 AND deleted_at IS NULL",
                workspace_id
            )
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def get_project(
            self, 
            project_id: str
        ) -> Optional[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                "SELECT id, workspace_id, owner_id, title, description, start_date, due_date, archived, created_at, updated_at FROM projects WHERE id=$1 AND deleted_at IS NULL",
                project_id
            )
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)

    async def update_project(
            self, 
            project_id: str, 
            fields: Dict[str, Any]
        ) -> Optional[Dict[str, Any]]:
        if not fields:
            return await self.get_project(project_id)
        updates, params = [], [project_id]
        for key, val in fields.items():
            updates.append(f"{key} = ${len(params)+1}")
            params.append(val)
        updates.append(f"updated_at = now()")
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                f"UPDATE projects SET {', '.join(updates)} WHERE id=$1 AND deleted_at IS NULL RETURNING id, workspace_id, owner_id, title, description, start_date, due_date, archived, created_at, updated_at",
                *params
            )
            return dict(row) if row else None
        finally:
            await self.db.release_connection(conn)

    async def delete_project(self, project_id: str) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE projects SET deleted_at=now() WHERE id=$1 AND deleted_at IS NULL", project_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)
