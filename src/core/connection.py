"""
Hive 连接管理模块
使用 impyla 连接 HiveServer2
"""

from typing import Optional, Any
from dataclasses import dataclass
from impala.dbapi import connect
from impala.error import HiveServer2Error

from src.utils.config import ConnectionConfig


@dataclass
class QueryResult:
    """查询结果"""
    columns: list[str]
    rows: list[tuple]
    row_count: int
    error: Optional[str] = None
    execution_time: float = 0.0
    
    @property
    def is_success(self) -> bool:
        return self.error is None


class HiveConnection:
    """Hive 连接类"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self._conn = None
        self._cursor = None
    
    @property
    def is_connected(self) -> bool:
        return self._conn is not None
    
    def connect(self) -> tuple[bool, str]:
        """
        建立连接
        返回: (成功与否, 错误信息)
        """
        try:
            auth = self.config.auth_mechanism
            
            # 根据认证方式设置参数
            connect_args = {
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
            }
            
            if auth == "NOSASL":
                connect_args["auth_mechanism"] = "NOSASL"
            elif auth in ("PLAIN", "LDAP"):
                connect_args["auth_mechanism"] = auth
                connect_args["user"] = self.config.username
                connect_args["password"] = self.config.password
            
            self._conn = connect(**connect_args)
            self._cursor = self._conn.cursor()
            return True, ""
        except Exception as e:
            self._conn = None
            self._cursor = None
            return False, str(e)
    
    def disconnect(self):
        """断开连接"""
        if self._cursor:
            try:
                self._cursor.close()
            except:
                pass
            self._cursor = None
        if self._conn:
            try:
                self._conn.close()
            except:
                pass
            self._conn = None
    
    def is_connection_alive(self) -> bool:
        """检查连接是否仍然活跃"""
        if not self._conn or not self._cursor:
            return False
        
        try:
            # 通过执行简单查询来检测连接
            self._cursor.execute("SELECT 1")
            self._cursor.fetchall()  # 消耗结果
            return True
        except Exception:
            return False
    
    def ensure_connection(self) -> tuple[bool, str]:
        """确保连接可用，如果断开则自动重连
        返回: (成功与否, 错误信息)
        """
        if self.is_connection_alive():
            return True, ""
        
        # 连接已断开，尝试重连
        return self.connect()
    
    def execute(self, sql: str) -> QueryResult:
        """执行 SQL 查询"""
        # 确保连接可用
        if not self.is_connected:
            return QueryResult([], [], 0, "未连接到数据库")
        
        # 检查连接是否仍然活跃，如果不活跃则尝试重连
        success, error = self.ensure_connection()
        if not success:
            return QueryResult([], [], 0, f"连接已断开且重连失败: {error}")
        
        try:
            self._cursor.execute(sql)
            
            # 检查是否有结果集
            if self._cursor.description is None:
                return QueryResult([], [], 0)
            
            # 尝试获取结果
            try:
                columns = [desc[0] for desc in self._cursor.description]
                rows = self._cursor.fetchall()
                return QueryResult(columns, rows, len(rows))
            except Exception:
                # 某些情况下 description 非空但 fetch 失败（罕见，但也处理一下）
                return QueryResult([], [], 0)
                
        except Exception as e:
            # 过滤掉 "no results" 错误（如果是误报）
            # 但通常 description is None 就能避免
            return QueryResult([], [], 0, str(e))
    
    def get_databases(self) -> list[str]:
        """获取所有数据库"""
        result = self.execute("SHOW DATABASES")
        if result.is_success:
            return [row[0] for row in result.rows]
        return []
    
    def get_tables(self, database: str = None) -> list[str]:
        """获取指定数据库的所有表"""
        if database:
            sql = f"SHOW TABLES IN {database}"
        else:
            sql = "SHOW TABLES"
        result = self.execute(sql)
        if result.is_success:
            return [row[0] for row in result.rows]
        return []
    
    def get_table_schema(self, table: str, database: str = None) -> list[tuple[str, str, str]]:
        """
        获取表结构
        返回: [(列名, 类型, 注释), ...]
        """
        if database:
            sql = f"DESCRIBE {database}.{table}"
        else:
            sql = f"DESCRIBE {table}"
        result = self.execute(sql)
        if result.is_success:
            schema = []
            for row in result.rows:
                # 跳过分区信息等额外行
                if row[0] and not row[0].startswith('#'):
                    col_name = row[0].strip()
                    col_type = row[1].strip() if len(row) > 1 and row[1] else ""
                    col_comment = row[2].strip() if len(row) > 2 and row[2] else ""
                    if col_name:
                        schema.append((col_name, col_type, col_comment))
            return schema
        return []
    
    def use_database(self, database: str) -> bool:
        """切换数据库"""
        result = self.execute(f"USE {database}")
        return result.is_success
