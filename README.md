<div align="center">

# AI-Persona

**Canonical Human Ontology + ontology-native Persona Engine**

<p>
  <img alt="Human Ontology" src="https://img.shields.io/badge/ontology-Human%20Ontology%20v2%20RC-6C63FF">
  <img alt="Engine" src="https://img.shields.io/badge/engine-Persona%20Generator-2F80ED">
  <img alt="Version" src="https://img.shields.io/badge/version-v2%20refactor-27AE60">
  <img alt="Research use" src="https://img.shields.io/badge/use-research%20%2F%20simulation-F2994A">
</p>

**唯一语义归属 · 局部 MECE · 类型化关系 · 可追溯生成**

</div>

AI-Persona 从统一的 Human Ontology 出发，把“人是什么”与“如何生成一个具体人物”分开。Human Ontology 定义唯一 canonical semantic homes；Persona Engine 负责实例化、生成与迁移。精神疾病知识库继续保留，但只是 Mental / Neurodevelopmental Health 下的可选 domain module，不再作为人的根结构。

> [!IMPORTANT]
> 这是研究与模拟基础设施，不是临床诊断工具，也不应把生成 Persona 直接视为真实患者群体的统计代表。

---

## Canonical Human Ontology

AI-Persona hosts the shared Human Ontology for AI-Persona, P003, AI-Ques and future person-centered systems.

**Current status**
- `human_ontology.v1.json` — compatibility canonical for legacy consumers.
- `human_ontology.v2.json` — **v2.0.0-rc2 release candidate** and semantic authority for new integrations.
- v2 is promoted to canonical only after the release gate is green and the PR is merged.

**System-wide rule**

> **One canonical semantic home + local MECE + typed relations.**

v2 does **not** force all human facts into one globally MECE tree. Domains are semantic namespaces; concrete concepts are typed as entity, quality/disposition, role, relation, process/event or state.

Key files:
- `ontology/human_ontology.v2.json` — v2 semantic namespaces and relation families
- `ontology/CANONICAL_FIELD_REGISTRY.json` — 31 reviewed first-class runtime/interoperability concepts
- `ontology/CANONICAL_CONCEPT_CATALOG.json` — exhaustive 205-concept catalog (31 reviewed + 174 provisional migrated leaves)
- `ontology/V1_TO_V2_MIGRATION.json` — v1 axis migration
- `ontology/V1_FIELD_MIGRATION.json` — complete migration of all 186 v1 subaxes/personality layers
- `ontology/persona_kernel.schema.json` — exchange schema
- `ontology/CONSUMER_CONTRACT.md` — AI-Persona / P003 / AI-Ques contract
- `ontology/HUMAN_ONTOLOGY_REVIEW.md` — ontology governance
- `ontology/RELEASE_GATE.md` — canonical-promotion gate
- `core/persona_kernel.py` — ontology-native runtime representation
- `core/kernel_generator.py` — safe v2 generation layer
- `core/legacy_adapter.py` — v1 Persona → v2 PersonaKernel bridge

Important consequences:
- birthplace / residence / migration are place relations; they do not imply culture;
- culture / language / religion are participation/exposure relations; citizenship is legal/institutional;
- identity/self-concept is distinct from roles, culture participation and legal status;
- diagnosis is an optional health-domain concept, never the root identity of a person;
- trait ≠ motive/value ≠ belief ≠ coping ≠ relationship observation ≠ narrative identity ≠ current state;
- relationship-specific facts live on relationships; person-level relational tendencies live under personality;
- events are time-indexed processes; roles are not events; role transitions are events;
- current resources/opportunities may be derived projections from work, relationships, institutions and context;
- generated/inferred/observed/measured/input-constraint values are epistemically distinct and carry provenance;
- every domain value must have matching field metadata; orphan/missing metadata is rejected;
- relations use typed `EntityRef` endpoints and predicate-specific target constraints;
- reviewed first-class concepts declare storage mode and value contracts.

The existing 6-domain × 4-stage event matrix, Archetype Grid and legacy six-field generation modules remain useful compatibility/content assets, but they are **not** the canonical ontology.

## Scientific validation

Human Ontology distinguishes engineering conformance, cross-model robustness and downstream validation.

