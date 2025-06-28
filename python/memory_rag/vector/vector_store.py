from copy import deepcopy
import json
from pydantic import ValidationError
from typing import Any, Dict, Optional
import logging

from core.memory_rag.utils import *
from core.memory_rag.config.base import MemoryConfig
from core.memory_rag.factory import EmbedderFactory, LlmFactory, VectorStoreFactory

logger = logging.getLogger(__name__)

def get_default_vector_config():
  return {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "openmemory",
                "path": "data/chroma_db_store",
            }
        },
        "llm": {
            "provider": "deepseek",
            "config": {
                "model": "deepseek-chat",
                "temperature": 0.1,
                "max_tokens": 2000,
                # "top_p": 0.9,
                # "top_k": 50,
                "api_key": "env:CHAT_API_KEY"
            }
        },
        "embedder": {
            "provider": "qwen",
            "config": {
                "model": "text-embedding-v4",
                "api_key": "env:DASHSCOPE_API_KEY"
            }
        },
        "version": "v0.3.0"
  }

def _build_filters_and_metadata(
        *,
        user_id: Optional[str] = None,
        character_id: Optional[str] = None,
        input_metadata: Optional[Dict[str, Any]] = None,
        input_filters: Optional[Dict[str, Any]] = None
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    base_metadata_template = deepcopy(input_metadata) if input_metadata else {}
    effective_query_filters = deepcopy(input_filters) if input_filters else {}

    session_ids_provided = []

    if user_id:
        base_metadata_template["user_id"] = user_id
        effective_query_filters["user_id"] = user_id
        session_ids_provided.append("user_id")

    if character_id:
        base_metadata_template["character_id"] = character_id
        effective_query_filters["character_id"] = character_id
        session_ids_provided.append("character_id")

    if not session_ids_provided:
        raise ValueError("At least one of 'user_id', 'agent_id', or 'run_id' must be provided.")
    
    return base_metadata_template, effective_query_filters

class MemoryVector:
    def __init__(self, config: MemoryConfig = MemoryConfig()):
        self.config = config

        self.embedding_model = EmbedderFactory.create(
            self.config.embedder.provider,
            self.config.embedder.config,
            self.config.vector_store.config
        )
        self.vector_store = VectorStoreFactory.create(
            self.config.vector_store.provider,
            self.config.vector_store.config
        )
        self.llm = LlmFactory.create(self.config.llm.provider, self.config.llm.config)
        # self.db = SQLiteManager(self.config.history_db_path) # TODO: implement SQLiteManager
        self.collection_name = self.config.vector_store.config.collection_name
        self.api_version = self.config.version

        # TODO：the migration config and initialize function of the vector store

        
    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]):
        try:
            config = cls._process_config(config_dict)
            config = MemoryConfig(**config_dict)
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        return cls(config)
    
    @staticmethod
    def _process_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        if "graph_store" in config_dict:
            if "vector_store" not in config_dict and "embedder" in config_dict:
                config_dict["vector_store"] = {}
                config_dict["vector_store"]["config"] = {}
                config_dict["vector_store"]["config"]["embedding_model_dims"] = config_dict["embedder"]["config"][
                    "embedding_dims"
                ]
        try:
            return config_dict
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise
        
    def add(
        self, 
        messages, 
        user_id: Optional[str] = None, 
        character_id: Optional[str] = None, 
        metadata: Optional[Dict[str, Any]] = None,
        infer: bool = False):
        # build filters
        processed_metadata, effective_filters = _build_filters_and_metadata(
            user_id=user_id,
            character_id=character_id,
            input_metadata=metadata,
        )

        # check messages type
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        elif isinstance(messages, dict):
            messages = [messages]

        elif not isinstance(messages, list):
            raise ValueError("messages must be str, dict, or list[dict]")
        
        # add memory data
        vector_store_result = self._add_to_vector_store(
            messages,
            processed_metadata,
            effective_filters,
            infer
        )

        logger.info("adding vector memory")
        return {"results": vector_store_result}
    
    def _add_to_vector_store(self, messages, metadata, filters, infer):
        if not infer:
            pass

        parsed_messages = parse_messages(messages)
        system_prompt, user_prompt = get_fact_retrieval_messages(parsed_messages)

        response = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        try:
            response = remove_code_blocks(response)
            new_retrieved_facts = json.loads(response)["facts"]
        except Exception as e:
            logging.error(f"Error in new_retrieved_facts: {e}")
            new_retrieved_facts = []

        if not new_retrieved_facts:
            logger.debug("No new facts retrieved from input. Skipping memory update LLM call.")

        retrieved_old_memory = []
        new_message_embeddings = {}
        for new_mem in new_retrieved_facts:
            messages_embeddings = self.embedding_model.embed(new_mem, "add")
            new_message_embeddings[new_mem] = messages_embeddings
            existing_memories = self.vector_store.search(
                query=new_mem,
                vectors=messages_embeddings,
                limit=5,
                filters=filters,
            )
            for mem in existing_memories:
                retrieved_old_memory.append({"id": mem.id, "text": mem.payload["data"]})

        unique_data = {}
        for item in retrieved_old_memory:
            unique_data[item["id"]] = item
        retrieved_old_memory = list(unique_data.values())
        logging.info(f"Total existing memories: {len(retrieved_old_memory)}")

        # mapping UUIDs with integers for handling UUID hallucinations
        temp_uuid_mapping = {}
        for idx, item in enumerate(retrieved_old_memory):
            temp_uuid_mapping[str(idx)] = item["id"]
            retrieved_old_memory[idx]["id"] = str(idx)

        if new_retrieved_facts:
            function_calling_prompt = get_update_memory_messages(
                retrieved_old_memory, new_retrieved_facts, self.config.custom_update_memory_prompt
            )

            try:
                response: str = self.llm.generate_response(
                    messages=[{"role": "user", "content": function_calling_prompt}],
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                logging.error(f"Error in new memory actions response: {e}")
                response = ""

            try:
                response = remove_code_blocks(response)
                new_memories_with_actions = json.loads(response)
            except Exception as e:
                logging.error(f"Invalid JSON response: {e}")
                new_memories_with_actions = {}
        else:
            new_memories_with_actions = {}

        returned_memories = []
        try:
            for resp in new_memories_with_actions.get("memory", []):
                logging.info(resp)
                try:
                    action_text = resp.get("text")
                    if not action_text:
                        logging.info("Skipping memory entry because of empty `text` field.")
                        continue

                    event_type = resp.get("event")
                    if event_type == "ADD":
                        memory_id = self._create_memory(
                            data=action_text,
                            existing_embeddings=new_message_embeddings,
                            metadata=deepcopy(metadata),
                        )
                        returned_memories.append({"id": memory_id, "memory": action_text, "event": event_type})
                    elif event_type == "UPDATE":
                        self._update_memory(
                            memory_id=temp_uuid_mapping[resp.get("id")],
                            data=action_text,
                            existing_embeddings=new_message_embeddings,
                            metadata=deepcopy(metadata),
                        )
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": action_text,
                                "event": event_type,
                                "previous_memory": resp.get("old_memory"),
                            }
                        )
                    elif event_type == "DELETE":
                        self._delete_memory(memory_id=temp_uuid_mapping[resp.get("id")])
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": action_text,
                                "event": event_type,
                            }
                        )
                    elif event_type == "NONE":
                        logging.info("NOOP for Memory.")
                except Exception as e:
                    logging.error(f"Error processing memory action: {resp}, Error: {e}")
        except Exception as e:
            logging.error(f"Error iterating new_memories_with_actions: {e}")

        keys, encoded_ids = process_telemetry_filters(filters)
        return returned_memories
        
    
    def get(self, memory_id):
        pass
    
    def get_all(self):
        pass
    
    def _get_all_from_vector_store(self, filters, limit):
        # Retrieve all items from the vector store with optional filters and limit
        pass
    
    def search(self, query: str):
        pass
    
    def _search_vector_store(self, query, filters, limit, threshold: Optional[float] = None):
        pass
    
    def update(self, memory_id, data):
        pass

    def delete(self, item_id):
        # Delete an item from the vector store
        pass
    
    def delete_all(self, user_id: Optional[str] = None, agent_id: Optional[str] = None, run_id: Optional[str] = None):
        pass
    
    def reset(self):
        pass

    def _create_memory(self, data, existing_embeddings, metadata=None):
        pass

    def _update_memory():
        pass

    def _delete_memory():
        pass