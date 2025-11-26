from typing import Any, Dict, List
from modules.databaseman import DatabaseManager

class SearchService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def search(self, workspace_id: str, query: str) -> Dict[str, List[Dict[str, Any]]]:
        conn = await self.db.get_connection(5.0)
        try:
            # Fallback to ILIKE if tsvector not populated
            tasks = await conn.fetch(
                """
                SELECT id, title, description, status, priority, workspace_id, project_id
                FROM tasks
                WHERE workspace_id=$1 AND deleted_at IS NULL AND (title ILIKE $2 OR description ILIKE $2)
                ORDER BY updated_at DESC
                """,
                workspace_id, f"%{query}%"
            )
            projects = await conn.fetch(
                """
                SELECT id, title, description, workspace_id
                FROM projects
                WHERE workspace_id=$1 AND deleted_at IS NULL AND (title ILIKE $2 OR description ILIKE $2)
                ORDER BY updated_at DESC
                """,
                workspace_id, f"%{query}%"
            )
            return {
                "tasks": [dict(r) for r in tasks],
                "projects": [dict(r) for r in projects]
            }
        finally:
            await self.db.release_connection(conn)
