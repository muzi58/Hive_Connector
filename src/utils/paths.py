"""
路径工具模块
处理资源加载和配置路径，支持 PyInstaller 打包环境
"""

import sys
import os
from pathlib import Path

def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径，适配打包后的运行环境"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时解压目录
        base_path = sys._MEIPASS
    else:
        # 尝试通过可执行文件路径判断是否在 .app bundle 内
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        
        # 检查是否在 macOS .app bundle 内 (Nuitka 打包)
        if 'Contents/MacOS' in exe_dir:
            # Nuitka 打包模式：资源在可执行文件同目录
            base_path = exe_dir
        else:
            # 开发模式：使用项目根目录
            # 获取当前文件所在目录的上两级（src/utils -> 项目根）
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_file_dir))
            base_path = project_root

    return os.path.join(base_path, relative_path)

def get_app_data_dir() -> Path:
    """获取应用数据存储目录 (macOS: ~/Library/Application Support/Hive Connect)"""
    if sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "Hive Connect"
    else:
        path = Path.home() / ".hive_connect"
    
    path.mkdir(parents=True, exist_ok=True)
    return path
