"""
Hive Connect 打包脚本
使用 PyInstaller 生成 macOS .app 应用包
"""

import os
import subprocess
import sys

def package():
    print("🚀 开始打包 Hive Connect...")
    
    # 确保资源目录存在
    if not os.path.exists("resources"):
        print("错误: 未找到 resources 目录")
        return

    # 获取图标路径
    icon_path = "resources/icons/app_icon.png"

    # 打包命令基本参数
    # 使用 sys.executable -m PyInstaller 确保使用当前虚拟环境的 pyinstaller
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--windowed", # 无终端模式
        "--name=Hive Connect",
        "--clean",
        # 包含资源文件 (格式: 原路径:目标路径)
        "--add-data=resources:resources",
        # 入口文件
        "main.py"
    ]
    
    # 添加图标配置
    if os.path.exists(icon_path):
        cmd.insert(6, f"--icon={icon_path}")

    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ 打包成功！应用位于 dist/Hive Connect.app")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生意外错误: {e}")

if __name__ == "__main__":
    package()
