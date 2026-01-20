#!/usr/bin/env python3
"""
HiveLight - 轻量级 Hive 数据库客户端
专为 macOS 设计
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

from src.ui.main_window import MainWindow
from src.utils.paths import get_resource_path


def main():
    # 启用高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Hive Connect")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hive Connect")
    
    # 设置默认字体
    font = QFont("SF Pro Text", 13)
    app.setFont(font)
    
    # 加载样式表
    try:
        style_path = get_resource_path("resources/style.qss")
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass
    
    # 创建主窗口
    window = MainWindow()
    window.setWindowIcon(QIcon(get_resource_path("resources/icons/app_icon.png")))
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
