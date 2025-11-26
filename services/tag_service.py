from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager

class TagService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_tag(self, workspace_id: str, name: str, color: Optional[str], user_id: str) -> Dict[str, Any]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                "INSERT INTO tags (workspace_id, name, color, created_by) VALUES ($1,$2,$3,$4) RETURNING id, workspace_id, name, color, created_by, created_at",
                workspace_id, name, color, user_id
            )
            return dict(row)
        finally:
            await self.db.release_connection(conn)

    async def list_tags(self, workspace_id: str) -> List[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            rows = await conn.fetch("SELECT id, workspace_id, name, color, created_by, created_at FROM tags WHERE workspace_id=$1", workspace_id)
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def attach_tag(self, task_id: str, tag_id: str) -> None:
        conn = await self.db.get_connection(5.0)
        try:
            await conn.execute("INSERT INTO task_tags (task_id, tag_id) VALUES ($1,$2) ON CONFLICT DO NOTHING", task_id, tag_id)
        finally:
            await self.db.release_connection(conn)

    async def detach_tag(self, task_id: str, tag_id: str) -> None:
        conn = await self.db.get_connection(5.0)
        try:
            await conn.execute("DELETE FROM task_tags WHERE task_id=$1 AND tag_id=$2", task_id, tag_id)
        finally:
            await self.db.release_connection(conn)