- **Tier A — achieved at machine level**: 184/184 declared machine competency questions pass; the RDF/OWL/SHACL projection is drift-checked.
- **Tier B1 — Multi-AI robustness, ready to run**: the same 24 adversarial cases / 56 atomic facts can be evaluated across GPT, Claude, Gemini, Qwen, DeepSeek or other configured providers. The analyzer reports agreement, adversarial gold accuracy, forbidden-inference false positives and **agreement-but-wrong**.
- **Tier B2 — optional stronger corroboration**: human/domain-expert annotation remains available but is no longer the current prerequisite.
- **Tier C — not yet achieved**: requires downstream P003 / AI-Ques evidence plus remaining semantic-web/external validation.

The benchmark does **not** treat AI consensus as truth. Tier B1 requires both high cross-model agreement and high accuracy against hidden adversarial gold, with zero critical agreement-but-wrong cases.

```bash
python scripts/evaluate_human_ontology.py
python scripts/build_multi_ai_benchmark.py --check
python scripts/test_multi_ai_benchmark.py

# Real multi-provider run: configure API keys/model IDs first.
python scripts/run_multi_ai_benchmark.py \
  --config evaluation/multi_ai_benchmark/models.local.json
```

See `evaluation/multi_ai_benchmark/README.md`. A green machine gate or a future green Multi-AI benchmark must not be described as human/expert validation or universal scientific validity. The reviewed runtime contract is green, while **56 provisional relation leaves** remain intentionally non-API-ready pending predicate review.

## 项目结构

```
AI-persona/
├── README.md                          # ← 本文件
│
├── diagnosis_ontology.json            # Phase 1: 诊断本体知识库 (156KB)
│                                      # ICD-11 Chapter 06 + DSM-5-TR
│                                      # 278 诊断 → 37 个生成范围
│
├── core/                              # Phase 2: 核心引擎 (9 个模块)
│   ├── __init__.py                    # 完整公开 API
│   ├── generator.py                   # PersonaGenerator 主类
│   ├── archetypes.py                  # ⭐ 人设元类型网格 (v1.2, 45型/10诊断)
│   ├── personality.py                 # OCEAN/legacy generation utilities
│   ├── events.py                      # 生活事件矩阵 (6域×4阶段,143模板)
│   ├── occupations.py                 # 职业体系 (79中类×8大类)
│   ├── triggers.py                    # 触发器系统 (ACEs/创伤/应激)
│   ├── cross_constraints.py           # 交叉约束校验 (诊断↔OCEAN↔人口学)
│   ├── stratification.py              # ⭐ 分层采样 (2025 小普查, 流行病学性别比)
│   └── README.md                      # 核心引擎完整文档
│
├── scripts/                           # 实用工具脚本
│   ├── generate_dataset.py            # 批量数据集生成
│   ├── analyze_dataset.py             # 数据集分析工具
│   └── _scratch/                      # 一次性构建脚本（归档备查）
│
├── data/                              # 参考数据
│   ├── demographic_baseline.json      # 2025 小普查人口基准 (性别/年龄/教育等)
│   ├── personality/                   # BFI标定 (bfi44/sd27/behavior)
│   └── personas.json                  # 临床角色配置 (心理评估用)
│
├── dataset/                           # Phase 3: 生成数据集
│   ├── persona_dataset_v1.json        # 740条人设 (3.9MB)
│   └── persona_dataset_v1_summary.csv # 统计摘要 (220KB)
│
├── ontology/                          # Human Ontology v1 compatibility + v2 rc2 contracts
│   ├── human_ontology.v2.json
│   ├── CANONICAL_FIELD_REGISTRY.json
│   ├── V1_FIELD_MIGRATION.json
│   ├── persona_kernel.schema.json
│   └── RELEASE_GATE.md
│
├── ontology_build/                    # legacy psychiatric ontology build toolchain
│   ├── build_ontology_part1.py        # 三部分构建脚本 (ICD-11 Chapter 06)
│   ├── build_ontology_part2.py        # DSM-5-TR
│   ├── build_ontology_part3.py        # 共病关联
│   ├── merge_ontology.py              # 合并工具
│   └── _diag_names.json              # 诊断中文名映射
│
└── skill/                             # WorkBuddy 技能
    └── SKILL.md                      # 一键安装技能
```

---

## 架构要点（v1.1 更新）

### ⭐ stratification.py — 人口学分层采样（本次架构改进核心）

| 旧版（v1.0） | 新版（v1.1） |
|-------------|-------------|
| 性别 50/50 抛硬币 | 按流行病学性别比加权（厌食症→90%女, ASD→80%男） |
| 年龄：诊断发病范围+均匀 | 普查校准 6 年龄带 + 带内权重 |
| 教育：硬编码 0.1/0.3/0.4 魔法数 | 7 级普查分布 + 诊断-教育联动调节 |

