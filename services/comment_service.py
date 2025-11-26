from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager
from core.exceptions import DatabaseConnectionError

class CommentService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def add_comment(self, resource_type: str, resource_id: str, user_id: str, content: str, reply_to: Optional[str]) -> Dict[str, Any]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO comments (resource_type, resource_id, user_id, content, reply_to_comment_id)
                VALUES ($1,$2,$3,$4,$5)
                RETURNING id, resource_type, resource_id, user_id, content, reply_to_comment_id, created_at, updated_at
                """,
                resource_type, resource_id, user_id, content, reply_to
            )
            if row is None:
                raise DatabaseConnectionError("Failed to create comment")
            return dict(row)
        finally:
            await self.db.release_connection(conn)

    async def list_comments(self, resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            rows = await conn.fetch(
                """
                SELECT id, resource_type, resource_id, user_id, content, reply_to_comment_id, created_at
                FROM comments
                WHERE resource_type=$1 AND resource_id=$2 AND deleted_at IS NULL
                ORDER BY created_at ASC
                """,
                resource_type, resource_id
            )
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def delete_comment(self, comment_id: str) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE comments SET deleted_at=now() WHERE id=$1 AND deleted_at IS NULL", comment_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)
