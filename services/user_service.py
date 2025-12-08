from typing import Dict, List, Optional, Any
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError


class UserService:
    """用户服务类，处理用户相关的业务逻辑"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def get_all_users(self) -> List[Dict[str, Any]]:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                rows = await conn.fetch("SELECT id, email, full_name, created_at FROM users")
                return [dict(row) for row in rows]
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    "SELECT id, email, full_name, display_name, created_at FROM users WHERE id = $1",
                    user_id,
                )
                return dict(row) if row else None
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    "SELECT id, email, full_name, password_hash, display_name, created_at FROM users WHERE email = $1",
                    email,
                )
                return dict(row) if row else None
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")

    async def create_user(self, email: str, full_name: str, password_hash: str) -> Dict[str, Any]:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO users (email, full_name, password_hash)
                    VALUES ($1, $2, $3)
                    RETURNING id, email, full_name, created_at
                    """,
                    email,
                    full_name,
                    password_hash
                )
                if not row:
                    raise DatabaseConnectionError("Failed to create user")

                await conn.execute(
                    "INSERT INTO user_profiles (user_id) VALUES ($1)",
                    row["id"],
                )
                return dict(row)
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")

    async def update_user_profile(self, user_id: str, full_name: Optional[str], display_name: Optional[str]) -> Optional[Dict[str, Any]]:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                update_fields = []
                params = [user_id]
                if full_name is not None:
                    update_fields.append(f"full_name = ${len(params)+1}")
                    params.append(full_name)
                if display_name is not None:
                    update_fields.append(f"display_name = ${len(params)+1}")
                    params.append(display_name)

                if update_fields:
                    update_fields.append(f"updated_at = now()")
                    update_query = f"""
                        UPDATE users
                        SET {', '.join(update_fields)}
                        WHERE id = $1
                        RETURNING id, email, full_name, display_name, created_at, updated_at
                    """
                    row = await conn.fetchrow(update_query, *params)
                    return dict(row) if row else None
                else:
                    row = await conn.fetchrow(
                        "SELECT id, email, full_name, display_name, created_at, updated_at FROM users WHERE id = $1",
                        user_id,
                    )
                    return dict(row) if row else None
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")

    async def delete_user(self, user_id: str) -> bool:
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                result = await conn.execute(
                    """
                    UPDATE users
                    SET deleted_at = now()
                    WHERE id = $1 AND deleted_at IS NULL
                    """,
                    user_id,
                )
                return result.startswith("UPDATE 1")
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
