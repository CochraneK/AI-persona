# AI-persona — 结构化 Persona 生成引擎

为精神病学 AI 评估生成全量模拟人物（健康对照 / 各类精神障碍患者），含人口学、职业、OCEAN 性格、生活事件时间线、System Prompt。

## 目录结构

```
AI-persona/
├── core/                     # ⚡ 核心引擎（10 个模块）
│   ├── __init__.py           #   导入封装，from core import generate_persona
│   ├── human_ontology.py     #   ⭐ canonical Human Ontology 加载器（v1.3）
│   ├── archetypes.py         #   ⭐ 人设元类型网格（v1.2，45 型 / 10 诊断）
│   ├── generator.py          #   PersonaGenerator 主类 + Persona dataclass
│   ├── personality.py        #   OCEAN 大五人格 + MECE 六维标签库（v2）
│   ├── events.py             #   生活事件矩阵（6域×4阶段，143模板）
│   ├── occupations.py        #   职业分类（79中类×8大类）
│   ├── triggers.py           #   触发器系统（症状/安全行为/生理/隐藏经历）
│   ├── stratification.py     #   分层抽样配置（2025 普查校准）
│   ├── cross_constraints.py  #   交叉约束校验
│   └── README.md             #   核心引擎文档
├── data/                     # 参考数据
│   ├── demographic_baseline.json  # 2025 小普查基准
│   ├── personas.json              # 临床角色配置
│   └── personality/               # BFI 标定
├── scripts/                  # 工具脚本
│   ├── generate_dataset.py   # 批量生成数据集
│   └── analyze_dataset.py    # 数据集分析
├── ontology_build/           # 诊断本体构建工具链
├── reports/                  # 报告生成
├── dataset/                  # 生成的数据集
├── diagnosis_ontology.json   # 诊断本体（156KB，278 诊断）
├── ontology/                 # ⭐ Canonical Human Ontology v1（v1.3 起接入生成器）
│   ├── human_ontology.v1.json  # 唯一权威源（19轴/10域/9阶段/13压力形态 + legacy_mappings）
│   └── README.md               # 本体设计文档
└── README.md                 # 项目文档
```

## 关键约定

- **导入路径**：`from core import generate_persona, PersonaGenerator`（不是 `from persona_generator`）
- **纯 Python 标准库**：零外部依赖，无需 pip install
- **诊断本体**：根目录 `diagnosis_ontology.json`，fallback 到 generator 内置硬编码
- **2025 普查基线**：`data/demographic_baseline.json` 是年龄/教育/城乡采样权重基准
- **Canonical Human Ontology（v1.3 起）**：`ontology/human_ontology.v1.json` 是唯一权威源，
  canonical id（life domains / developmental stages / event pressure shapes / locale 值）
  **一律经 `core/human_ontology.py` 的函数引用**（`canonical_*()` / `map_legacy_*()`），
  禁止在业务模块本地重定义或硬编码。legacy 6×4 事件矩阵与地区标签（城市/农村/城镇）
  经 `legacy_mappings` 映射；`LifeEvent.canonical_domain/canonical_stages` 与
  `Persona.locale_canonical` 为只读派生字段，不改变 RNG 流与既有输出。
- **人设元类型（v1.2 起）**：`core/archetypes.py` 定义每诊断的有限人设型网格，**型决定心理内核**。
  已覆盖 10 个诊断（depressive/anxiety/social_anxiety/ptsd/ocd/adhd/schizophrenia/
  bipolar_manic/borderline_pd/anorexia），其余诊断自动回退旧逻辑。
  ⚠️ 修改深层叙事字段时**优先用 archetype 专属池**，不要把 `ocean` 传给
  `adjust_storr_*_by_ocean`——那些函数在极端 OCEAN 下会整体替换文本、抹平人设型。

## 快速使用

```python
from core import generate_persona, batch_generate

# 单个 Persona
p = generate_persona(primary_diagnosis="重度抑郁障碍", rng_seed=42)
print(p.system_prompt)

# 批量生成
personas = batch_generate(20, seed_pool=[
    "重度抑郁障碍", "广泛性焦虑障碍", "精神分裂症",
])
```

## 快速命令

```bash
# 批量生成数据集（100 条）
python scripts/generate_dataset.py --count 100

# 分析已有数据集
python scripts/analyze_dataset.py
```

## 深入文档

- 核心引擎文档：`core/README.md`（模块 API、参数说明、理论依据）
- 项目总览：`README.md`
- 数据基准：`data/demographic_baseline.json`
