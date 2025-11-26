from typing import Dict, List, Optional, Any
from modules.databaseman import DatabaseManager, DBTimeoutError
from core.exceptions import DatabaseConnectionError, DatabaseTimeoutError, ResourceNotFoundError

class WorkspaceService:
    """工作空间服务类，处理工作空间相关的业务逻辑"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化工作空间服务
        
        Args:
            db_manager (DatabaseManager): 数据库管理器实例
        """
        self.db_manager = db_manager
    
    async def create_workspace(self, name: str, description: Optional[str], owner_user_id: str) -> Dict[str, Any]:
        """
        创建新工作空间
        
        Args:
            name (str): 工作空间名称
            description (Optional[str]): 工作空间描述
            owner_user_id (str): 所有者用户ID
            
        Returns:
            Dict[str, Any]: 新创建的工作空间信息
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    """
                    INSERT INTO workspaces (name, description, owner_user_id)
                    VALUES ($1, $2, $3)
                    RETURNING id, name, description, owner_user_id, created_at
                    """,
                    name, description, owner_user_id
                )
                if row:
                    return dict(row)
                else:
                    raise DatabaseConnectionError("Failed to create workspace")
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")
    
    async def get_all_workspaces(self) -> List[Dict[str, Any]]:
        """
        获取所有工作空间列表
        
        Returns:
            List[Dict[str, Any]]: 工作空间列表
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                rows = await conn.fetch(
                    "SELECT id, name, description, owner_user_id, created_at FROM workspaces WHERE deleted_at IS NULL"
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
    
    async def get_workspace_by_id(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        根据ID获取工作空间信息
        
        Args:
            workspace_id (str): 工作空间ID
            
        Returns:
            Optional[Dict[str, Any]]: 工作空间信息，如果未找到则返回None
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                row = await conn.fetchrow(
                    "SELECT id, name, description, owner_user_id, created_at, updated_at FROM workspaces WHERE id = $1 AND deleted_at IS NULL",
                    workspace_id
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
    
    async def update_workspace(self, workspace_id: str, name: Optional[str], description: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        更新工作空间信息
        
        Args:
            workspace_id (str): 工作空间ID
            name (Optional[str]): 工作空间名称
            description (Optional[str]): 工作空间描述
            
        Returns:
            Optional[Dict[str, Any]]: 更新后的工作空间信息，如果未找到则返回None
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                # 构建更新语句
                update_fields = []
                params = [workspace_id]
                if name is not None:
                    update_fields.append(f"name = ${len(params)+1}")
                    params.append(name)
                if description is not None:
                    update_fields.append(f"description = ${len(params)+1}")
                    params.append(description)
                
                if update_fields:
                    update_fields.append(f"updated_at = ${len(params)+1}")
                    params.append("now()")
                    
                    update_query = f"""
                        UPDATE workspaces 
                        SET {', '.join(update_fields)}
                        WHERE id = $1 AND deleted_at IS NULL
                        RETURNING id, name, description, owner_user_id, created_at, updated_at
                    """
                    
                    row = await conn.fetchrow(update_query, *params)
                    if row:
                        return dict(row)
                else:
                    # 如果没有要更新的字段，直接返回当前工作空间信息
                    row = await conn.fetchrow(
                        "SELECT id, name, description, owner_user_id, created_at, updated_at FROM workspaces WHERE id = $1 AND deleted_at IS NULL",
                        workspace_id
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
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """
        删除工作空间（软删除）
        
        Args:
            workspace_id (str): 工作空间ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            DatabaseConnectionError: 数据库连接失败
            DatabaseTimeoutError: 数据库操作超时
        """
        try:
            conn = await self.db_manager.get_connection(5.0)
            try:
                result = await conn.execute(
                    """
                    UPDATE workspaces 
                    SET deleted_at = now()
                    WHERE id = $1 AND deleted_at IS NULL
                    """,
                    workspace_id
                )
                # 检查是否实际删除了记录
                if result.startswith("UPDATE 1"):
                    return True
                return False
            finally:
                await self.db_manager.release_connection(conn)
        except ConnectionError as e:
            raise DatabaseConnectionError(f"Failed to connect to database: {str(e)}")
        except DBTimeoutError as e:
            raise DatabaseTimeoutError(f"Database operation timed out: {str(e)}")
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected error: {str(e)}")