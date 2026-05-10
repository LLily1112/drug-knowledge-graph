"""
知识图谱构建主程序

从结构化数据中提取药物实体与关系，导入 Neo4j 构建知识图谱。

使用方法:
    python main.py --data data/KG1.csv --neo4j-uri bolt://localhost:7687 --neo4j-password your_password
"""

import argparse
import os
import sys

from .schema import ENTITY_TYPES
from .extractor import load_data, extract_entities_and_relationships, extract_drug_properties
from .neo4j_manager import connect, clear_graph, create_constraints, create_nodes, create_relationships, update_drug_properties


def parse_args():
    parser = argparse.ArgumentParser(description="肥胖症用药知识图谱构建工具")
    parser.add_argument(
        "--data", type=str, default="data/KG1.csv",
        help="数据文件路径 (CSV 或 Excel)，默认: data/KG1.csv"
    )
    parser.add_argument(
        "--encoding", type=str, default="gbk",
        help="CSV 文件编码，默认: gbk"
    )
    parser.add_argument(
        "--neo4j-uri", type=str, default="bolt://localhost:7687",
        help="Neo4j 连接 URI，默认: bolt://localhost:7687"
    )
    parser.add_argument(
        "--neo4j-user", type=str, default="neo4j",
        help="Neo4j 用户名，默认: neo4j"
    )
    parser.add_argument(
        "--neo4j-password", type=str, default="password",
        help="Neo4j 密码，默认: password"
    )
    parser.add_argument(
        "--skip-clear", action="store_true",
        help="跳过清空数据库步骤（不清除已有数据）"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # 检查数据文件是否存在
    if not os.path.exists(args.data):
        print(f"[ERROR] 数据文件不存在: {args.data}")
        sys.exit(1)

    # ---- Step 1: 加载数据 ----
    print("=" * 60)
    print("[Step 1] 加载数据...")
    print("=" * 60)
    df = load_data(args.data, args.encoding)
    print(f"  成功加载 {len(df)} 条药物记录\n")

    # ---- Step 2: 提取实体和关系 ----
    print("=" * 60)
    print("[Step 2] 提取实体和关系...")
    print("=" * 60)
    entity_dict, relationships_list = extract_entities_and_relationships(df)

    total_entities = sum(len(v) for v in entity_dict.values())
    print(f"  实体总数: {total_entities}")
    for etype, entities in entity_dict.items():
        print(f"    {etype}: {len(entities)} 个")
    print(f"  关系总数: {len(relationships_list)}\n")

    # ---- Step 3: 提取药物属性 ----
    print("=" * 60)
    print("[Step 3] 提取药物属性...")
    print("=" * 60)
    properties_map = extract_drug_properties(df)
    print(f"  已提取 {len(properties_map)} 个药物的属性信息\n")

    # ---- Step 4: 连接 Neo4j ----
    print("=" * 60)
    print("[Step 4] 连接 Neo4j 数据库...")
    print("=" * 60)
    try:
        graph = connect(args.neo4j_uri, args.neo4j_user, args.neo4j_password)
        print(f"  已连接: {args.neo4j_uri}\n")
    except Exception as e:
        print(f"[ERROR] 无法连接 Neo4j: {e}")
        print("  请确保 Neo4j 服务已启动，并检查连接参数。")
        sys.exit(1)

    # ---- Step 5: 清空数据库（可选） ----
    if not args.skip_clear:
        print("=" * 60)
        print("[Step 5] 清空数据库...")
        print("=" * 60)
        clear_graph(graph)
        print()

    # ---- Step 6: 创建约束 ----
    print("=" * 60)
    print("[Step 6] 创建唯一性约束...")
    print("=" * 60)
    create_constraints(graph, ENTITY_TYPES)
    print()

    # ---- Step 7: 创建节点 ----
    print("=" * 60)
    print("[Step 7] 创建节点...")
    print("=" * 60)
    create_nodes(graph, entity_dict)
    print()

    # ---- Step 8: 创建关系 ----
    print("=" * 60)
    print("[Step 8] 创建关系...")
    print("=" * 60)
    create_relationships(graph, relationships_list)
    print()

    # ---- Step 9: 更新药物属性 ----
    print("=" * 60)
    print("[Step 9] 更新药物属性...")
    print("=" * 60)
    update_drug_properties(graph, properties_map)
    print()

    # ---- 完成 ----
    print("=" * 60)
    print("知识图谱构建完成！")
    print(f"  节点总数: {total_entities}")
    print(f"  关系总数: {len(relationships_list)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
