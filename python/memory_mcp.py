from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from memory_client import get_memory_client
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
async def add_memories(text: str) -> str:
    memory_client = get_memory_client_safe()
    return memory_client

@mcp.tool()
def search_memory():
    return "search_memory"

@mcp.tool()
def list_memories():
    return "list_memories"

if __name__ == "__main__":
    mcp.run("sse")