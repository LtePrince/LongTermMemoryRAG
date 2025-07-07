from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Union, List
from memoryrag.graph_store.light_neo4j import LightNeo4jMemory

from memoryrag.config import EmbeddingConfig, Neo4jConfig
from memoryrag.embedding import QwenEmbedding

load_dotenv()

mcp = FastMCP("graph-rag-memory",version="0.1.0")
config = Neo4jConfig().from_env()
light_memory_client = LightNeo4jMemory(config)
embeder = QwenEmbedding(EmbeddingConfig.from_env().get_config())

light_memory_client._ensure_vector_index()

@mcp.tool(description="Add node extracted from messages to graph memory. The properties should include 'id', 'name', 'type', 'description', 'created_at', and 'updated_at'.")
async def add_node(node_type: str, properties: Dict[str, Any]):
    properties['embedding'] = embeder.embed(properties.get('description', ''))
    result = await light_memory_client.add_node(node_type, properties)
    return result

@mcp.tool(description="Add relationship between two nodes. The properties should include 'start_node_id', 'end_node_id', 'rel_type', 'description' and 'created_at'")
async def add_relationship(start_node_id: str, end_node_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None):
    result = await light_memory_client.add_relationship(start_node_id, end_node_id, rel_type, properties)
    return result

@mcp.tool(description="Update a node in the graph, change its properties. The properties may include 'id', 'name', 'type', 'description', 'created_at', and 'updated_at'.  ")
async def update_node(node_id: str, properties: Dict[str, Any]):
    result = await light_memory_client.update_node(node_id, properties)
    return result

@mcp.tool(description="Delete a node and all of its relationships from the graph, to use this tool, you should search the node first and get its id.")
async def delete_node(node_id: str):
    result = await light_memory_client.delete_node(node_id)
    return result

@mcp.tool(description="Delete a relationship between two nodes, to use this tool, you should search the relationship first and get the start_node_id, end_node_id and rel_type.")
async def delete_relationship(start_node_id: str, end_node_id: str, rel_type: str):
    result = await light_memory_client.delete_relationship(start_node_id, end_node_id, rel_type)
    return result

@mcp.tool(description="Search for nodes in the graph, you can specify the node type and filters. The filters should be a dictionary with keys like 'id', 'name', 'type', etc.")
async def search_nodes(node_type: str, filters: Optional[Dict[str, Any]] = None):
    result = await light_memory_client.search_nodes(node_type, filters)
    return result

@mcp.tool(description="Search for relationships between two nodes, you should specify the start_node_id, end_node_id and rel_type. The result will include the relationship properties.")
async def search_relationships(start_node_id: str, end_node_id: str, rel_type: str):
    result = await light_memory_client.search_relationships(start_node_id, end_node_id, rel_type)
    return result

if __name__ == "__main__":
    mcp.run("sse")