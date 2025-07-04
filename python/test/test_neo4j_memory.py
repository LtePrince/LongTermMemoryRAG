"""
Test Neo4jMemory class and its add method
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

def test_neo4j_memory_add():
    """Test Neo4jMemory add method with character data"""
    # Load environment variables
    load_dotenv()
    
    try:
        from memoryrag.config.config import Neo4jConfig
        from memoryrag.graph_store.neo4j import Neo4jMemory
        
        # Test loading Neo4j configuration from environment
        neo4j_config = Neo4jConfig.from_env()
        neo4j_config.validate()
        
        print("✅ Neo4j配置加载成功!")
        print(f"Neo4j URL: {neo4j_config.url}")
        print(f"Neo4j用户: {neo4j_config.username}")
        print(f"Neo4j数据库: {neo4j_config.database}")
        
        # Initialize Neo4jMemory instance
        print("\n🔄 正在初始化Neo4jMemory实例...")
        memory = Neo4jMemory(neo4j_config)
        print("✅ Neo4jMemory实例初始化成功!")
        
        # Test data - character description
        test_data = """浅川夏帆，一名品学兼优的高中生。
            外表看似文静内向，但内心细腻，情感丰富，有时会有些小小的固执和不安全感。
            在朋友风雪面前，她会展露出自己活泼和依赖的一面。
            她非常看重和风雪的关系，并且很在意风雪对她的看法。
            风雪和她下周将要一起参加学校的文化节活动。"""

        # Test filters
        test_filters = {
            "user_id": "test_user_001",
            "agent_id": "asakawa_naho"
        }
        
        print(f"\n🔄 正在添加测试数据...")
        print(f"数据内容: {test_data[:50]}...")
        print(f"过滤器: {test_filters}")
        
        # Call add method
        # entity_type_map = memory.add(test_data, test_filters)
        # print(entity_type_map)

        entity_type_map = memory._retrieve_nodes_from_data(test_data, test_filters)
        print(entity_type_map)

        # relation = memory._establish_nodes_relations_from_data(test_data, test_filters, entity_type_map)
        # print(relation)

        # search_output = memory._search_graph_db(node_list=list(entity_type_map.keys()), filters=test_filters)
        # print(search_output)
        
        print("\n✅ 数据添加成功!")
        print(f"添加的实体数量: {len(entity_type_map.get('entities', []))}")
        print(f"添加的关系数量: {len(entity_type_map.get('relations', []))}")
        
        if entity_type_map.get('entities'):
            print("添加的实体:")
            for entity in entity_type_map['entities']:
                print(f"  - {entity}")

        if entity_type_map.get('relations'):
            print("添加的关系:")
            for relation in entity_type_map['relations'][:5]:  # 只显示前5个
                print(f"  - {relation}")
            if len(entity_type_map['relations']) > 5:
                print(f"  ... 以及其他共 {len(entity_type_map['relations'])} 个关系")

        print("\n🎉 Neo4jMemory add方法测试完成!")
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保安装了所需的依赖包:")
        print("pip install langchain-neo4j rank-bm25")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        print(f"详细错误信息:")
        traceback.print_exc()

def test_neo4j_memory_search():
    """Test Neo4jMemory search method"""
    # Load environment variables
    load_dotenv()
    
    try:
        from memoryrag.config.config import Neo4jConfig
        from memoryrag.graph_store.neo4j import Neo4jMemory
        
        # Initialize Neo4jMemory instance
        neo4j_config = Neo4jConfig.from_env()
        memory = Neo4jMemory(neo4j_config)
        
        # Test search
        search_query = "浅川夏帆"
        test_filters = {
            "user_id": "test_user_001",
            "agent_id": "asakawa_naho"
        }
        
        print(f"\n🔍 正在搜索: {search_query}")
        search_results = memory.search(search_query, test_filters, limit=10)
        
        print(f"✅ 搜索完成! 找到 {len(search_results)} 个结果")
        for i, result in enumerate(search_results[:3], 1):  # 只显示前3个结果
            print(f"结果 {i}:")
            print(f"  源: {result.get('source', '')}")
            print(f"  关系: {result.get('relationship', '')}")
            print(f"  目标: {result.get('destination', '')}")
        
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Neo4jMemory 测试 ===")
    
    # Test add method
    test_neo4j_memory_add()
    
    # # Test search method
    # print("\n" + "="*50)
    # test_neo4j_memory_search()
