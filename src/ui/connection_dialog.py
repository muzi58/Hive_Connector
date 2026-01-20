"""
连接管理对话框
Navicat 风格
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QPushButton,
    QLabel, QMessageBox, QTabWidget, QWidget,
    QCheckBox, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QColor

from src.utils.config import ConnectionConfig


class ConnectionDialog(QDialog):
    """Navicat 风格连接配置对话框"""
    
    def __init__(self, parent=None, config: ConnectionConfig = None):
        super().__init__(parent)
        self.config = config
        self.result_config = None
        self._init_ui()
        
        if config:
            self._load_config(config)
    
    def _init_ui(self):
        """初始化界面 (DBeaver 风格)"""
        self.setWindowTitle("连接到数据库" if not self.config else f"编辑连接 - {self.config.name}")
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. 专业头部 (DBeaver 风格)
        header_widget = QWidget()
        header_widget.setFixedHeight(85)
        header_widget.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F8F9FA); 
                border-bottom: 1px solid #E0E0E0; 
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(25, 12, 25, 12)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        main_title = QLabel("通用 Hive 连接设置")
        main_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; border: none; background: transparent;")
        sub_title = QLabel("Hadoop / Apache Hive 2 连接设置")
        sub_title.setStyleSheet("font-size: 12px; color: #777; border: none; background: transparent;")
        text_layout.addWidget(main_title)
        text_layout.addWidget(sub_title)
        header_layout.addLayout(text_layout)
        
        header_layout.addStretch()
        
        icon_label = QLabel("🐘")
        icon_label.setStyleSheet("font-size: 42px; background: transparent; border: none;")
        header_layout.addWidget(icon_label)
        
        main_layout.addWidget(header_widget)
        
        # 2. 内容区域
        content_container = QWidget()
        content_container.setStyleSheet("background-color: #FFFFFF;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(25, 20, 25, 20)
        content_layout.setSpacing(18)
        
        # 连接名称 - 更加精致的布局
        name_group = QWidget()
        name_group_layout = QHBoxLayout(name_group)
        name_group_layout.setContentsMargins(0, 0, 0, 0)
        name_group_layout.setSpacing(12)
        
        name_title = QLabel("连接名称:")
        name_title.setStyleSheet("font-weight: 600; color: #444;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: Hive_Production")
        self.name_edit.setFixedHeight(30)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 0 10px;
                background: #FFFFFF;
            }
            QLineEdit:focus { border-color: #4DABF7; }
        """)
        name_group_layout.addWidget(name_title)
        name_group_layout.addWidget(self.name_edit)
        content_layout.addWidget(name_group)
        
        # 标签页配置
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #DEE2E6; top: -1px; background: #FFFFFF; }
            QTabBar { background: #F8F9FA; border-bottom: 1px solid #DEE2E6; }
            QTabBar::tab { 
                background: #F1F3F5; 
                border: 1px solid #DEE2E6; 
                border-bottom: none;
                padding: 8px 20px; 
                min-width: 80px;
                font-size: 12px;
                color: #666;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { 
                background: #FFFFFF; 
                border-bottom: 1px solid #FFFFFF;
                color: #339AF0;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background: #E9ECEF; }
        """)
        
        # 主要标签页
        general_tab = QWidget()
        self._init_general_tab(general_tab)
        self.tab_widget.addTab(general_tab, "主要")
        
        # 驱动属性标签页
        driver_tab = QWidget()
        driver_layout = QVBoxLayout(driver_tab)
        driver_layout.addWidget(QLabel("驱动属性（默认）"))
        driver_layout.addStretch()
        self.tab_widget.addTab(driver_tab, "驱动属性")
        
        # SSH 标签页
        ssh_tab = QWidget()
        ssh_layout = QVBoxLayout(ssh_tab)
        ssh_layout.addWidget(QLabel("SSH 通道配置（暂未实现）"))
        ssh_layout.addStretch()
        self.tab_widget.addTab(ssh_tab, "SSH")
        
        content_layout.addWidget(self.tab_widget)
        main_layout.addWidget(content_container)
        
        # 3. 底部按钮区 (DBeaver 布局: 测试左，取消/完成右)
        footer_widget = QWidget()
        footer_widget.setFixedHeight(50)
        footer_widget.setStyleSheet("background: #F8F9FA; border-top: 1px solid #DEE2E6;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(15, 0, 15, 0)
        
        self.test_btn = QPushButton("测试连接(T)...")
        self.test_btn.clicked.connect(self._test_connection)
        self.test_btn.setFixedWidth(120)
        footer_layout.addWidget(self.test_btn)
        
        footer_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setFixedWidth(90)
        footer_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("完成(F)")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._save)
        self.save_btn.setFixedWidth(100)
        self.save_btn.setStyleSheet("""
            QPushButton { background-color: #228BE6; color: white; font-weight: bold; border: none; }
            QPushButton:hover { background-color: #1C7ED6; }
        """)
        footer_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(footer_widget)
        

    def _init_general_tab(self, parent: QWidget):
        """初始化主要标签页（精细化分组布局）"""
        v_layout = QVBoxLayout(parent)
        v_layout.setContentsMargins(20, 20, 20, 20)
        v_layout.setSpacing(20)
        
        group_style = """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #FAFCFE;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
                color: #228BE6;
            }
        """
        
        # --- 常规分组 ---
        group_common = QGroupBox("网络/常规")
        group_common.setStyleSheet(group_style)
        common_layout = QFormLayout(group_common)
        common_layout.setContentsMargins(15, 20, 40, 20)
        common_layout.setSpacing(15)
        common_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        common_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("localhost")
        common_layout.addRow("主机:", self.host_edit)
        
        port_layout = QHBoxLayout()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(10000)
        self.port_spin.setFixedWidth(110)
        port_layout.addWidget(self.port_spin)
        port_layout.addStretch()
        common_layout.addRow("端口:", port_layout)
        
        self.database_edit = QLineEdit()
        self.database_edit.setText("default")
        common_layout.addRow("数据库/模式:", self.database_edit)
        
        v_layout.addWidget(group_common)
        
        # --- 认证分组 ---
        group_auth = QGroupBox("安全/认证")
        group_auth.setStyleSheet(group_style)
        auth_layout = QFormLayout(group_auth)
        auth_layout.setContentsMargins(15, 20, 40, 20)
        auth_layout.setSpacing(15)
        auth_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.auth_combo = QComboBox()
        self.auth_combo.addItems(["NOSASL (无认证)", "PLAIN (用户名/密码)", "LDAP"])
        self.auth_combo.currentIndexChanged.connect(self._on_auth_changed)
        auth_layout.addRow("认证类型:", self.auth_combo)
        
        self.username_edit = QLineEdit()
        self.username_label = QLabel("用户名:")
        auth_layout.addRow(self.username_label, self.username_edit)
        
        pwd_container = QWidget()
        pwd_horiz = QHBoxLayout(pwd_container)
        pwd_horiz.setContentsMargins(0, 0, 0, 0)
        pwd_horiz.setSpacing(8)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_horiz.addWidget(self.password_edit)
        
        self.pwd_visible_btn = QPushButton("👁️")
        self.pwd_visible_btn.setFixedWidth(30)
        self.pwd_visible_btn.setCheckable(True)
        self.pwd_visible_btn.setStyleSheet("""
            QPushButton { border: none; background: transparent; font-size: 14px; }
            QPushButton:hover { color: #228BE6; }
        """)
        self.pwd_visible_btn.clicked.connect(self._toggle_password_visibility)
        pwd_horiz.addWidget(self.pwd_visible_btn)
        
        self.save_pwd_check = QCheckBox("保存密码")
        self.save_pwd_check.setChecked(True)
        pwd_horiz.addWidget(self.save_pwd_check)
        
        self.password_label = QLabel("密码:")
        auth_layout.addRow(self.password_label, pwd_container)
        
        v_layout.addWidget(group_auth)
        v_layout.addStretch()
        
        # 初始默认认证方式：用户名/密码 (Index 1)
        self.auth_combo.setCurrentIndex(1)
        self._on_auth_changed(1)
    
    def _on_auth_changed(self, index: int):
        """认证方式改变"""
        need_auth = index > 0  # 非 NOSASL 需要认证
        self.username_label.setVisible(need_auth)
        self.username_edit.setVisible(need_auth)
        self.password_label.setVisible(need_auth)
        self.password_edit.setVisible(need_auth)
        self.save_pwd_check.setVisible(need_auth)
        self.pwd_visible_btn.setVisible(need_auth)

    def _toggle_password_visibility(self):
        """切换密码可见性"""
        is_visible = self.pwd_visible_btn.isChecked()
        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if is_visible else QLineEdit.EchoMode.Password
        )
        self.pwd_visible_btn.setText("👁️" if not is_visible else "🙈")
    
    def _load_config(self, config: ConnectionConfig):
        """加载配置到表单"""
        self.name_edit.setText(config.name)
        self.host_edit.setText(config.host)
        self.port_spin.setValue(config.port)
        self.database_edit.setText(config.database)
        self.username_edit.setText(config.username)
        self.password_edit.setText(config.password)
        
        # 设置认证方式
        auth_map = {"NOSASL": 0, "PLAIN": 1, "LDAP": 2}
        self.auth_combo.setCurrentIndex(auth_map.get(config.auth_mechanism, 0))
    
    def _get_config(self) -> ConnectionConfig:
        """从表单获取配置"""
        auth_map = {0: "NOSASL", 1: "PLAIN", 2: "LDAP"}
        return ConnectionConfig(
            name=self.name_edit.text().strip(),
            host=self.host_edit.text().strip(),
            port=self.port_spin.value(),
            database=self.database_edit.text().strip() or "default",
            username=self.username_edit.text().strip(),
            password=self.password_edit.text() if self.save_pwd_check.isChecked() else "",
            auth_mechanism=auth_map[self.auth_combo.currentIndex()]
        )
    
    def _validate(self) -> tuple[bool, str]:
        """验证表单"""
        if not self.name_edit.text().strip():
            return False, "请输入连接名称"
        if not self.host_edit.text().strip():
            return False, "请输入主机地址"
        return True, ""
    
    def _test_connection(self):
        """测试连接"""
        valid, msg = self._validate()
        if not valid:
            QMessageBox.warning(self, "验证失败", msg)
            return
        
        from src.core.connection import HiveConnection
        
        config = self._get_config()
        conn = HiveConnection(config)
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        self.test_btn.repaint()
        
        try:
            success, error = conn.connect()
            if success:
                QMessageBox.information(self, "连接成功", "成功连接到 Hive 服务器！")
                conn.disconnect()
            else:
                QMessageBox.critical(self, "连接失败", f"无法连接到服务器:\n{error}")
        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("测试连接")
    
    def _save(self):
        """保存配置"""
        valid, msg = self._validate()
        if not valid:
            QMessageBox.warning(self, "验证失败", msg)
            return
        
        self.result_config = self._get_config()
        self.accept()
