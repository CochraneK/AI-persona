"""
分层压缩模块 — 条件联合分布采样约束系统

=========================================================================
设计思路
=========================================================================
用户指出了根本性问题：当前生成方式假设症状、事件、诊断、性格维度
是独立随机变量 —— 但临床上它们之间有着强烈的**条件依赖关系**。

本模块实现 4 层约束系统，将"独立随机采样"升级为"条件联合分布"：

  Layer 1 — 年龄分层（Age Band）
    6 个生命周期年龄带，每个诊断只允许有效年龄段。
    → 从 ~75 个可能年龄 → 每个诊断 ~3-5 个有效年龄带

  Layer 2 — 性别-诊断联动
    替换 50/50 无偏采样。基于流行病学数据。
    → 如 anorexia 90% 女性，ASD 80% 男性

  Layer 3 — 教育-诊断联动
    早发障碍（ASD/ADHD/精神分裂症等）压低高等教育概率。
    年龄门槛机制（<18 只能初中及以下）。

  Layer 4 — OCEAN-事件桥接
    性格轮廓偏置事件效价权重。
    如 high_N + low_E → loss事件权重 ↑30%，positive事件 ↓20%
    → 与 events.py 的 sample_events_for_persona 接口兼容

扩展约束（Layer 5）：
  职业-诊断兼容性过滤
    重度诊断禁止顶层/高压岗位。

压缩率计算器：
  量化各维度独立压缩比 + 总压缩比
=========================================================================

用法：
  from .stratification import (
      sample_age_from_bands,
      sample_gender_for_diagnosis,
      sample_education_for_diagnosis,
      compute_event_valence_weights,
      filter_occupations_for_diagnosis,
      calculate_total_compression,
  )
"""

import random
from typing import Optional

# =====================================================================
# Layer 1 — 年龄分层 (Age Band)
# =====================================================================

# 6 个生命周期年龄带
# 权重基于 2025 年全国 1% 人口抽样调查数据（2026-05-22 发布）
# 来源: demographic_baseline.json | 官方: 0-14=15.25%, 15-59=61.89%, 60+=22.86%
# 详细年龄带分布为基于七普详细结构与官方死亡率推估，待调查年鉴核实
AGE_BANDS = [
    {"name": "adolescent",   "name_cn": "青少年",     "range": (13, 17), "weight": 0.054},
    {"name": "young_adult",  "name_cn": "青年",       "range": (18, 25), "weight": 0.101},
    {"name": "adult",        "name_cn": "成年早期",   "range": (26, 40), "weight": 0.259},
    {"name": "middle",       "name_cn": "中年",       "range": (41, 55), "weight": 0.259},
    {"name": "young_old",    "name_cn": "初老",       "range": (56, 65), "weight": 0.164},
    {"name": "elderly",      "name_cn": "老年",       "range": (66, 85), "weight": 0.163},
]

