"""
查询工作线程
在后台执行 SQL 查询，避免阻塞 UI
"""

from PySide6.QtCore import QThread, Signal

from src.core.connection import HiveConnection, QueryResult


class QueryWorker(QThread):
    """查询工作线程"""
    
    # 信号
    finished = Signal(QueryResult)  # 查询完成
    progress = Signal(str)          # 进度信息
    
    def __init__(self, connection: HiveConnection, sql: str):
        super().__init__()
        self.connection = connection
        self.sql = sql
        self._cancelled = False
    
    def run(self):
        """执行查询"""
        import time
        self.progress.emit("正在执行查询...")
        
        start_time = time.time()
        result = self.connection.execute(self.sql)
        end_time = time.time()
        
        result.execution_time = end_time - start_time
        
        if not self._cancelled:
            self.finished.emit(result)
    
    def cancel(self):
        """取消查询"""
        self._cancelled = True
        # 注意：impyla 不支持真正的取消，只能标记
        self.terminate()


class MetadataWorker(QThread):
    """元数据加载工作线程"""
    
    # 信号
    databases_loaded = Signal(list)  # 数据库列表加载完成
    tables_loaded = Signal(str, list)  # 表列表加载完成 (database, tables)
    schema_loaded = Signal(str, str, list)  # 表结构加载完成 (database, table, schema)
    error = Signal(str)  # 错误
    
    def __init__(self, connection: HiveConnection, task: str, **kwargs):
        super().__init__()
        self.connection = connection
        self.task = task
        self.kwargs = kwargs
    
    def run(self):
        """执行任务"""
        try:
            if self.task == "databases":
                databases = self.connection.get_databases()
                self.databases_loaded.emit(databases)
            
            elif self.task == "tables":
                database = self.kwargs.get("database")
                tables = self.connection.get_tables(database)
                self.tables_loaded.emit(database, tables)
            
            elif self.task == "schema":
                database = self.kwargs.get("database")
                table = self.kwargs.get("table")
                schema = self.connection.get_table_schema(table, database)
                self.schema_loaded.emit(database, table, schema)
                
        except Exception as e:
            self.error.emit(str(e))
