# 知识图谱模式设计文档

## 1. 数据来源

数据来源于《减重药物临床应用专家共识》，涵盖 5 种肥胖症治疗药物的结构化用药信息。

## 2. 实体类型设计

### 2.1 Drug（药物）

药物是知识图谱的核心实体，包含以下属性：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 药物名称（唯一标识） |
| dosage_strategy | string | 剂量策略 |
| efficacy | string | 有效性数据 |
| children_dosage | string | 儿童用药建议 |
| elderly_dosage | string | 老年人用药建议 |
| liver_dosage | string | 肝功能不全用药建议 |
| perioperative_dosage | string | 围术期用药建议 |
| pregnancy_dosage | string | 妊娠期用药建议 |
| renal_dosage | string | 肾功能不全用药建议 |

### 2.2 DrugClass（药物分类）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 分类名称（唯一标识） |

### 2.3 Protein（蛋白质/受体）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 蛋白质/受体名称（唯一标识） |

### 2.4 BiologicalProcess（生物过程）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 生物过程名称（唯一标识） |

### 2.5 Disease（疾病/适应症）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 疾病名称（唯一标识） |

### 2.6 AdverseReaction（不良反应）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 不良反应名称（唯一标识） |

### 2.7 Contraindication（禁忌症）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 禁忌症名称（唯一标识） |

### 2.8 SpecialPopulation（特殊人群）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 人群标识（英文，唯一标识） |

### 2.9 ClinicalTrial（临床试验）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 试验名称缩写（唯一标识） |

### 2.10 Comorbidity（合并症）

| 属性名 | 类型 | 说明 |
|--------|------|------|
| name | string | 合并症名称（唯一标识） |

## 3. 关系类型设计

| 关系类型 | 源实体 | 目标实体 | 说明 |
|---------|--------|---------|------|
| BELONGS_TO | Drug | DrugClass | 药物属于某药理学分类 |
| TARGETS | Drug | Protein | 药物作用的蛋白质/受体靶点 |
| AFFECTS | Drug | BiologicalProcess | 药物影响的生物过程 |
| TREATS | Drug | Disease | 药物治疗的疾病/适应症 |
| CAUSES | Drug | AdverseReaction | 药物引起的不良反应 |
| ABSOLUTE_CI | Drug | Contraindication | 绝对禁忌症 |
| RELATIVE_CI | Drug | Contraindication | 相对禁忌症 |
| HAS_DOSAGE_FOR | Drug | SpecialPopulation | 特殊人群用药建议 |
| STUDIED_IN | Drug | ClinicalTrial | 相关临床试验 |
| FIRST_CHOICE_FOR | Drug | Comorbidity | 合并症首选药物 |

## 4. 数据提取规则

### 4.1 作用机制提取

使用正则表达式从文本中提取：
- **蛋白质/受体**: 匹配 `激活/抑制/双重激活` + `受体/酶` 模式
- **生物过程**: 匹配 `延缓/抑制/减少` + `活性/吸收/排空/食欲` 模式

### 4.2 多值字段分割

以下字段使用中文顿号「、」作为分隔符：
- 适应症、安全性（不良反应）、绝对禁忌症、相对禁忌症、合并症首先使用药物

### 4.3 不良反应清洗

自动移除括号中的发生率数据，例如：
- 原文: `恶心/呕吐（>30%）` → 清洗后: `恶心/呕吐`
- 原文: `油性便（20-30%）` → 清洗后: `油性便`

### 4.4 临床试验提取

从有效性字段中提取括号内的大写字母研究名称，例如：
- `减重9.6%（STEP2）` → `STEP2`
- `降低MACE风险20%（SELECT）` → `SELECT`

## 5. 图谱统计

- **药物数量**: 5
- **实体类型**: 10
- **关系类型**: 10（含 ABSOLUTE_CI 和 RELATIVE_CI 两种禁忌关系）
- **节点总数**: 约 40+
- **关系总数**: 约 60+
