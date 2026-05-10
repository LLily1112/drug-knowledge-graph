"""
实体与关系定义模块

定义知识图谱中所有实体类型和关系类型。
"""

# ============================================================
# 实体类型
# ============================================================
ENTITY_TYPES = [
    "Drug",             # 药物
    "DrugClass",        # 药物分类
    "Protein",          # 蛋白质/受体
    "BiologicalProcess",# 生物过程
    "Disease",          # 疾病/适应症
    "AdverseReaction",  # 不良反应
    "Contraindication", # 禁忌症
    "SpecialPopulation",# 特殊人群
    "ClinicalTrial",    # 临床试验
    "Comorbidity"       # 合并症
]

# ============================================================
# 关系类型: (源实体, 关系名, 目标实体)
# ============================================================
RELATIONSHIP_TYPES = [
    ("Drug", "BELONGS_TO", "DrugClass"),
    ("Drug", "TARGETS", "Protein"),
    ("Drug", "AFFECTS", "BiologicalProcess"),
    ("Drug", "TREATS", "Disease"),
    ("Drug", "CAUSES", "AdverseReaction"),
    ("Drug", "CONTRAINDICATED_IN", "Contraindication"),
    ("Drug", "HAS_DOSAGE_FOR", "SpecialPopulation"),
    ("Drug", "STUDIED_IN", "ClinicalTrial"),
    ("Drug", "FIRST_CHOICE_FOR", "Comorbidity"),
]

# ============================================================
# 特殊人群中英文映射
# ============================================================
SPECIAL_POPULATION_MAP = {
    "儿童": "Children",
    "老人": "Elderly",
    "肝功能不全": "LiverDysfunction",
    "围术期": "Perioperative",
    "妊娠期": "Pregnancy",
    "肾功能不全": "RenalDysfunction",
}

# ============================================================
# 特殊人群属性名映射 (中文列名 -> 英文属性名)
# ============================================================
POPULATION_PROPERTY_MAP = [
    ("儿童", "children_dosage"),
    ("老人", "elderly_dosage"),
    ("肝功能不全", "liver_dosage"),
    ("围术期", "perioperative_dosage"),
    ("妊娠期", "pregnancy_dosage"),
    ("肾功能不全", "renal_dosage"),
]
