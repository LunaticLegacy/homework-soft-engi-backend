import psycopg2
from psycopg2 import pool

from typing import Any, Optional

class DBManager:
    def __init__(
        self,
        db_url: str,
        db_password: str,
        db_database_name: str,
        minconn: int = 1,
        maxconn: int = 10
    ):
        """
        初始化类。

        Args:
            db_url (str): 数据库服务器URL地址。
            db_password (str): 连接数据库服务器的密码。
            db_database_name(str): 访问到数据库服务器时，需要访问的数据库名。
        """
        # 初始化所有变量。
        self.db_url: str = db_url
        self.db_password: str = db_password
        self.db_database_name: str = db_database_name

        # 初始化连接池。
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None  # 先暂时不初始化
        self._init_connection_pool(minconn, maxconn)

        pass


    def _init_connection_pool(self, minconn: int, maxconn: int):
        """
        初始化数据库连接。该函数只会在__init__中调用。
        Args:
            minconn (int): 最小连接数。
            maxconn (int): 最大连接数。
        """
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=minconn,
                maxconn=maxconn,
                host=self.db_url,
                database=self.db_database_name,
                password=self.db_password
            )
        except Exception as e:
            raise ConnectionError(f"Initialization of SQL connection pool failed: {str(e)}")
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """
        从连接池获取连接。
        """
        if self.connection_pool is None:
            raise ConnectionError("连接池未初始化")
        return self.connection_pool.getconn()

    def release_connection(self, connection: psycopg2.extensions.connection):
        """
        释放连接回连接池。
        Args:
            connection (psycopg2.extensions.connection): 连接
        """
        if self.connection_pool is not None:
            self.connection_pool.putconn(connection)

    def close_all_connections(self):
        """
        关闭所有连接。
        """
        if self.connection_pool is not None:
            self.connection_pool.closeall()
            self.connection_pool = None

