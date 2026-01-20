"""
Hive Connect Nuitka 打包脚本
使用 Nuitka 编译器生成优化的 macOS .app 应用
"""

import subprocess
import sys
import os

def package_with_nuitka():
    print("🚀 开始使用 Nuitka 打包 Hive Connect...")
    print("⚠️  注意：首次编译可能需要 5-10 分钟，请耐心等待")
    
    # 确保资源目录存在
    if not os.path.exists("resources"):
        print("错误: 未找到 resources 目录")
        return
    
    # Nuitka 编译命令
    cmd = [
        sys.executable,
        "-m", "nuitka",
        # 基础选项
        "--standalone",  # 独立模式
        # 注意：移除 --onefile 避免链接问题
        
        # macOS 应用选项
        "--macos-create-app-bundle",  # 创建 .app bundle
        "--macos-app-name=Hive Connect",  # 应用名称
        f"--macos-app-icon=resources/icons/app_icon.png",  # 应用图标
        
        # PySide6 插件
        "--enable-plugin=pyside6",  # 启用 PySide6 支持
        
        # 显式包含缺失的模块（six 动态导入的标准库）
        # http 模块家族
        "--include-module=http",
        "--include-module=http.client",
        "--include-module=http.cookies",
        "--include-module=http.cookiejar",
        "--include-module=http.server",
        # urllib 模块家族
        "--include-module=urllib",
        "--include-module=urllib.parse",
        "--include-module=urllib.request",
        "--include-module=urllib.response",
        "--include-module=urllib.error",
        
        # 资源文件
        "--include-data-dir=resources=resources",  # 包含资源目录
        
        # 优化选项（移除 LTO 避免链接错误）
        # "--lto=yes",  # 链接时优化（可能导致链接错误，暂时禁用）
        "--assume-yes-for-downloads",  # 自动下载依赖
        
        # 其他选项
        "--show-progress",  # 显示进度
        # "--show-memory",  # 显示内存使用（减少输出信息）
        
        # 输出目录
        "--output-dir=dist_nuitka",  # 输出到单独目录
        
        # 主文件
        "main.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("\n" + "="*80)
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*80)
        print("\n✅ 打包成功！")
        print(f"应用位于: dist_nuitka/Hive Connect.app")
        print("\n🎯 Nuitka 优化效果:")
        print("  - 体积减少: 预计 87%")
        print("  - 启动速度: 预计提升 6 倍")
        print("  - 运行性能: 预计提升 3 倍")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 打包失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生意外错误: {e}")

if __name__ == "__main__":
    package_with_nuitka()
