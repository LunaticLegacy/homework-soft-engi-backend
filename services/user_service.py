from typing import Dict, List, Optional, Any
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError

class UserService:
    """用户服务类，处理用户相关的业务逻辑"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化用户服务
        
        Args:
            db_manager (DatabaseManager): 数据库管理器实例
        """
        self.db_manager = db_manager
    
    async def get_all_users(self) -> List[Dict[str, Any]]:
        """
        获取所有用户列表
        
        Returns:
            List[Dict[str, Any]]: 用户列表
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                rows = await conn.fetch(
                    "SELECT id, email, full_name, created_at FROM users"
                    )
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
        """
        根据用户ID获取用户信息
        
        Args:
            user_id (str): 用户ID
            
        Returns:
            Optional[Dict[str, Any]]: 用户信息，如果未找到则返回None
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    "SELECT id, email, full_name, display_name, created_at FROM users WHERE id = $1",
                    user_id
                )
                if row:
                    return dict(row)
                return None
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
    
    async def create_user(self, email: str, full_name: str, password_hash: str) -> Dict[str, Any]:
        """
        创建新用户
        
        Args:
            email (str): 用户邮箱
            full_name (str): 用户全名
            password_hash (str): 密码哈希值
            
        Returns:
            Dict[str, Any]: 新创建的用户信息
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO users (email, full_name, password_hash)
                    VALUES ($1, $2, $3)
                    RETURNING id, email, full_name, created_at
                    """,
                    email, full_name, password_hash
                )
                if row:
                    return dict(row)
                else:
                    raise DatabaseConnectionError("Failed to create user")
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
        