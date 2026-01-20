"""
数据库树形视图
显示数据库 -> 表 -> 字段的层级结构
"""

from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction

from src.core.connection import HiveConnection
from src.core.query_worker import MetadataWorker
from src.utils.paths import get_resource_path


class DatabaseTree(QTreeWidget):
    """数据库树形视图"""
    
    # 信号
    table_double_clicked = Signal(str, str)  # (database, table)
    generate_select = Signal(str, str)       # 生成 SELECT 语句
    
    # 节点类型
    TYPE_DATABASE = 0
    TYPE_TABLE = 1
    TYPE_COLUMN = 2
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection: HiveConnection = None
        self._workers = []
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        self.setHeaderLabel("数据库浏览器")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        
        # 设置样式
        self.setIndentation(20)
        self.setAnimated(True)
        
        # 加载图标
        self.icon_db = QIcon(get_resource_path("resources/icons/database.svg"))
        self.icon_table = QIcon(get_resource_path("resources/icons/table.svg"))
        self.icon_column = QIcon(get_resource_path("resources/icons/column.svg"))
    
    def set_connection(self, connection: HiveConnection):
        """设置连接"""
        self.connection = connection
        self.refresh()
    
    def clear_connection(self):
        """清除连接"""
        self.connection = None
        self.clear()
    
    def refresh(self):
        """刷新数据库列表"""
        self.clear()
        if not self.connection or not self.connection.is_connected:
            return
        
        # 异步加载数据库列表
        worker = MetadataWorker(self.connection, "databases")
        worker.databases_loaded.connect(self._on_databases_loaded)
        worker.error.connect(self._on_error)
        self._workers.append(worker)
        worker.start()
    
    def _on_databases_loaded(self, databases: list):
        """数据库列表加载完成"""
        self.clear()
        for db in databases:
            item = QTreeWidgetItem([db])
            item.setIcon(0, self.icon_db)
            item.setData(0, Qt.ItemDataRole.UserRole, self.TYPE_DATABASE)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, db)
            # 添加占位子项，使其可展开
            placeholder = QTreeWidgetItem(["加载中..."])
            item.addChild(placeholder)
            self.addTopLevelItem(item)
    
    def _on_item_expanded(self, item: QTreeWidgetItem):
        """展开节点时加载子项"""
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_type == self.TYPE_DATABASE:
            # 检查是否是占位符
            if item.childCount() == 1 and item.child(0).text(0) == "加载中...":
                database = item.data(0, Qt.ItemDataRole.UserRole + 1)
                self._load_tables(item, database)
        
        elif item_type == self.TYPE_TABLE:
            # 加载表结构
            if item.childCount() == 1 and item.child(0).text(0) == "加载中...":
                database = item.data(0, Qt.ItemDataRole.UserRole + 1)
                table = item.data(0, Qt.ItemDataRole.UserRole + 2)
                self._load_schema(item, database, table)
    
    def _load_tables(self, parent_item: QTreeWidgetItem, database: str):
        """加载表列表"""
        worker = MetadataWorker(self.connection, "tables", database=database)
        worker.tables_loaded.connect(lambda db, tables: self._on_tables_loaded(parent_item, db, tables))
        worker.error.connect(self._on_error)
        self._workers.append(worker)
        worker.start()
    
    def _on_tables_loaded(self, parent_item: QTreeWidgetItem, database: str, tables: list):
        """表列表加载完成"""
        # 移除占位符
        parent_item.takeChildren()
        
        for table in tables:
            item = QTreeWidgetItem([table])
            item.setIcon(0, self.icon_table)
            item.setData(0, Qt.ItemDataRole.UserRole, self.TYPE_TABLE)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, database)
            item.setData(0, Qt.ItemDataRole.UserRole + 2, table)
            # 添加占位子项
            placeholder = QTreeWidgetItem(["加载中..."])
            item.addChild(placeholder)
            parent_item.addChild(item)
    
    def _load_schema(self, parent_item: QTreeWidgetItem, database: str, table: str):
        """加载表结构"""
        worker = MetadataWorker(self.connection, "schema", database=database, table=table)
        worker.schema_loaded.connect(lambda db, tbl, schema: self._on_schema_loaded(parent_item, schema))
        worker.error.connect(self._on_error)
        self._workers.append(worker)
        worker.start()
    
    def _on_schema_loaded(self, parent_item: QTreeWidgetItem, schema: list):
        """表结构加载完成"""
        # 移除占位符
        parent_item.takeChildren()
        
        for col_name, col_type, col_comment in schema:
            display = f"{col_name} ({col_type})"
            if col_comment:
                display += f" -- {col_comment}"
            item = QTreeWidgetItem([display])
            item.setIcon(0, self.icon_column)
            item.setData(0, Qt.ItemDataRole.UserRole, self.TYPE_COLUMN)
            item.setData(0, Qt.ItemDataRole.UserRole + 1, col_name)
            parent_item.addChild(item)
    
    def _on_error(self, error: str):
        """错误处理"""
        QMessageBox.warning(self, "加载失败", error)
    
    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击节点"""
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        
        if item_type == self.TYPE_TABLE:
            database = item.data(0, Qt.ItemDataRole.UserRole + 1)
            table = item.data(0, Qt.ItemDataRole.UserRole + 2)
            self.table_double_clicked.emit(database, table)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.itemAt(pos)
        if not item:
            return
        
        item_type = item.data(0, Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        
        if item_type == self.TYPE_DATABASE:
            database = item.data(0, Qt.ItemDataRole.UserRole + 1)
            
            action = QAction(f"切换到 {database}", self)
            action.triggered.connect(lambda: self._use_database(database))
            menu.addAction(action)
            
            action = QAction("刷新", self)
            action.triggered.connect(lambda: self._refresh_database(item))
            menu.addAction(action)
        
        elif item_type == self.TYPE_TABLE:
            database = item.data(0, Qt.ItemDataRole.UserRole + 1)
            table = item.data(0, Qt.ItemDataRole.UserRole + 2)
            
            action = QAction("生成 SELECT 语句", self)
            action.triggered.connect(lambda: self.generate_select.emit(database, table))
            menu.addAction(action)
            
            action = QAction("查看表结构", self)
            action.triggered.connect(lambda: self._describe_table(database, table))
            menu.addAction(action)
        
        if menu.actions():
            menu.exec(self.mapToGlobal(pos))
    
    def _use_database(self, database: str):
        """切换数据库"""
        if self.connection:
            self.connection.use_database(database)
    
    def _refresh_database(self, item: QTreeWidgetItem):
        """刷新数据库"""
        item.takeChildren()
        placeholder = QTreeWidgetItem(["加载中..."])
        item.addChild(placeholder)
        database = item.data(0, Qt.ItemDataRole.UserRole + 1)
        self._load_tables(item, database)
    
    def _describe_table(self, database: str, table: str):
        """查看表结构 - 通过信号让主窗口执行"""
        self.table_double_clicked.emit(database, table)
