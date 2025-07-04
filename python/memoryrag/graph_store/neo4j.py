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

from memoryrag.utils.prompt import (
    EXTRACT_ENTITIES_PROMPT, 
    EXTRACT_RELATIONS_PROMPT
    )
from memoryrag.utils.tools import EXTRACT_ENTITIES_TOOL, RELATIONS_TOOL
import json

logger = logging.getLogger(__name__)

class Neo4jMemory:
    def __init__(self, config):
        self.config = config
        self.graph = Neo4jGraph(
            self.config.url,
            self.config.username,
            self.config.password,
            self.config.database,
            refresh_schema=False,
        )
        
        # 使用新的初始化方式
        embedding_config = EmbeddingConfig.from_env()
        self.embedding_model = QwenEmbedding(embedding_config.get_config())
        
        # 初始化 LLM 模型
        llm_config = LlmConfig.from_env()
        self.llm = DeepSeekLLM(llm_config.get_config())

        self.llm_provider = "deepseek"  # 固定使用 deepseek
        self.user_id = None

        # 阈值配置
        self.merge_threshold = 0.85     # 语义相似度高于此值，倾向于合并
        self.split_threshold_len = 500  # 段落文本长度超过此值，考虑分裂
        self.split_threshold_entities = 10 # 段落关联实体数量超过此值，考虑分裂
        self.prompt_user_threshold = 0.6 # 相似度在此值与 merge_threshold 之间，考虑询问用户

        # 确保Neo4j中存在向量索引 (仅在初始化时尝试创建一次)
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

    def _generate_embedding(self, text: str) -> List[float]:
        """生成文本的向量嵌入。"""
        try:
            return self.embedding_model.embed(text)
        except Exception as e:
            print(f"Error generating embedding for text: '{text[:50]}...' - {e}")
            return []

    def _summarize_text(self, text: str) -> str:
        """使用LLM总结文本，提取核心信息。"""
        prompt = f"请简洁地总结以下对话段落，提取其核心信息和关键主题。限制在50字以内。\n\n对话段落：{text}"
        messages = [{"role": "user", "content": prompt}]
        try:
            return self.llm.generate_response(messages)
        except Exception as e:
            print(f"Error summarizing text: '{text[:50]}...' - {e}")
            return text # 失败时返回原始文本

    def _extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """使用LLM从文本中提取实体和关系，返回结构化JSON。"""
        prompt = f"""
        从以下文本中提取关键实体（Concept or Entity二选一）以及它们之间的关系。
        请以JSON格式返回结果，格式如下：
        {{
            "entities": [
                {{"name": "实体名称", "type": "实体类型", "description": "描述，不超过20字"}},
                // ...
            ],
            "relations": [
                {{"source": "源实体名称", "target": "目标实体名称", "type": "关系类型", "description": "描述，不超过20字"}},
                // ...
            ]
        }}
        实体类型，和关系名称必须为英文大写，空格转下划线。
        如果无法提取实体或关系，则返回空列表。请确保JSON格式严格正确，并仅包含JSON内容。

        
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"文本：{text}"}
        ]
        try:
            llm_response = self.llm.generate_response(messages, response_format="json_object")
            # 尝试解析LLM的JSON输出
            parsed_data = json.loads(llm_response)
            return {
                "entities": parsed_data.get("entities", []),
                "relations": parsed_data.get("relations", [])
            }
        except json.JSONDecodeError as e:
            print(f"LLM did not return valid JSON for extraction: {e}. Response: {llm_response[:200]}...")
            return {"entities": [], "relations": []}
        except Exception as e:
            print(f"Error during entity/relation extraction: {e}. LLM response: {llm_response[:200]}...")
            return {"entities": [], "relations": []}

    def _add_or_merge_node_and_connect(self, node_data: Dict, source_paragraph_id: str):
        """
        辅助方法：将单个实体或概念添加到图中，如果存在则合并，并连接到源段落。
        Args:
            node_data: 包含 'name', 'type', 'description' 的字典。
            source_paragraph_id: 节点所属的 Paragraph ID。
        """
        name = node_data.get("name")
        node_type = node_data.get("type", "Generic") # 默认为 Generic，但会检查是否是Concept
        description = node_data.get("description", "")
        
        if not name: return

        # 根据类型决定节点标签和关系类型
        if node_type == "Concept":
            label = "Concept"
            rel_to_paragraph_type = "MENTIONS_CONCEPT"
        else: # 默认为 Entity，或 LLM 识别出的其他实体类型
            label = "Entity"
            rel_to_paragraph_type = "CONTAINS_ENTITY"

        # MERGE 节点，并更新时间戳和属性
        merge_node_query = f"""
        MERGE (n:{label} {{name: $name}})
        ON CREATE SET n.type = $type, n.description = $description, n.first_mentioned = datetime(), n.last_mentioned = datetime()
        ON MATCH SET n.last_mentioned = datetime(), n.description = COALESCE(n.description, $description)
        WITH n
        MATCH (p:Paragraph {{id: $source_paragraph_id}})
        MERGE (p)-[r:{rel_to_paragraph_type}]->(n)
        """
        self.graph.query(merge_node_query, params={
            "name": name,
            "type": node_type, # 存储原始的 type 属性
            "description": description,
            "source_paragraph_id": source_paragraph_id
        })
        # print(f"Merged/Added {label}: {name}, linked to Paragraph: {source_paragraph_id} by {rel_to_paragraph_type}")

    def _add_or_update_relation(self, relation_data: Dict, paragraph_id: str):
        """辅助方法：将单个关系添加到图中，如果存在则更新。"""
        source_name = relation_data.get("source")
        target_name = relation_data.get("target")
        rel_type = relation_data.get("type", "RELATES_TO").upper().replace(" ", "_") # 关系类型转大写，空格转下划线
        description = relation_data.get("description", "")

        if not source_name or not target_name: return

        # 确保源和目标实体存在，然后MERGE关系
        merge_relation_query = f"""
        MATCH (source:Entity {{name: $source_name}})
        MATCH (target:Entity {{name: $target_name}})
        MERGE (source)-[r:{rel_type}]->(target)
        ON CREATE SET r.description = $description, r.source_paragraph_id = $paragraph_id, r.timestamp = datetime()
        ON MATCH SET r.timestamp = datetime(), r.description = COALESCE(r.description, $description) // 更新描述
        RETURN r
        """
        self.graph.query(merge_relation_query, params={
            "source_name": source_name,
            "target_name": target_name,
            "type": rel_type,
            "description": description,
            "paragraph_id": paragraph_id
        })
        # print(f"Merged/Added Relation: ({source_name})-[:{rel_type}]->({target_name}) from Paragraph: {paragraph_id}")

    def _clean_paragraph_relations(self, paragraph_id: str):
        """删除一个段落的所有直接关系 (CONTAINS_ENTITY, MENTIONS_CONCEPT, FOLLOWS)。"""
        query = f"""
        MATCH (p:Paragraph {{id: $paragraph_id}})-[r]-()
        DELETE r
        """
        self.graph.query(query, params={"paragraph_id": paragraph_id})
        # print(f"Cleaned all relations for Paragraph: {paragraph_id}")

    def _detect_similar_paragraphs(self, new_paragraph_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """检测图中与新段落语义相似的现有段落。"""
        if not new_paragraph_embedding:
            return []
        
        query = f"""
        CALL db.index.vector.queryNodes('paragraph_embedding_index', $top_k, $embedding)
        YIELD node AS p, score
        WHERE score >= $min_score
        RETURN p.id AS id, p.text AS text, p.summary AS summary, score
        ORDER BY score DESC
        """
        results = self.graph.query(query, params={
            "embedding": new_paragraph_embedding,
            "top_k": top_k,
            "min_score": self.prompt_user_threshold # 只考虑可能合并或需要确认的范围
        })
        return results
    
    def _prompt_user_for_confirmation(self, new_text: str, existing_paragraph: Dict) -> str:
        """
        利用LLM模拟询问用户以确认合并或建立关系。
        在实际系统中，这将是一个交互式过程。
        返回值模拟用户的选择，可以是 'merge', 'new', 'relate:<relation_type>'
        """
        existing_summary = existing_paragraph.get("summary", existing_paragraph.get("text", "无摘要"))
        prompt = f"""
        检测到一段新信息与现有记忆可能相关。请判断如何处理：

        现有记忆摘要："{existing_summary[:100]}..."
        新信息内容："{new_text[:100]}..."

        1. 是否认为新信息是现有记忆的**补充或更新**？ (选择 'merge')
        2. 还是认为新信息是**一个全新的话题**？ (选择 'new')
        3. 或者，新信息与现有记忆之间存在**特定关系**（如 '相关', '导致', '前提' 等）？
           如果是，请明确指出关系类型 (例如: 'relate:补充', 'relate:导致').

        请只回复 'merge', 'new', 或 'relate:<关系类型>'。
        """
        messages = [{"role": "user", "content": prompt + "\n\n请严格按照指定格式返回一个词或短语作为决策："}]
        try:
            # 实际系统中，这里会通过对话系统与用户交互
            # 这里的LLM调用是模拟用户决策，而非直接决策
            user_decision = self.llm.generate_response(messages)
            user_decision = user_decision.strip().lower()

            if user_decision == "merge":
                return "merge"
            elif user_decision == "new":
                return "new"
            elif user_decision.startswith("relate:"):
                # 提取关系类型，去除 'relate:' 前缀
                relation_type = user_decision[len("relate:"):].strip()
                if relation_type:
                    return f"relate:{relation_type}"
            
            print(f"LLM模拟用户决策时返回未知格式: {user_decision}, 默认为'new'")
            return "new" # 默认创建新节点
        except Exception as e:
            print(f"Error simulating user confirmation: {e}. Defaulting to 'new'.")
            return "new"

    def _split_paragraph(self, paragraph_id: str, original_text: str):
        """
        辅助方法：当Paragraph过大时，利用LLM进行分裂。
        将一个大Paragraph分裂为多个小Paragraph或Concept节点。
        """
        print(f"Attempting to split large Paragraph: {paragraph_id}")
        prompt = f"""
        以下是一个较长的对话或信息段落，请将其分解为多个逻辑上独立但相互关联的子段落或核心概念。
        对每个子段落或概念，提供其文本（如果需要新的Paragraph）或名称（如果是一个Concept），以及与原始段落的关系类型（例如：CONTAINS_SUBTOPIC, MENTIONS_CONCEPT ）。
        请以JSON格式返回结果，格式如下：
        {{
            "splits": [
                {{
                    "type": "Paragraph" | "Concept",
                    "id": "新的唯一ID",
                    "content": "文本内容" | "概念名称",
                    "relationship_type_to_original": "CONTAINS_SUBTOPIC" // 或 MENTION_CONCEPT 等
                }},
                // ...
            ]
        }}
        原始段落：{original_text}
        """
        messages = [{"role": "user", "content": prompt}]
        try:
            llm_response = self.llm.generate_response(messages, response_format="json_object")
            split_data = json.loads(llm_response)
            
            if not split_data or not split_data.get("splits"):
                print(f"LLM returned no valid splits for {paragraph_id}.")
                return

            original_summary = self._summarize_text(original_text)

            # 更新原节点为“容器”或“摘要”
            update_original_query = f"""
            MATCH (p:Paragraph {{id: $paragraph_id}})
            SET p.text = $original_text, p.summary = $original_summary, p.is_container = TRUE, p.embedding = $embedding
            """
            self.graph.query(update_original_query, params={
                "paragraph_id": paragraph_id,
                "original_text": f"此段落已分裂，其核心内容已分解至子节点。原始摘要：{original_summary}",
                "original_summary": original_summary,
                "embedding": self._generate_embedding(original_summary) # 容器节点使用摘要嵌入
            })
            
            for split_item in split_data["splits"]:
                split_type = split_item.get("type")
                split_content = split_item.get("content")
                new_split_id = str(uuid.uuid4())
                rel_type_to_original = split_item.get("relationship_type_to_original", "CONTAINS_SUBTOPIC").upper().replace(" ", "_")

                if not split_content: continue

                if split_type == "Paragraph":
                    # --- DEBUG: 验证原始 Paragraph 节点是否存在 ---
                    check_paragraph_query = """
                    MATCH (op:Paragraph {id: $original_id})
                    RETURN op.id AS foundId
                    """
                    found_paragraph_result = self.graph.query(check_paragraph_query, params={"original_id": paragraph_id})

                    if not found_paragraph_result:
                        print(f"DEBUG ALERT: Original Paragraph with ID '{paragraph_id}' NOT FOUND. Skipping MENTIONS_CONCEPT creation.")
                        return # 或者 break/continue，避免尝试创建关系
                    else:
                        print(f"DEBUG: Original Paragraph '{found_paragraph_result[0]['foundId']}' found for linking Concept.")
                    # --- END DEBUG DEBUG ---
                    # 创建新的Paragraph节点
                    new_embedding = self._generate_embedding(split_content)
                    new_summary = self._summarize_text(split_content)
                    create_split_paragraph_query = f"""
                    CREATE (sp:Paragraph {{
                        id: $new_id,
                        text: $content,
                        summary: $summary,
                        timestamp: datetime(),
                        embedding: $embedding
                    }})
                    WITH sp
                    MATCH (op:Paragraph {{id: $original_id}})
                    CREATE (op)-[r:{rel_type_to_original}]->(sp)
                    """
                    self.graph.query(create_split_paragraph_query, params={
                        "new_id": new_split_id,
                        "content": split_content,
                        "summary": new_summary,
                        "embedding": new_embedding,
                        "original_id": paragraph_id
                    })
                    print(f"Split to new Paragraph: {new_split_id}, linked by {rel_type_to_original}")

                    # 为新的子段落提取实体和关系
                    extracted_data = self._extract_entities_and_relations(split_content)
                    for entity_data in extracted_data["entities"]:
                        self._add_or_merge_node_and_connect(entity_data, new_split_id)
                    for relation_data in extracted_data["relations"]:
                        self._add_or_update_relation(relation_data, new_split_id)


                elif split_type == "Concept":
                    rel_type_to_original = "MENTIONS_CONCEPT"
                    # --- DEBUG: 验证原始 Paragraph 节点是否存在 ---
                    check_paragraph_query = """
                    MATCH (op:Paragraph {id: $original_id})
                    RETURN op.id AS foundId
                    """
                    found_paragraph_result = self.graph.query(check_paragraph_query, params={"original_id": paragraph_id})

                    if not found_paragraph_result:
                        print(f"DEBUG ALERT: Original Paragraph with ID '{paragraph_id}' NOT FOUND. Skipping MENTIONS_CONCEPT creation.")
                        return # 或者 break/continue，避免尝试创建关系
                    else:
                        print(f"DEBUG: Original Paragraph '{found_paragraph_result[0]['foundId']}' found for linking Concept.")
                    # --- END DEBUG DEBUG ---
                    # 创建新的Concept节点
                    merge_concept_query = f"""
                    MERGE (c:Concept {{name: $name}})
                    ON CREATE SET c.description = $description, c.first_mentioned = datetime(), c.last_mentioned = datetime()
                    ON MATCH SET c.last_mentioned = datetime()
                    WITH c
                    MATCH (op:Paragraph {{id: $original_id}})
                    CREATE (op)-[r:{rel_type_to_original}]->(c)
                    """
                    self.graph.query(merge_concept_query, params={
                        "name": split_content,
                        "description": f"概念：{split_content} 源自段落 {paragraph_id}",
                        "original_id": paragraph_id
                    })
                    print(f"Split to new Concept: {split_content}, linked by {rel_type_to_original}")
                else:
                    print(f"Unknown split type: {split_type}")

        except json.JSONDecodeError as e:
            print(f"LLM did not return valid JSON for splitting: {e}. Response: {llm_response[:200]}...")
        except Exception as e:
            print(f"Error during paragraph splitting for {paragraph_id}: {e}")

    def add(self, paragraph_text: str, prev_paragraph_id: Optional[str] = None) -> str:
        """
        将一个对话段落添加到记忆图中，并智能处理合并、分裂或创建新节点。
        Args:
            paragraph_text: 要添加的对话段落文本。
            prev_paragraph_id: 如果有，表示前一个对话段落的ID，用于建立FOLLOWS关系。
        Returns:
            处理后对应的Paragraph节点的ID (新创建或合并到的ID)。
        """
        paragraph_id = str(uuid.uuid4()) # 为新传入的段落生成临时ID

        # 1. 生成段落的Embedding和初步总结
        embedding = self._generate_embedding(paragraph_text)
        summary = self._summarize_text(paragraph_text)

        # 2. 相似度检测与决策
        similar_paragraphs = self._detect_similar_paragraphs(embedding)
        
        target_paragraph_id = paragraph_id # 默认为新创建

        if similar_paragraphs:
            # 取最相似的一个进行决策
            most_similar = similar_paragraphs[0]
            score = most_similar["score"]
            existing_id = most_similar["id"]
            existing_text = most_similar["text"]

            if score >= self.merge_threshold:
                # 高相似度，直接合并到现有节点
                target_paragraph_id = existing_id
                print(f"High similarity ({score:.2f}) with existing paragraph {existing_id}. Merging.")
                # 更新现有节点的文本、摘要、嵌入
                update_query = f"""
                MATCH (p:Paragraph {{id: $existing_id}})
                SET p.text = p.text + '\n\n' + $new_text,
                    p.summary = $new_summary,
                    p.embedding = $new_embedding,
                    p.timestamp = datetime()
                """
                self.graph.query(update_query, params={
                    "existing_id": existing_id,
                    "new_text": paragraph_text,
                    "new_summary": self._summarize_text(existing_text + "\n" + paragraph_text), # 重新总结
                    "new_embedding": self._generate_embedding(existing_text + "\n" + paragraph_text) # 重新生成嵌入
                })
                # 清理旧的实体关系，重新提取和添加
                self._clean_paragraph_relations(existing_id)
                extracted_data = self._extract_entities_and_relations(paragraph_text)
                for entity_data in extracted_data["entities"]:
                    self._add_or_merge_node_and_connect(entity_data, existing_id)
                for relation_data in extracted_data["relations"]:
                    self._add_or_update_relation(relation_data, existing_id)

            elif score >= self.prompt_user_threshold:
                # 中等相似度，询问用户
                print(f"Medium similarity ({score:.2f}) with existing paragraph {existing_id}. Prompting user.")
                user_decision = self._prompt_user_for_confirmation(paragraph_text, most_similar)
                
                if user_decision == "merge":
                    target_paragraph_id = existing_id
                    print(f"User chose to merge with {existing_id}.")
                    update_query = f"""
                    MATCH (p:Paragraph {{id: $existing_id}})
                    SET p.text = p.text + '\n\n' + $new_text,
                        p.summary = $new_summary,
                        p.embedding = $new_embedding,
                        p.timestamp = datetime()
                    """
                    self.graph.query(update_query, params={
                        "existing_id": existing_id,
                        "new_text": paragraph_text,
                        "new_summary": self._summarize_text(existing_text + "\n" + paragraph_text),
                        "new_embedding": self._generate_embedding(existing_text + "\n" + paragraph_text)
                    })
                    self._clean_paragraph_relations(existing_id)
                    extracted_data = self._extract_entities_and_relations(paragraph_text)
                    for entity_data in extracted_data["entities"]:
                        self._add_or_merge_node_and_connect(entity_data, existing_id)
                    for relation_data in extracted_data["relations"]:
                        self._add_or_update_relation(relation_data, existing_id)

                elif user_decision.startswith("relate:"):
                    target_paragraph_id = paragraph_id # 创建新节点，但建立关系
                    rel_type = user_decision[len("relate:"):].strip().upper().replace(" ", "_")
                    print(f"User chose to create new node and relate by '{rel_type}'.")
                    # 继续执行创建新段落的逻辑，并在最后创建关系
                    # 首次创建Paragraph节点
                    create_paragraph_query = f"""
                    CREATE (p:Paragraph {{
                        id: $id, text: $text, summary: $summary,
                        timestamp: datetime(), embedding: $embedding
                    }})
                    RETURN p.id
                    """
                    self.graph.query(create_paragraph_query, params={
                        "id": paragraph_id, "text": paragraph_text,
                        "summary": summary, "embedding": embedding
                    })
                    print(f"Created new Paragraph node: {paragraph_id}")
                    
                    # 建立与用户指定的关系
                    create_user_relation_query = f"""
                    MATCH (p_new:Paragraph {{id: $new_id}}), (p_exist:Paragraph {{id: $exist_id}})
                    CREATE (p_new)-[r:{rel_type}]->(p_exist)
                    RETURN r
                    """
                    self.graph.query(create_user_relation_query, params={
                        "new_id": paragraph_id,
                        "exist_id": existing_id,
                    })
                    print(f"Created user-specified relation: ({paragraph_id})-[:{rel_type}]->({existing_id})")

                else: # 'new' 或其他未知情况，创建新节点
                    target_paragraph_id = paragraph_id
                    print(f"User chose to create new paragraph (or default).")
                    # 继续执行创建新段落的逻辑
                    create_paragraph_query = f"""
                    CREATE (p:Paragraph {{
                        id: $id, text: $text, summary: $summary,
                        timestamp: datetime(), embedding: $embedding
                    }})
                    RETURN p.id
                    """
                    self.graph.query(create_paragraph_query, params={
                        "id": paragraph_id, "text": paragraph_text,
                        "summary": summary, "embedding": embedding
                    })
                    print(f"Created new Paragraph node: {paragraph_id}")
            else:
                # 相似度低，创建新节点
                target_paragraph_id = paragraph_id
                print(f"Low similarity ({score:.2f}). Creating new paragraph.")
                create_paragraph_query = f"""
                CREATE (p:Paragraph {{
                    id: $id, text: $text, summary: $summary,
                    timestamp: datetime(), embedding: $embedding
                }})
                RETURN p.id
                """
                self.graph.query(create_paragraph_query, params={
                    "id": paragraph_id, "text": paragraph_text,
                    "summary": summary, "embedding": embedding
                })
                print(f"Created new Paragraph node: {paragraph_id}")
        else:
            # 没有相似段落，直接创建新节点
            target_paragraph_id = paragraph_id
            print(f"No similar paragraphs found. Creating new paragraph.")
            create_paragraph_query = f"""
            CREATE (p:Paragraph {{
                id: $id, text: $text, summary: $summary,
                timestamp: datetime(), embedding: $embedding
            }})
            RETURN p.id
            """
            self.graph.query(create_paragraph_query, params={
                "id": paragraph_id, "text": paragraph_text,
                "summary": summary, "embedding": embedding
            })
            print(f"Created new Paragraph node: {paragraph_id}")

        # 3. 提取并添加实体和关系 (针对最终目标段落ID)
        # 如果是合并，则提取的数据应是新增加的文本部分。
        # 这里为了简化，我们假设_extract_entities_and_relations针对整个（合并后的）文本，
        # 或者针对新传入的paragraph_text，然后更新已有的实体/关系。
        # 实际可能需要更精细的逻辑来处理合并后的实体/关系去重。
        extracted_data = self._extract_entities_and_relations(paragraph_text)
        for entity_data in extracted_data["entities"]:
            self._add_or_merge_node_and_connect(entity_data, target_paragraph_id)
        for relation_data in extracted_data["relations"]:
            self._add_or_update_relation(relation_data, target_paragraph_id)

        # 4. 建立与前一个段落的FOLLOWS关系 (如果有效的话)
        if prev_paragraph_id and target_paragraph_id != prev_paragraph_id: # 避免自己关注自己
            follow_query = f"""
            MATCH (prev:Paragraph {{id: $prev_id}}), (curr:Paragraph {{id: $curr_id}})
            MERGE (prev)-[:FOLLOWS]->(curr)
            """
            self.graph.query(follow_query, params={"prev_id": prev_paragraph_id, "curr_id": target_paragraph_id})
            print(f"Created FOLLOWS relationship from {prev_paragraph_id} to {target_paragraph_id}")
        
        # 5. 检查是否需要分裂
        # 如果最终的Paragraph节点过大，则进行分裂
        current_paragraph_info = self.graph.query(f"MATCH (p:Paragraph {{id: $id}}) RETURN p.text, p.id", params={"id": target_paragraph_id})
        if current_paragraph_info:
            current_text = current_paragraph_info[0]["p.text"]
            # 统计当前段落关联的实体数量
            entity_count_query = f"MATCH (p:Paragraph {{id: $id}})-[:CONTAINS_ENTITY]->(e:Entity) RETURN count(e) as count"
            entity_count_result = self.graph.query(entity_count_query, params={"id": target_paragraph_id})
            entity_count = entity_count_result[0]["count"] if entity_count_result else 0

            if len(current_text) > self.split_threshold_len or entity_count > self.split_threshold_entities:
                self._split_paragraph(target_paragraph_id, current_text)

        return target_paragraph_id

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        在记忆图中搜索与查询相关的段落和实体，返回聚合后的结构化信息。
        """
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            return []

        retrieved_data = []
        retrieved_paragraph_ids = set() # 用set去重

        # 1. 语义搜索相关段落
        semantic_search_query = f"""
        CALL db.index.vector.queryNodes('paragraph_embedding_index', $top_k, $query_embedding)
        YIELD node AS p, score
        WHERE score >= $threshold
        RETURN p.id AS paragraph_id, p.text AS paragraph_text, p.summary AS paragraph_summary, score
        ORDER BY score DESC
        """
        paragraph_results = self.graph.query(semantic_search_query, params={
            "query_embedding": query_embedding,
            "top_k": top_k,
            "threshold": self.prompt_user_threshold # 搜索阈值可以灵活调整，这里用prompt_user_threshold作为最低相关性
        })
        
        for record in paragraph_results:
            # print(f"Retrieved Paragraph: {record['paragraph_id']} (Score: {record['score']:.4f})")
            # print(type(record["paragraph_id"]))
            paragraph_id = record["paragraph_id"]
            if paragraph_id not in retrieved_paragraph_ids:
                retrieved_paragraph_ids.add(paragraph_id)
                retrieved_data.append({
                    "type": "paragraph",
                    "id": paragraph_id,
                    "text": record["paragraph_text"],
                    "summary": record["paragraph_summary"],
                    "score": record["score"]
                })
                # print(f"Retrieved Paragraph: {paragraph_id} (Score: {record['score']:.4f})")

        # 2. 扩展相关实体、概念及其直接关系 (围绕已检索段落)
        if retrieved_paragraph_ids:
            # print(retrieved_paragraph_ids)
            # 查找这些段落中包含的实体和概念
            entities_concepts_query = f"""
            MATCH (p:Paragraph)-[:CONTAINS_ENTITY]->(e:Entity)
            WHERE p.id IN $paragraph_ids
            RETURN DISTINCT e.name AS name, e.type AS type, e.description AS description, 'entity' AS node_type
            UNION ALL
            MATCH (p:Paragraph)-[:MENTIONS_CONCEPT]->(c:Concept)
            WHERE p.id IN $paragraph_ids
            RETURN DISTINCT c.name AS name, 'Concept' AS type, c.description AS description, 'concept' AS node_type
            """
            nodes_results = self.graph.query(entities_concepts_query, params={"paragraph_ids": list(retrieved_paragraph_ids)})
            
            seen_nodes = set()
            for record in nodes_results:
                node_identifier = (record["node_type"], record["name"])
                if node_identifier not in seen_nodes:
                    seen_nodes.add(node_identifier)
                    retrieved_data.append({
                        "type": record["node_type"],
                        "name": record["name"],
                        "entity_type" if record["node_type"] == 'entity' else "concept_type": record["type"],
                        "description": record["description"]
                    })
                    # print(f"Retrieved {record['node_type'].capitalize()}: {record['name']}")
            
            # 查找这些实体/概念之间的直接关系 (为了提供结构化上下文)
            # 限制关系的深度和数量，避免返回过多无关信息
            relations_query = f"""
            MATCH (p:Paragraph)-[:CONTAINS_ENTITY|MENTIONS_CONCEPT]->(n1)-[r]->(n2)
            WHERE p.id IN $paragraph_ids AND (n1:Entity OR n1:Concept) AND (n2:Entity OR n2:Concept)
            RETURN DISTINCT n1.name AS source_name, labels(n1) AS source_labels, TYPE(r) AS relation_type, n2.name AS target_name, labels(n2) AS target_labels
            LIMIT 20
            """
            relation_results = self.graph.query(relations_query, params={"paragraph_ids": list(retrieved_paragraph_ids)})
            for record in relation_results:
                retrieved_data.append({
                    "type": "relation",
                    "source": record["source_name"],
                    "source_type": record["source_labels"],
                    "relation_type": record["relation_type"],
                    "target": record["target_name"],
                    "target_type": record["target_labels"]
                })
                # print(f"Retrieved Relation: ({record['source_name']})-[:{record['relation_type']}]->({record['target_name']})")

        # 3. (可选) 考虑用户ID，检索用户专属信息
        if self.user_id:
            user_info_query = f"""
            MATCH (u:User {{id: $user_id}})-[r]-(n)
            RETURN u.name AS user_name, TYPE(r) AS relation_type, labels(n) AS related_node_type, n.name AS related_node_name, n.description AS related_node_description
            LIMIT 5 # 限制用户相关信息数量
            """
            user_results = self.graph.query(user_info_query, params={"user_id": self.user_id})
            for record in user_results:
                retrieved_data.append({
                    "type": "user_related",
                    "user_name": record["user_name"],
                    "relation_type": record["relation_type"],
                    "related_node_type": record["related_node_type"],
                    "related_node_name": record["related_node_name"],
                    "related_node_description": record["related_node_description"]
                })

        return retrieved_data


    def update(self, paragraph_id: str, new_text: Optional[str] = None) -> bool:
        """
        更新记忆图中指定段落的文本，并重新处理其嵌入、总结、实体和关系。
        Args:
            paragraph_id: 要更新的段落ID。
            new_text: 新的段落文本。如果为None，则仅重新处理现有文本。
        Returns:
            更新是否成功。
        """
        # 1. 获取现有段落信息
        get_paragraph_query = f"""
        MATCH (p:Paragraph {{id: $paragraph_id}})
        RETURN p.text AS old_text
        """
        result = self.graph.query(get_paragraph_query, params={"paragraph_id": paragraph_id})
        if not result:
            print(f"Paragraph with ID {paragraph_id} not found for update.")
            return False

        old_text = result[0]["old_text"]
        text_to_process = new_text if new_text is not None else old_text

        # 2. 生成新的Embedding和Summary
        new_embedding = self._generate_embedding(text_to_process)
        new_summary = self._summarize_text(text_to_process)

        # 3. 更新Paragraph节点属性
        update_paragraph_query = f"""
        MATCH (p:Paragraph {{id: $paragraph_id}})
        SET p.text = $new_text, p.summary = $new_summary, p.embedding = $new_embedding, p.timestamp = datetime()
        """
        self.graph.query(update_paragraph_query, params={
            "paragraph_id": paragraph_id,
            "new_text": text_to_process,
            "new_summary": new_summary,
            "new_embedding": new_embedding
        })
        print(f"Updated Paragraph node: {paragraph_id}")

        # 4. 清理旧的实体和关系 (只删除与该段落的 CONTAINS_ENTITY)
        self._clean_paragraph_relations(paragraph_id)

        # 5. 提取并添加新的实体和关系
        extracted_data = self._extract_entities_and_relations(text_to_process)
        for entity_data in extracted_data["entities"]:
            self._add_or_merge_node_and_connect(entity_data, paragraph_id)
        for relation_data in extracted_data["relations"]:
            self._add_or_update_relation(relation_data, paragraph_id)
        
        # 6. 检查是否需要分裂 (更新后可能变大)
        if len(text_to_process) > self.split_threshold_len:
            self._split_paragraph(paragraph_id, text_to_process)

        return True

    def delete(self, paragraph_id: str) -> bool:
        """
        从记忆图中删除一个对话段落及其所有直接相关联的边。
        Args:
            paragraph_id: 要删除的段落ID。
        Returns:
            删除是否成功。
        """
        # 1. 首先删除与该段落直接相关的所有关系 (包括 CONTAINS_ENTITY, MENTIONS_CONCEPT, FOLLOWS, 和作为父节点的CONTAINS_SUBTOPIC)
        delete_relations_query = f"""
        MATCH (p:Paragraph {{id: $paragraph_id}})-[r]-()
        DELETE r
        """
        self.graph.query(delete_relations_query, params={"paragraph_id": paragraph_id})
        print(f"Deleted all relationships connected to Paragraph: {paragraph_id}")

        # 2. 删除Paragraph节点本身
        delete_paragraph_query = f"""
        MATCH (p:Paragraph {{id: $paragraph_id}})
        DELETE p
        """
        result = self.graph.query(delete_paragraph_query, params={"paragraph_id": paragraph_id})
        
        if result:
            print(f"Deleted Paragraph node: {paragraph_id}")
            # 3. (可选) 清理可能因为该段落删除而变得“孤立”的实体和概念
            # 建议作为后台任务或手动触发，因为可能涉及全图扫描，开销较大。
            # self._clean_isolated_nodes() 
            return True
        else:
            print(f"Paragraph with ID {paragraph_id} not found for deletion.")
            return False

    def _clean_isolated_nodes(self):
        """
        清理图中不再被任何段落提及或与其他实体有关系的孤立实体和概念。
        此操作应谨慎执行，建议在非高峰期运行。
        """
        print("Running isolated node cleanup...")
        
        # 修改 Cypher 查询，返回删除的节点数量
        cleanup_entities_query = """
        MATCH (e:Entity)
        WHERE NOT EXISTS((e)<-[:CONTAINS_ENTITY]-()) // 不再被任何Paragraph包含
        AND NOT EXISTS((e)--()) // 不再与任何其他实体有关系
        DETACH DELETE e
        RETURN count(e) AS deletedCount
        """
        cleanup_concepts_query = """
        MATCH (c:Concept)
        WHERE NOT EXISTS((c)<-[:MENTIONS_CONCEPT]-()) // 不再被任何Paragraph提及
        AND NOT EXISTS((c)--()) // 不再与任何其他节点有关系
        DETACH DELETE c
        RETURN count(c) AS deletedCount
        """
        
        try:
            # self.graph.query 返回的是列表，所以需要从列表中取第一个元素的字典
            entities_result = self.graph.query(cleanup_entities_query)
            # 提取删除的数量，如果列表不为空且字典中有 'deletedCount'
            deleted_entities_count = entities_result[0]['deletedCount'] if entities_result and 'deletedCount' in entities_result[0] else 0
            print(f"Cleaned up isolated entities. Nodes deleted: {deleted_entities_count}")
            
            concepts_result = self.graph.query(cleanup_concepts_query)
            deleted_concepts_count = concepts_result[0]['deletedCount'] if concepts_result and 'deletedCount' in concepts_result[0] else 0
            print(f"Cleaned up isolated concepts. Nodes deleted: {deleted_concepts_count}")

        except Exception as e:
            print(f"Error during isolated node cleanup: {e}")