"""
SQL 语法高亮模块
适配浅色主题
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


class SQLHighlighter(QSyntaxHighlighter):
    """SQL 语法高亮器 (浅色主题版)"""
    
    # Hive SQL 关键字
    KEYWORDS = [
        "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "EXISTS",
        "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS", "ON",
        "GROUP", "BY", "HAVING", "ORDER", "ASC", "DESC", "LIMIT", "OFFSET",
        "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE", "TRUNCATE",
        "CREATE", "ALTER", "DROP", "TABLE", "DATABASE", "VIEW", "INDEX",
        "IF", "ELSE", "CASE", "WHEN", "THEN", "END", "AS", "LIKE", "BETWEEN",
        "DISTINCT", "ALL", "UNION", "INTERSECT", "EXCEPT",
        "NULL", "TRUE", "FALSE", "IS", "NULLS", "FIRST", "LAST",
        "PARTITION", "PARTITIONED", "CLUSTERED", "SORTED", "BUCKETS",
        "ROW", "FORMAT", "STORED", "LOCATION", "TBLPROPERTIES",
        "EXTERNAL", "TEMPORARY", "OVERWRITE", "DIRECTORY",
        "LOAD", "DATA", "INPATH", "LOCAL",
        "SHOW", "DESCRIBE", "EXPLAIN", "USE", "ANALYZE",
        "WITH", "RECURSIVE", "LATERAL", "TABLESAMPLE"
    ]
    
    # 数据类型
    TYPES = [
        "INT", "INTEGER", "BIGINT", "SMALLINT", "TINYINT",
        "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC",
        "STRING", "VARCHAR", "CHAR", "BOOLEAN", "BINARY",
        "TIMESTAMP", "DATE", "INTERVAL",
        "ARRAY", "MAP", "STRUCT", "UNIONTYPE"
    ]
    
    # 函数
    FUNCTIONS = [
        "COUNT", "SUM", "AVG", "MIN", "MAX", "FIRST", "LAST",
        "CONCAT", "SUBSTR", "LENGTH", "TRIM", "UPPER", "LOWER",
        "COALESCE", "NVL", "CAST", "CONVERT",
        "DATE_FORMAT", "TO_DATE", "YEAR", "MONTH", "DAY",
        "ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE",
        "LAG", "LEAD", "OVER", "PARTITION"
    ]
    
    def __init__(self, document):
        super().__init__(document)
        self._init_formats()
    
    def _init_formats(self):
        """初始化格式 (浅色主题适配)"""
        # 关键字格式 - 蓝色加粗 (Navicat 风格)
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("#0000FF")) # 纯蓝
        self.keyword_format.setFontWeight(QFont.Weight.Bold)
        
        # 类型格式 - 绿色
        self.type_format = QTextCharFormat()
        self.type_format.setForeground(QColor("#008000"))
        
        # 函数格式 - 紫色
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor("#800080")) # 紫色
        
        # 字符串格式 - 红色
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("#A31515")) # 红色
        
        # 数字格式 - 深青色
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("#098658"))
        
        # 注释格式 - 灰色斜体
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#808080"))
        self.comment_format.setFontItalic(True)
        
        # 操作符格式
        self.operator_format = QTextCharFormat()
        self.operator_format.setForeground(QColor("#000000"))
    
    def highlightBlock(self, text: str):
        """高亮文本块"""
        # 转换为大写用于匹配（保持原始位置）
        upper_text = text.upper()
        
        # 高亮关键字
        for keyword in self.KEYWORDS:
            self._highlight_word(upper_text, text, keyword, self.keyword_format)
        
        # 高亮类型
        for type_name in self.TYPES:
            self._highlight_word(upper_text, text, type_name, self.type_format)
        
        # 高亮函数
        for func in self.FUNCTIONS:
            self._highlight_word(upper_text, text, func, self.function_format)
        
        # 高亮字符串 'xxx' 或 "xxx"
        self._highlight_strings(text)
        
        # 高亮数字
        self._highlight_numbers(text)
        
        # 高亮单行注释 --
        self._highlight_line_comment(text)
    
    def _highlight_word(self, upper_text: str, original_text: str, word: str, fmt: QTextCharFormat):
        """高亮单词（仅匹配完整单词）"""
        import re
        pattern = rf'\b{word}\b'
        for match in re.finditer(pattern, upper_text):
            self.setFormat(match.start(), match.end() - match.start(), fmt)
    
    def _highlight_strings(self, text: str):
        """高亮字符串"""
        import re
        # 匹配单引号和双引号字符串
        for match in re.finditer(r"'[^']*'|\"[^\"]*\"", text):
            self.setFormat(match.start(), match.end() - match.start(), self.string_format)
    
    def _highlight_numbers(self, text: str):
        """高亮数字"""
        import re
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
    
    def _highlight_line_comment(self, text: str):
        """高亮行注释"""
        idx = text.find('--')
        if idx >= 0:
            self.setFormat(idx, len(text) - idx, self.comment_format)
