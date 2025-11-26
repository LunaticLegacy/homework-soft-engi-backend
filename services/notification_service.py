from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager
from core.exceptions import DatabaseConnectionError

class NotificationService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_notification(self, user_id: str, level: str, title: str, body: str, data: Optional[dict], channel: str = "in_app") -> Dict[str, Any]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO notifications (user_id, level, title, body, data, channel)
                VALUES ($1,$2,$3,$4,$5,$6)
                RETURNING id, user_id, level, title, body, data, is_read, channel, created_at
                """,
                user_id, level, title, body, data or {}, channel
            )
            if row is None:
                raise DatabaseConnectionError("Failed to create notification")
            return dict(row)
        finally:
            await self.db.release_connection(conn)

    async def list_notifications(self, user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            query = "SELECT id, user_id, level, title, body, data, is_read, channel, created_at FROM notifications WHERE user_id=$1"
            params = [user_id]
            if unread_only:
                query += " AND is_read=FALSE"
            query += " ORDER BY created_at DESC"
            rows = await conn.fetch(query, *params)
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def mark_read(self, notification_id: str) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE notifications SET is_read=TRUE, delivered_at=now() WHERE id=$1", notification_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)
