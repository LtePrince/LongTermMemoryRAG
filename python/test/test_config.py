"""
Test configuration and ChromaDB setup
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

def test_config():
    """Test configuration loading from environment"""
    # Load environment variables
    load_dotenv()
    
    try:
        from memoryrag.config.config import ChromaDBConfig, EmbeddingConfig, LlmConfig, Neo4jConfig
        
        # Test loading configuration from environment
        config = ChromaDBConfig.from_env()
        config.validate()
        
        print("✅ ChromaDB configuration loaded successfully!")
        print(f"ChromaDB path: {config.path}")
        print(f"ChromaDB collection: {config.collection_name}")
        if config.host and config.port:
            print(f"ChromaDB server: {config.host}:{config.port}")
        
        # Test embedding configuration
        embedding_config = EmbeddingConfig.from_env()
        print("\n✅ Embedding configuration loaded successfully!")
        print(f"Embedding model: {embedding_config.model}")
        print(f"Embedding dimensions: {embedding_config.dimensions}")
        print(f"Embedding base_url: {embedding_config.base_url}")
        print(f"API key configured: {'Yes' if embedding_config.api_key else 'No'}")
        
        # Test LLM configuration
        llm_config = LlmConfig.from_env()
        print("\n✅ LLM configuration loaded successfully!")
        print(f"LLM model: {llm_config.model}")
        print(f"LLM base_url: {llm_config.base_url}")
        print(f"LLM temperature: {llm_config.temperature}")
        print(f"API key configured: {'Yes' if llm_config.api_key else 'No'}")
        
        # Test Neo4j configuration
        neo4j_config = Neo4jConfig.from_env()
        neo4j_config.validate()
        print("\n✅ Neo4j configuration loaded successfully!")
        print(f"Neo4j URL: {neo4j_config.url}")
        print(f"Neo4j user: {neo4j_config.user}")
        print(f"Neo4j database: {neo4j_config.database}")
        
        return config, embedding_config, llm_config, neo4j_config
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return None, None, None, None


def test_neo4j(neo4j_config):
    """Test Neo4j connection"""
    try:
        from langchain_neo4j import Neo4jGraph
        
        # Test Neo4j connection using config.get_config()
        config = neo4j_config.get_config()
        
        # Create driver and test connection
        graph = Neo4jGraph(
            config['url'],
            config['user'],
            config['password'],
            config['database'] if 'database' in config else "neo4j",
            refresh_schema=False,
        )
        
        # Test connection with a simple query
        result = graph.query("RETURN 'Neo4j connection successful' AS message")
        message = result[0]["message"] if result and len(result) > 0 else "No response"
        
        # Test basic node count
        count_result = graph.query("MATCH (n) RETURN count(n) AS node_count")
        node_count = count_result[0]["node_count"] if count_result and len(count_result) > 0 else 0
        
        print("✅ Neo4j connection test successful!")
        print(f"Connection message: {message}")
        print(f"Total nodes in database: {node_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection test failed: {e}")
        return False


def test_llm(llm_config):
    """Test LLM functionality"""
    try:
        from memoryrag.llm.deepseek import DeepSeekLLM
        
        # Create LLM instance using config.get_config()
        llm = DeepSeekLLM(llm_config.get_config())
        
        # Test LLM generation
        test_messages = [
            {"role": "user", "content": "你好，请简单介绍一下自己，回复要简短。"}
        ]
        print(f"\n🤖 Testing LLM with messages: {test_messages}")
        
        response = llm.generate_response(test_messages)
        
        print("✅ LLM response generated successfully!")
        print(f"Response type: {type(response)}")
        print(f"Response preview: {response[:100]}...")
        
        return llm
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return None


def test_embedding(embedding_config):
    """Test embedding functionality"""
    try:
        from memoryrag.embedding.qwen import QwenEmbedding
        
        # Create embedding instance using config.get_config()
        embedding = QwenEmbedding(embedding_config.get_config())
        
        # Test embedding generation
        test_text = "Hello, this is a test sentence for embedding generation."
        print(f"\n🔍 Testing embedding with text: '{test_text}'")
        
        vector = embedding.embed(test_text)
        
        print("✅ Embedding generated successfully!")
        print(f"Vector dimensions: {len(vector)}")
        print(f"First 5 values: {vector[:5]}")
        print(f"Embedding type: {type(vector[0])}")
        
        return embedding
        
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return None


def test_chromadb(config):
    """Test ChromaDB connection"""
    try:
        from memoryrag.vector_store.chromadb_store import ChromaDB
        
        # Create ChromaDB store using config.get_config()
        store = ChromaDB(config.get_config())
        
        print("✅ ChromaDB store created successfully!")
        print(f"Collection name: {store.collection_name}")
        print(f"Document count: {store.count()}")
        
        return store
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return None


if __name__ == "__main__":
    print("🧪 Testing Memory RAG configuration and setup...")
    print("=" * 60)
    
    # Test configuration
    config, embedding_config, llm_config, neo4j_config = test_config()
    if not config or not embedding_config or not llm_config or not neo4j_config:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # # Test embedding
    # embedding = test_embedding(embedding_config)
    # if not embedding:
    #     print("⚠️  Embedding test failed, continuing with other tests...")
    
    # print("\n" + "=" * 60)
    
    # # Test LLM
    # llm = test_llm(llm_config)
    # if not llm:
    #     print("⚠️  LLM test failed, continuing with other tests...")
    
    # print("\n" + "=" * 60)
    
    # Test Neo4j
    neo4j_success = test_neo4j(neo4j_config)
    if not neo4j_success:
        print("⚠️  Neo4j test failed, continuing with ChromaDB test...")
    
    print("\n" + "=" * 60)
    
    # Test ChromaDB
    store = test_chromadb(config)
    if not store:
        sys.exit(1)
    
    print("\n🎉 All tests completed!")
