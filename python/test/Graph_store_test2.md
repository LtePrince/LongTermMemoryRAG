
--- Cleaning up previous test data ---

--- Adding initial conversation segment ---
No similar paragraphs found. Creating new paragraph.
Created new Paragraph node: 96bb3bee-6420-47ec-9789-d28b3390f56b
Added paragraph 1 with ID: 96bb3bee-6420-47ec-9789-d28b3390f56b

--- Adding a related conversation segment (should merge) ---
Medium similarity (0.81) with existing paragraph 96bb3bee-6420-47ec-9789-d28b3390f56b. Prompting user.
User chose to merge with 96bb3bee-6420-47ec-9789-d28b3390f56b.
Processed paragraph 2. Final ID (merged/new): 96bb3bee-6420-47ec-9789-d28b3390f56b

--- Adding a moderately related segment (should prompt user) ---
Medium similarity (0.83) with existing paragraph 96bb3bee-6420-47ec-9789-d28b3390f56b. Prompting user.
User chose to create new paragraph (or default).
Created new Paragraph node: 801b0f52-cce6-48a6-a8e6-d9b605a47db4
Created FOLLOWS relationship from 96bb3bee-6420-47ec-9789-d28b3390f56b to 801b0f52-cce6-48a6-a8e6-d9b605a47db4
Processed paragraph 3. Final ID (merged/new/relate): 801b0f52-cce6-48a6-a8e6-d9b605a47db4

--- Adding a new, unrelated conversation segment ---
Medium similarity (0.70) with existing paragraph 96bb3bee-6420-47ec-9789-d28b3390f56b. Prompting user.
User chose to create new paragraph (or default).
Created new Paragraph node: 8ac44e01-3b9d-4db9-8d17-70a5f508753e
Created FOLLOWS relationship from 801b0f52-cce6-48a6-a8e6-d9b605a47db4 to 8ac44e01-3b9d-4db9-8d17-70a5f508753e
Added paragraph 4 with ID: 8ac44e01-3b9d-4db9-8d17-70a5f508753e

--- Adding a very long paragraph (should trigger split) ---
Medium similarity (0.73) with existing paragraph 96bb3bee-6420-47ec-9789-d28b3390f56b. Prompting user.
User chose to merge with 96bb3bee-6420-47ec-9789-d28b3390f56b.
Attempting to split large Paragraph: 96bb3bee-6420-47ec-9789-d28b3390f56b
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: 0c44802b-e6a2-435c-afdb-270b4ff7ed13, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: 2b0ae323-7009-493d-9f39-b881613989f3, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 项目A的第二阶段实施方案, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: 187e236d-8277-4638-bd9f-bc12979d6ab7, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 用户需求调研, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: c41afbd9-4dc2-4089-9628-f2180cbae28d, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 技术团队将进行架构设计评审, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: b7befddb-93e5-4f68-960e-e492781c2340, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 数据迁移工作, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: 3fd51be5-aa25-443e-8005-8426e52e862c, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 市场推广部门的初步推广计划, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: dbc62786-caf7-4571-9a10-62bf99a96f75, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 张三强调了风险管理的重要性, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: 18acffa2-9b16-499f-a4a7-a6df5610780b, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 王五提及了资源分配的挑战, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: d4404031-1ebf-49a7-9e71-4fca5b63d833, linked by CONTAINS_SUBTOPIC
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Concept: 会议持续了三个小时，最终形成了详细的任务分解WBS和时间表, linked by MENTIONS_CONCEPT
DEBUG: Original Paragraph '96bb3bee-6420-47ec-9789-d28b3390f56b' found for linking Concept.
Split to new Paragraph: c6a13f50-d61c-4c6f-97d5-2d79aca96f57, linked by CONTAINS_SUBTOPIC
Processed long paragraph. Final ID: 96bb3bee-6420-47ec-9789-d28b3390f56b

