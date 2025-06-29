"""
Database configuration management
"""
import os
from typing import Optional

from dataclasses import dataclass

@dataclass
class EmbeddingConfig:
    """Embedding 模型配置，兼容 QwenEmbedding """
    api_key: Optional[str] = None
    model: str = "text-embedding-v4"
    dimensions: int = 1024
    encoding_format: str = "float"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    @classmethod
    def from_env(cls, prefix: str = "EMBEDDING") -> "EmbeddingConfig":
        """从环境变量读取 embedding 配置"""
        return cls(
            api_key=os.getenv(f"{prefix}_API_KEY") or os.getenv("DASHSCOPE_API_KEY"),
            model=os.getenv(f"{prefix}_MODEL", "text-embedding-v4"),
            dimensions=1024,  # 固定维度
            encoding_format="float",  # 固定编码格式
            base_url=os.getenv(f"{prefix}_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        )
    
    def get_config(self) -> dict:
        """返回用于初始化 QwenEmbedding 的配置字典"""
        return {
            'api_key': self.api_key,
            'model': self.model,
            'dimensions': self.dimensions,
            'encoding_format': self.encoding_format,
            'base_url': self.base_url
        }
    
@dataclass 
class LlmConfig:
    """Llm 模型配置"""
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000
    top_p: float = 0.1
    top_k: int = 1

    @classmethod
    def from_env(cls, prefix: str = "LLM") -> "LlmConfig":
        """从环境变量读取 LLM 配置"""
        return cls(
            model=os.getenv(f"{prefix}_MODEL", "deepseek-chat"),
            base_url=os.getenv(f"{prefix}_BASE_URL", "https://api.deepseek.com"),
            api_key=os.getenv(f"{prefix}_API_KEY") or os.getenv("CHAT_API_KEY"),
            temperature=0.1,  # 固定参数
            max_tokens=2000,  # 固定参数
            top_p=0.1,  # 固定参数
            top_k=1  # 固定参数
        )
    
    def get_config(self) -> dict:
        """返回用于初始化 DeepSeekLLM 的配置字典"""
        return {
            'model': self.model,
            'base_url': self.base_url,
            'api_key': self.api_key,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'top_k': self.top_k
        }
    
    def validate(self):
        """Validate LLM configuration"""
        if not self.model or not self.base_url:
            raise ValueError("LLM configuration must include 'model' and 'base_url'")
        if not self.base_url.startswith("http"):
            raise ValueError("LLM base_url must start with 'http' or 'https'")
        if not self.api_key:
            raise ValueError("LLM API key must be provided")

@dataclass
class SQLiteConfig:
    """SQLite database configuration"""
    db_path: str = "conversations.db"
    table_name: str = "conversations"
    enable_wal: bool = True  # Write-Ahead Logging for better performance
    timeout: int = 30  # Connection timeout in seconds
    
    @classmethod
    def from_env(cls, prefix: str = "SQLITE") -> "SQLiteConfig":
        """Create SQLite config from environment variables"""
        return cls(
            db_path=os.getenv(f"{prefix}_DB_PATH", "conversations.db"),
            table_name=os.getenv(f"{prefix}_TABLE_NAME", "conversations"),
            enable_wal=os.getenv(f"{prefix}_ENABLE_WAL", "true").lower() == "true",
            timeout=int(os.getenv(f"{prefix}_TIMEOUT", "30"))
        )
    
    def get_config(self) -> dict:
        """返回用于初始化 SQLite 相关组件的配置字典"""
        return {
            'db_path': self.db_path,
            'table_name': self.table_name,
            'enable_wal': self.enable_wal,
            'timeout': self.timeout
        }

@dataclass
class ChromaDBConfig:
    """ChromaDB configuration class"""
    collection_name: str = "openmemory"
    path: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    
    @classmethod
    def from_env(cls) -> 'ChromaDBConfig':
        """Create ChromaDBConfig from environment variables"""
        return cls(
            collection_name=os.getenv("CHROMA_COLLECTION_NAME", "openmemory"),
            path=os.getenv("CHROMA_DB_PATH", "data/chroma_db_store"),
            host=os.getenv("CHROMA_HOST") if os.getenv("CHROMA_HOST") else None,
            port=int(os.getenv("CHROMA_PORT")) if os.getenv("CHROMA_PORT") else None,
        )
    
    def get_config(self) -> dict:
        """返回用于初始化 ChromaDB 的配置字典"""
        return {
            'collection_name': self.collection_name,
            'path': self.path,
            'host': self.host,
            'port': self.port
        }
    
    def validate(self):
        """Validate configuration"""
        if not self.path and not (self.host and self.port):
            raise ValueError("Either 'path' or both 'host' and 'port' must be provided for ChromaDB")
        
@dataclass
class Neo4jConfig:
    """Neo4j database configuration"""
    url: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"
    database: str = "neo4j"

    @classmethod
    def from_env(cls) -> 'Neo4jConfig':
        """Create Neo4jConfig from environment variables"""
        return cls(
            url=os.getenv("NEO4J_URL", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            database=os.getenv("NEO4J_DATABASE", "neo4j")
        )
    
    def get_config(self) -> dict:
        """返回用于初始化 Neo4j 驱动的配置字典"""
        return {
            'url': self.url,
            'user': self.user,
            'password': self.password,
            'database': self.database
        }
    
    def validate(self):
        """Validate Neo4j configuration"""
        if not self.url or not self.user or not self.password:
            raise ValueError("Neo4j configuration must include 'url', 'user', and 'password'")
        if not self.url.startswith("bolt://"):
            raise ValueError("Neo4j URI must start with 'bolt://'")