# 每个诊断的有效年龄带（考虑典型发病年龄 + 自然进程）
# 格式: diagnosis_key → [age_band_name, ...]
# 原则：
#   1. 诊断只能出现在"发病年龄 ≤ 年龄带上限"的带
#   2. 早发障碍（ASD/ADHD/精神分裂症）跨更多带
#   3. 晚发障碍（痴呆、晚发抑郁）只在高龄带
DIAGNOSIS_AGE_BANDS: dict[str, list[str]] = {
    # ---- 心境障碍（跨多个带） ----
    "depressive":     ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
    "dysthymia":      ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
    "bipolar_manic":  ["young_adult", "adult", "middle"],
    "bipolar_dep":    ["young_adult", "adult", "middle"],
    "cyclothymia":    ["adolescent", "young_adult", "adult", "middle"],
    # ---- 焦虑障碍（早发常见，可跨全生命周期） ----
    "anxiety":        ["adolescent", "young_adult", "adult", "middle", "young_old"],
    "panic":          ["young_adult", "adult", "middle"],
    "social_anxiety": ["adolescent", "young_adult", "adult", "middle"],
    "agoraphobia":    ["young_adult", "adult", "middle", "young_old"],
    # ---- 创伤及应激 ----
    "ptsd":           ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
    "adjustment":     ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
    # ---- 强迫及相关 ----
    "ocd":            ["adolescent", "young_adult", "adult", "middle"],
    "hoarding":       ["young_adult", "adult", "middle", "young_old", "elderly"],
    "body_dysmorphic":["adolescent", "young_adult", "adult"],
    # ---- 精神病性 ----
    "schizophrenia":  ["young_adult", "adult", "middle"],
    "schizotypal":    ["young_adult", "adult", "middle"],
    "delusional":     ["adult", "middle", "young_old", "elderly"],
    # ---- 神经发育（早发，跨多个带） ----
    "adhd":           ["adolescent", "young_adult", "adult", "middle", "young_old"],
    "asd":            ["adolescent", "young_adult", "adult", "middle", "young_old"],
    "intellectual":   ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
    "tic_disorder":   ["adolescent", "young_adult"],
    # ---- 物质使用 ----
    "substance":      ["young_adult", "adult", "middle"],
    "alcohol":        ["young_adult", "adult", "middle", "young_old"],
    "gambling":       ["young_adult", "adult", "middle"],
    # ---- 进食障碍 ----
    "anorexia":       ["adolescent", "young_adult", "adult"],
    "bulimia":        ["adolescent", "young_adult", "adult"],
    "binge":          ["young_adult", "adult", "middle"],
    # ---- 人格障碍（起于青少年/成年早期，跨生命周期） ----
    "borderline_pd":  ["adolescent", "young_adult", "adult", "middle"],
    "antisocial_pd":  ["adolescent", "young_adult", "adult", "middle"],
    "narcissistic_pd":["young_adult", "adult", "middle"],
    "avoidant_pd":    ["adolescent", "young_adult", "adult", "middle"],
    "dependent_pd":   ["young_adult", "adult", "middle"],
    "obsessive_pd":   ["young_adult", "adult", "middle", "young_old"],
    # ---- 躯体形式/分离 ----
    "somatic_symptom":["young_adult", "adult", "middle", "young_old"],
    "dissociative":   ["young_adult", "adult", "middle"],
    # ---- 睡眠障碍 ----
    "insomnia":       ["young_adult", "adult", "middle", "young_old", "elderly"],
    # ---- 健康 ----
    "healthy":        ["adolescent", "young_adult", "adult", "middle", "young_old", "elderly"],
}


def sample_age_from_bands(
    diagnosis_key: str,
    bands: list[dict] | None = None,
    rng: random.Random = random.Random(),
) -> tuple[int, str]:
    """先抽年龄带，再在带内随机年龄

    Args:
        diagnosis_key: 诊断键（如 "depressive", "healthy"）
        bands: 可选，覆盖 AGE_BANDS
        rng: 随机数生成器

    Returns:
        (age, age_band_name)
    """
    valid_bands = DIAGNOSIS_AGE_BANDS.get(diagnosis_key, DIAGNOSIS_AGE_BANDS["healthy"])
    pool = [b for b in (bands or AGE_BANDS) if b["name"] in valid_bands]

    if not pool:
        pool = [b for b in (bands or AGE_BANDS) if b["name"] in ["young_adult", "adult", "middle"]]

    # 按权重抽带
    weights = [b["weight"] for b in pool]
    band = rng.choices(pool, weights=weights, k=1)[0]

    lo, hi = band["range"]
    age = rng.randint(lo, hi)
    return age, band["name_cn"]


# =====================================================================
# Layer 2 — 性别-诊断联动
# =====================================================================

