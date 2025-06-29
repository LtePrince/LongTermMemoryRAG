from memoryrag.memory import Memory, PATTERN

_memory_client = None

def get_memory_client(pattern: PATTERN = PATTERN.GRAPH) -> Memory:
    global _memory_client

    # 如果已经初始化过，直接返回
    if _memory_client is not None:
        return _memory_client
    try:
        _memory_client = Memory(pattern)
        return _memory_client
        
    except Exception as e:
        print(f"Warning: Exception occurred while initializing memory client: {e}")
        print("Server will continue running with limited memory functionality")
        return None