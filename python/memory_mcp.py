from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from memory_client import get_memory_client
from typing import Union, List
import logging

load_dotenv()

mcp = FastMCP("graph-rag-memory",version="0.1.0")

def get_memory_client_safe():
    """Get memory client with error handling. Returns None if client cannot be initialized."""
    try:
        return get_memory_client()
    except Exception as e:
        logging.warning(f"Failed to get memory client: {e}")
        return None

@mcp.tool()
async def add_memories(messages: Union[str, List[str]]) -> str:
    """
    添加记忆到存储中
    Args:
        messages: 要添加的消息，可以是单个字符串或字符串列表
    Returns:
        操作结果的字符串描述
    """
    memory_client = get_memory_client_safe()
    if not memory_client:
        return "Memory client not available"
    
    if not messages:
        return "No messages to add"
    
    try:
        # 将消息标准化为列表（根据Memory.add方法的期望）
        if isinstance(messages, str):
            # 如果是字符串，转换为列表
            message_list = [messages]
        else:
            # 如果是列表，直接使用
            message_list = messages
        
        # 调用memory客户端的add方法
        result = memory_client.add(message_list)
        return f"Successfully added memories: {result}."
        
    except Exception as e:
        logging.error(f"Failed to add memories: {e}")
        return f"Failed to add memories: {str(e)}"

@mcp.tool()
def search_memory():
    return "search_memory"

@mcp.tool()
def list_memories():
    return "list_memories"

if __name__ == "__main__":
    mcp.run("sse")