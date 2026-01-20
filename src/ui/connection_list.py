"""
连接列表组件
仿 Navicat 左侧连接面板
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QMenu, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction, QFont

from src.utils.config import config_manager, ConnectionConfig


class ConnectionListItem(QListWidgetItem):
    """连接列表项"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(f"📊 {config.name}")
        self.config = config
        self.is_connected = False
        
        # 设置字体
        font = QFont()
        font.setPointSize(13)
        self.setFont(font)
        
        # 添加提示信息
        self.setToolTip(f"{config.host}:{config.port}\n数据库: {config.database}")
    
    def set_connected(self, connected: bool):
        """设置连接状态"""
        self.is_connected = connected
        if connected:
            self.setText(f"🟢 {self.config.name}")
        else:
            self.setText(f"📊 {self.config.name}")


class ConnectionList(QWidget):
    """连接列表面板"""
    
    # 信号
    connection_selected = Signal(ConnectionConfig)
    connection_double_clicked = Signal(ConnectionConfig)
    new_connection_requested = Signal()
    edit_connection_requested = Signal(ConnectionConfig)
    delete_connection_requested = Signal(ConnectionConfig)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._load_connections()
    
    def _init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 标题和新建按钮
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # 新建连接按钮
        self.new_btn = QPushButton("+ 新建连接")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:pressed {
                background-color: #004FC4;
            }
        """)
        self.new_btn.clicked.connect(self.new_connection_requested.emit)
        header_layout.addWidget(self.new_btn)
        
        layout.addLayout(header_layout)
        
        # 连接列表
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        layout.addWidget(self.list_widget)
    
    def _load_connections(self):
        """加载连接列表"""
        self.list_widget.clear()
        for conn in config_manager.config.connections:
            item = ConnectionListItem(conn)
            self.list_widget.addItem(item)
    
    def refresh(self):
        """刷新列表"""
        self._load_connections()
    
    def _on_item_clicked(self, item: ConnectionListItem):
        """点击项"""
        self.connection_selected.emit(item.config)
    
    def _on_item_double_clicked(self, item: ConnectionListItem):
        """双击项"""
        self.connection_double_clicked.emit(item.config)
    
    def _show_context_menu(self, pos):
        """显示右键菜单"""
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
        """)
        
        connect_action = QAction("连接", self)
        connect_action.triggered.connect(lambda: self.connection_double_clicked.emit(item.config))
        menu.addAction(connect_action)
        
        menu.addSeparator()
        
        edit_action = QAction("编辑...", self)
        edit_action.triggered.connect(lambda: self.edit_connection_requested.emit(item.config))
        menu.addAction(edit_action)
        
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self.delete_connection_requested.emit(item.config))
        menu.addAction(delete_action)
        
        menu.exec(self.list_widget.mapToGlobal(pos))
    
    def set_connection_status(self, config: ConnectionConfig, connected: bool):
        """设置连接状态"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if isinstance(item, ConnectionListItem) and item.config.name == config.name:
                item.set_connected(connected)
                break
    
    def get_selected_connection(self) -> ConnectionConfig:
        """获取选中的连接"""
        item = self.list_widget.currentItem()
        if isinstance(item, ConnectionListItem):
            return item.config
        return None
