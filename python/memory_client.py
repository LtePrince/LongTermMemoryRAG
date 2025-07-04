import logging
import threading
from typing import Optional, Dict
from memoryrag.memory import Memory, PATTERN

logger = logging.getLogger(__name__)

# 线程锁，确保线程安全
_lock = threading.Lock()
# 存储不同模式的客户端实例
_memory_clients: Dict[PATTERN, Memory] = {}


def get_memory_client(pattern: PATTERN = PATTERN.GRAPH) -> Optional[Memory]:
    """
    获取内存客户端实例（单例模式）
    Args:
        pattern: 存储模式，默认为图模式
    Returns:
        Memory 实例，初始化失败时返回 None   
    Thread-safe: 是
    """
    global _memory_clients
    
    with _lock:
        # 如果客户端不存在，尝试创建
        if pattern not in _memory_clients:
            try:
                logger.info(f"正在初始化内存客户端，模式: {pattern.value}")
                _memory_clients[pattern] = Memory(pattern)
                
            except Exception as e:
                logger.error(f"内存客户端初始化失败，模式: {pattern.value}, 错误: {e}")
                return None
        
        return _memory_clients.get(pattern)