所有人口学采样委托到 `stratification.py`，`generator.py` 不再维护自己的采样逻辑。

---

## Phase 路线图

| 阶段 | 状态 | 内容 |
|------|------|------|
| **Phase 1** | ✅ 完成 | 诊断本体知识库 (ICD-11 + DSM-5-TR, 278诊断, 156KB) |
| **Phase 2** | ✅ 完成 | legacy v1.x 核心引擎（用于兼容与复现） |
| **Phase 3** | ✅ 完成 | v1 数据集 (740条人设, 37诊断×20种子) |
| **Phase 3.5** | ✅ 完成 | **Archetype Grid v1.2** (10诊断/45型/720深层身份，深层字段多样性 3.5~10×) |
| **Phase 3.6** | ⏸️ legacy | 网格扩展不再是 v2 canonical ontology 的前置条件 |
| **Phase 3.7** | ✅ rc2 | Human Ontology v2 + PersonaKernel + 186-field migration + 205-concept catalog + typed EntityRef graph + semantic firewall |
| **Phase 4** | 🚧 验证框架已就绪 | Multi-AI semantic robustness（Tier B1）+ 可选专家复核（Tier B2） |
| **Phase 5** | 📋 规划 | LLM 心理评估应用集成 |

---

## 核心能力

### 1️⃣ Legacy Archetype Grid → Narrative Identity asset

> ⚠️ **v1.1 及以前的「三层空间」模型已作废**。

```
【旧模型（虚假，已作废）】
  全组合上限 (10²⁹) → 有效核心身份 (10⁷~10⁸) → 同人设变体 (~75)
  问题：10²⁹ 是软概率分布的名义组合数，不可枚举、不可覆盖验证；
        而真正决定人设内核的字段模板池却极小，内核严重同质。

【新模型（v1.2 Archetype Grid）】
  诊断 (37)
    └─ 人设元类型 archetype (每诊断 4~5 个)      ← 硬网格，可枚举
         └─ 型内变体 (wounds × desires × needs)  ← 深层叙事内核
              └─ 表层变体 (OCEAN/标签/事件)      ← 不改心理内核
```

**实测对比（同诊断同人口学，200 次生成的去重率）**：

| 深层字段 | v1.1（旧） | v1.2（Archetype Grid） | 提升 |
|---------|-----------|----------------------|------|
| values_beliefs | 11 | **39** | 3.5× |
| social_relations | 17 | **61** | 3.6× |
| formative_wound | 5 | **20** | 4× |
| compensatory_desire | 1 | **10** | 10× |
| storr_need | 1 | **10** | 10× |

**当前网格规模**：10 诊断 / **45 个人设型** / **720 个可区分深层身份**。

```bash
python core/archetypes.py   # 查看完整空间报告
```

**设计原则**：
1. **叙事模板不等于心理真值** — Archetype Grid 作为 `narrative_identity` 的 legacy generative asset；旧版 diagnosis-keyed 采样不应解释为诊断决定人格
2. **型是硬网格** — 有限、显式声明，不是概率软约束，使「有多少种不同的人」成为可回答的问题
3. **OCEAN 只微调不覆盖** — 旧 `adjust_*_by_ocean` 在极端 OCEAN 下会整体替换文本、抹平型，v1.2 已规避
4. **向后兼容** — 未定义网格的诊断自动回退旧逻辑，不破坏现有行为

### 2️⃣ Legacy OCEAN 诊断条件化先验

旧生成器保留 37 个诊断 × 5 维 OCEAN 范围用于兼容/研究复现。Human Ontology v2 中，OCEAN 只是 `personality_psychology.temperament_traits` 下的一个特质模型；默认 `KernelGenerator` 不允许诊断决定非健康人格。

### 3️⃣ Legacy 六维生成模块（非 canonical ontology）

| 维度 | 描述 |
|------|------|
| 社会关系 | 朋友/家庭/社交模式 |
| 价值观 | 核心信念、禁忌、欲望 |
| 沟通风格 | 直率/委婉、正式/非正式 |
| 生活习惯 | 作息、饮食、爱好、成瘾 |
| 能力技能 | 职业适配、认知优势 |
| Erikson 阶段 | 心理社会发展阶段 |

### 4️⃣ 事件矩阵

6 领域 × 4 人生阶段 = 24 格，共 143 个事件模板，支持诊断关联触发与 LCU 应激评分。

### 5️⃣ Persona 完整字段（43 个，与 `Persona` dataclass 一致）

