"""
肥胖症用药知识图谱构建工具

基于《中国肥胖症诊疗指南》专家共识，从结构化数据中提取药物实体与关系，
构建以 Neo4j 为存储的知识图谱。

实体类型:
    - Drug: 药物
    - DrugClass: 药物分类
    - Protein: 蛋白质/受体
    - BiologicalProcess: 生物过程
    - Disease: 疾病/适应症
    - AdverseReaction: 不良反应
    - Contraindication: 禁忌症
    - SpecialPopulation: 特殊人群
    - ClinicalTrial: 临床试验
    - Comorbidity: 合并症

关系类型:
    - BELONGS_TO: 药物属于某分类
    - TARGETS: 药物作用于某蛋白质/受体
    - AFFECTS: 药物影响某生物过程
    - TREATS: 药物治疗某疾病
    - CAUSES: 药物引起某不良反应
    - ABSOLUTE_CI / RELATIVE_CI: 绝对/相对禁忌
    - HAS_DOSAGE_FOR: 药物在某特殊人群中的用法
    - STUDIED_IN: 药物在某临床试验中被研究
    - FIRST_CHOICE_FOR: 药物是某合并症的首选
"""

__version__ = "1.0.0"
__author__ = "LLily1112"
