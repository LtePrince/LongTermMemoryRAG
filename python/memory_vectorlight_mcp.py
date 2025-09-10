from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Union, List
from memoryrag.vector_store.light_vector_store import *

from memoryrag.config import EmbeddingConfig, ChromaDBConfig
from memoryrag.embedding import QwenEmbedding

load_dotenv()

mcp = FastMCP("vector-rag-memory",version="0.1.0")