- 基本档案（9）：id / label / age / gender / occupation / occupation_code / education / locale / marital_status
- 诊断（3）：primary_diagnosis / primary_diagnosis_en / comorbidities
- **人设元类型（3，v1.2）**：archetype_key / archetype_name / archetype_one_liner
- 心理剖面（5）：ocean / ocean_description / personality_tags / cognitive_styles / coping_styles
- legacy 六维生成字段（6）：social_relations / values_beliefs / communication_style / lifestyle_habits / skills_abilities / erikson_stage
- 动机与信念（4）：core_desire / core_fear / dysfunctional_beliefs / stress_pattern
- Storr 叙事链（3）：formative_wound / compensatory_desire / storr_need
- Weiland 弧线（2）：arc_type / arc_description
- 症状与表征（4）：triggers / safety_behaviors / physical_appearance / hidden_experiences
- 事件与状态（3）：life_events / life_events_text / current_status
- 输出（1）：system_prompt

> ⚠️ 旧文档曾列出 `scene` / `self_description` / `life_story` / `persona_id` / `diagnosis_key` 等字段——**代码中并不存在**，v1.2 已按 dataclass 实况修正。

---

## 快速开始

```bash
# 全量生成（37 诊断 × 20 seed = 740 条）
python scripts/generate_dataset.py

# 指定诊断与数量（v1.2 起支持 CLI 参数）
python scripts/generate_dataset.py \
  --diagnoses depressive,adhd,anorexia \
  --samples-per-diagnosis 20 \
  --output dataset/my_personas.json
```

> 可用参数：`--diagnoses`（逗号分隔诊断键）、`--samples-per-diagnosis` / `--count`、
> `--output`（JSON 路径）、`--csv-output`（CSV 路径）。不带参数即全量。
> 脚本固定同时输出 JSON 与 CSV 摘要两种格式。

### 生成单条 Persona

```python
from core import generate_persona

# 诊断用中文名；rng_seed 保证可复现
p = generate_persona(primary_diagnosis="精神分裂症", rng_seed=42)
print(p.system_prompt)          # 完整的 LLM System Prompt
print(p.archetype_name)         # 人设元类型（v1.2）
print(p.current_status)         # 当前状态摘要
```

### 生成批量 Persona

```python
from core import batch_generate

personas = batch_generate(20, rng_seed=2024, seed_pool=[
    "重度抑郁障碍", "广泛性焦虑障碍", "精神分裂症",
    "双相I型障碍", "无精神障碍（健康）",
])
```

### 自定义配置

```python
from core import PersonaGenerator

gen = PersonaGenerator(
    event_count=8,
    personality_tag_count=5,
    healthy_ratio=0.3,
    age_range=(18, 80),
    rng_seed=42,
)
personas = gen.batch(5)
```

> ⚠️ 旧示例中的 `PersonaGenerator(ontology_path=...)`、`gen.generate(diagnosis=..., seed=...)`
> 与 `persona.summary` 均**不存在**（构造函数无 `ontology_path`；`generate()` 用
> `primary_diagnosis`；seed 在构造函数；无 `summary` 字段，应为 `current_status`）。v1.2 已修正。

---

## 设计哲学

1. **一个 canonical semantic home** — 同一概念只定义一次；其他位置通过 typed reference / projection 使用。
2. **Local MECE** — 只有回答同一个问题、同一抽象层级的 sibling classification 才要求互斥/穷尽；连续、多值、关系、时间性事实不强行 MECE。
3. **类型分离** — entity / quality-disposition / role / relation / process-event / state 不混为一棵树。
4. **证据来源分离** — observed / measured / inferred / generated / input_constraint 不互相冒充，推断与生成值带 provenance。
5. **Health is a domain, not identity** — 精神疾病体系完整保留，但不会定义人的人格、价值、能力或人生轨迹。
6. **Legacy 可复现** — v1.x PersonaGenerator、Archetype Grid、诊断条件化 OCEAN 与旧数据集继续可运行，但不再主导 canonical ontology。

---

## 版本

`v2.0.0-rc2` — Human Ontology v2 release candidate：18 个 semantic namespaces、205-concept catalog（31 reviewed + 174 provisional migrated）、typed EntityRef graph、PersonaKernel metadata completeness、186 个 v1 字段级迁移、psychiatric health-only semantic firewall 与自动 release gate。

`v1.2` — 2026-09-09 **Archetype Grid**：新增 `core/archetypes.py`，用「人设元类型硬网格」替代作废的三层空间模型，深层字段多样性提升 3.5~10×，修正 README 中 10²⁹ 的错误表述

`v1.1` — 2026-09-09 架构改进（stratification.py 激活、文件目录清理）
