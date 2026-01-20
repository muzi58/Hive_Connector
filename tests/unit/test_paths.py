"""
简化的资源路径工具单元测试
"""
import pytest
import os
import sys
from pathlib import Path


class TestPaths:
    """路径工具测试类"""
    
    def test_get_resource_path_normal_mode(self):
        """测试开发模式下的资源路径解析"""
        from src.utils.paths import get_resource_path
        
        # 测试相对路径解析
        path = get_resource_path("resources/style.qss")
        assert "resources" in path
        assert "style.qss" in path
        assert os.path.isabs(path)
    
    def test_get_app_data_dir_creates_directory(self, tmp_path, monkeypatch):
        """测试应用数据目录创建"""
        from src.utils.paths import get_app_data_dir
        
        # Mock sys.platform 和 Path.home()
        monkeypatch.setattr(sys, 'platform', 'darwin')
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        app_data = get_app_data_dir()
        
        # 验证目录被创建
        assert app_data.exists()
        assert app_data.is_dir()
    
    def test_get_app_data_dir_macos_path(self, tmp_path, monkeypatch):
        """测试 macOS 平台的应用数据目录路径格式"""
        from src.utils.paths import get_app_data_dir
        
        monkeypatch.setattr(sys, 'platform', 'darwin')
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        app_data = get_app_data_dir()
        
        # 验证路径包含正确的组件
        assert "Application Support" in str(app_data)
        assert "Hive Connect" in str(app_data)
    
    def test_get_app_data_dir_other_platform_path(self, tmp_path, monkeypatch):
        """测试其他平台的应用数据目录路径格式"""
        from src.utils.paths import get_app_data_dir
        
        monkeypatch.setattr(sys, 'platform', 'linux')
        monkeypatch.setattr(Path, 'home', lambda: tmp_path)
        
        app_data = get_app_data_dir()
        
        # 验证路径包含正确的组件
        assert ".hive_connect" in str(app_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
