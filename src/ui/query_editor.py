"""
SQL 查询编辑器
带语法高亮的 SQL 输入区域
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QTableView, QTableWidget, QTableWidgetItem, QTabWidget,
    QSplitter, QMessageBox, QLabel, QPushButton, 
    QHeaderView, QTextEdit, QProgressBar, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QRect, QSize, QEvent, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QColor, QPainter, QTextFormat, QWheelEvent, QKeySequence

from src.utils.syntax import SQLHighlighter
from src.core.connection import HiveConnection, QueryResult
from src.core.query_worker import QueryWorker


class LineNumberArea(QWidget):
    """行号区域"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class SQLEditor(QPlainTextEdit):
    """带有行号的 SQL 编辑器"""
    
    execute_requested = Signal()  # 请求执行
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_area = LineNumberArea(self)
        self._zoom_accumulator = 0  # 触控板缩放累加器
        
        # 信号连接
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        
        self._init_ui()
        self.update_line_number_area_width(0)
        self.highlight_current_line()
    
    def line_number_area_width(self):
        """计算行号区域宽度"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 5 + self.fontMetrics().horizontalAdvance('9') * digits + 6
        return space

    def update_line_number_area_width(self, _):
        """更新边距"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """更新行号区域"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        """绘制行号"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#F0F0F0"))  # 浅灰色背景

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        # 获取当前行
        current_block = self.textCursor().block()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                # 当前行高亮
                painter.setPen(QColor("#000000") if block == current_block else QColor("#808080"))
                font = self.font()
                font.setBold(block == current_block)
                painter.setFont(font)
                
                painter.drawText(2, int(top), self.line_number_area.width() - 8, self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def highlight_current_line(self):
        """高亮当前行"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#E3F2FD").lighter(108)  # 非常浅的蓝色
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)
        self.line_number_area.update() # 重绘行号以更新加粗样式
    
    def _init_ui(self):
        """初始化界面"""
        # 设置字体
        font = QFont("Menlo", 13) # 使用 Menlo 或 SF Mono
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 设置 Tab 宽度
        self.setTabStopDistance(40)
        
        # 设置占位符
        self.setPlaceholderText("在此输入 SQL 查询语句...\n\nCMD+Enter 执行")
        
        # 启用语法高亮
        self.highlighter = SQLHighlighter(self.document())
        
        # 样式由 qss 控制，但行号区域需要代码控制
        self.setFrameShape(QPlainTextEdit.Shape.NoFrame) # 移除边框以融入布局
        
    def _on_cursor_position_changed(self): # Renamed method
        """光标位置变化"""
        # 信号冒泡到 QueryEditor
        parent = self.parentWidget()
        while parent and not hasattr(parent, 'update_cursor_info'):
            parent = parent.parentWidget()
        if parent:
            parent.update_cursor_info()
    
    def keyPressEvent(self, event):
        """键盘事件"""
        # Cmd+Enter 执行查询
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.execute_requested.emit()
            return
        
        # Cmd+L 清空
        if event.key() == Qt.Key.Key_L and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.clear()
            return
        
        super().keyPressEvent(event)
    
    def wheelEvent(self, event):
        """处理滚轮事件（支持 Ctrl + 滚轮缩放字体）"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            return # 消耗事件
        super().wheelEvent(event)

    def viewportEvent(self, event):
        """确保视口也能处理原生手势事件"""
        if event.type() == QEvent.Type.NativeGesture:
            if self.nativeGestureEvent(event):
                return True
        return super().viewportEvent(event)

    def nativeGestureEvent(self, event):
        """处理触控板原生缩放手势"""
        if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
            # macOS 触控板事件非常频繁且增量较小，使用极灵敏的累加器
            self._zoom_accumulator += event.value()
            if self._zoom_accumulator > 0.01:
                self.zoom_in()
                self._zoom_accumulator = 0
            elif self._zoom_accumulator < -0.01:
                self.zoom_out()
                self._zoom_accumulator = 0
            return True
        return False # 不再调用 super()，因为 QPlainTextEdit 可能未暴露该虚函数

    def zoom_in(self):
        """增大字体"""
        self.zoomIn(1)
        self.update_line_number_area_width(0)

    def zoom_out(self):
        """减小字体"""
        # 限制最小字号，防止缩得太小看不见
        if self.font().pointSize() > 6 or self.font().pixelSize() > 6:
            self.zoomOut(1)
            self.update_line_number_area_width(0)
    
    def get_current_sql(self) -> str:
        """获取当前要执行的 SQL（增强版：支持注释、字符串过滤及光标回溯）"""
        cursor = self.textCursor()
        
        # 1. 如果有选中文本，直接返回并去除两端空白
        if cursor.hasSelection():
            return cursor.selectedText().replace('\u2029', '\n').strip()
        
        text = self.toPlainText()
        pos = cursor.position()
        
        # 获取所有语句及其边界
        statements = self._get_all_statements(text)
        
        # 找到光标落在哪条语句中
        target_stmt = ""
        for start, end, content in statements:
            # 如果光标在语句范围内，或者在语句末尾的分号上
            if start <= pos <= end:
                target_stmt = content.strip()
                break
        
        # 如果当前位置没找到有效语句（可能在空白区或分号后）
        if not target_stmt:
            # 策略：向前寻找最近的一条语句
            best_prev = ""
            for start, end, content in statements:
                if end <= pos:
                    best_prev = content.strip()
                else:
                    break
            target_stmt = best_prev
                
        return target_stmt

    def _get_all_statements(self, text: str) -> list[tuple[int, int, str]]:
        """基于状态机解析所有 SQL 语句，排除注释和字符串干扰"""
        statements = []
        start = 0
        i = 0
        n = len(text)
        
        in_single_quote = False
        in_double_quote = False
        in_single_comment = False # --
        in_multi_comment = False  # /* */
        
        while i < n:
            char = text[i]
            
            # 处理多行注释结束
            if in_multi_comment:
                if char == '*' and i + 1 < n and text[i+1] == '/':
                    in_multi_comment = False
                    i += 1
            # 处理单行注释结束 (兼容 \n 和 \r)
            elif in_single_comment:
                if char == '\n' or char == '\r':
                    in_single_comment = False
            # 处理引号结束
            elif in_single_quote:
                if char == "'" and (i == 0 or text[i-1] != '\\'):
                    in_single_quote = False
            elif in_double_quote:
                if char == '"' and (i == 0 or text[i-1] != '\\'):
                    in_double_quote = False
            # 处理新状态开始
            else:
                if char == '/' and i + 1 < n and text[i+1] == '*':
                    in_multi_comment = True
                    i += 1
                elif char == '-' and i + 1 < n and text[i+1] == '-':
                    in_single_comment = True
                    i += 1
                elif char == "'":
                    in_single_quote = True
                elif char == '"':
                    in_double_quote = True
                elif char == ';':
                    # 发现有效分号，分割语句
                    statements.append((start, i + 1, text[start:i]))
                    start = i + 1
            
            i += 1
            
        # 别忘了最后一个没有分号的语句
        if start < n:
            content = text[start:].strip()
            if content:
                statements.append((start, n, text[start:]))
                
        return statements


class VirtualTableModel(QAbstractTableModel):
    """虚拟表格数据模型 - 支持大数据量按需渲染"""
    
    def __init__(self, columns=None, rows=None, parent=None):
        super().__init__(parent)
        self._columns = columns or []
        self._rows = rows or []
    
    def rowCount(self, parent=QModelIndex()):
        """返回总行数"""
        return len(self._rows)
    
    def columnCount(self, parent=QModelIndex()):
        """返回总列数"""
        return len(self._columns)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """返回单元格数据"""
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        
        if row >= len(self._rows) or col >= len(self._columns):
            return None
        
        value = self._rows[row][col]
        
        if role == Qt.ItemDataRole.DisplayRole:
            # 显示文本
            if value is None:
                return "NULL"
            return str(value)
        elif role == Qt.ItemDataRole.ForegroundRole:
            # NULL 值显示为灰色
            if value is None:
                return QColor("#999999")
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            # 文本左对齐
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """返回表头数据"""
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section < len(self._columns):
                    return self._columns[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None
    
    def set_data(self, columns, rows):
        """更新数据"""
        self.beginResetModel()
        self._columns = columns
        self._rows = rows
        self.endResetModel()


class ResultTable(QTableView):
    """查询结果表格 - 使用虚拟滚动"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = VirtualTableModel()
        self.setModel(self._model)
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.verticalHeader().setDefaultSectionSize(32)
        
        # 优化滚动灵敏度
        self.horizontalScrollBar().setSingleStep(20)
        
        # 样式由 style.qss 全局控制
    
    def set_result(self, result: QueryResult):
        """设置查询结果 - 使用虚拟模型"""
        if not result or not result.columns:
            self._model.set_data([], [])
            return
        
        columns = result.columns
        rows = result.rows
        
        # 清洗列名：去除表名前缀
        clean_columns = []
        for col in columns:
            if '.' in col:
                col = col.split('.')[-1]
            clean_columns.append(col)
        
        # 更新模型数据（虚拟滚动的关键：不创建 widget，只存储数据）
        self._model.set_data(clean_columns, rows)
        
        # 动态调整列宽
        self._adjust_column_widths(clean_columns, rows)
    
    def _adjust_column_widths(self, columns, rows):
        """智能调整列宽"""
        MAX_COL_WIDTH = 500
        SAMPLE_SIZE = min(100, len(rows))  # 只采样前 100 行来计算宽度
        
        for col_idx in range(len(columns)):
            max_width = len(columns[col_idx]) * 10  # 表头宽度
            
            # 采样部分行来估算最大宽度
            for row_idx in range(SAMPLE_SIZE):
                if row_idx < len(rows):
                    value = rows[row_idx][col_idx]
                    text_width = len(str(value)) if value else 4
                    max_width = max(max_width, text_width * 8 + 20)
            
            estimated_width = min(max_width, MAX_COL_WIDTH)
            self.setColumnWidth(col_idx, max(80, estimated_width))
    
    def wheelEvent(self, event: QWheelEvent):
        """重写滚轮事件，优化横向滚动灵敏度"""
        # 如果按下 Shift 或者当前没有纵向滚动条，进行横向滚动
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier or \
           self.verticalScrollBar().maximum() == 0:
            delta = event.angleDelta().y() or event.angleDelta().x()
            # 乘以一个系数（如 0.5）来降低灵敏度，使体验更丝滑
            new_val = self.horizontalScrollBar().value() - int(delta * 0.5)
            self.horizontalScrollBar().setValue(new_val)
            event.accept()
            return

        super().wheelEvent(event)


class QueryEditor(QWidget):
    """查询编辑器组件（包含编辑器和结果表格）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection: HiveConnection = None
        self.worker: QueryWorker = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面 (DBeaver 风格)"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 分割器：编辑器 + 结果
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        
        # --- 编辑器部分 ---
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container) # 改为垂直布局以容纳本地工具栏
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        
        # 1.1 编辑器本地工具栏 (Navicat 风格)
        self.editor_toolbar = QWidget()
        self.editor_toolbar.setFixedHeight(32)
        self.editor_toolbar.setStyleSheet("""
            QWidget { background: #F8F9FA; border-bottom: 1px solid #DEE2E6; }
            QPushButton { 
                border: none; padding: 4px 8px; background: transparent; 
                border-radius: 4px; color: #444; font-size: 12px;
            }
            QPushButton:hover { background: #E9ECEF; }
            QPushButton:pressed { background: #DEE2E6; }
        """)
        et_layout = QHBoxLayout(self.editor_toolbar)
        et_layout.setContentsMargins(10, 0, 10, 0)
        et_layout.setSpacing(15)
        
        self.run_btn = QPushButton("▶ 运行")
        self.run_btn.setToolTip("执行查询 (Ctrl+Enter)")
        self.run_btn.clicked.connect(self.execute_query)
        et_layout.addWidget(self.run_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_query)
        et_layout.addWidget(self.stop_btn)
        
        et_layout.addSeparator = lambda: et_layout.addWidget(QLabel("|")) # 简单的垂直线
        line = QLabel("|")
        line.setStyleSheet("color: #DEE2E6; margin: 0 5px;")
        et_layout.addWidget(line)
        
        self.save_btn = QPushButton("💾 保存")
        et_layout.addWidget(self.save_btn)
        
        self.format_btn = QPushButton("🧹 格式化")
        et_layout.addWidget(self.format_btn)
        
        et_layout.addStretch()
        
        editor_layout.addWidget(self.editor_toolbar)
        
        self.editor = SQLEditor()
        self.editor.execute_requested.connect(self.execute_query)
        editor_layout.addWidget(self.editor)
        
        splitter.addWidget(editor_container)
        
        # --- 结果面板部分 ---
        result_container = QWidget()
        result_layout = QVBoxLayout(result_container)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.setSpacing(0)
        
        # 结果本地工具栏
        self.result_toolbar = QWidget()
        self.result_toolbar.setFixedHeight(30)
        self.result_toolbar.setStyleSheet("""
            QWidget { background: #F8F9FA; border-bottom: 1px solid #E0E0E0; }
            QPushButton { 
                border: none; padding: 2px 10px; background: transparent; 
                font-size: 12px; color: #555; height: 22px;
            }
            QPushButton:hover { background: #E9ECEF; color: #000; }
            QLabel { color: #666; font-size: 11px; margin-left:10px; }
        """)
        rt_layout = QHBoxLayout(self.result_toolbar)
        rt_layout.setContentsMargins(4, 0, 4, 0)
        rt_layout.setSpacing(8)
        
        self.res_refresh_btn = QPushButton("🔄 刷新")
        rt_layout.addWidget(self.res_refresh_btn)
        
        self.res_export_btn = QPushButton("📤 导出")
        self.res_export_btn.clicked.connect(self.export_csv)
        rt_layout.addWidget(self.res_export_btn)
        
        rt_layout.addStretch()
        
        self.res_info_label = QLabel("未查询")
        rt_layout.addWidget(self.res_info_label)
        
        result_layout.addWidget(self.result_toolbar)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; background-color: #E5E5E5; margin: 0px; }
            QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #007AFF, stop:0.5 #5AC8FA, stop:1 #007AFF); }
        """)
        self.progress_bar.hide()
        result_layout.addWidget(self.progress_bar)
        
        self.result_tabs = QTabWidget()
        self.result_tabs.setDocumentMode(True)
        self.result_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: white; }
            QTabBar::tab { 
                padding: 6px 20px; 
                font-size: 11px; 
                background: #F1F3F5;
                color: #666;
                border: 1px solid #DEE2E6;
                border-bottom: none;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
                color: #007AFF;
                font-weight: bold;
                border-bottom: 2px solid #007AFF;
            }
        """)
        
        self.result_table = ResultTable()
        self.result_tabs.addTab(self.result_table, "结果")
        
        self.message_view = QTextEdit()
        self.message_view.setReadOnly(True)
        self.message_view.setStyleSheet("background: white; border: none; padding: 8px; font-family: 'SF Mono', monospace; font-size: 11px;")
        self.result_tabs.addTab(self.message_view, "信息")
        
        result_layout.addWidget(self.result_tabs)
        splitter.addWidget(result_container)
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # 底部状态栏 (局部)
        self.bottom_status = QWidget()
        self.bottom_status.setFixedHeight(22)
        self.bottom_status.setStyleSheet("background: #F8F9FA; border-top: 1px solid #E0E0E0;")
        bs_layout = QHBoxLayout(self.bottom_status)
        bs_layout.setContentsMargins(10, 0, 10, 0)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 11px;")
        bs_layout.addWidget(self.status_label)
        
        bs_layout.addStretch()
        
        self.cursor_label = QLabel("1 : 1")
        self.cursor_label.setStyleSheet("color: #666; font-size: 11px;")
        bs_layout.addWidget(self.cursor_label)
        
        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setStyleSheet("color: #666; font-size: 11px; margin-left: 15px;")
        bs_layout.addWidget(self.encoding_label)
        
        main_layout.addWidget(self.bottom_status)
        
    def update_cursor_info(self):
        """更新光标位置信息"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.cursor_label.setText(f"{line} : {col}")
    
    def set_connection(self, connection: HiveConnection):
        """设置连接"""
        self.connection = connection
        # self.side_exec_btn.setEnabled(connection is not None and connection.is_connected) # Removed as per instruction
    
    def set_sql(self, sql: str):
        """设置编辑器内容"""
        self.editor.setPlainText(sql)

    def get_sql(self) -> str:
        """获取编辑器内容"""
        return self.editor.toPlainText()
    
    def append_sql(self, sql: str):
        """追加 SQL 语句"""
        current = self.editor.toPlainText()
        if current and not current.endswith('\n'):
            current += '\n\n'
        self.editor.setPlainText(current + sql)
    
    def execute_query(self):
        """执行查询"""
        if not self.connection or not self.connection.is_connected:
            QMessageBox.warning(self, "警告", "请先连接到数据库")
            return
        
        # 获取当前 SQL 并彻底去除前后空白
        sql = self.editor.get_current_sql().strip()
        if not sql:
            return
            
        # 移除末尾所有的分号及其间的空白（HiveServer2/impyla 不支持末尾分号）
        while sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # 保存到历史
        from src.utils.config import config_manager
        config_manager.add_to_history(sql)
        
        # 准备显示
        self.update_button_states(True)
        self.status_label.setText("正在执行查询...")
        self.res_info_label.setText("执行中...")
        
        self.message_view.clear()
        self.message_view.append(f"> 执行 SQL:\n{sql}\n")
        self.message_view.append("正在执行...")
        
        self.worker = QueryWorker(self.connection, sql)
        self.worker.finished.connect(self._on_query_finished)
        self.worker.start()
    
    def stop_query(self):
        """停止查询"""
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("正在取消...")
            self.message_view.append("正在取消...")
    
    def update_button_states(self, is_running: bool):
        """更新按钮状态"""
        self.run_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)
        if is_running:
            self.progress_bar.show()
            self.progress_bar.setRange(0, 0) # 忙碌动画
        else:
            self.progress_bar.hide()
    
    def _on_query_finished(self, result: QueryResult):
        """查询完成"""
        self.update_button_states(False)
        self.worker = None
        
        time_str = f"{result.execution_time:.5f}s"
        
        if result.error:
            # 显示错误
            self.status_label.setText(f"错误 - 耗时: {time_str}")
            self.message_view.append(f"\n[错误] {result.error}")
            self.message_view.append(f"耗时: {time_str}")
            self.result_tabs.setCurrentIndex(1) # 切换到信息 Tab
            QMessageBox.critical(self, "查询错误", result.error)
        else:
            # 显示成功
            msg = f"查询成功 - 返回 {result.row_count} 行 - 耗时: {time_str}"
            self.status_label.setText(msg)
            
            self.message_view.append(f"\n[成] {msg}")
            
            # 更新结果表
            self.result_table.set_result(result)
            self.result_tabs.setTabText(0, f"结果 ({result.row_count})")
            self.res_info_label.setText(f"总计: {result.row_count} 行 | 耗时: {time_str}")
            
            # 智能切换 Tab: 如果有结果行，切换到结果页；否则(如USE语句)停留在信息页或切换到信息页？
            # Navicat 逻辑：如果有结果，显示结果页。
            if result.columns:
                self.result_tabs.setCurrentIndex(0)
            else:
                self.result_tabs.setCurrentIndex(1)
    
    def export_csv(self):
        """导出为 CSV"""
        if self.result_table.rowCount() == 0:
            QMessageBox.information(self, "无数据", "没有数据可以导出")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", "", "CSV 文件 (*.csv)"
        )
        
        if not path:
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # 写入表头
                headers = []
                for col in range(self.result_table.columnCount()):
                    headers.append(self.result_table.horizontalHeaderItem(col).text())
                f.write(','.join(headers) + '\n')
                
                # 写入数据
                for row in range(self.result_table.rowCount()):
                    cells = []
                    for col in range(self.result_table.columnCount()):
                        item = self.result_table.item(row, col)
                        text = item.text() if item else ""
                        # 处理包含逗号的值
                        if ',' in text or '"' in text or '\n' in text:
                            text = '"' + text.replace('"', '""') + '"'
                        cells.append(text)
                    f.write(','.join(cells) + '\n')
            
            self.status_label.setText(f"已导出到 {path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))

    def clear(self):
        """清空编辑器"""
        self.editor.clear()
