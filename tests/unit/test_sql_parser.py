"""
SQL 解析器单元测试
测试 SQLEditor 的多语句分割功能
"""
import pytest


class TestSQLParser:
    """SQL 解析器测试类"""
    
    def test_single_statement(self, qtbot):
        """测试单条 SQL 语句"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("SELECT * FROM users")
        
        statements = editor._get_all_statements()
        assert len(statements) == 1
        assert statements[0][2].strip() == "SELECT * FROM users"
    
    def test_multiple_statements_with_semicolon(self, qtbot):
        """测试用分号分隔的多条语句"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = "SELECT * FROM users;\nSELECT * FROM orders;\nSELECT * FROM products"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 3
    
    def test_semicolon_in_string(self, qtbot):
        """测试字符串内的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = "SELECT * FROM users WHERE name = 'John;Doe'"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 1
        assert "John;Doe" in statements[0][2]
    
    def test_semicolon_in_single_line_comment(self, qtbot):
        """测试单行注释中的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = "SELECT * FROM users -- this is a ; comment\nSELECT * FROM orders"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 应该只识别出 2 条有效语句（注释行不算）
        assert len(statements) == 2
    
    def test_semicolon_in_multiline_comment(self, qtbot):
        """测试多行注释中的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = """SELECT * FROM users
/* this is a 
multi-line ; comment */
SELECT * FROM orders"""
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 2
    
    def test_empty_text(self, qtbot):
        """测试空文本"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        editor.setPlainText("")
        
        statements = editor._get_all_statements()
        assert len(statements) == 0
    
    def test_only_comments(self, qtbot):
        """测试纯注释文本"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = "-- comment 1\n/* comment 2 */"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 纯注释应该不产生有效语句
        assert len(statements) == 0 or all(not s[2].strip() for s in statements)
    
    def test_complex_mixed_scenario(self, qtbot):
        """测试复杂混合场景"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        qtbot.addWidget(editor)
        sql = """
-- 查询用户
SELECT * FROM users WHERE name = 'Alice;Bob';
/* 
这是多行注释;
包含分号
*/
SELECT * FROM orders; -- 订单查询;
SELECT 'test;value' AS col
"""
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 应该识别出 3 条有效语句
        assert len(statements) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



class TestSQLParser:
    """SQL 解析器测试类"""
    
    def test_single_statement(self):
        """测试单条 SQL 语句"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        editor.setPlainText("SELECT * FROM users")
        
        statements = editor._get_all_statements()
        assert len(statements) == 1
        assert statements[0][2].strip() == "SELECT * FROM users"
    
    def test_multiple_statements_with_semicolon(self):
        """测试用分号分隔的多条语句"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = "SELECT * FROM users;\nSELECT * FROM orders;\nSELECT * FROM products"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 3
    
    def test_semicolon_in_string(self):
        """测试字符串内的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = "SELECT * FROM users WHERE name = 'John;Doe'"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 1
        assert "John;Doe" in statements[0][2]
    
    def test_semicolon_in_single_line_comment(self):
        """测试单行注释中的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = "SELECT * FROM users -- this is a ; comment\nSELECT * FROM orders"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 应该只识别出 2 条有效语句（注释行不算）
        assert len(statements) == 2
    
    def test_semicolon_in_multiline_comment(self):
        """测试多行注释中的分号应被忽略"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = """SELECT * FROM users
/* this is a 
multi-line ; comment */
SELECT * FROM orders"""
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        assert len(statements) == 2
    
    def test_empty_text(self):
        """测试空文本"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        editor.setPlainText("")
        
        statements = editor._get_all_statements()
        assert len(statements) == 0
    
    def test_only_comments(self):
        """测试纯注释文本"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = "-- comment 1\n/* comment 2 */"
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 纯注释应该不产生有效语句
        assert len(statements) == 0 or all(not s[2].strip() for s in statements)
    
    def test_complex_mixed_scenario(self):
        """测试复杂混合场景"""
        from src.ui.query_editor import SQLEditor
        editor = SQLEditor()
        sql = """
-- 查询用户
SELECT * FROM users WHERE name = 'Alice;Bob';
/* 
这是多行注释;
包含分号
*/
SELECT * FROM orders; -- 订单查询;
SELECT 'test;value' AS col
"""
        editor.setPlainText(sql)
        
        statements = editor._get_all_statements()
        # 应该识别出 3 条有效语句
        assert len(statements) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
