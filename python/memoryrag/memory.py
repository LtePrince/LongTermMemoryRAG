from enum import Enum

class PATTERN(Enum):
    """
    枚举类定义不同的内存模式
    """
    GRAPH = "graph"
    VECTOR = "vector"
    HYBRID = "hybrid"

class Memory():
    """
    Memory class for managing conversation memories.
    
    This class provides methods to add, update, delete, and retrieve conversation memories.
    It uses a vector store to manage embeddings and metadata associated with conversations.
    """

    def __init__(self, pattern: PATTERN = PATTERN.GRAPH):
        self.pattern = pattern
        self._create_client()

    def _create_client(self):
        """Create and return the vector store client"""
        if self.pattern == PATTERN.GRAPH:
            # 创建图数据库客户端
            print(f"创建图存储客户端用于集合")
            return "GraphClient"  # 实际应该返回图数据库客户端
        elif self.pattern == PATTERN.VECTOR:
            # 创建向量数据库客户端
            print(f"创建向量存储客户端用于集合")
            return "VectorClient"  # 实际应该返回向量数据库客户端
        elif self.pattern == PATTERN.HYBRID:
            # 创建混合存储客户端
            print(f"创建混合存储客户端用于集合")
            return "HybridClient"  # 实际应该返回混合客户端
        else:
            raise ValueError(f"不支持的存储模式: {self.pattern}")