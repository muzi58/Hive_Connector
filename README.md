# Hive Connect

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Build](https://img.shields.io/badge/build-Nuitka-green.svg)

**Hive Connect** 是一个专为 macOS 设计的现代化、高性能 Hive 数据库客户端。它基于 PySide6 构建，并使用 Nuitka 编译技术，在 Apple Silicon 芯片上提供原生的极速体验。

**Hive Connect** is a modern, high-performance Hive database client designed for macOS. Built with PySide6 and compiled using Nuitka, it delivers a native, blazing-fast experience on Apple Silicon.

## 🚀 主要特性 / Key Features

### 🇨🇳 中文
*   ⚡️ **极致性能**：使用 Nuitka 静态编译，启动速度提升 6 倍，不仅体积小巧，运行更流畅。
*   🔗 **多连接管理**：轻松管理多个 Hive 环境，支持 SASL、LDAP 等多种认证方式。
*   ✏️ **智能编辑器**：内置语法高亮、自动行号、智能缩进的 SQL 编辑器。
*   🌲 **可视化浏览**：直观的树形结构查看数据库、表结构和字段信息。
*   📊 **数据交互**：清晰的结果展示网格，支持大数据量快速渲染。
*   🖥 **macOS 适配**：遵循 macOS 设计规范，提供原生的视觉和交互体验。

### 🇺🇸 English
*   ⚡️ **High Performance**: Statically compiled with Nuitka, launching 6x faster with a smaller footprint and smoother execution.
*   🔗 **Connection Manager**: Easily manage multiple Hive environments with support for SASL, LDAP, and more.
*   ✏️ **Smart Editor**: Built-in SQL editor with syntax highlighting, line numbering, and smart indentation.
*   🌲 **Visual Explorer**: Intuitive tree view for browsing databases, table schemas, and columns.
*   📊 **Data Grid**: Clean result visualization optimized for rendering large datasets quickly.
*   🖥 **macOS Optimized**: Designed following macOS guidelines for a truly native look and feel.

---

## 📦 安装与使用 / Installation

### 📥 方式一：下载应用 (推荐) / Option 1: Download App (Recommended)
1.  访问 [Releases](https://github.com/muzi58/Hive_Connector/releases) 页面。
2.  下载最新版本的 `Hive_Connector_macOS_ARM64.zip`。
3.  解压并将 `Hive Connect.app` 拖入 **应用程序 (Applications)** 文件夹。
4.  双击运行。

1.  Visit the [Releases](https://github.com/muzi58/Hive_Connector/releases) page.
2.  Download the latest `Hive_Connector_macOS_ARM64.zip`.
3.  Unzip and drag `Hive Connect.app` to your **Applications** folder.
4.  Launch and enjoy.

### 🛠 方式二：手动构建 / Option 2: Build from Source

如果您是开发者，可以从源码构建：
If you are a developer, you can build from source:

```bash
# 1. Clone repository
git clone https://github.com/muzi58/Hive_Connector.git
cd Hive_Connector

# 2. Create virtual environment (Python 3.13 recommended)
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run in dev mode
python main.py

# 5. Build optimized app with Nuitka
python package_nuitka.py
```

---

## ⌨️ 快捷键 / Shortcuts

| 快捷键 (Shortcut) | 功能 (Function) |
|-------------------|-----------------|
| `Cmd + Enter`     | 执行 SQL (Execute SQL) |
| `Cmd + N`         | 新建连接 (New Connection) |
| `Cmd + T`         | 新建查询 (New Query Tab) |
| `Cmd + W`         | 关闭当前标签 (Close Tab) |

---

## 📄 许可证 / License

本项目采用 [Apache License 2.0](LICENSE) 开源协议。
This project is licensed under the [Apache License 2.0](LICENSE).
