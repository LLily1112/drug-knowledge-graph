"""
Neo4j 图数据库操作模块

负责将提取的实体和关系导入 Neo4j 数据库。
"""

from py2neo import Graph, Node


def connect(uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password") -> Graph:
    """连接 Neo4j 数据库。

    Args:
        uri: Neo4j 连接 URI。
        user: 用户名。
        password: 密码。

    Returns:
        py2neo Graph 实例。
    """
    graph = Graph(uri, auth=(user, password))
    return graph


def clear_graph(graph: Graph):
    """清空图中所有节点和关系。

    注意: 仅建议在开发环境使用！

    Args:
        graph: py2neo Graph 实例。
    """
    graph.run("MATCH (n) DETACH DELETE n")
    print("[INFO] 已清空图数据库。")


def create_constraints(graph: Graph, entity_types: list):
    """为每种实体类型创建唯一性约束。

    Args:
        graph: py2neo Graph 实例。
        entity_types: 实体类型列表。
    """
    for entity_type in entity_types:
        graph.run(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{entity_type}) "
            f"REQUIRE n.name IS UNIQUE"
        )
        print(f"[INFO] 已创建约束: {entity_type}.name IS UNIQUE")


def create_nodes(graph: Graph, entity_dict: dict):
    """批量创建节点。

    Args:
        graph: py2neo Graph 实例。
        entity_dict: {实体类型: {实体名称集合}}
    """
    for entity_type, entities in entity_dict.items():
        for name in entities:
            node = Node(entity_type, name=name)
            graph.merge(node, entity_type, "name")
            print(f"  [NODE] {entity_type} - {name}")


def create_relationships(graph: Graph, relationships_list: list):
    """批量创建关系。

    Args:
        graph: py2neo Graph 实例。
        relationships_list: [(源类型, 源名称, 关系类型, 目标类型, 目标名称)]
    """
    for rel in relationships_list:
        src_type, src_name, rel_type, tgt_type, tgt_name = rel

        query = f"""
            MATCH (a:{src_type} {{name: $src_name}})
            MATCH (b:{tgt_type} {{name: $tgt_name}})
            MERGE (a)-[r:{rel_type}]->(b)
            RETURN r
        """
        try:
            result = graph.run(query, src_name=src_name, tgt_name=tgt_name).data()
            if result:
                print(f"  [REL]  {src_name} -[{rel_type}]-> {tgt_name}")
            else:
                print(f"  [FAIL] {src_name} -[{rel_type}]-> {tgt_name}")
        except Exception as e:
            print(f"  [ERR]  创建关系失败: {e}")


def update_drug_properties(graph: Graph, properties_map: dict):
    """更新药物节点的属性。

    Args:
        graph: py2neo Graph 实例。
        properties_map: {药物名称: {属性名: 属性值}}
    """
    for drug_name, props in properties_map.items():
        query = """
            MATCH (d:Drug {name: $name})
            SET d += $props
            RETURN d
        """
        result = graph.run(query, name=drug_name, props=props).data()
        if result:
            print(f"  [PROP] 已更新属性: {drug_name}")
        else:
            print(f"  [FAIL] 更新属性失败: {drug_name}")
