"""
pytest 配置文件
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture
def qapp(qapp_args):
    """Qt Application fixture"""
    from PySide6.QtWidgets import QApplication
    return QApplication(qapp_args)
