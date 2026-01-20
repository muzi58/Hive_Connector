"""
简化的配置管理单元测试
基于实际的 ConfigManager API
"""
import pytest
import json
from pathlib import Path
import tempfile
import shutil


class TestConfigManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_add_and_get_connection(self, temp_config_dir, monkeypatch):
        """测试添加和获取连接配置"""
        from src.utils.config import ConfigManager, ConnectionConfig
        from src.utils.paths import get_app_data_dir
        
        # Mock get_app_data_dir
        monkeypatch.setattr("src.utils.config.get_app_data_dir", lambda: temp_config_dir)
        
        config_mgr = ConfigManager()
        
        conn = ConnectionConfig(
            name="Test Connection",
            host="localhost",
            port=10000,
            database="default",
            auth_mechanism="NOSASL"
        )
        
        config_mgr.add_connection(conn)
        
        # 获取连接
        retrieved = config_mgr.get_connection("Test Connection")
        assert retrieved is not None
        assert retrieved.name == "Test Connection"
        assert retrieved.host == "localhost"
    
    def test_remove_connection(self, temp_config_dir, monkeypatch):
        """测试删除连接配置"""
        from src.utils.config import ConfigManager, ConnectionConfig
        
        monkeypatch.setattr("src.utils.config.get_app_data_dir", lambda: temp_config_dir)
        config_mgr = ConfigManager()
        
        # 添加连接
        conn = ConnectionConfig(name="Test", host="localhost", port=10000, database="default", auth_mechanism="NOSASL")
        config_mgr.add_connection(conn)
        
        # 验证存在
        assert config_mgr.get_connection("Test") is not None
        
        # 删除
        config_mgr.remove_connection("Test")
        
        # 验证已删除
        assert config_mgr.get_connection("Test") is None
    
    def test_config_persistence(self, temp_config_dir, monkeypatch):
        """测试配置持久化"""
        from src.utils.config import ConfigManager, ConnectionConfig
        
        monkeypatch.setattr("src.utils.config.get_app_data_dir", lambda: temp_config_dir)
        
        # 创建并保存配置
        config_mgr1 = ConfigManager()
        conn = ConnectionConfig(name="Test", host="localhost", port=10000, database="default", auth_mechanism="NOSASL")
        config_mgr1.add_connection(conn)
        
        # 重新加载配置
        config_mgr2 = ConfigManager()
        retrieved = config_mgr2.get_connection("Test")
        
        assert retrieved is not None
        assert retrieved.name == "Test"
        assert retrieved.host == "localhost"
    
    def test_update_existing_connection(self, temp_config_dir, monkeypatch):
        """测试更新已存在的连接（同名替换）"""
        from src.utils.config import ConfigManager, ConnectionConfig
        
        monkeypatch.setattr("src.utils.config.get_app_data_dir", lambda: temp_config_dir)
        config_mgr = ConfigManager()
        
        # 添加初始连接
        conn1 = ConnectionConfig(name="Test", host="localhost", port=10000, database="default", auth_mechanism="NOSASL")
        config_mgr.add_connection(conn1)
        
        # 添加同名连接（应该替换）
        conn2 = ConnectionConfig(name="Test", host="newhost", port=10001, database="newdb", auth_mechanism="PLAIN")
        config_mgr.add_connection(conn2)
        
        # 验证更新
        retrieved = config_mgr.get_connection("Test")
        assert retrieved.host == "newhost"
        assert retrieved.port == 10001


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
