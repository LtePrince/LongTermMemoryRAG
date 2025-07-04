from enum import Enum
import logging
from typing import Optional, Dict, Any

from memoryrag.config.config import ChromaDBConfig, EmbeddingConfig, LlmConfig, Neo4jConfig
from memoryrag.vector_store import ChromaDB
from memoryrag.graph_store import Neo4jMemory
from memoryrag.llm import DeepSeekLLM
from memoryrag.embedding import QwenEmbedding

logger = logging.getLogger(__name__)


class PATTERN(Enum):
    """内存存储模式枚举"""
    GRAPH = "graph"
    VECTOR = "vector"
    HYBRID = "hybrid"

class Memory:
    """
    记忆管理类，用于管理对话记忆。
    
    支持三种存储模式：
    - GRAPH: 图数据库存储
    - VECTOR: 向量数据库存储  
    - HYBRID: 图+向量混合存储
    """
    def __init__(self, pattern: PATTERN = PATTERN.GRAPH):
        """
        初始化记忆管理器
        Args:
            pattern: 存储模式，默认为图模式
        """
        self.pattern = pattern
        
        # 初始化通用组件
        self._init_common_components()
        # 初始化存储组件
        self._init_storage_components()
        
        logger.info(f"记忆管理器初始化完成，使用模式: {pattern.value}")

    def _init_common_components(self):
        """初始化通用组件（embedding 和 LLM）"""
        # 嵌入模型配置
        embedding_config = EmbeddingConfig.from_env()
        self.embedding = QwenEmbedding(embedding_config.get_config())
        # LLM 配置
        llm_config = LlmConfig.from_env()
        self.llm = DeepSeekLLM(llm_config.get_config())

    def _init_storage_components(self):
        """根据模式初始化存储组件"""
        # 初始化存储状态
        self.graph: Optional[Neo4jMemory] = None
        self.vector: Optional[ChromaDB] = None
        self.enable_graph = False
        self.enable_vector = False
        # 根据模式创建相应的存储客户端
        if self.pattern in [PATTERN.GRAPH, PATTERN.HYBRID]:
            self._init_graph_storage()
            
        if self.pattern in [PATTERN.VECTOR, PATTERN.HYBRID]:
            self._init_vector_storage()

    def _init_graph_storage(self):
        """初始化图存储"""
        try:
            graph_config = Neo4jConfig.from_env()
            self.graph = Neo4jMemory(graph_config)
            self.enable_graph = True
            logger.info("图存储客户端初始化成功")
        except Exception as e:
            logger.error(f"图存储客户端初始化失败: {e}")
            raise

    def _init_vector_storage(self):
        """初始化向量存储"""
        try:
            vector_config = ChromaDBConfig.from_env()
            self.vector = ChromaDB(vector_config.get_config())
            self.enable_vector = True
            logger.info("向量存储客户端初始化成功")
        except Exception as e:
            logger.error(f"向量存储客户端初始化失败: {e}")
            raise

    def add(self, messages: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        添加消息到记忆中
        Args:
            messages: 要添加的消息内容
            filters: 过滤条件（用户ID、代理ID等） 
        Returns:
            添加结果的字典
        """
        if not messages:
            raise ValueError("消息内容不能为空")
            
        results = {}
        
        try:
            # 根据启用的存储模式添加消息
            if self.enable_graph:
                results['graph'] = self._add_to_graph(messages, filters)
            if self.enable_vector:
                results['vector'] = self._add_to_vector(messages, filters)
            logger.info(f"消息添加成功，模式: {self.pattern.value}")
            return results
            
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            raise

    def _add_to_graph(self, messages: str, filters: Optional[Dict[str, Any]]) -> Any:
        """添加消息到图存储"""
        return "add to graph"

    def _add_to_vector(self, messages: str, filters: Optional[Dict[str, Any]]) -> Any:
        return "add to vector"

    def search():
        pass

    def update():
        pass

    def get():
        pass

    def get_all():
        pass

    def delete():
        pass

    def reset():
        pass