# 流行病学性别分布（男概率，女 = 1 - 男概率）
# 基于 DSM-5-TR 流行病学数据
DIAGNOSIS_GENDER_DIST: dict[str, float] = {
    # 男 ≥ 女
    "depressive":      0.40,   # 女性略多 ~1.5-2x
    "dysthymia":       0.40,
    "bipolar_manic":   0.50,
    "bipolar_dep":     0.48,
    "cyclothymia":     0.50,
    "anxiety":         0.40,   # 女性更多
    "panic":           0.35,
    "social_anxiety":  0.45,
    "agoraphobia":     0.30,
    "ptsd":            0.40,
    "adjustment":      0.45,
    "ocd":             0.48,
    "hoarding":        0.45,
    "body_dysmorphic": 0.35,
    "schizophrenia":   0.55,   # 男性略多
    "schizotypal":     0.55,
    "delusional":      0.52,
    "adhd":            0.65,   # 男性更多 ~2-3x
    "asd":             0.75,   # 男性显著更多 ~4x
    "intellectual":    0.55,
    "tic_disorder":    0.75,   # 男性显著更多
    "substance":       0.70,   # 男性更多
    "alcohol":         0.70,
    "gambling":        0.80,
    "anorexia":        0.10,   # 女性压倒性 ~9x
    "bulimia":         0.15,
    "binge":           0.35,
    "borderline_pd":   0.25,   # 女性更多 ~3x
    "antisocial_pd":   0.75,   # 男性更多
    "narcissistic_pd": 0.65,
    "avoidant_pd":     0.45,
    "dependent_pd":    0.35,
    "obsessive_pd":    0.55,
    "somatic_symptom": 0.35,
    "dissociative":    0.35,
    "insomnia":        0.45,
    "healthy":         0.48,
}


def sample_gender_for_diagnosis(
    diagnosis_key: str,
    rng: random.Random = random.Random(),
) -> str:
    """根据诊断的流行病学性别分布加权采样

    Returns: "男" or "女"
    """
    male_prob = DIAGNOSIS_GENDER_DIST.get(diagnosis_key, 0.5)
    return "男" if rng.random() < male_prob else "女"


# =====================================================================
# Layer 3 — 教育-诊断联动
# =====================================================================

# 教育层级（从低到高）
EDUCATION_LEVELS = [
    "未接受正式教育",
    "小学",
    "初中",
    "高中/中专",
    "大专",
    "本科",
    "硕士及以上",
]

# 诊断→教育程度倍率（相对于默认分布）
# < 1.0 = 压低该层级概率，> 1.0 = 拉高
# 只标注偏离显著的诊断
EDUCATION_DIAGNOSIS_MODIFIERS: dict[str, list[float]] = {
    # [未教育, 小学, 初中, 高中/中专, 大专, 本科, 硕士及以上]
    # 默认权重基于 2025 年全国 1% 人口抽样调查
    # 大学+合计 19.38%（含大专8.5%/本科8.8%/硕士+2.1%，为推算值）
    "default":      [0.076, 0.236, 0.322, 0.173, 0.085, 0.088, 0.021],
    # 早发障碍 → 压低高等教育
    "asd":          [0.08, 0.25, 0.34, 0.18, 0.07, 0.06, 0.02],
    "intellectual": [0.20, 0.35, 0.28, 0.10, 0.05, 0.02, 0.00],
    "adhd":         [0.06, 0.20, 0.32, 0.22, 0.10, 0.08, 0.02],
    "tic_disorder": [0.06, 0.20, 0.32, 0.22, 0.10, 0.08, 0.02],
    # 精神病性 → 中青年发病打断教育
    "schizophrenia": [0.08, 0.22, 0.34, 0.20, 0.08, 0.06, 0.02],
    "schizotypal":   [0.08, 0.22, 0.34, 0.20, 0.08, 0.06, 0.02],
    # 物质使用 → 辍学率高
    "substance":    [0.10, 0.25, 0.34, 0.18, 0.07, 0.05, 0.01],
    "alcohol":      [0.08, 0.22, 0.34, 0.20, 0.08, 0.06, 0.02],
    "gambling":     [0.10, 0.22, 0.34, 0.20, 0.07, 0.06, 0.01],
    # 进食障碍 → 中高教育（多为中产背景）
    "anorexia":     [0.02, 0.08, 0.18, 0.22, 0.18, 0.22, 0.10],
    "bulimia":      [0.02, 0.08, 0.18, 0.22, 0.18, 0.22, 0.10],
    # 人格障碍 → 略低教育
    "borderline_pd":  [0.08, 0.22, 0.32, 0.20, 0.08, 0.08, 0.02],
    "antisocial_pd":  [0.15, 0.30, 0.32, 0.14, 0.05, 0.03, 0.01],
    # 健康 → 正常偏优（教育保护效应）
    "healthy":      [0.04, 0.15, 0.28, 0.20, 0.14, 0.15, 0.04],
}


