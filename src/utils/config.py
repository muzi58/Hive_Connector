"""
配置管理模块
管理连接配置的持久化存储
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ConnectionConfig:
    """Hive 连接配置"""
    name: str
    host: str
    port: int = 10000
    database: str = "default"
    username: str = ""
    password: str = ""
    auth_mechanism: str = "PLAIN"  # PLAIN, NOSASL, LDAP
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConnectionConfig":
        return cls(**data)


@dataclass 
class AppConfig:
    """应用配置"""
    connections: list[ConnectionConfig] = field(default_factory=list)
    last_connection: Optional[str] = None
    query_history: list[str] = field(default_factory=list)
    max_history: int = 50
    open_queries: list[str] = field(default_factory=lambda: [""])  # 当前打开的查询内容
    
    def to_dict(self) -> dict:
        return {
            "connections": [c.to_dict() for c in self.connections],
            "last_connection": self.last_connection,
            "query_history": self.query_history,
            "max_history": self.max_history,
            "open_queries": self.open_queries
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        connections = [ConnectionConfig.from_dict(c) for c in data.get("connections", [])]
        return cls(
            connections=connections,
            last_connection=data.get("last_connection"),
            query_history=data.get("query_history", []),
            max_history=data.get("max_history", 50),
            open_queries=data.get("open_queries", [""])
        )


from src.utils.paths import get_app_data_dir


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self.config_dir = get_app_data_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return AppConfig.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass
        return AppConfig()
    
    def save(self):
        """保存配置"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config.to_dict(), f, indent=2, ensure_ascii=False)
    
    def add_connection(self, conn: ConnectionConfig):
        """添加连接"""
        # 检查是否已存在同名连接
        for i, c in enumerate(self.config.connections):
            if c.name == conn.name:
                self.config.connections[i] = conn
                self.save()
                return
        self.config.connections.append(conn)
        self.save()
    
    def remove_connection(self, name: str):
        """删除连接"""
        self.config.connections = [c for c in self.config.connections if c.name != name]
        self.save()
    
    def get_connection(self, name: str) -> Optional[ConnectionConfig]:
        """获取连接配置"""
        for c in self.config.connections:
            if c.name == name:
                return c
        return None
    
    def add_to_history(self, sql: str):
        """添加查询历史"""
        sql = sql.strip()
        if not sql:
            return
        # 移除重复
        if sql in self.config.query_history:
            self.config.query_history.remove(sql)
        self.config.query_history.insert(0, sql)
        # 限制数量
        self.config.query_history = self.config.query_history[:self.config.max_history]
        self.save()


# 全局配置实例
config_manager = ConfigManager()
