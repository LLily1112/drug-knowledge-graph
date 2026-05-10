"""
数据提取模块

从结构化 CSV/Excel 数据中提取实体和关系。
"""

import re
import pandas as pd
from collections import defaultdict

from .schema import (
    SPECIAL_POPULATION_MAP,
    POPULATION_PROPERTY_MAP,
)


def load_data(filepath: str, encoding: str = "gbk") -> pd.DataFrame:
    """加载数据文件（CSV 或 Excel）。

    Args:
        filepath: 数据文件路径。
        encoding: CSV 文件编码，默认 gbk。

    Returns:
        pandas DataFrame。
    """
    if filepath.endswith(".xlsx"):
        return pd.read_excel(filepath, sheet_name="KG1")
    elif filepath.endswith(".csv"):
        return pd.read_csv(filepath, encoding=encoding)
    else:
        raise ValueError(f"不支持的文件格式: {filepath}")


def extract_entities_and_relationships(df: pd.DataFrame):
    """从 DataFrame 中提取所有实体和关系。

    Args:
        df: 包含药物信息的 DataFrame。

    Returns:
        tuple: (entity_dict, relationships_list)
            - entity_dict: {实体类型: {实体名称集合}}
            - relationships_list: [(源类型, 源名称, 关系类型, 目标类型, 目标名称)]
    """
    entity_dict = defaultdict(set)
    relationships_list = []

    for _, row in df.iterrows():
        drug_name = row["药物名称"]
        entity_dict["Drug"].add(drug_name)

        # 1. 药物分类
        _extract_drug_class(row, drug_name, entity_dict, relationships_list)

        # 2. 作用机制 -> 蛋白质 + 生物过程
        _extract_mechanism(row, drug_name, entity_dict, relationships_list)

        # 3. 适应症
        _extract_indications(row, drug_name, entity_dict, relationships_list)

        # 4. 不良反应
        _extract_adverse_reactions(row, drug_name, entity_dict, relationships_list)

        # 5. 禁忌症（绝对 + 相对）
        _extract_contraindications(row, drug_name, entity_dict, relationships_list)

        # 6. 特殊人群
        _extract_special_populations(row, drug_name, entity_dict, relationships_list)

        # 7. 临床试验
        _extract_clinical_trials(row, drug_name, entity_dict, relationships_list)

        # 8. 合并症
        _extract_comorbidities(row, drug_name, entity_dict, relationships_list)

    return dict(entity_dict), relationships_list


def _split_by_chinese_comma(text: str) -> list:
    """按中文顿号「、」分割文本。"""
    return [item.strip() for item in str(text).split("、") if item.strip()]


def _extract_drug_class(row, drug_name, entity_dict, relationships_list):
    """提取药物分类。"""
    if pd.notna(row["分类"]):
        drug_class = row["分类"]
        entity_dict["DrugClass"].add(drug_class)
        relationships_list.append(("Drug", drug_name, "BELONGS_TO", "DrugClass", drug_class))


def _extract_mechanism(row, drug_name, entity_dict, relationships_list):
    """从作用机制中提取蛋白质/受体和生物过程。"""
    if pd.notna(row["作用机制"]):
        mechanism = row["作用机制"]

        # 提取蛋白质/受体
        protein_matches = re.findall(
            r"(?:激活|抑制|双重激活)([\w\-]+(?:受体|酶))", mechanism
        )
        for protein in set(protein_matches):
            entity_dict["Protein"].add(protein)
            relationships_list.append(("Drug", drug_name, "TARGETS", "Protein", protein))

        # 提取生物过程
        process_matches = re.findall(
            r"(?:延缓|抑制|减少)([\w\s]+(?:活性|吸收|排空|食欲))", mechanism
        )
        for process in set(process_matches):
            clean_process = process.strip()
            if clean_process:
                entity_dict["BiologicalProcess"].add(clean_process)
                relationships_list.append(
                    ("Drug", drug_name, "AFFECTS", "BiologicalProcess", clean_process)
                )


def _extract_indications(row, drug_name, entity_dict, relationships_list):
    """提取适应症。"""
    if pd.notna(row["适应症"]):
        for disease in _split_by_chinese_comma(row["适应症"]):
            entity_dict["Disease"].add(disease)
            relationships_list.append(("Drug", drug_name, "TREATS", "Disease", disease))


def _extract_adverse_reactions(row, drug_name, entity_dict, relationships_list):
    """提取不良反应（移除括号中的发生率数据）。"""
    if pd.notna(row["安全性"]):
        for reaction in _split_by_chinese_comma(row["安全性"]):
            clean_reaction = re.sub(r"\([^)]*\)", "", reaction).strip()
            if clean_reaction:
                entity_dict["AdverseReaction"].add(clean_reaction)
                relationships_list.append(
                    ("Drug", drug_name, "CAUSES", "AdverseReaction", clean_reaction)
                )


def _extract_contraindications(row, drug_name, entity_dict, relationships_list):
    """提取绝对禁忌症和相对禁忌症。"""
    for col, rel_type in [("绝对禁忌症", "ABSOLUTE_CI"), ("相对禁忌症", "RELATIVE_CI")]:
        if pd.notna(row[col]):
            for ci in _split_by_chinese_comma(row[col]):
                entity_dict["Contraindication"].add(ci)
                relationships_list.append(
                    ("Drug", drug_name, rel_type, "Contraindication", ci)
                )


def _extract_special_populations(row, drug_name, entity_dict, relationships_list):
    """提取特殊人群用法。"""
    for col_ch in SPECIAL_POPULATION_MAP.keys():
        if pd.notna(row[col_ch]):
            pop_en = SPECIAL_POPULATION_MAP[col_ch]
            entity_dict["SpecialPopulation"].add(pop_en)
            relationships_list.append(
                ("Drug", drug_name, "HAS_DOSAGE_FOR", "SpecialPopulation", pop_en)
            )


def _extract_clinical_trials(row, drug_name, entity_dict, relationships_list):
    """从有效性描述中提取临床试验名称。"""
    if pd.notna(row["有效性"]):
        trials = re.findall(r"\(([A-Z]+研究)\)", row["有效性"])
        for trial in set(trials):
            entity_dict["ClinicalTrial"].add(trial)
            relationships_list.append(
                ("Drug", drug_name, "STUDIED_IN", "ClinicalTrial", trial)
            )


def _extract_comorbidities(row, drug_name, entity_dict, relationships_list):
    """提取合并症首选药物信息。"""
    if pd.notna(row["合并症首先使用药物"]):
        for comorbidity in _split_by_chinese_comma(row["合并症首先使用药物"]):
            entity_dict["Comorbidity"].add(comorbidity)
            relationships_list.append(
                ("Drug", drug_name, "FIRST_CHOICE_FOR", "Comorbidity", comorbidity)
            )


def extract_drug_properties(df: pd.DataFrame) -> dict:
    """提取药物属性信息。

    Args:
        df: 包含药物信息的 DataFrame。

    Returns:
        dict: {药物名称: {属性名: 属性值}}
    """
    properties_map = {}

    for _, row in df.iterrows():
        drug_name = row["药物名称"]
        props = {}

        # 剂量策略
        if pd.notna(row["剂量策略"]):
            props["dosage_strategy"] = str(row["剂量策略"])

        # 有效性
        if pd.notna(row["有效性"]):
            props["efficacy"] = str(row["有效性"])

        # 特殊人群属性
        for col_ch, prop_name in POPULATION_PROPERTY_MAP:
            if pd.notna(row[col_ch]):
                props[prop_name] = str(row[col_ch])

        if props:
            properties_map[drug_name] = props

    return properties_map
