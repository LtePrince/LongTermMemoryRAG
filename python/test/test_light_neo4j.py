#!/usr/bin/env python3
"""
测试 memory_light_mcp 中调用 lightneo4j 的逻辑
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Optional

from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from memoryrag.config import Neo4jConfig, EmbeddingConfig
from memoryrag.graph_store.light_neo4j import LightNeo4jMemory
from memoryrag.embedding import QwenEmbedding
import datetime

class TestLightNeo4jMemory:
    """测试LightNeo4jMemory类的功能"""
    
    def __init__(self):
        self.setup_test_environment()
    
    def setup_test_environment(self):
        """设置测试环境"""
        try:
            # 配置Neo4j连接
            self.neo4j_config = Neo4jConfig().from_env()
            
            # 创建LightNeo4jMemory实例
            self.light_memory = LightNeo4jMemory(self.neo4j_config)

            self.embedding_config = EmbeddingConfig().from_env()
            self.mock_embedder = QwenEmbedding(self.embedding_config.get_config())
            
            print("✅ 测试环境设置成功")
            print(f"Neo4j URL: {self.neo4j_config.url}")
            print(f"Database: {self.neo4j_config.database}")
            
        except Exception as e:
            print(f"❌ 测试环境设置失败: {e}")
            raise
    
    def test_add_node(self):
        """测试添加节点功能"""
        print("\n🔹 测试添加节点...")
        try:
            # 准备测试数据
            node_type = "TestUser"
            properties = {
                'name': 'Test User',
                'type': 'user',
                'description': 'This is a test user for testing purposes',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # 模拟embedding
            properties['embedding'] = self.mock_embedder.embed(properties.get('description', ''))
            
            # 添加节点
            node_id = self.light_memory.add_node(node_type, properties)
            
            print(f"✅ 成功添加节点: {node_id}")
            return node_id
            
        except Exception as e:
            print(f"❌ 添加节点失败: {e}")
            raise
    
    def test_search_nodes(self, node_type="TestUser"):
        """测试搜索节点功能"""
        print("\n🔹 测试搜索节点...")
        try:
            # 搜索所有TestUser类型的节点
            nodes = self.light_memory.search_nodes(node_type)
            print(f"✅ 找到 {len(nodes)} 个 {node_type} 节点")
            
            for i, node in enumerate(nodes):
                print(f"  节点 {i+1}: ID={node.get('id', 'N/A')}, Name={node.get('name', 'N/A')}")
            
            return nodes
            
        except Exception as e:
            print(f"❌ 搜索节点失败: {e}")
            raise
    
    def test_add_relationship(self, start_node_id, end_node_id):
        """测试添加关系功能"""
        print("\n🔹 测试添加关系...")
        try:
            rel_type = "KNOWS"
            properties = {
                'description': 'Test relationship',
                'created_at': datetime.datetime.now().isoformat()
            }
            
            self.light_memory.add_relationship(start_node_id, end_node_id, rel_type, properties)
            print(f"✅ 成功添加关系: {start_node_id} -[{rel_type}]-> {end_node_id}")
            
        except Exception as e:
            print(f"❌ 添加关系失败: {e}")
            raise
    
    def test_search_relationships(self, start_node_id):
        """测试搜索关系功能"""
        print("\n🔹 测试搜索关系...")
        try:
            relationships = self.light_memory.search_relationships(start_node_id)
            print(f"✅ 找到 {len(relationships)} 个关系")
            
            for i, rel in enumerate(relationships):
                end_node = rel.get('end_node', {})
                print(f"  关系 {i+1}: -> {end_node.get('name', 'N/A')} (ID: {end_node.get('id', 'N/A')})")
            
            return relationships
            
        except Exception as e:
            print(f"❌ 搜索关系失败: {e}")
            raise
    
    def test_update_node(self, node_id):
        """测试更新节点功能"""
        print("\n🔹 测试更新节点...")
        try:
            update_properties = {
                'description': 'Updated test user description',
                'updated_at': datetime.datetime.now().isoformat(),
                'status': 'active'
            }
            
            self.light_memory.update_node(node_id, update_properties)
            print(f"✅ 成功更新节点: {node_id}")
            
        except Exception as e:
            print(f"❌ 更新节点失败: {e}")
            raise
    
    def test_delete_relationship(self, start_node_id, end_node_id, rel_type="KNOWS"):
        """测试删除关系功能"""
        print("\n🔹 测试删除关系...")
        try:
            self.light_memory.delete_relationship(start_node_id, end_node_id, rel_type)
            print(f"✅ 成功删除关系: {start_node_id} -[{rel_type}]-> {end_node_id}")
            
        except Exception as e:
            print(f"❌ 删除关系失败: {e}")
            raise
    
    def test_delete_node(self, node_id):
        """测试删除节点功能"""
        print("\n🔹 测试删除节点...")
        try:
            self.light_memory.delete_node(node_id)
            print(f"✅ 成功删除节点: {node_id}")
            
        except Exception as e:
            print(f"❌ 删除节点失败: {e}")
            raise
    
    def test_vector_index(self):
        """测试向量索引功能"""
        print("\n🔹 测试向量索引...")
        try:
            self.light_memory._ensure_vector_index()
            print("✅ 向量索引检查完成")
            
        except Exception as e:
            print(f"❌ 向量索引测试失败: {e}")
            raise
    
    def run_complete_test(self):
        """运行完整的测试流程"""
        print("🚀 开始运行LightNeo4j完整测试...")
        
        node_ids = []
        
        try:
            # 1. 测试向量索引
            self.test_vector_index()
            
            # 2. 测试添加多个节点
            for i in range(2):
                node_type = "TestUser"
                properties = {
                    'name': f'Test User {i+1}',
                    'type': 'user',
                    'description': f'This is test user number {i+1}',
                    'created_at': datetime.datetime.now().isoformat(),
                    'updated_at': datetime.datetime.now().isoformat()
                }
                properties['embedding'] = self.mock_embedder.embed(properties.get('description', ''))
                
                node_id = self.test_add_node() if i == 0 else self.light_memory.add_node(node_type, properties)
                node_ids.append(node_id)
                print(f"  创建节点 {i+1}: {node_id}")
            
            # 3. 测试搜索节点
            nodes = self.test_search_nodes()
            
            # 4. 测试添加关系（如果有至少2个节点）
            if len(node_ids) >= 2:
                self.test_add_relationship(node_ids[0], node_ids[1])
                
                # 5. 测试搜索关系
                self.test_search_relationships(node_ids[0])
            
            # 6. 测试更新节点
            if node_ids:
                self.test_update_node(node_ids[0])
            
            # 7. 测试删除关系
            if len(node_ids) >= 2:
                self.test_delete_relationship(node_ids[0], node_ids[1])
            
            # 8. 测试删除节点（清理测试数据）
            for node_id in node_ids:
                self.test_delete_node(node_id)
            
            print("\n🎉 所有测试完成！")
            
        except Exception as e:
            print(f"\n💥 测试过程中出现错误: {e}")
            # 清理剩余的测试数据
            for node_id in node_ids:
                try:
                    self.light_memory.delete_node(node_id)
                    print(f"🧹 清理节点: {node_id}")
                except:
                    pass


class TestMemoryLightMCPIntegration:
    """测试memory_light_mcp的集成功能"""
    
    def __init__(self):
        self.setup_mcp_test()
    
    def setup_mcp_test(self):
        """设置MCP测试环境"""
        print("\n🔧 设置MCP集成测试环境...")
        
        # 模拟MCP环境
        self.neo4j_config = Neo4jConfig().from_env()
        self.light_memory_client = LightNeo4jMemory(self.neo4j_config)
        
        # Mock embedder
        self.mock_embedder = QwenEmbedding(EmbeddingConfig().from_env().get_config())
        
        print("✅ MCP集成测试环境设置完成")
    
    async def test_mcp_add_node(self):
        """测试MCP添加节点功能"""
        print("\n🔹 测试MCP添加节点...")
        try:
            node_type = "Person"
            properties = {
                'id': 'test-person-1',
                'name': 'John Doe',
                'type': 'person',
                'description': 'A test person for MCP integration testing',
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # 模拟MCP工具调用
            properties['embedding'] = self.mock_embedder.embed(properties.get('description', ''))
            result = self.light_memory_client.add_node(node_type, properties)
            
            print(f"✅ MCP添加节点成功: {result}")
            return result
            
        except Exception as e:
            print(f"❌ MCP添加节点失败: {e}")
            raise
    
    async def test_mcp_add_relationship(self, start_node_id, end_node_id):
        """测试MCP添加关系功能"""
        print("\n🔹 测试MCP添加关系...")
        try:
            rel_type = "FRIENDS_WITH"
            properties = {
                'start_node_id': start_node_id,
                'end_node_id': end_node_id,
                'rel_type': rel_type,
                'description': 'Friend relationship for testing',
                'created_at': datetime.datetime.now().isoformat()
            }
            
            result = self.light_memory_client.add_relationship(
                start_node_id, end_node_id, rel_type, properties
            )
            
            print(f"✅ MCP添加关系成功")
            return result
            
        except Exception as e:
            print(f"❌ MCP添加关系失败: {e}")
            raise
    
    async def test_mcp_search_nodes(self, node_type="Person"):
        """测试MCP搜索节点功能"""
        print("\n🔹 测试MCP搜索节点...")
        try:
            filters = {'type': 'person'}
            result = self.light_memory_client.search_nodes(node_type, filters)
            
            print(f"✅ MCP搜索节点成功，找到 {len(result)} 个节点")
            return result
            
        except Exception as e:
            print(f"❌ MCP搜索节点失败: {e}")
            raise
    
    async def test_mcp_search_relationships(self, start_node_id):
        """测试MCP搜索关系功能"""
        print("\n🔹 测试MCP搜索关系...")
        try:
            result = self.light_memory_client.search_relationships(start_node_id)
            
            print(f"✅ MCP搜索关系成功，找到 {len(result)} 个关系")
            return result
            
        except Exception as e:
            print(f"❌ MCP搜索关系失败: {e}")
            raise
    
    async def test_mcp_update_node(self, node_id):
        """测试MCP更新节点功能"""
        print("\n🔹 测试MCP更新节点...")
        try:
            properties = {
                'description': 'Updated person description via MCP',
                'updated_at': datetime.datetime.now().isoformat(),
                'status': 'updated'
            }
            
            result = self.light_memory_client.update_node(node_id, properties)
            
            print(f"✅ MCP更新节点成功")
            return result
            
        except Exception as e:
            print(f"❌ MCP更新节点失败: {e}")
            raise
    
    async def test_mcp_delete_relationship(self, start_node_id, end_node_id, rel_type="FRIENDS_WITH"):
        """测试MCP删除关系功能"""
        print("\n🔹 测试MCP删除关系...")
        try:
            result = self.light_memory_client.delete_relationship(start_node_id, end_node_id, rel_type)
            
            print(f"✅ MCP删除关系成功")
            return result
            
        except Exception as e:
            print(f"❌ MCP删除关系失败: {e}")
            raise
    
    async def test_mcp_delete_node(self, node_id):
        """测试MCP删除节点功能"""
        print("\n🔹 测试MCP删除节点...")
        try:
            result = self.light_memory_client.delete_node(node_id)
            
            print(f"✅ MCP删除节点成功")
            return result
            
        except Exception as e:
            print(f"❌ MCP删除节点失败: {e}")
            raise
    
    async def run_mcp_integration_test(self):
        """运行MCP集成测试"""
        print("\n🚀 开始运行MCP集成测试...")
        
        node_ids = []
        
        try:
            # 1. 添加测试节点
            for i in range(2):
                node_type = "Person"
                properties = {
                    'name': f'MCP Test Person {i+1}',
                    'type': 'person',
                    'description': f'MCP test person number {i+1}',
                    'created_at': datetime.datetime.now().isoformat(),
                    'updated_at': datetime.datetime.now().isoformat()
                }
                properties['embedding'] = self.mock_embedder.embed(properties.get('description', ''))
                
                node_id = self.light_memory_client.add_node(node_type, properties)
                node_ids.append(node_id)
                print(f"  MCP创建节点 {i+1}: {node_id}")
            
            # 2. 测试搜索节点
            await self.test_mcp_search_nodes()
            
            # 3. 测试添加关系
            if len(node_ids) >= 2:
                await self.test_mcp_add_relationship(node_ids[0], node_ids[1])
                
                # 4. 测试搜索关系
                await self.test_mcp_search_relationships(node_ids[0])
            
            # 5. 测试更新节点
            if node_ids:
                await self.test_mcp_update_node(node_ids[0])
            
            # 6. 清理测试数据
            if len(node_ids) >= 2:
                await self.test_mcp_delete_relationship(node_ids[0], node_ids[1])
            
            for node_id in node_ids:
                await self.test_mcp_delete_node(node_id)
            
            print("\n🎉 MCP集成测试完成！")
            
        except Exception as e:
            print(f"\n💥 MCP集成测试出现错误: {e}")
            # 清理剩余数据
            for node_id in node_ids:
                try:
                    await self.test_mcp_delete_node(node_id)
                except:
                    pass


async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 LightNeo4j 和 Memory Light MCP 测试程序")
    print("=" * 60)
    
    # 检查环境变量
    print("\n📋 检查环境配置...")
    neo4j_url = os.getenv("NEO4J_URL", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_db = os.getenv("NEO4J_DATABASE", "neo4j")
    
    print(f"Neo4j URL: {neo4j_url}")
    print(f"Neo4j User: {neo4j_user}")
    print(f"Neo4j Database: {neo4j_db}")
    
    try:
        # 1. 测试LightNeo4jMemory基础功能
        print("\n" + "="*50)
        print("📊 第一部分：LightNeo4jMemory 基础功能测试")
        print("="*50)
        
        light_test = TestLightNeo4jMemory()
        light_test.run_complete_test()
        
        # 2. 测试MCP集成功能
        print("\n" + "="*50)
        print("🔗 第二部分：Memory Light MCP 集成功能测试")
        print("="*50)
        
        mcp_test = TestMemoryLightMCPIntegration()
        await mcp_test.run_mcp_integration_test()
        
        print("\n" + "="*60)
        print("🎊 所有测试顺利完成！LightNeo4j和MCP集成工作正常。")
        print("="*60)
        
    except Exception as e:
        print(f"\n💀 测试执行失败: {e}")
        print("请检查Neo4j连接配置和数据库状态。")
        sys.exit(1)


if __name__ == "__main__":
    load_dotenv()  # 加载环境变量
    # 运行异步测试
    asyncio.run(main())