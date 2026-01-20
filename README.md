# HiveLight

轻量级 Hive 数据库客户端，专为 macOS 设计。

## 功能特性

- 🔗 **连接管理** - 支持多个 Hive 连接配置
- 🌲 **数据库浏览** - 树形展示数据库、表、字段
- ✏️ **SQL 编辑器** - 语法高亮，快捷执行
- 📊 **结果展示** - 表格形式展示查询结果
- 💾 **导出功能** - 支持导出为 CSV

## 安装

### 1. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行

```bash
python main.py
```

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+Enter` | 执行查询 |
| `Cmd+N` | 新建连接 |
| `Cmd+L` | 清空编辑器 |
| `Cmd+Q` | 退出 |

## 技术栈

- Python 3.12+
- PySide6 (Qt6)
- impyla (Hive 连接)

## 打包为应用

```bash
pip install pyinstaller
pyinstaller --name HiveLight --windowed --onefile main.py
```

打包后的应用位于 `dist/HiveLight.app`

## License

MIT
