from typing import Any, Dict, List, Optional
from modules.databaseman import DatabaseManager
from core.exceptions import DatabaseConnectionError

class AttachmentService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    async def create_attachment(self, owner_id: str, attached_to_type: str, attached_to_id: str, file_name: str, file_size: Optional[int], content_type: Optional[str], storage_key: str, attachment_type: str = "file", metadata: Optional[dict] = None) -> Dict[str, Any]:
        conn = await self.db.get_connection(5.0)
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO attachments (owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                RETURNING id, owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata, created_at
                """,
                owner_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata or {}
            )
            if row is None:
                raise DatabaseConnectionError("Failed to create attachment")
            return dict(row)
        finally:
            await self.db.release_connection(conn)

    async def list_attachments(self, attached_to_type: str, attached_to_id: str) -> List[Dict[str, Any]]:
        conn = await self.db.get_connection(5.0)
        try:
            rows = await conn.fetch(
                "SELECT id, owner_user_id, attached_to_type, attached_to_id, file_name, file_size, content_type, storage_key, attachment_type, metadata, created_at FROM attachments WHERE attached_to_type=$1 AND attached_to_id=$2 AND deleted_at IS NULL",
                attached_to_type, attached_to_id
            )
            return [dict(r) for r in rows]
        finally:
            await self.db.release_connection(conn)

    async def delete_attachment(self, attachment_id: str) -> bool:
        conn = await self.db.get_connection(5.0)
        try:
            result = await conn.execute("UPDATE attachments SET deleted_at=now() WHERE id=$1 AND deleted_at IS NULL", attachment_id)
            return result.startswith("UPDATE 1")
        finally:
            await self.db.release_connection(conn)
