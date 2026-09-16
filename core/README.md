> ## Canonical ontology notice
>
> Shared human/persona concepts are now governed by `../ontology/human_ontology.v1.json`.
> This core generator may keep legacy field names and the 6-domain × 4-stage event matrix for compatibility, but those structures are not the canonical ontology.
>
> **Rule: orthogonal axes across the system; MECE within each axis.**
> Personality fields must map to the canonical 7-layer personality model. New ontology concepts require `../ontology/HUMAN_ONTOLOGY_REVIEW.md`.

# Persona Generator — 精神病学评估用全量 Persona 生成引擎

> 生成具有统计学意义的模拟人物（Patient/Healthy），用于精神病学 AI 评估与模拟。

---

## 目录

1. [概述](#1-概述)
2. [职业分类（occupations.py）](#2-职业分类occupationspy)
3. [性格系统（personality.py）](#3-性格系统personalitypy)
4. [Will Storr 叙事因果链增强（personality.py）](#4-will-storr-叙事因果链增强personalitypy)
5. [K.M. Weiland 角色弧线（personality.py）](#5-km-weiland-角色弧线personalitypy)
6. [症状触发器与生理特征（triggers.py）](#6-症状触发器与生理特征triggerspy)
7. [生活事件（events.py）](#7-生活事件eventspy)
8. [主生成器（generator.py）](#8-主生成器generatorpy)
9. [快速开始](#9-快速开始)
10. [参数可调性](#10-参数可调性)
11. [输出示例](#11-输出示例)

---

## 0. 人设元类型网格（archetypes.py）— v1.2 核心

> **为什么需要它**：v1.1 及以前宣称「三层空间 10²⁹ → 10⁷~10⁸ → 75 变体」，
> 但实测发现真正决定人设内核的字段模板池极小（价值观 11 种、社交 17 种、
> 创伤每诊断 5 条、补偿欲望/内在需要每诊断仅 1 条），内核严重同质；
> 而 10²⁹ 只是概率软约束的名义组合数，无法枚举与覆盖验证。

### 模型

```
诊断 (37)
  └─ 人设元类型 archetype（每诊断 4~5 个）      ← 硬网格，可枚举
       └─ 型内变体 wounds × desires × needs     ← 深层叙事内核
            └─ 表层 OCEAN / 标签 / 事件          ← 不改变心理内核
```

### 每个 archetype 含

| 字段 | 说明 |
|------|------|
| key / name_cn / one_liner | 型标识与一句话特征 |
| weight | 同一诊断内的采样权重 |
| `wounds` | 形成性创伤池（3-5 条，**型专属**） |
| `compensatory_desires` | 补偿性欲望（2-3 条，取代旧的全局单值） |
| `storr_needs` | 内在需要（2-3 条，取代旧的全局单值） |
| core_desire / core_fear | 覆盖诊断默认 |
| `values_tone` / `social_tone` | 注入 MECE 六维的型专属基调 |
| `ocean_bias` | OCEAN 偏置（微调，使同诊断不同型轮廓可区分） |

### 用法

```python
from core.archetypes import (
    sample_archetype, get_archetypes, has_archetypes,
    sample_from_archetype, apply_archetype_tone, apply_ocean_bias,
    calculate_archetype_compression, ARCHETYPES,
)

a = sample_archetype("depressive", rng)   # None 表示该诊断未定义网格（回退旧逻辑）
print(a["name_cn"], a["one_liner"])

calculate_archetype_compression()         # 打印空间报告
# 命令行： python core/archetypes.py
```

### ⚠️ 改动深层叙事字段时的注意

`cross_constraints.adjust_storr_*_by_ocean()` 在极端 OCEAN 下会**整体替换**
wound / desire / need 文本，把人设型抹平。`generator.py` 因此**刻意不传 ocean**
给这些函数，以保持型的完整性。新增类似调整逻辑时请沿用此原则：
**型专属模板优先，OCEAN 只做措辞微调，不做整体替换**。

### 当前覆盖

10 个诊断 / **45 个人设型** / **720 个可区分深层身份**：

`depressive`(5) `anxiety`(5) `social_anxiety`(4) `ptsd`(5) `ocd`(4)
`adhd`(5) `schizophrenia`(4) `bipolar_manic`(4) `borderline_pd`(5) `anorexia`(4)

未覆盖的 27 个诊断自动回退旧采样逻辑（向后兼容，不报错）。

### 实测效果（同诊断同人口学，200 次生成去重率）

| 深层字段 | v1.1 | v1.2 | 提升 |
|---------|------|------|------|
| values_beliefs | 11 | 39 | 3.5× |
| social_relations | 17 | 61 | 3.6× |
| formative_wound | 5 | 20 | 4× |
| compensatory_desire | 1 | 10 | 10× |
| storr_need | 1 | 10 | 10× |

---

## 1. 概述

本包生成结构化的 **Persona 档案**，包含：人口学信息 + 精神科诊断 + 人设元类型(Archetype) + 大五人格(OCEAN) + 核心动机(Egri) + 功能障碍信念(CBT) + 压力应激模式 + Will Storr 叙事因果链(Wound→Lie→Desire→Need) + K.M. Weiland 角色弧线(正弧/负弧/平坦弧) + 症状触发器 + 生活事件时间线 + 外貌特征 + 隐藏经历 + 当前状态摘要，最终组装为一个适用于 LLM 评估的 **System Prompt**。

### 模块依赖关系

```
diagnosis_ontology.json  ←  generator.py  ──→  occupations.py
                                │                     │
                                ├──→ archetypes.py    │   ⭐ v1.2 心理内核
                                ├──→ personality.py   │
                                ├──→ triggers.py      │
                                └──→ events.py        │
                                      OCCUPATIONS(79) ←┘
```

---

## 2. 职业分类（occupations.py）

### 数据来源与取舍逻辑

**来源**：《中华人民共和国职业分类大典(2022年版)》——由人社部、市监局、统计局联合发布，2022年9月审定。

**粒度选择：79 中类（而非 1636 细类）**

| 粒度 | 层级 | 数量 | 说明 |
|------|------|------|------|
| 大类 | 1 位数字 | 8 | 过于宽泛，如"专业技术人员"无法区分医生和程序员 |
| **中类** | 2 位数字 | **79** | ✅ **本引擎采用的最佳粒度** |
| 小类 | 3 位数字 | 449 | 可在 occupation_detail 中补充 |
| 细类 | 6 位数字 | 1636 | 过于细碎，淹没 CLI 参数且无实际收益 |

**取舍理由**：
1. **Persona 不需要精确职业代码**。中类粒度（如"4-04 信息传输、软件和信息技术服务人员"）足够锚定人口学特征和职业压力评估。
2. **79 中类在 CLI 上可读且可筛选**（`--occupation-filter`）。1636 细类无法在命令行中有效呈现。
3. **通过 `occupation_detail` 字段可以补充精确岗位**。如果某个人物需要更具体的职业（如"软件架构师"），可在 system_prompt 中用自然语言描述，无须增加分类层级。

### 职业分布概率（可调）

默认按大类加权，以映射真实人口结构：

| 大类 | 默认权重 | 说明 |
|------|----------|------|
| 1 — 党政机关负责人 | 0.05 | 比例较小 |
| 2 — 专业技术人员 | **0.30** | 高权重，覆盖大量脑力劳动者 |
| 3 — 办事人员 | 0.10 | |
| 4 — 生活服务人员 | **0.25** | 高权重，覆盖大量服务行业 |
| 5 — 农林牧渔 | 0.08 | |
| 6 — 生产制造人员 | **0.18** | 高权重，覆盖大量体力劳动者 |
| 7 — 军人 | 0.02 | 小样本 |
| 8 — 不便分类 | 0.02 | 含自由职业 |

### 特殊标识

- `[S]` 数字职业：97 个中类标注为数字职业（如 6-25 计算机、通信和其他电子设备制造人员）
- `[L]` 绿色职业：134 个中类标注为绿色职业（如 2-03 农业技术人员）

### 精神障碍-职业压力关联

每个中类标注了 `stress_level`（high/medium/low），供诊断采样时做匹配：

- **高压职业**：医疗(2-05)、金融(2-06)、法律(2-07)、采矿(6-16)、建筑(6-29) → 与焦虑/抑郁/物质使用障碍强相关
- **中压职业**：教育(2-08)、行政(3-01)、制造(6-18) 等
- **低压职业**：农业(5-01/5-03)、水利环境(4-09)、农林牧渔辅助(5-05) 等

### 参数调整

通过 `PersonaGenerator` 构造函数调整：
- `occupation_major_weights`：自定义 8 个大类的采样权重
- `occupation_major_filter`：只使用特定大类
- `occupation_stress_filter`：只使用特定压力水平

---

## 3. 性格系统（personality.py）

### 理论基础：大五人格(OCEAN)

采用 **McCrae & Costa 的五因素模型(FFM)**，这是心理学界最成熟、跨文化验证最充分的人格模型（已验证于 50+ 国家和地区）。

### MECE 性保证

大五的 5 个维度是通过因子分析得到的**正交因子**，彼此独立且联合覆盖人格空间的所有方差。

| 维度 | 低分端 | 高分端 | 方差贡献 |
|------|--------|--------|----------|
| N 神经质 | 情绪稳定/放松 | 情绪敏感/紧张 | 最大（约 20%） |
| E 外向性 | 内向/安静 | 外向/活跃 | 第二大 |
| O 开放性 | 传统/务实 | 好奇/开放 | 第三 |
| A 宜人性 | 怀疑/竞争 | 友善/合作 | 第四 |
| C 尽责性 | 随意/散漫 | 自律/有序 | 第五 |

### MECE 性格标签库

每个维度分为**高低两极 → 10 个特质簇**，每个簇含 5-7 个标签，共 **50 个核心标签**。

**结构示例**：
```
N_high (情绪敏感): 敏感多虑, 紧张不安, 忧心忡忡, 情绪波动大, 缺乏安全感, 容易焦虑, 自我要求过高
N_low  (情绪稳定): 沉着冷静, 情绪稳定, 心理韧性好, 抗压能力强, 随遇而安, 心态平和, 不易焦虑
...
```

**MECE 保证**：
- 每个维度的低/高两极**互斥**——一个人不可能同时"敏感多虑"和"沉着冷静"
- 10 个特质簇 **联合覆盖** 所有人格空间——OCEAN 的正交因子结构确保任何人格特征均可映射到 5 维 × 2 极的坐标中
- 每个簇内的标签是同义/近义描述，可互换而不损失语义

### 诊断→OCEAN 范围映射（实证依据）

每个诊断预置了 OCEAN 的典型分数范围（1-10 分），依据以下实证研究：

| 研究 | 来源 | 关键发现 |
|------|------|----------|
| Kotov et al. (2010) | J Abnorm Psychol | 几乎所有精神障碍均与高 N 相关 |
| Malouff et al. (2005) | Psychol Bull | 抑郁 = 高 N + 低 E + 低 C |
| Samuel & Widiger (2008) | Psychol Bull | 人格障碍的 FFM 特征谱 |
| Ruiz et al. (2008) | Clin Psychol Rev | 物质使用障碍 = 低 A + 低 C |
| Samuel et al. (2009) | J Abnorm Psychol | OCD = 高 C + 高 N |

**示例映射**（完整列表见代码中的 `DIAGNOSIS_OCEAN_RANGES`）：
```python
"depressive":  {"N": (7,10), "E": (1,4), "O": (4,7), "A": (5,8), "C": (2,5)}
"schizophrenia":{"N": (7,10), "E": (1,4), "O": (7,10), "A": (3,6), "C": (2,5)}
"healthy":     {"N": (2,5),  "E": (3,7), "O": (4,7), "A": (5,8), "C": (4,7)}
```

### 认知风格与应对方式

- **15 种认知风格**：反刍思维、灾难化思维、非黑即白思维、正念觉察等
- **15 种应对方式**：问题解决导向、回避/否认、物质使用、自我责备等
- 每个诊断关联其最典型的认知-应对模式，采样时自动匹配

### Lajos Egri 三维增强

基于 **Lajos Egri 三维角色理论**（生理/社会/心理）和 **Beck 认知三角(CBT, 1979)**，为每个诊断预置以下心理动力学要素：

#### 核心欲望与核心恐惧 (Core Desire / Core Fear)

每个诊断有独特的欲望-恐惧结构，驱动角色的底层行为逻辑：

| 诊断 | 核心欲望 | 核心恐惧 |
|------|---------|---------|
| 抑郁障碍 | 被理解、被接纳、感受到存在的价值 | 被抛弃、成为负担、永远无法好转 |
| 精神分裂症 | 控制自己的思想和感知、被理解 | 再次失控、无法分辨真实与幻觉、被迫害 |
| 边缘型人格障碍 | 真正被爱、被完整接纳 | 被抛弃、被拒绝、被背叛 |

#### 功能障碍信念 (Dysfunctional Beliefs)

每个诊断预置 **Beck 认知三角** 三组负性自动化信念：

| 诊断 | 关于自己 | 关于世界 | 关于未来 |
|------|---------|---------|---------|
| 广泛性焦虑 | 我是脆弱的，无法应对困难 | 世界是危险的，灾难随时可能发生 | 未来充满不确定性，我必须做好准备 |
| 强迫症 | 我对自己的思想和行为负有全部责任 | 世界有严格的规则，不遵守就会有惩罚 | 如果我停止控制，一切都会变得混乱 |

#### 压力应激模式 (Stress Response Pattern)

基于 **Bracha (2004) 5F 应激扩展模型**：

| 应激模式 | 描述 |
|---------|------|
| 战斗 Fight | 通过攻击/对抗应对威胁 |
| 逃跑 Flight | 通过回避/逃离应对威胁 |
| 冻结 Freeze | 通过不动/顺从应对威胁 |
| 讨好 Fawn | 通过安抚/讨好应对威胁 |
| 自伤 Self-harm | 通过伤害自己缓解情绪 |

每个诊断预置 primary 和 secondary 两种应激模式，采样时自动从高概率模式中选取。

---

## 4. Will Storr 叙事因果链增强（personality.py）

### 理论基础

基于 **Will Storr《The Science of Storytelling》(2019)** 的四步角色动机模型：

```
Wound（形成性创伤）
  ↓  "因为发生了 X……"
Lie（错误信念）
  ↓  "所以我深信 Y……"
Desire（补偿性欲望）
  ↓  "于是我拼命追求 Z 来证明自己……"
Need（内在需要）
      "但我真正需要的是学会 W……"
```

### 与 Egri 的关系

| 维度 | Lajos Egri | Will Storr | 关系 |
|------|-----------|-----------|------|
| 欲望 | 抽象、普世的渴望（如"被爱"） | 具体的补偿性目标（如"必须成为 CEO 来证明自己"） | 互补：Egri 是静态维度，Storr 是动态叙事 |
| 恐惧 | ——— | Lie（错误信念）← 映射到 dysfunctional_beliefs | 嵌套整合 |
| 创伤 | 生理维度的特质 | Wound（形成性创伤）→ 直接指向信念的形成 | Storr 提供因果解释 |
| 需要 | 无 | Need（内在需要）→ 与 Lie 正相反的疗愈方向 | **全新字段** |

### 新增字段

| 字段 | 含义 | 在叙事链中的位置 |
|------|------|-----------------|
| `formative_wound` | 形成性创伤——导致错误信念的关键人生经历 | Wound |
| `compensatory_desire` | 补偿性欲望——为对抗谎言而追求的外在目标 | Storr Desire |
| `storr_need` | 内在需要——角色真正的疗愈方向，通常与 Lie 相反 | Need |

### 诊断映射示例

| 诊断 | 形成性创伤 | 错误信念 | 补偿性欲望 | 内在需要 |
|------|-----------|---------|-----------|---------|
| 重度抑郁 | 被主要照顾者长期忽视 | 我是无能的、不够好 | 拼命证明自己值得存在 | 即使不完美也值得被爱 |
| 强迫症 | 一次疏忽导致严重后果被惩罚 | 如果我放松警惕，灾难会发生 | 用仪式获得对不确定性的控制 | 接受生活本质上的不确定 |
| 边缘型人格障碍 | 依恋关系极不稳定 | 我必定会被抛弃 | 用激烈的关系测试对方的忠诚 | 学会独自一人也安全 |
| 社交焦虑 | 当众出丑被全班嘲笑 | 别人都在评判我 | 在人群中隐形 | 不需要被所有人喜欢 |

### 在 System Prompt 中的呈现

生成后的 System Prompt 包含「人物叙事链」章节，将以上四个要素串联为一条连贯的因果叙事：

```
## 人物叙事链（造成今日之他的因果路径）
- **形成性创伤**：童年时期长期被主要照顾者忽视，情感需求得不到回应
- **错误信念**：我是无能的、有缺陷的、不够好
- **补偿性欲望（想要）**：拼命寻找被认可的证明——出色完成任务、取悦他人
- **内在需要（真正需要）**：接纳自己是不完美的——但这不代表你不值得被爱
```

这让 LLM 在进行临床评估时能理解角色的「所以然」，而不仅仅是「是什么」。

---

## 5. K.M. Weiland 角色弧线（personality.py）

> 来源：*Creating Character Arcs* (K.M. Weiland, 2016)
> 定位：为每个角色分配一个**变化轨迹类型**，补完 Egri 静态维度 + Storr 因果链的最后一块拼图

### 三种弧线类型

| 弧线 | 英文 | 临床类比 | 阶段路径 |
|------|------|---------|---------|
| **正弧** | Positive Change Arc | 接受治疗、获得洞见、症状改善的康复轨迹 | 谎言→渴望→真相冲击→冲突→转变→新常态 |
| **负弧** | Negative Change Arc | 拒绝治疗、否认病情、症状恶化的衰退轨迹 | 潜力→首次拒绝→持续滑落→临界点→彻底堕落 |
| **平坦弧** | Flat Arc | 症状稳定/康复期，接纳自我、影响他人 | 已信真相→考验→坚持→影响他人→世界改变 |

### 诊断→弧线映射依据

弧线分配基于 Weiland 的原型原则和临床推理：

- **正弧（27/37 诊断）**：绝大多数精神障碍的**预期轨迹**——疾病本身意味着有可以改善和成长的空间。主要抑郁、焦虑障碍、强迫症、创伤相关障碍等都属于此。
- **负弧（4/37 诊断）**：疾病本身具有**自我强化、拒绝干预**的逻辑：双相躁狂（药物不依从→复发循环）、妄想障碍（信念固化）、反社会/自恋人格（缺少治疗动机）。
- **平坦弧（6/37 诊断）**：疾病改变的不是角色的"本质"，而是其**与世界的共存方式**：精神分裂症（长期功能维持）、孤独症谱系（神经多样性）、抽动障碍（接受自我）、健康人群（已有韧性基础）。

### 采样函数

```python
from core.personality import sample_arc_type, DIAGNOSIS_ARC_MAPPINGS, WEILAND_ARC_TYPES

# 采样弧线
arc_info = sample_arc_type("depressive")
print(arc_info["arc_type"])        # "positive"
print(arc_info["arc_name"])         # "正弧（Positive Change Arc）"
print(arc_info["trajectory"])       # "从否定自我价值到理解被爱的理由..."
```

### 在 System Prompt 中的呈现

生成的 Persona System Prompt 中会增加以下弧线章节：

```
## 角色弧线（K.M. Weiland — Creating Character Arcs）
- 弧线类型：正弧（Positive Change Arc）
- 轨迹描述：从仪式化控制到学会放手——最艰难但最深刻的正弧
- 角色的潜力方向：在叙事中沿着这条弧线前进...
```

---

## 6. 症状触发器与生理特征（triggers.py）

---

## 7. 生活事件（events.py）

### MECE 设计：2D 事件矩阵

采用 **6 个领域 × 4 个时间阶段 = 24 格** 的 2D 矩阵，每格包含多个事件模板。

**领域划分（MECE：互斥 + 全覆盖）**：

| 领域 | 覆盖范围 | 互斥保证 |
|------|----------|----------|
| 家庭 Family | 亲属关系、家庭结构、婚姻 | 只涉及血缘/姻缘关系 |
| 教育 Education | 正式学习、学术经历 | 不覆盖职业培训（归入职业） |
| 职业 Occupation | 工作、就业、事业 | 不覆盖学习（归入教育） |
| 健康 Health | 身心疾病、医疗、生理 | 不覆盖社会性健康（归入家庭/人际） |
| 经济 Finance | 收入、资产、消费 | 不覆盖工作收入以外的财务 |
| 人际 Interpersonal | 朋友、社交、社区 | 不覆盖家庭成员（归入家庭） |

**时间阶段**：
| 阶段 | 年龄范围 | 事件模板数 |
|------|----------|-----------|
| 童年 Childhood | 0-12 岁 | 32 |
| 青少年 Adolescence | 13-17 岁 | 30 |
| 成年 Adulthood | 18-40 岁 | 53 |
| 中老年 Mid/Older | 41 岁+ | 28 |
| **总计** | | **143** |

### 事件标注

每个事件包含三个关键属性：

1. **效价(Valence)**：positive（44 个）/ negative（67 个）/ neutral（32 个）
2. **诊断关联(Diagnosis Relation)**：trigger（触发因素）/ maintain（维持因素）
3. **领域+阶段(2D 坐标)**：确保覆盖全人生

### 诊断关联触发事件

示例：抑郁障碍的典型触发事件
```python
LifeEvent("family", "childhood", "父母离异", ..., diagnosis_relation={"depressive": "trigger"})
LifeEvent("occupation", "adulthood", "被裁员/失业", ..., diagnosis_relation={"depressive": "trigger"})
```

**采样逻辑**：
1. 优先从诊断关联事件中抽取 1-2 个（如果有诊断）
2. 按效价比例（默认 positive:negative:neutral = 3:4:3）从通用事件中分层采样
3. 按时间顺序排列，形成完整的人生时间线

---

## 8. 主生成器（generator.py）

### Persona 字段结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | str | P-000001 格式 |
| label | str | depressive_0001 格式 |
| age | int | 根据诊断发病年龄范围采样 |
| gender | str | 男/女 |
| occupation | str | 职业中类名 |
| occupation_code | str | 如 "2-02" |
| education | str | 小学~硕士及以上 |
| locale | str | 城市/农村/城镇 |
| marital_status | str | 已婚/未婚/离异/丧偶 |
| primary_diagnosis | str | 主诊断中文名 |
| comorbidities | list[str] | 共病列表 |
| ocean | dict | {"N":7, "E":1, ...} |
| ocean_description | str | 自然语言描述 |
| personality_tags | list[str] | 精选性格标签 |
| cognitive_styles | list[str] | 典型认知风格 |
| coping_styles | list[str] | 常用应对方式 |
| core_desire | str | 核心欲望（Lajos Egri） |
| core_fear | str | 核心恐惧（Lajos Egri） |
| dysfunctional_beliefs | dict | 认知三角：自己/世界/未来 |
| stress_pattern | dict | 主要+次要应激模式 |
| formative_wound | str | 形成性创伤（Storr Wound） |
| compensatory_desire | str | 补偿性欲望（Storr Desire） |
| storr_need | str | 内在需要（Storr Need） |
| arc_type | str | 角色弧线类型（Weiland）：positive/negative/flat |
| arc_description | str | 弧线名称+轨迹描述 |
| triggers | list[str] | 症状触发因素 |
| safety_behaviors | list[str] | 安全行为（维持症状的应对策略）|
| physical_appearance | list[str] | 外貌特征描述 |
| hidden_experiences | list[str] | 不会主动告诉别人的秘密 |
| life_events | list[LifeEvent] | 事件对象列表 |
| life_events_text | str | 格式化时间线文本 |
| current_status | str | 当前功能状态摘要 |
| system_prompt | str | 完整的 LLM System Prompt |

### 生成流水线

```
诊断采样 → 人口学 → 职业 → 共病 → OCEAN → 核心欲望/恐惧 → Storr叙事链 → 角色弧线
    → 功能障碍信念 → 应激模式 → 触发器 → 安全行为 → 外貌特征 → 隐藏经历 → 生活事件 → System Prompt
```

共 **16 步**，三步一体（Egri 静态维度 → Storr 因果链 → Weiland 弧线方向），每一步使用独立的随机种子的子采样器，保证不同维度间的去相关性。

---

## 9. 快速开始

### 安装

```bash
# 无需安装依赖，纯 Python 标准库
# 确保目录结构：
# AI-persona/
#   core/
#     __init__.py
#     occupations.py
#     personality.py
#     triggers.py
#     events.py
#     generator.py
#   diagnosis_ontology.json  (可选)
```

### 基础用法

```python
from core import generate_persona

# 随机生成一个 Persona（可能会是健康人群或患者）
p = generate_persona()
print(p.system_prompt)

# 生成指定诊断的 Persona
p = generate_persona(primary_diagnosis="重度抑郁障碍", rng_seed=42)
print(f"{p.label}: {p.age}岁 {p.gender}，{p.occupation}")
print(p.system_prompt)

# 指定性别和年龄
p = generate_persona("广泛性焦虑障碍", gender="男", age=35)
print(f"{p.age}岁 {p.gender}，核心恐惧：{p.core_fear}")

# 生成健康对照
p = generate_persona(primary_diagnosis="无精神障碍（健康）")
```

### 批量生成

```python
from core import batch_generate

# 生成 10 个 Persona（随机诊断分布）
personas = batch_generate(10, rng_seed=2024)

# 指定诊断种子池，循环使用
personas = batch_generate(20, seed_pool=[
    "重度抑郁障碍", "广泛性焦虑障碍", "精神分裂症",
    "双相I型障碍", "无精神障碍（健康）",
])
```

### 自定义配置

```python
from core import PersonaGenerator

gen = PersonaGenerator(
    # 调节 8 个大类权重
    occupation_major_weights={2: 0.35, 4: 0.25, 6: 0.20, 3: 0.10, 5: 0.05, 1: 0.03, 7: 0.01, 8: 0.01},
    # 调节事件数量
    event_count=8,
    # 调节事件效价比
    event_positive_ratio=0.25,
    event_negative_ratio=0.50,
    event_neutral_ratio=0.25,
    # 调节性格标签数量
    personality_tag_count=5,
    # 调节健康人群比例
    healthy_ratio=0.3,
    # 年龄范围
    age_range=(18, 80),
)

# 生成 5 个
personas = gen.batch(5)

# 逐个访问
for p in personas:
    with open(f"personas/{p.label}.json", "w", encoding="utf-8") as f:
        import json
        f.write(json.dumps({
            "id": p.id,
            "label": p.label,
            "age": p.age,
            "diagnosis": p.primary_diagnosis,
            "ocean": p.ocean,
            "events": [e.name_cn for e in p.life_events],
            "system_prompt": p.system_prompt,
        }, ensure_ascii=False, indent=2))
```

---

## 10. 参数可调性

所有关键参数均可在 `PersonaGenerator` 构造函数中自定义：

| 参数组 | 参数 | 默认值 | 说明 |
|--------|------|--------|------|
| **职业** | `occupation_major_weights` | 见代码 | 8 个大类的采样权重 |
| | `occupation_major_filter` | None | 只使用指定大类 |
| | `occupation_stress_filter` | None | 只使用指定压力水平 |
| **性格** | `personality_tag_count` | 4 | 每个 Persona 的性格标签数 |
| | `cognitive_count` | 2 | 认知风格数 |
| | `coping_count` | 2 | 应对方式数 |
| **触发器** | `trigger_count` | 3 | 症状触发因素数 |
| | `safety_behavior_count` | 2 | 安全行为数 |
| **隐藏经历** | `hidden_experience_count` | 2 | 隐藏经历数 |
| **事件** | `event_count` | 6 | 每个 Persona 的事件数 |
| | `event_positive_ratio` | 0.3 | 积极事件比例 |
| | `event_negative_ratio` | 0.4 | 消极事件比例 |
| | `event_neutral_ratio` | 0.3 | 中性事件比例 |
| **人口学** | `age_range` | (18, 75) | 年龄范围 |
| | `healthy_ratio` | 0.2 | 健康人群占比 |
| **全局** | `rng_seed` | None | 随机种子（可复现） |

---

## 11. 输出示例

### 生成一个重度抑郁障碍 Persona 的 System Prompt

```
# Persona 档案

## 基本信息
- 年龄：66岁
- 性别：女性
- 职业：金融服务人员
- 教育程度：高中/中专
- 居住地：城市
- 婚姻状况：丧偶

## 精神科诊断
- 主诊断：重度抑郁障碍
- 共病诊断：边缘型人格障碍、强迫症

## 性格特征
- 大五人格(OCEAN)：情绪敏感/紧张(N=10)；偏内向(E=4)；偏传统(O=4)；友善/合作(A=8)；偏自律(C=5)
- 性格标签：不拘小节，缺乏安全感，善于交际，条理清晰
- 典型认知风格：灾难化思维、选择性关注负面
- 常用应对方式：自我责备、退缩/孤立

## 核心动机
- 最深层的渴望：被理解、被接纳、感受到存在的价值
- 最深层的恐惧：被抛弃、成为他人的负担、永远无法好转

## 功能障碍信念
- 对关于自己的信念：我是无能的、有缺陷的、不够好
- 对关于世界的信念：世界是冷漠的，别人不会真正关心我
- 对关于未来的信念：未来没有希望，情况永远不会好转

## 压力应激模式
- 主要应激反应：冻结Freeze、退缩Withdraw
- 次要应激反应：讨好Fawn

## 症状触发因素
- 长期没有获得正面反馈
- 阴雨天或秋冬季节交替
- 结束一段亲密关系后

## 安全行为（应对症状的策略）
- 拒绝回复消息、切断外界联系
- 反复确认自己是不是被讨厌了

## 外貌特征
矮小，身材丰满，温柔面容，烫卷发，眼神锐利，面带风霜，不安地变换姿势。

## 隐藏经历（他/她不会主动告诉别人的事）
- 在社交媒体上装出正常的样子，实际上非常痛苦
- 暗中存了一笔应急金，谁也不知道

## 人生经历
以下是从出生到现在的关键事件：

【童年】
  ✓ 有零花钱/压岁钱

【青少年】
  ✗ 家庭重组/继父母进入

【成年】
  ✗ 被信任的人利用
  ✗ 工作与家庭平衡困难

【中老年】
  ✗ 社会活动参与少/孤独
  ● 与成年子女同住

## 当前状态
重度抑郁障碍缓解期，但仍有一定残余症状，
近期经历了「被信任的人利用」事件，
当前社会功能轻度受损，仍可维持基本日常活动

## 评估指示
请以精神科临床评估的方式，对上述人物进行访谈和量表施测。
评估目标：验证诊断、评估当前严重程度、了解功能损害。
```

---

## License

Psych-Bench 项目内部使用。
