import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()  # 加载环境变量

import time

from memoryrag.graph_store import Neo4jMemory
from memoryrag.config import LlmConfig, Neo4jConfig



if __name__ == "__main__":

    config = Neo4jConfig.from_env()
    memory = Neo4jMemory(config)

    # 清理旧数据 (仅用于测试)
    print("\n--- Cleaning up previous test data ---")
    memory.graph.query("MATCH (n) DETACH DELETE n") # 慎用在生产环境
    memory._ensure_vector_index() # 重新确保索引存在

    print("\n--- Adding initial conversation segment ---")
    para1_id = memory.add(
        "用户：你好，我想了解一下关于我们上个季度项目A的进展情况，张三负责的那个。"
    )
    print(f"Added paragraph 1 with ID: {para1_id}")
    time.sleep(1)

    print("\n--- Adding a related conversation segment (should merge) ---")
    # 这段话和第一段高度相关，应该会被合并
    para2_id = memory.add(
        "AI：好的。项目A目前已完成第一阶段的目标，张三正在准备第二阶段的启动会议。",
        prev_paragraph_id=para1_id
    )
    print(f"Processed paragraph 2. Final ID (merged/new): {para2_id}") # 应该和para1_id一样

    time.sleep(1)

    print("\n--- Adding a moderately related segment (should prompt user) ---")
    # 这段话可能需要用户确认是合并还是建立关系
    para3_text = "用户：那王五最近在忙什么？他是不是也在负责其他项目？"
    # 模拟用户可能会选择 'new' 或 'relate'
    # 注意：这里因为_prompt_user_for_confirmation是模拟的，总是返回'new'，
    # 实际运行时，你需要修改DeepSeekLLM的invoke方法来模拟不同的用户响应，或者在外部进行交互。
    para3_id = memory.add(
        para3_text,
        prev_paragraph_id=para2_id if para2_id else para1_id
    )
    print(f"Processed paragraph 3. Final ID (merged/new/relate): {para3_id}")
    time.sleep(1)

    print("\n--- Adding a new, unrelated conversation segment ---")
    # 这段话应该会创建新节点
    para4_id = memory.add(
        "用户：我最近在玩一款太空探索游戏，叫'星际漫游者'，里面有很多外星生物。",
        prev_paragraph_id=para3_id
    )
    print(f"Added paragraph 4 with ID: {para4_id}")
    time.sleep(1)

    print("\n--- Adding a very long paragraph (should trigger split) ---")
    long_text = "今天我们团队深入讨论了项目A的第二阶段实施方案，其中包括了多个子任务。首先，我们需要完成用户需求调研，这涉及到与十个关键客户进行深度访谈，预计需要两周时间。其次，技术团队将进行架构设计评审，确保系统可扩展性和安全性，预计在一周内完成。第三，数据迁移工作是重中之重，我们将使用新的ETL工具，并计划在下个月初完成。此外，市场推广部门也提出了初步的推广计划，包括线上广告投放和线下沙龙活动。张三强调了风险管理的重要性，特别是关于数据隐私合规性方面。王五则提及了资源分配的挑战，尤其是高级开发人员的招聘进度。会议持续了三个小时，最终形成了详细的任务分解WBS和时间表。大家对项目成功充满信心。"
    para_long_id = memory.add(long_text, prev_paragraph_id=para2_id if para2_id else para1_id)
    print(f"Processed long paragraph. Final ID: {para_long_id}")
    time.sleep(2) # 留时间让分裂操作完成

    print("\n--- Searching for '项目A的进展' ---")
    search_results = memory.search("项目A的进展", top_k=3)
    for res in search_results:
        print(f"  Type: {res.get('type')}, ID/Name: {res.get('id') or res.get('name')}, Score/Description: {res.get('score') or res.get('description')}")
    
    print("\n--- Searching for '太空游戏' ---")
    search_results_game = memory.search("太空游戏", top_k=2)
    for res in search_results_game:
        print(f"  Type: {res.get('type')}, ID/Name: {res.get('id') or res.get('name')}, Score/Description: {res.get('score') or res.get('description')}")

    print("\n--- Updating paragraph 1 ---")
    updated_para1 = memory.update(para1_id, "用户：我上次问了项目A的进展，张三说第一阶段完成了，第二阶段在准备。现在有什么新情况吗？")
    print(f"Paragraph {para1_id} updated: {updated_para1}")
    time.sleep(1)

    print("\n--- Deleting paragraph 4 ---")
    deleted_para4 = memory.delete(para4_id)
    print(f"Paragraph {para4_id} deleted: {deleted_para4}")
    time.sleep(1)

    print("\n--- Running isolated node cleanup (optional) ---")
    memory._clean_isolated_nodes()

    print("\n--- Done ---")