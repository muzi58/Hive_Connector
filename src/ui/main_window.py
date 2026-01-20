"""
主窗口
HiveLight 应用的主界面 (Navicat 风格)
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QStatusBar, QMessageBox,
    QMenu, QMenuBar, QComboBox, QLabel, QStackedWidget,
    QPushButton, QTabWidget, QInputDialog, QLineEdit
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence, QIcon
from typing import Optional
import os
from src.utils.paths import get_resource_path

from src.ui.connection_dialog import ConnectionDialog
from src.ui.connection_list import ConnectionList
from src.ui.database_tree import DatabaseTree
from src.ui.query_editor import QueryEditor
from src.core.connection import HiveConnection
from src.utils.config import config_manager, ConnectionConfig


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.connection: HiveConnection = None
        self._init_ui()
        self._init_menu()
    
    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("HiveLight")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 移除之前的样式表设置，使用全局 style.qss
        
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1) # 分割线宽度
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
            }
        """)
        
        # 左侧边栏：使用 StackedWidget 提供连接列表/数据库树视图
        self.left_sidebar = QStackedWidget()
        self.left_sidebar.setMinimumWidth(250)
        self.left_sidebar.setMaximumWidth(400)
        self.left_sidebar.setStyleSheet("background-color: #FAFAFA;")
        
        # 页面 0: 连接列表
        self.conn_list = ConnectionList()
        self.conn_list.new_connection_requested.connect(self._new_connection)
        self.conn_list.connection_double_clicked.connect(self._connect_to)
        self.conn_list.connection_selected.connect(self._on_connection_selected)
        self.conn_list.edit_connection_requested.connect(self._edit_connection)
        self.conn_list.delete_connection_requested.connect(self._delete_connection)
        self.left_sidebar.addWidget(self.conn_list)
        
        # 页面 1: 数据库树
        db_widget = QWidget()
        db_layout = QVBoxLayout(db_widget)
        db_layout.setContentsMargins(0, 0, 0, 0)
        db_layout.setSpacing(0)
        
        # 顶部返回栏
        back_bar = QWidget()
        back_bar.setStyleSheet("background: #F0F0F0; border-bottom: 1px solid #E0E0E0;")
        back_layout = QHBoxLayout(back_bar)
        back_layout.setContentsMargins(8, 4, 8, 4)
        
        back_btn = QPushButton("⬅ 返回列表")
        back_btn.setFlat(True)
        back_btn.setStyleSheet("""
            QPushButton {
                text-align: left; 
                font-weight: bold; 
                color: #555;
                font-size: 13px;
                background: transparent;
                border: none;
            }
            QPushButton:hover { color: #007AFF; }
        """)
        back_btn.clicked.connect(self._disconnect)
        back_layout.addWidget(back_btn)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFlat(True)
        refresh_btn.setToolTip("刷新数据库")
        refresh_btn.clicked.connect(self._refresh_tree)
        back_layout.addWidget(refresh_btn)
        
        db_layout.addWidget(back_bar)
        
        self.db_tree = DatabaseTree()
        self.db_tree.table_double_clicked.connect(self._on_table_double_clicked)
        self.db_tree.generate_select.connect(self._generate_select)
        db_layout.addWidget(self.db_tree)
        
        self.left_sidebar.addWidget(db_widget)
        
        splitter.addWidget(self.left_sidebar)
        
        # 右侧：查询编辑器
        self.query_tabs = QTabWidget()
        self.query_tabs.setTabsClosable(True)
        self.query_tabs.setDocumentMode(True)
        self.query_tabs.setMovable(True)
        self.query_tabs.setElideMode(Qt.TextElideMode.ElideRight)
        self.query_tabs.tabCloseRequested.connect(self._close_query_tab)
        # 启用右键菜单
        self.query_tabs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.query_tabs.customContextMenuRequested.connect(self._show_tab_context_menu)
        # 动态获取关闭按钮图标路径
        close_icon_path = get_resource_path("resources/icons/chevron-right-dark.svg")
        self.query_tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; background: white; }}
            QTabBar::tab {{ 
                background: #F1F3F5; 
                border: 1px solid #DEE2E6; 
                border-bottom: none;
                padding: 6px 12px; 
                min-width: 80px;
                max-width: 200px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
                color: #495057;
            }}
            QTabBar::tab:selected {{ 
                background: white; 
                border-bottom: 2px solid #339AF0;
                color: #212529;
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{ background: #E9ECEF; }}
            QTabBar::close-button {{
                subcontrol-position: right;
                image: url({close_icon_path}); /* 动态自适应路径 */
                width: 12px;
                height: 12px;
            }}
            QTabBar::close-button:hover {{
                background: #FF4D4F;
                border-radius: 2px;
            }}
        """)
        splitter.addWidget(self.query_tabs)
        
        splitter.setSizes([280, 920])
        layout.addWidget(splitter)
        
        # 工具栏 (移到最后创建，以确保组件已存在)
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #F8F9FA;
                border-bottom: 1px solid #DEE2E6;
                spacing: 20px;
                padding: 10px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                color: #444;
                font-size: 11px;
                font-weight: 500;
            }
            QToolButton:hover {
                background: #E9ECEF;
            }
            QToolButton:pressed {
                background: #DEE2E6;
            }
        """)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # 连接动作
        self.connect_action = QAction(" 连接", self)
        self.connect_action.setIcon(QIcon(get_resource_path("resources/icons/database.svg")))
        self.connect_action.triggered.connect(self._toggle_connection)
        self.connect_action.setEnabled(False) # 初始禁用，直到选择连接
        toolbar.addAction(self.connect_action)
        
        # 新建连接
        new_conn_action = QAction(" 新建连接", self)
        new_conn_action.setIcon(QIcon(get_resource_path("resources/icons/database.svg")))
        new_conn_action.triggered.connect(self._new_connection)
        toolbar.addAction(new_conn_action)
        
        toolbar.addSeparator()
        
        # 查询动作
        query_action = QAction(" 新建查询", self)
        query_action.setIcon(QIcon(get_resource_path("resources/icons/table.svg")))
        query_action.triggered.connect(lambda: self._new_query_tab())
        toolbar.addAction(query_action)
        
        # 加载持久化的查询内容
        self._load_pending_queries()
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def _load_pending_queries(self):
        """从配置加载查询内容"""
        queries = config_manager.config.open_queries
        if not queries:
            queries = [""]
        
        for content in queries:
            self._new_query_tab(content, skip_dialog=True)

    def _new_query_tab(self, content: str = "", name: str = None, skip_dialog: bool = False):
        """新建查询标签页"""
        if not isinstance(content, str):
            content = ""
            
        # 确定标签名称
        if name is None:
            if skip_dialog:
                name = f"查询 {self.query_tabs.count() + 1}"
            else:
                # 只有在手动创建（skip_dialog=False）时才弹出对话框
                default_name = f"查询 {self.query_tabs.count() + 1}"
                text, ok = QInputDialog.getText(
                    self, "新建查询", "请输入查询名称:", 
                    QLineEdit.EchoMode.Normal, default_name
                )
                if ok:
                    name = text.strip() or default_name
                else:
                    return None # 用户取消

        editor = QueryEditor()
        editor.set_sql(content)
        if self.connection:
            editor.set_connection(self.connection)
        
        self.query_tabs.addTab(editor, name)
        self.query_tabs.setCurrentWidget(editor)
        return editor

    def _show_tab_context_menu(self, pos):
        """显示标签页右键菜单"""
        index = self.query_tabs.tabBar().tabAt(pos)
        if index == -1:
            return
            
        menu = QMenu(self)
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self._rename_tab(index))
        menu.addAction(rename_action)
        
        close_action = QAction("关闭", self)
        close_action.triggered.connect(lambda: self._close_query_tab(index))
        menu.addAction(close_action)
        
        menu.exec(self.query_tabs.mapToGlobal(pos))

    def _rename_tab(self, index: int):
        """重命名指定标签页"""
        old_name = self.query_tabs.tabText(index)
        text, ok = QInputDialog.getText(
            self, "重命名标签", "请输入新名称:", 
            QLineEdit.EchoMode.Normal, old_name
        )
        if ok and text:
            self.query_tabs.setTabText(index, text)

    def _close_query_tab(self, index: int):
        """关闭标签页"""
        if self.query_tabs.count() > 1:
            widget = self.query_tabs.widget(index)
            self.query_tabs.removeTab(index)
            widget.deleteLater()
        else:
            # 最后一个标签页不关闭，清空内容
            self.query_tabs.currentWidget().set_sql("")
    
    def _save_all_queries(self):
        """保存所有标签页内容"""
        queries = []
        for i in range(self.query_tabs.count()):
            editor = self.query_tabs.widget(i)
            if isinstance(editor, QueryEditor):
                queries.append(editor.editor.toPlainText())
        
        config_manager.config.open_queries = queries
        config_manager.save()

    def _get_current_editor(self) -> Optional[QueryEditor]:
        """获取当前活动的编辑器"""
        widget = self.query_tabs.currentWidget()
        if isinstance(widget, QueryEditor):
            return widget
        return None


    def _execute_current(self):
        """执行当前编辑器的查询"""
        editor = self._get_current_editor()
        if editor:
            editor.execute_query()

    def _clear_current(self):
        """清空当前编辑器内容并重置连接"""
        editor = self._get_current_editor()
        if editor:
            editor.set_sql("")
    
    def _init_menu(self):
        """初始化菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        new_conn_action = QAction("新建连接...", self)
        new_conn_action.setShortcut(QKeySequence.StandardKey.New)
        new_conn_action.triggered.connect(self._new_connection)
        file_menu.addAction(new_conn_action)
        
        new_query_action = QAction("新建查询", self)
        new_query_action.setShortcut(QKeySequence("Cmd+T"))
        new_query_action.triggered.connect(lambda: self._new_query_tab())
        file_menu.addAction(new_query_action)
        
        quit_action = QAction("退出", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        toggle_sidebar = QAction("显示/隐藏侧边栏", self)
        toggle_sidebar.triggered.connect(lambda: self.left_sidebar.setVisible(not self.left_sidebar.isVisible()))
        view_menu.addAction(toggle_sidebar)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于 HiveLight", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _on_connection_selected(self, config: ConnectionConfig):
        """连接选择变化"""
        self.connect_action.setEnabled(True)
    
    def _connect_to(self, config: ConnectionConfig):
        """连接到指定配置"""
        if self.connection and self.connection.is_connected:
            self.connection.disconnect()
        
        self.statusBar().showMessage(f"正在连接到 {config.host}:{config.port}...")
        
        self.connection = HiveConnection(config)
        success, error = self.connection.connect()
        
        if success:
            self.statusBar().showMessage(f"已连接到 {config.host}:{config.port}")
            self.connect_action.setText("🔌 断开")
            try:
                self.connect_action.triggered.disconnect()
            except Exception:
                pass
            self.connect_action.triggered.connect(self._disconnect)
            
            # 切换左侧视图
            self.left_sidebar.setCurrentIndex(1)
            self.db_tree.set_connection(self.connection)
            
            # 更新所有标签页的连接对象
            for i in range(self.query_tabs.count()):
                editor = self.query_tabs.widget(i)
                if isinstance(editor, QueryEditor):
                    editor.set_connection(self.connection)
                    
            self.conn_list.set_connection_status(config, True)
            
            # 保存最后使用的连接
            config_manager.config.last_connection = config.name
            config_manager.save()
        else:
            self.connection = None
            self.statusBar().showMessage("连接失败")
            QMessageBox.critical(self, "连接失败", f"无法连接到服务器:\n{error}")
    
    def _toggle_connection(self):
        """切换连接状态"""
        if self.connection and self.connection.is_connected:
            self._disconnect()
        else:
            config = self.conn_list.get_selected_connection()
            if config:
                self._connect_to(config)
    
    def _disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.disconnect()
            # 更新状态列表中的图标
            self.conn_list.set_connection_status(self.connection.config, False)
            self.connection = None
        
        self.connect_action.setText("🔌 连接")
        try:
            self.connect_action.triggered.disconnect()
        except Exception:
            pass
        self.connect_action.triggered.connect(self._toggle_connection)
        
        self.db_tree.clear_connection()
        
        # 更新所有标签页的状态
        for i in range(self.query_tabs.count()):
            editor = self.query_tabs.widget(i)
            if isinstance(editor, QueryEditor):
                editor.set_connection(None)
        
        # 切换回列表视图
        self.left_sidebar.setCurrentIndex(0)
        self.statusBar().showMessage("已断开连接")
    
    def _refresh_tree(self):
        """刷新数据库树"""
        self.db_tree.refresh()
    
    def _new_connection(self):
        """新建连接"""
        dialog = ConnectionDialog(self)
        if dialog.exec() and dialog.result_config:
            config_manager.add_connection(dialog.result_config)
            self.conn_list.refresh()
    
    def _edit_connection(self, config: ConnectionConfig):
        """编辑连接"""
        dialog = ConnectionDialog(self, config)
        if dialog.exec() and dialog.result_config:
            config_manager.add_connection(dialog.result_config)
            self.conn_list.refresh()
            
    def _delete_connection(self, config: ConnectionConfig):
        """删除连接"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除连接 '{config.name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.connection and self.connection.config.name == config.name:
                self._disconnect()
            config_manager.remove_connection(config.name)
            self.conn_list.refresh()
    
    def _on_table_double_clicked(self, database: str, table: str):
        """双击表"""
        sql = f"SELECT * FROM {database}.{table} LIMIT 100"
        editor = self._get_current_editor()
        if not editor:
            editor = self._new_query_tab(name=f"Select {table}", skip_dialog=True)
        editor.set_sql(sql)
    
    def _generate_select(self, database: str, table: str):
        """生成 SELECT 语句"""
        if not self.connection:
            return
        
        schema = self.connection.get_table_schema(table, database)
        columns = [col[0] for col in schema]
        
        if columns:
            cols_str = ",\n    ".join(columns)
            sql = f"SELECT\n    {cols_str}\nFROM {database}.{table}\nLIMIT 100"
        else:
            sql = f"SELECT * FROM {database}.{table} LIMIT 100"
        
        editor = self._get_current_editor()
        if not editor:
            editor = self._new_query_tab(name=f"SQL {table}", skip_dialog=True)
        editor.set_sql(sql)
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 HiveLight",
            "<h2>HiveLight</h2>"
            "<p>轻量级 Hive 数据库客户端 (Navicat 风格)</p>"
            "<p>版本: 1.1.0</p>"
            "<p>专为 macOS 设计</p>"
        )
    
    def closeEvent(self, event):
        """关闭事件：保存查询内容并断开连接"""
        self._save_all_queries()
        if self.connection:
            self._disconnect()
        event.accept()