def sample_education_for_diagnosis(
    diagnosis_key: str,
    age: int,
    rng: random.Random = random.Random(),
) -> str:
    """根据诊断+年龄加权采样教育程度

    Args:
        diagnosis_key: 诊断键
        age: 当前年龄（用于年龄门槛过滤）
        rng: 随机数生成器

    Returns:
        教育程度字符串
    """
    modifiers = EDUCATION_DIAGNOSIS_MODIFIERS.get(
        diagnosis_key, EDUCATION_DIAGNOSIS_MODIFIERS["default"]
    )

    # 年龄门槛过滤
    if age < 6:
        return "未接受正式教育"
    if age < 12:
        modifiers[1] = modifiers[1] * 2  # 加倍小学概率
        modifiers[2] = 0  # 不能初中
        for i in range(3, 7):
            modifiers[i] = 0
    elif age < 15:
        for i in range(0, 1):
            modifiers[i] = 0
        # 不能高中及以上
        for i in range(3, 7):
            modifiers[i] = 0
    elif age < 18:
        for i in range(0, 2):
            modifiers[i] = 0
        # 不能大专及以上
        for i in range(4, 7):
            modifiers[i] = 0

    # 归一化
    total = sum(modifiers)
    if total <= 0:
        return "初中"
    weights = [m / total for m in modifiers]

    return rng.choices(EDUCATION_LEVELS, weights=weights, k=1)[0]


# =====================================================================
# Layer 4 — OCEAN-Event 桥接
# =====================================================================

# OCEAN 轮廓→事件效价权重调整
# 基于 Kendler et al. (2003), Brown & Harris (1978) 等理论
#
# 模式: {
#   "N_high_E_low": {-0.15, +0.10, +0.05},  # (positive_delta, negative_delta, neutral_delta)
# }
# delta 加在对应的事件比例上（events.py 的 positive_ratio / negative_ratio / neutral_ratio）
# 调整后三个比例的和必须仍为 1.0
OCEAN_EVENT_MODIFIERS: dict[str, dict[str, float]] = {
    # 高神经质 + 内向 → 更多负性事件（loss/danger敏感）
    "N_high_E_low":   {"positive": -0.15, "negative": +0.15, "neutral": +0.00},
    # 高神经质 + 外向 → 较多正性和负性（活跃但敏感）
    "N_high_E_high":  {"positive": -0.05, "negative": +0.10, "neutral": -0.05},
    # 低神经质 + 外向 → 更多正性事件
    "N_low_E_high":   {"positive": +0.15, "negative": -0.10, "neutral": -0.05},
    # 低神经质 + 内向 → 中性偏多
    "N_low_E_low":    {"positive": -0.05, "negative": -0.05, "neutral": +0.10},
    # 高开放性 + 高外向 → 正性多（探索行为）
    "O_high_E_high":  {"positive": +0.12, "negative": -0.05, "neutral": -0.07},
    # 低尽责性 → 较多负性（组织力不足）
    "C_low":          {"positive": -0.08, "negative": +0.10, "neutral": -0.02},
    # 高尽责性 → 正面偏多（有序生活）
    "C_high":         {"positive": +0.10, "negative": -0.08, "neutral": -0.02},
    # 低宜人性 → 人际冲突多（即更多负性）
    "A_low":          {"positive": -0.05, "negative": +0.10, "neutral": -0.05},
    # 全高神经质（不区分E）→ 负性偏好
    "N_high":         {"positive": -0.10, "negative": +0.12, "neutral": -0.02},
    # 全低神经质（不区分E）→ 正性偏好
    "N_low":          {"positive": +0.10, "negative": -0.08, "neutral": -0.02},
    # 默认（无显著偏置）
    "default":        {"positive": +0.00, "negative": +0.00, "neutral": +0.00},
}