--- Searching for '项目A的进展' ---
  Type: paragraph, ID/Name: 96bb3bee-6420-47ec-9789-d28b3390f56b, Score/Description: 0.8505973815917969
  Type: paragraph, ID/Name: 2b0ae323-7009-493d-9f39-b881613989f3, Score/Description: 0.8303251266479492
  Type: paragraph, ID/Name: 187e236d-8277-4638-bd9f-bc12979d6ab7, Score/Description: 0.8095946311950684
  Type: entity, ID/Name: 张三, Score/Description: 项目A的负责人
  Type: entity, ID/Name: 项目A, Score/Description: 上个季度的项目
  Type: entity, ID/Name: AI, Score/Description: 人工智能
  Type: entity, ID/Name: 子任务, Score/Description: 项目A的子任务
  Type: entity, ID/Name: 第二阶段实施方案, Score/Description: 项目A的实施阶段
  Type: entity, ID/Name: 团队, Score/Description: 讨论项目A的团队
  Type: entity, ID/Name: 推广计划, Score/Description: 市场活动计划
  Type: entity, ID/Name: 时间表, Score/Description: 项目计划
  Type: entity, ID/Name: WBS, Score/Description: 任务分解工具
  Type: entity, ID/Name: 高级开发人员, Score/Description: 招聘对象
  Type: entity, ID/Name: 资源分配, Score/Description: 项目挑战
  Type: entity, ID/Name: 王五, Score/Description: 人名
  Type: entity, ID/Name: 数据隐私合规性, Score/Description: 风险点
  Type: entity, ID/Name: 风险管理, Score/Description: 项目考虑因素
  Type: entity, ID/Name: 线下沙龙活动, Score/Description: 推广方式
  Type: entity, ID/Name: 线上广告投放, Score/Description: 推广方式
  Type: entity, ID/Name: 市场推广部门, Score/Description: 提出推广计划
  Type: entity, ID/Name: ETL工具, Score/Description: 数据迁移工具
  Type: entity, ID/Name: 数据迁移, Score/Description: 重要项目任务
  Type: entity, ID/Name: 架构设计评审, Score/Description: 技术任务
  Type: entity, ID/Name: 技术团队, Score/Description: 执行架构设计评审
  Type: entity, ID/Name: 关键客户, Score/Description: 调研对象
  Type: entity, ID/Name: 用户需求调研, Score/Description: 项目阶段任务
  Type: concept, ID/Name: 会议持续了三个小时，最终形成了详细的任务分解WBS和时间表, Score/Description: 概念：会议持续了三个小时，最终形成了详细的任务分解WBS和时间表 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 王五提及了资源分配的挑战, Score/Description: 概念：王五提及了资源分配的挑战 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 张三强调了风险管理的重要性, Score/Description: 概念：张三强调了风险管理的重要性 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 市场推广部门的初步推广计划, Score/Description: 概念：市场推广部门的初步推广计划 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 数据迁移工作, Score/Description: 概念：数据迁移工作 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 技术团队将进行架构设计评审, Score/Description: 概念：技术团队将进行架构设计评审 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 用户需求调研, Score/Description: 概念：用户需求调研 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: concept, ID/Name: 项目A的第二阶段实施方案, Score/Description: 概念：项目A的第二阶段实施方案 源自段落 96bb3bee-6420-47ec-9789-d28b3390f56b
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None

--- Searching for '太空游戏' ---
  Type: paragraph, ID/Name: 8ac44e01-3b9d-4db9-8d17-70a5f508753e, Score/Description: 0.7963249683380127
  Type: paragraph, ID/Name: 2b0ae323-7009-493d-9f39-b881613989f3, Score/Description: 0.6507713794708252
  Type: entity, ID/Name: 张三, Score/Description: 项目A的负责人
  Type: entity, ID/Name: 项目A, Score/Description: 上个季度的项目
  Type: entity, ID/Name: AI, Score/Description: 人工智能
  Type: entity, ID/Name: 外星生物, Score/Description: 游戏中的外星生物
  Type: entity, ID/Name: 星际漫游者, Score/Description: 太空探索游戏
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None
  Type: relation, ID/Name: None, Score/Description: None

--- Updating paragraph 1 ---
Updated Paragraph node: 96bb3bee-6420-47ec-9789-d28b3390f56b
Paragraph 96bb3bee-6420-47ec-9789-d28b3390f56b updated: True

--- Done ---