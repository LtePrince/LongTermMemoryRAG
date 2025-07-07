import importlib
import logging
from typing import List, Dict, Any, Optional
import uuid # 用于生成唯一ID
import json # 用于解析LLM的JSON输出
import time # 用于时间戳

try:
    from langchain_neo4j import Neo4jGraph
except ImportError:
    raise ImportError("langchain_neo4j is not installed. Please install it using pip install langchain-neo4j")

# 新的配置和组件导入
from memoryrag.embedding import QwenEmbedding
from memoryrag.llm import DeepSeekLLM
from memoryrag.config import EmbeddingConfig, LlmConfig

import json

logger = logging.getLogger(__name__)

class LightNeo4jMemory:
    def __init__(self, config):
        self.config = config
        self.graph = Neo4jGraph(
            self.config.url,
            self.config.username,
            self.config.password,
            self.config.database,
            refresh_schema=False,
        )
        self.user_id = None

        self._ensure_vector_index()

    def _ensure_vector_index(self):
        """确保Paragraph节点上的embedding属性有向量索引。"""
        index_name = "paragraph_embedding_index"
        dimension = 1024 # 根据你的QwenEmbedding模型实际输出维度设置
        try:
            # 使用IF NOT EXISTS避免重复创建报错
            self.graph.query(f"""
                CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                FOR (p:Paragraph) ON (p.embedding)
                OPTIONS {{indexConfig: {{
                    `vector.dimensions`: {dimension},
                    `vector.similarity_function`: 'cosine'
                }}}}
            """)
            # print(f"Ensured vector index '{index_name}' exists for :Paragraph(embedding).")
        except Exception as e:
            print(f"Error ensuring vector index: {e}. Please check Neo4j version (>=5.x) and permissions.")

    def add_node(self, node_type: str, properties: Dict[str, Any]) -> str:
        """
        添加节点到图数据库
        Args:
            node_type: 节点类型（如 'User', 'Agent', 'Message' 等）
            properties: 节点属性字典
        Returns:
            新节点的唯一ID
        """
        node_id = str(uuid.uuid4())
        properties['id'] = node_id
        query = f"""
            CREATE (n:{node_type} $properties)
            RETURN n.id AS id
        """
        result = self.graph.query(query, params={"properties": properties})
        if result:
            node_id = result[0]['id']
            logger.info(f"Added {node_type} node with ID: {node_id}")
        else:
            logger.error(f"Failed to add {node_type} node with properties: {properties}")
            raise Exception(f"Failed to add {node_type} node")
        return node_id
    
    def add_relationship(self, start_node_id: str, end_node_id: str, rel_type: str, properties: Optional[Dict[str, Any]] = None):
        """
        添加关系到图数据库
        Args:
            start_node_id: 起始节点ID
            end_node_id: 结束节点ID
            rel_type: 关系类型（如 'BELONGS_TO', 'HAS_MESSAGE' 等）
            properties: 关系属性字典（可选）
        """
        # 检查起始节点是否存在
        start_exists = self.graph.query(
            "MATCH (n) WHERE n.id = $id RETURN n LIMIT 1", params={"id": start_node_id}
        )
        if not start_exists:
            logger.error(f"Start node with id {start_node_id} does not exist.")
            raise Exception(f"Start node with id {start_node_id} does not exist.")

        # 检查结束节点是否存在
        end_exists = self.graph.query(
            "MATCH (n) WHERE n.id = $id RETURN n LIMIT 1", params={"id": end_node_id}
        )
        if not end_exists:
            logger.error(f"End node with id {end_node_id} does not exist.")
            raise Exception(f"End node with id {end_node_id} does not exist.")
        query = f"""
            MATCH (a), (b)
            WHERE a.id = $start_id AND b.id = $end_id
            CREATE (a)-[r:{rel_type} $properties]->(b)
        """
        parameters = {
            "start_id": start_node_id,
            "end_id": end_node_id,
            "properties": properties or {}
        }
        self.graph.query(query, params=parameters)
        logger.info(f"Added relationship {rel_type} from {start_node_id} to {end_node_id}")

    def update_node(self, node_id: str, properties: Dict[str, Any]):
        """        更新节点属性
        Args:
            node_id: 节点ID
            properties: 要更新的属性字典
        """
        query = f"""
            MATCH (n) WHERE n.id = $id
            SET n += $properties
        """
        parameters = {
            "id": node_id,
            "properties": properties
        }
        self.graph.query(query, params=parameters)
        logger.info(f"Updated node {node_id} with properties: {properties}")

    def delete_node(self, node_id: str):
        """
        删除节点及其所有关系
        Args:
            node_id: 要删除的节点ID
        """
        query = f"""
            MATCH (n) WHERE n.id = $id
            DETACH DELETE n
        """
        parameters = {"id": node_id}
        self.graph.query(query, params=parameters)
        logger.info(f"Deleted node {node_id} and all its relationships")    

    def delete_relationship(self, start_node_id: str, end_node_id: str, rel_type: str):
        """
        删除两个节点之间的关系
        Args:
            start_node_id: 起始节点ID
            end_node_id: 结束节点ID
            rel_type: 关系类型
        """
        # 检查起始节点是否存在
        start_exists = self.graph.query(
            "MATCH (n) WHERE n.id = $id RETURN n LIMIT 1", params={"id": start_node_id}
        )
        if not start_exists:
            logger.error(f"Start node with id {start_node_id} does not exist.")
            raise Exception(f"Start node with id {start_node_id} does not exist.")

        # 检查结束节点是否存在
        end_exists = self.graph.query(
            "MATCH (n) WHERE n.id = $id RETURN n LIMIT 1", params={"id": end_node_id}
        )
        if not end_exists:
            logger.error(f"End node with id {end_node_id} does not exist.")
            raise Exception(f"End node with id {end_node_id} does not exist.")
        query = f"""
            MATCH (a)-[r:{rel_type}]->(b)
            WHERE a.id = $start_id AND b.id = $end_id
            DELETE r
        """
        parameters = {
            "start_id": start_node_id,
            "end_id": end_node_id
        }
        self.graph.query(query, params=parameters)
        logger.info(f"Deleted relationship {rel_type} from {start_node_id} to {end_node_id}")

    def search_nodes(self, node_type: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        根据类型和过滤条件搜索节点
        Args:
            node_type: 节点类型（如 'User', 'Agent', 'Message' 等）
            filters: 过滤条件字典（可选）
        Returns:
            符合条件的节点列表
        """
        query = f"MATCH (n:{node_type})"
        if filters:
            filter_clauses = [f"n.{k} = ${k}" for k in filters.keys()]
            query += " WHERE " + " AND ".join(filter_clauses)
        query += " RETURN n"
        
        parameters = filters or {}
        results = self.graph.query(query, params=parameters)
        return [dict(record['n']) for record in results]

    def search_relationships(self, start_node_id: str, rel_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        根据起始节点ID和关系类型搜索关系
        Args:
            start_node_id: 起始节点ID
            rel_type: 关系类型（可选）
        Returns:
            符合条件的关系列表
        """
        query = f"MATCH (a)-[r"
        if rel_type:
            query += f":{rel_type}"
        query += f"]->(b) WHERE a.id = $start_id RETURN r, b"
        
        parameters = {"start_id": start_node_id}
        results = self.graph.query(query, params=parameters)
        
        formatted_results = []
        for record in results:
            try:
                rel_dict = {}
                node_dict = {}
                
                # 安全地转换关系对象
                if hasattr(record['r'], '_properties'):
                    rel_dict = dict(record['r']._properties)
                elif hasattr(record['r'], '__dict__'):
                    rel_dict = record['r'].__dict__
                else:
                    rel_dict = dict(record['r']) if record['r'] else {}
                
                # 安全地转换节点对象
                if hasattr(record['b'], '_properties'):
                    node_dict = dict(record['b']._properties)
                elif hasattr(record['b'], '__dict__'):
                    node_dict = record['b'].__dict__
                else:
                    node_dict = dict(record['b']) if record['b'] else {}
                
                formatted_results.append({
                    "relationship": rel_dict,
                    "end_node": node_dict
                })
            except Exception as e:
                logger.warning(f"Error converting relationship record: {e}")
                continue
        
        return formatted_results   