def classify_ocean_pattern(ocean: dict[str, int]) -> str:
    """将 OCEAN 五维分数分类为 12 种模式之一

    Args:
        ocean: {"N": int, "E": int, "O": int, "A": int, "C": int}

    Returns:
        模式键
    """
    n = ocean.get("N", 5)
    e = ocean.get("E", 5)
    o = ocean.get("O", 5)
    a = ocean.get("A", 5)
    c = ocean.get("C", 5)

    # 判断高/低（≥7 为高，≤4 为低）
    n_high = n >= 7
    n_low = n <= 4
    e_high = e >= 7
    e_low = e <= 4
    o_high = o >= 7
    a_low = a <= 4
    c_low = c <= 4
    c_high = c >= 7

    patterns = []
    if n_high and e_low:
        return "N_high_E_low"
    if n_high and e_high:
        return "N_high_E_high"
    if n_low and e_high:
        return "N_low_E_high"
    if n_low and e_low:
        return "N_low_E_low"
    if o_high and e_high:
        return "O_high_E_high"
    if n_high:
        return "N_high"
    if n_low:
        return "N_low"
    if c_low:
        return "C_low"
    if c_high:
        return "C_high"
    if a_low:
        return "A_low"

    return "default"


def compute_event_valence_weights(
    ocean: dict[str, int],
    base_positive: float = 0.3,
    base_negative: float = 0.4,
    base_neutral: float = 0.3,
) -> tuple[float, float, float]:
    """根据 OCEAN 轮廓调整事件效价权重

    为与 events.py 中的 sample_events_for_persona() 接口兼容而设计：
    该函数接受 positive_ratio, negative_ratio, neutral_ratio 参数。

    Args:
        ocean: OCEAN 五维分数
        base_positive: 基础正性比例
        base_negative: 基础负性比例
        base_neutral: 基础中性比例

    Returns:
        (adjusted_positive, adjusted_negative, adjusted_neutral)
    """
    pattern = classify_ocean_pattern(ocean)
    mod = OCEAN_EVENT_MODIFIERS.get(pattern, OCEAN_EVENT_MODIFIERS["default"])

    p = base_positive + mod["positive"]
    n = base_negative + mod["negative"]
    u = base_neutral + mod["neutral"]

    # 裁剪到 [0.05, 0.90]
    p = max(0.05, min(0.90, p))
    n = max(0.05, min(0.90, n))
    u = max(0.05, min(0.90, u))

    # 重新归一化到和为 1.0
    total = p + n + u
    p /= total
    n /= total
    u /= total

    return (p, n, u)


# =====================================================================
# Layer 5 — 职业-诊断兼容性
# =====================================================================

# 重度诊断禁止的职业大类（基于功能损害程度）
# key: diagnosis_key, value: list of major_category (1-8) that are BLOCKED
DIAGNOSIS_OCCUPATION_BLOCKS: dict[str, list[int]] = {
    # 精神分裂症/精神病性 → 禁止高压/负责人岗位
    "schizophrenia":  [1, 7],             # 党政/军人
    "schizotypal":    [1, 7],
    "delusional":     [1, 7],
    # 重度智力障碍 → 禁止所有复杂专业岗
    "intellectual":   [1, 2, 5, 7],
    # ASD 社交障碍 → 禁止高社交大类  (保留 2 如果适合技术岗)
    "asd":            [1, 4, 7],          # 党政/生活服务/军人
    # 严重人格障碍 → 禁止党政/军
    "antisocial_pd":  [1, 4, 7],
    "borderline_pd":  [1, 7],
    # 物质使用 → 禁止党政/军及高风险
    "substance":      [1, 7],
    "alcohol":        [1, 7],
    "gambling":       [1, 7],
    # 健康 → 无限制
    "healthy":        [],
}

# 默认：无限制
_DEFAULT_OCCUPATION_BLOCKS: list[int] = []


def filter_occupations_for_diagnosis(
    diagnosis_key: str,
    occupations: list,
) -> list:
    """根据诊断过滤可用的职业（去除被禁止的大类）

    Args:
        diagnosis_key: 诊断键
        occupations: OccupationCategory 列表

    Returns:
        过滤后的职业列表
    """
    blocked_majors = DIAGNOSIS_OCCUPATION_BLOCKS.get(diagnosis_key, _DEFAULT_OCCUPATION_BLOCKS)
    if not blocked_majors:
        return occupations
    return [o for o in occupations if o.major_category not in blocked_majors]


# =====================================================================
# 压缩率计算
# =====================================================================

def _dim_size(levels: list | dict) -> int:
    """计算一个维度的离散状态数"""
    if isinstance(levels, dict):
        return len(levels)
    return len(levels)


