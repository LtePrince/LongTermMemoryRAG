"""
ChromaDB vector store implementation
"""
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("chromadb is required. Install with: pip install chromadb")

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result data structure for conversation memories"""
    id: str
    score: float  # distance/similarity score
    text: str  # conversation text
    user_id: str
    character_id: str
    timestamp: str
    metadata: Dict[str, Any]  # additional metadata


class ChromaDB():
    """Simplified ChromaDB vector store implementation"""
    
    def __init__(self, config: dict):
        """
        Initialize ChromaDB store
        
        Args:
            config: 配置字典，包含 collection_name, path, host, port 等参数
        """
        client = config.get("client")
        if client:
            self.client = client
        else:
            self.settings = Settings(anonymized_telemetry=False)

            host = config.get("host")
            port = config.get("port")
            if host and port:
                # 如果指定了 host 和 port，使用 HttpClient
                self.client = chromadb.HttpClient(host=host, port=port)
            else:
                # 使用 PersistentClient 替代 Client + Settings
                path = config.get("path", "db")
                self.client = chromadb.PersistentClient(path=path)

        self.collection_name = config.get("collection_name", "openmemory")
        self.collection = self._create_collection()
    
    def _create_collection(self):
        """Create or get collection"""
        try:
            collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection '{self.collection_name}' ready")
            return collection
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def insert(self, text: str, embedding: List[float], user_id: str, 
               character_id: str, additional_metadata: Optional[Dict[str, Any]] = None):
        """
        Insert conversation memory to the collection
        
        Args:
            text: Conversation text
            embedding: Embedding vector of the text
            user_id: User identifier
            character_id: Character/Agent identifier  
            additional_metadata: Additional metadata (optional)
        """
        from datetime import datetime
        
        try:
            # Create single conversation record with all IDs
            timestamp = int(datetime.now().timestamp() * 1000)
            conversation_id = f"conversation_{timestamp}"
            
            # Prepare metadata with all required fields
            metadata = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'character_id': character_id,
                'text': text,
                'timestamp': datetime.now().isoformat(),
            }
            
            # Store single record with all information
            self.collection.add(
                ids=[conversation_id],
                embeddings=[embedding],
                metadatas=[metadata]
            )
            
            logger.info(f"Inserted conversation memory for user {user_id} and character {character_id}")
            
        except Exception as e:
            logger.error(f"Failed to insert conversation memory: {e}")
            raise
    
    def search(self, query_embedding: List[float], user_id: str, character_id: str, 
               limit: int = 5) -> List[SearchResult]:
        """
        Search for similar conversation memories for specific user and character
        
        Args:
            query_embedding: Query embedding vector
            user_id: User identifier
            character_id: Character identifier
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            # Search by user_id and character_id pattern in IDs
            id_pattern = f"{user_id}_{character_id}"
            
            # Get all conversations for this user-character pair first
            all_results = self.collection.get()
            
            # Filter by user_id and character_id from IDs
            filtered_ids = [id for id in all_results.get('ids', []) if id.startswith(id_pattern)]
            
            if not filtered_ids:
                return []
            
            # Now do similarity search within this subset
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(limit, len(filtered_ids)),
                include=['metadatas', 'distances']
            )
            
            return self._parse_search_results(results, user_id, character_id)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def _parse_search_results(self, results: Dict, user_id: str, character_id: str) -> List[SearchResult]:
        """Parse ChromaDB query results into SearchResult objects"""
        search_results = []
        
        # ChromaDB returns nested lists, we take the first (and only) query result
        ids = results.get('ids', [[]])[0]
        distances = results.get('distances', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        
        for i in range(len(ids)):
            conversation_id = ids[i]
            # Extract user_id and character_id from ID
            if conversation_id.startswith(f"{user_id}_{character_id}"):
                metadata = metadatas[i] if i < len(metadatas) else {}
                result = SearchResult(
                    id=conversation_id,
                    score=distances[i] if i < len(distances) else 0.0,
                    text=metadata.get('text', ''),
                    user_id=user_id,
                    character_id=character_id,
                    timestamp=metadata.get('timestamp', ''),
                    metadata=metadata
                )
                search_results.append(result)
        
        return search_results
    
    def update(self, conversation_id: str, text: Optional[str] = None, 
               embedding: Optional[List[float]] = None, 
               additional_metadata: Optional[Dict[str, Any]] = None):
        """
        Update conversation memory
        
        Args:
            conversation_id: Conversation ID to update (user_id_character_id_timestamp format)
            text: New text content (optional)
            embedding: New embedding vector (optional)
            additional_metadata: Additional metadata to update (optional)
        """
        try:
            update_params = {'ids': [conversation_id]}
            
            if embedding:
                update_params['embeddings'] = [embedding]
                
            if text or additional_metadata:
                # Get existing metadata first
                existing = self.collection.get(ids=[conversation_id])
                if existing['metadatas']:
                    metadata = existing['metadatas'][0].copy()
                    
                    if text:
                        metadata['text'] = text
                    
                    if additional_metadata:
                        metadata.update(additional_metadata)
                    
                    update_params['metadatas'] = [metadata]
            
            self.collection.update(**update_params)
            logger.info(f"Updated conversation memory {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to update conversation memory {conversation_id}: {e}")
            raise
    
    def delete(self, conversation_id: str):
        """
        Delete conversation memory by ID
        
        Args:
            conversation_id: Conversation ID to delete (user_id_character_id_timestamp format)
        """
        try:
            self.collection.delete(ids=[conversation_id])
            logger.info(f"Deleted conversation memory {conversation_id}")
        except Exception as e:
            logger.error(f"Failed to delete conversation memory {conversation_id}: {e}")
            raise
    
    def reset(self):
        """Reset collection (delete all conversation memories)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._create_collection()
            logger.warning(f"Reset collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            raise
    
    def count(self) -> int:
        """Get total number of conversation memories"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Failed to count conversation memories: {e}")
            return 0
