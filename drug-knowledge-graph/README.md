# Drug Knowledge Graph | 肥胖症用药知识图谱

基于《减重药物临床应用专家共识》，利用 Python 从结构化数据中提取药物实体与关系，构建以 Neo4j 为存储的**肥胖症用药知识图谱**。

## 项目背景

本项目对《减重药物临床应用专家共识》进行知识图谱建模，涵盖 5 种主流减肥药物（司美格鲁肽、替尔泊肽、奥利司他、利拉鲁肽、贝那鲁肽）的完整用药信息，包括药物分类、作用机制、适应症、不良反应、禁忌症、特殊人群用药、临床试验及合并症处理等维度。

## 知识图谱概览

### 实体类型 (10 种)

| 实体类型 | 说明 | 示例 |
|---------|------|------|
| **Drug** | 药物 | 司美格鲁肽2.4mg、替尔泊肽、奥利司他 |
| **DrugClass** | 药物分类 | GLP-1受体激动剂、GIP/GLP-1双受体激动剂 |
| **Protein** | 蛋白质/受体 | GLP-1受体、胃肠脂肪酶 |
| **BiologicalProcess** | 生物过程 | 胃排空、胃肠脂肪酶活性 |
| **Disease** | 疾病/适应症 | 肥胖症 |
| **AdverseReaction** | 不良反应 | 恶心/呕吐、胆囊疾病风险 |
| **Contraindication** | 禁忌症 | 甲状腺髓样癌史、胰腺炎活动期 |
| **SpecialPopulation** | 特殊人群 | Children、Elderly、Pregnancy |
| **ClinicalTrial** | 临床试验 | STEP2、LEADER、SELECT |
| **Comorbidity** | 合并症 | 2型糖尿病、心血管疾病、多囊卵巢综合征 |

### 关系类型 (9 种)

```
Drug --[BELONGS_TO]--> DrugClass          药物属于某分类
Drug --[TARGETS]--> Protein               药物作用于某蛋白质/受体
Drug --[AFFECTS]--> BiologicalProcess     药物影响某生物过程
Drug --[TREATS]--> Disease                药物治疗某疾病
Drug --[CAUSES]--> AdverseReaction        药物引起某不良反应
Drug --[ABSOLUTE_CI]--> Contraindication  绝对禁忌
Drug --[RELATIVE_CI]--> Contraindication  相对禁忌
Drug --[HAS_DOSAGE_FOR]--> SpecialPopulation  特殊人群用法
Drug --[STUDIED_IN]--> ClinicalTrial      临床试验
Drug --[FIRST_CHOICE_FOR]--> Comorbidity  合并症首选药物
```

## 项目结构

```
drug-knowledge-graph/
├── data/
│   └── KG1.csv              # 原始数据（药物信息结构化表）
├── src/
│   ├── __init__.py           # 包初始化
│   ├── schema.py             # 实体与关系类型定义
│   ├── extractor.py          # 数据提取模块（从CSV/Excel提取实体和关系）
│   ├── neo4j_manager.py      # Neo4j 数据库操作模块
│   └── main.py               # 主程序入口
├── docs/
│   └── schema_design.md      # 知识图谱模式设计文档
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 环境要求

- Python 3.8+
- Neo4j 4.x / 5.x（需提前安装并启动）

## 安装

```bash
# 克隆项目
git clone https://github.com/LLily1112/drug-knowledge-graph.git
cd drug-knowledge-graph

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 启动 Neo4j

确保 Neo4j 服务已启动，默认连接地址为 `bolt://localhost:7687`。

### 2. 运行构建程序

```bash
# 使用默认参数
python -m src.main

# 自定义参数
python -m src.main \
    --data data/KG1.csv \
    --encoding gbk \
    --neo4j-uri bolt://localhost:7687 \
    --neo4j-user neo4j \
    --neo4j-password your_password

# 跳过清空数据库（增量更新）
python -m src.main --skip-clear
```

### 3. 在 Neo4j Browser 中查看

打开 [http://localhost:7474](http://localhost:7474)，运行 Cypher 查询：

```cypher
// 查看所有药物及其分类
MATCH (d:Drug)-[r:BELONGS_TO]->(c:DrugClass)
RETURN d.name, r, c.name

// 查看某药物的所有关系
MATCH (d:Drug {name: '司美格鲁肽2.4mg'})-[r]-(n)
RETURN d, r, n

// 查看所有禁忌症
MATCH (d:Drug)-[:ABSOLUTE_CI|RELATIVE_CI]->(c:Contraindication)
RETURN d.name, type(r), c.name

// 查看合并症首选药物
MATCH (d:Drug)-[:FIRST_CHOICE_FOR]->(co:Comorbidity)
RETURN d.name, co.name
```

## 命令行参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--data` | `data/KG1.csv` | 数据文件路径（CSV 或 Excel） |
| `--encoding` | `gbk` | CSV 文件编码 |
| `--neo4j-uri` | `bolt://localhost:7687` | Neo4j 连接 URI |
| `--neo4j-user` | `neo4j` | Neo4j 用户名 |
| `--neo4j-password` | `password` | Neo4j 密码 |
| `--skip-clear` | `False` | 跳过清空数据库 |

## 数据说明

`data/KG1.csv` 包含以下字段：

| 字段 | 说明 |
|------|------|
| 药物名称 | 药品通用名 |
| 分类 | 药理学分类 |
| 作用机制 | 药物作用靶点和机制描述 |
| 适应症 | 临床适应症 |
| 有效性 | 临床试验数据及疗效 |
| 安全性 | 不良反应及发生率 |
| 绝对禁忌症 | 绝对禁忌情况 |
| 相对禁忌症 | 相对禁忌情况 |
| 剂量策略 | 推荐剂量及调整方案 |
| 儿童/老人/肝功能不全/围术期/妊娠期/肾功能不全 | 特殊人群用药建议 |
| 合并症首先使用药物 | 合并症首选药物推荐 |

## 技术栈

- **数据提取**: Python, pandas, regex
- **图数据库**: Neo4j
- **数据库驱动**: py2neo

## 许可证

MIT License

## 致谢

本项目数据来源于《减重药物临床应用专家共识》，仅供学术研究和学习交流使用。