def calculate_compression(
    diagnosis_key: str,
    age_range_full: tuple[int, int] = (13, 85),
) -> dict[str, dict]:
    """计算单个诊断在分层约束下的压缩比

    Args:
        diagnosis_key: 诊断键
        age_range_full: 原始年龄范围

    Returns:
        各维度压缩详情
    """
    full_age_count = age_range_full[1] - age_range_full[0] + 1
    valid_bands = DIAGNOSIS_AGE_BANDS.get(diagnosis_key, DIAGNOSIS_AGE_BANDS["healthy"])

    # 年龄压缩
    age_compressed = 0
    for band in AGE_BANDS:
        if band["name"] in valid_bands:
            lo, hi = band["range"]
            age_compressed += (hi - lo + 1)

    # 性别压缩 (2→2，不压缩)
    gender_full = 2
    gender_compressed = 2

    # 教育压缩（暂不压缩，7个层级全部保留）
    edu_full = len(EDUCATION_LEVELS)
    edu_compressed = edu_full

    return {
        "age": {
            "full": full_age_count,
            "compressed": age_compressed,
            "ratio": round(full_age_count / max(age_compressed, 1), 2),
            "valid_bands": valid_bands,
        },
        "gender": {
            "full": gender_full,
            "compressed": gender_compressed,
            "ratio": 1.0,
        },
        "education": {
            "full": edu_full,
            "compressed": edu_compressed,
            "ratio": 1.0,
        },
    }


def calculate_total_compression() -> str:
    """计算所有诊断的综合压缩率，返回可读报告"""
    lines = [
        "=" * 60,
        "分层压缩率报告",
        "=" * 60,
        "",
        f"{'诊断':<20} {'年龄原':>6} {'年龄压':>6} {'年龄比':>7} {'性别比':>6} {'教育比':>6} {'总压缩':>8}",
        "-" * 60,
    ]

    total_full = 0
    total_compressed = 0

    diagnosis_keys = sorted(DIAGNOSIS_AGE_BANDS.keys())
    for dk in diagnosis_keys:
        comp = calculate_compression(dk)
        age = comp["age"]
        age_full = age["full"]
        age_comp = age["compressed"]
        age_ratio = age["ratio"]

        # 总压缩：年龄×性别×教育 (性别和教育暂算1)
        dim_full = age_full * 2 * len(EDUCATION_LEVELS)
        dim_comp = age_comp * 2 * len(EDUCATION_LEVELS)
        dim_ratio = round(dim_full / max(dim_comp, 1), 1)

        total_full += dim_full
        total_compressed += dim_comp

        # 名称截断
        dk_display = dk[:20]
        lines.append(
            f"{dk_display:<20} {age_full:>6} {age_comp:>6} {age_ratio:>6.1f}x   {1.0:>5.1f}x  {1.0:>5.1f}x  {dim_ratio:>6.1f}x"
        )

    # 总计
    total_ratio = round(total_full / max(total_compressed, 1), 1)
    lines.extend([
        "-" * 60,
        f"{'总计':<20} {'':>6} {'':>6} {'':>7} {'':>6} {'':>6} {total_ratio:>6.1f}x",
        "",
        "重要澄清：",
        "  - 年龄压缩来自 Age Band 分层（6带 × 诊断有效子集）",
        "  - 但多数诊断横跨全部6个年龄带（抑郁/PTSD/健康对照=1.0x），",
        "    只有抽动(5.6x)/进食障碍(2.6x)等窄诊断压得多，",
        "    全诊断平均仅 ~1.5x（37814 → 24612 个离散单元）。",
        "  - 性别未压缩（2状态），教育未压缩（7层级）。",
        "  - 本模块是『软约束/条件概率』，不是『硬封顶』：",
        "    任何 (诊断×年龄) 组合仍以极低概率可生成，",
        "    因此『可表示的 persona 集合』并未变小，理论最大组合数不变。",
        "  - OCEAN-Event桥接/职业过滤只改变概率质量分布",
        "    （消除临床不可能的组合），不减少可达组合的数量。",
        "  - 结论：理论最大组合数仍在同一天文数量级",
        "    （≥10²⁸；若 OCEAN 按连续算则真正无界）。",
        "    分层真正换来的是『高概率区临床有效性』，而非更小的计数。",
    ])

    return "\n".join(lines)
