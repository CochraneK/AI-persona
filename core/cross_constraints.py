"""
交叉约束模块 — 实现 OCEAN→认知应对/OCEAN→事件/OCEAN→职业/OCEAN→社交/教育→职业 全部5条原有+
OCEAN→沟通风格/OCEAN→生活习惯/OCEAN→价值观/OCEAN→能力/OCEAN→Erikson/
OCEAN→触发器/OCEAN→外观/OCEAN→隐藏经历/OCEAN→Storr链/OCEAN→应激模式 共15条约束

=========================================================================
设计思路
=========================================================================
generator.py 的 generate() 方法目前按维度独立采样：
  ocean = sample_ocean(...)           # 只看诊断
  cognitive, coping = ...             # 只看诊断
  social_relations = ...              # 只看诊断
  events = sample_events_for_persona(...) # 只看诊断
  etc.

本模块实现各维度间的"条件依赖"：

  约束 1: OCEAN→认知应对 (P1)        — 加权重采样
  约束 2: OCEAN→事件效价 (P0)        — 加权调整
  约束 3: OCEAN→职业偏好              — 加权调整
  约束 4: OCEAN→社交关系              — 后处理调整
  约束 5: 教育→职业                   — 硬过滤+软加权
  ---- v3 新增 ----
  约束 6: OCEAN→沟通风格              — E/N 影响沟通参数
  约束 7: OCEAN→生活习惯              — C/N 影响日常节奏
  约束 8: OCEAN→价值观信念            — O/C 影响价值观权重
  约束 9: OCEAN→能力技能              — O/C/A 影响能力描述
  约束10: OCEAN→Erikson阶段           — N/E 影响解决状态
  约束11: OCEAN→触发器类型            — N/E/C 影响触发池偏置
  约束12: OCEAN→安全行为              — N/E 影响应对风格
  约束13: OCEAN→外观特征              — N/C 影响外貌描述
  约束14: OCEAN→隐藏经历              — O/N 影响经历类型
  约束15: OCEAN→Storr因果链           — N/E/O 影响创伤/欲望类型
  约束16: OCEAN→应激模式              — N/E 影响主要应激方向

用法:
  from .cross_constraints import (
      adjust_cognitive_coping_by_ocean,
      adjust_event_ratios_by_ocean,
      adjust_occupation_weights_by_ocean,
      adjust_social_relations_by_ocean,
      filter_occupations_by_education,
      # v3 新增
      adjust_values_beliefs_by_ocean,
      adjust_communication_style_by_ocean,
      adjust_lifestyle_habits_by_ocean,
      adjust_skills_abilities_by_ocean,
      adjust_erikson_stage_by_ocean,
      adjust_storr_wound_by_ocean,
      adjust_storr_desire_by_ocean,
      adjust_storr_need_by_ocean,
      adjust_stress_response_by_ocean,
      adjust_triggers_by_ocean,
      adjust_safety_behaviors_by_ocean,
      adjust_physical_appearance_by_ocean,
      adjust_hidden_experiences_by_ocean,
      select_event_types_by_ocean,
  )
=========================================================================
"""

import copy
import random
from typing import Optional

from .stratification import classify_ocean_pattern, OCEAN_EVENT_MODIFIERS, compute_event_valence_weights

# =====================================================================
# 约束1 — OCEAN→认知应对加权 (P1)
# =====================================================================

# OCEAN 轮廓→认知风格权重调整
# 每个轮廓对特定的认知风格施加倍率
OCEAN_COGNITIVE_MODIFIERS: dict[str, dict[str, float]] = {
    "N_high_E_low": {
        # 高神+内向：加重反刍、灾难化、消极归因；降低理性/正念
        "反刍思维": 2.0, "灾难化思维": 2.0, "消极归因": 1.8,
        "选择性关注负面": 1.5, "读心术倾向": 1.5,
        "理性分析": 0.3, "正念觉察": 0.3, "灵活应变": 0.4,
        "自我效能感高": 0.3,
    },
    "N_high_E_high": {
        # 高神+外向：情绪波动大、情感推理
        "情感推理": 2.0, "灾难化思维": 1.5, "非黑即白思维": 1.5,
        "比较思维": 1.3, "过度概括": 1.3,
        "理性分析": 0.5, "正念觉察": 0.5,
    },
    "N_low_E_high": {
        # 低神+外向：理性、灵活、自我效能高
        "理性分析": 2.0, "灵活应变": 2.0, "自我效能感高": 2.0,
        "正念觉察": 1.8, "未来导向思维": 1.5,
        "反刍思维": 0.2, "灾难化思维": 0.3, "消极归因": 0.3,
    },
    "N_low_E_low": {
        # 低神+内向：理性、接纳，但灵活性可能不高
        "理性分析": 1.8, "接纳": 1.5, "正念觉察": 1.5,
        "完美主义倾向": 1.2,
        "灾难化思维": 0.3, "反刍思维": 0.4,
        "情感推理": 0.4,
    },
    "O_high_E_high": {
        # 高开+外向：灵活、未来导向
        "灵活应变": 2.0, "未来导向思维": 2.0, "自我效能感高": 1.5,
        "理性分析": 1.3,
        "非黑即白思维": 0.3, "灾难化思维": 0.4,
    },
    "C_low": {
        # 低尽责：拖延、容易分心、情感推理
        "拖延倾向": 3.0, "容易分心": 2.5, "情感推理": 1.5,
        "自我效能感低": 2.0,
        "理性分析": 0.4, "未来导向思维": 0.4,
    },
    "C_high": {
        # 高尽责：计划导向、完美主义
        "完美主义倾向": 2.0, "未来导向思维": 1.8, "理性分析": 1.5,
        "拖延倾向": 0.2, "容易分心": 0.3, "自我效能感低": 0.2,
    },
    "A_low": {
        # 低宜人：比较思维、读心术、非黑即白
        "比较思维": 2.0, "读心术倾向": 1.8, "非黑即白思维": 1.5,
        "情感推理": 1.3,
        "正念觉察": 0.4, "灵活应变": 0.5,
    },
    "N_high": {
        # 纯高神（不区分E）：通用加权
        "灾难化思维": 1.5, "反刍思维": 1.5, "消极归因": 1.3,
        "选择性关注负面": 1.3,
        "理性分析": 0.5, "正念觉察": 0.5, "自我效能感高": 0.4,
    },
    "N_low": {
        # 纯低神（不区分E）：通用加权
        "理性分析": 1.5, "灵活应变": 1.5, "正念觉察": 1.5,
        "自我效能感高": 1.5,
        "灾难化思维": 0.3, "反刍思维": 0.4,
    },
}

# OCEAN 轮廓→应对方式权重调整
OCEAN_COPING_MODIFIERS: dict[str, dict[str, float]] = {
    "N_high_E_low": {
        "退缩/孤立": 2.5, "回避/否认": 2.0, "自我责备": 2.0,
        "问题解决导向": 0.3, "寻求社会支持": 0.3, "积极重构": 0.3,
    },
    "N_high_E_high": {
        "情绪宣泄": 2.5, "发泄": 2.0, "物质使用": 1.5,
        "寻求社会支持": 1.3,
        "退缩/孤立": 0.3, "回避/否认": 0.5,
    },
    "N_low_E_high": {
        "问题解决导向": 2.5, "寻求社会支持": 2.0, "积极重构": 2.0,
        "幽默化解": 1.5, "计划行动": 1.5,
        "退缩/孤立": 0.2, "物质使用": 0.3, "自我责备": 0.3,
    },
    "N_low_E_low": {
        "接纳": 2.0, "计划行动": 1.8, "问题解决导向": 1.5,
        "转移注意力": 1.3,
        "情绪宣泄": 0.3, "发泄": 0.3, "寻求社会支持": 0.5,
    },
    "O_high_E_high": {
        "积极重构": 2.0, "幽默化解": 2.0, "问题解决导向": 1.5,
        "寻求社会支持": 1.5,
        "回避/否认": 0.3, "退缩/孤立": 0.3,
    },
    "C_low": {
        "回避/否认": 1.8, "转移注意力": 2.0, "自我安慰": 1.5,
        "物质使用": 1.3,
        "计划行动": 0.3, "问题解决导向": 0.4,
    },
    "C_high": {
        "计划行动": 2.5, "问题解决导向": 2.0, "接纳": 1.5,
        "积极重构": 1.3,
        "物质使用": 0.2, "发泄": 0.3, "回避/否认": 0.4,
    },
    "A_low": {
        "发泄": 2.0, "情绪宣泄": 1.8, "物质使用": 1.3,
        "回避/否认": 1.3,
        "寻求社会支持": 0.3, "接纳": 0.5,
    },
    "N_high": {
        "回避/否认": 1.5, "自我责备": 1.5, "情绪宣泄": 1.3,
        "问题解决导向": 0.4, "积极重构": 0.5,
    },
    "N_low": {
        "问题解决导向": 1.8, "积极重构": 1.8, "接纳": 1.5,
        "计划行动": 1.5,
        "物质使用": 0.3, "情绪宣泄": 0.4, "自我责备": 0.3,
    },
}

# 默认加权（所有轮廓通用）
_DEFAULT_MODIFIER: float = 1.0


def adjust_cognitive_coping_by_ocean(
    cognitive_styles: list[str],
    coping_styles: list[str],
    ocean: dict[str, int],
    rng: random.Random,
    n_cognitive: int = 2,
    n_coping: int = 2,
) -> tuple[list[str], list[str]]:
    """根据 OCEAN 轮廓调整认知和应对风格的采样权重

    不会添加新风格，只从已有诊断池中按加权重新采样。

    Args:
        cognitive_styles: 按诊断抽出的候选认知风格列表（来自 DIAGNOSIS_COGNITIVE_MAP）
        coping_styles: 按诊断抽出的候选应对风格列表（来自 DIAGNOSIS_COPING_MAP）
        ocean: OCEAN 五维分数
        rng: 随机数生成器
        n_cognitive: 需要的认知风格数
        n_coping: 需要的应对风格数

    Returns:
        (选中的认知风格列表, 选中的应对风格列表)
    """
    pattern = classify_ocean_pattern(ocean)

    # ---- 认知风格加权采样 ----
    cog_mod = OCEAN_COGNITIVE_MODIFIERS.get(pattern, {})
    cog_weights = []
    for style in cognitive_styles:
        w = cog_mod.get(style, _DEFAULT_MODIFIER)
        # 确保权重 > 0
        w = max(w, 0.01)
        cog_weights.append(w)

    # 归一化
    total_cog = sum(cog_weights)
    if total_cog <= 0:
        total_cog = 1.0
    cog_probs = [w / total_cog for w in cog_weights]

    selected_cog = rng.choices(
        cognitive_styles,
        weights=cog_probs,
        k=min(n_cognitive, len(cognitive_styles)),
    )
    # 去重（如果选到重复的）
    selected_cog = list(dict.fromkeys(selected_cog))

    # ---- 应对风格加权采样 ----
    cop_mod = OCEAN_COPING_MODIFIERS.get(pattern, {})
    cop_weights = []
    for style in coping_styles:
        w = cop_mod.get(style, _DEFAULT_MODIFIER)
        w = max(w, 0.01)
        cop_weights.append(w)

    total_cop = sum(cop_weights)
    if total_cop <= 0:
        total_cop = 1.0
    cop_probs = [w / total_cop for w in cop_weights]

    selected_cop = rng.choices(
        coping_styles,
        weights=cop_probs,
        k=min(n_coping, len(coping_styles)),
    )
    selected_cop = list(dict.fromkeys(selected_cop))

    return selected_cog, selected_cop


# =====================================================================
# 约束2 — OCEAN→事件桥接 (P0)
# =====================================================================

def adjust_event_ratios_by_ocean(
    ocean: dict[str, int],
    base_positive: float = 0.3,
    base_negative: float = 0.4,
    base_neutral: float = 0.3,
) -> tuple[float, float, float]:
    """根据 OCEAN 轮廓调整事件效价比例

    复用 stratification.py 的 compute_event_valence_weights()。

    Returns:
        (adjusted_positive, adjusted_negative, adjusted_neutral)
    """
    return compute_event_valence_weights(
        ocean=ocean,
        base_positive=base_positive,
        base_negative=base_negative,
        base_neutral=base_neutral,
    )


# =====================================================================
# 约束3 — OCEAN→职业偏好
# =====================================================================

# 8 个职业大类的 OCEAN 轮廓偏置倍率
# 格式: pattern → {major_category: weight_multiplier}
# 大类: 1=党政, 2=专业技术人员, 3=办事人员, 4=生活服务,
#       5=农林牧渔, 6=生产运输, 7=军人, 8=不便分类
OCEAN_PROFESSION_BIAS: dict[str, dict[int, float]] = {
    "N_high_E_low": {
        # 高神+内向 → 低压低社交岗位
        3: 1.5,   # 办事员
        5: 1.3,   # 农林牧渔（独立工作）
        6: 1.2,   # 生产运输
        1: 0.3,   # 党政（高压）
        4: 0.6,   # 生活服务（高社交）
    },
    "N_high_E_high": {
        # 高神+外向 → 不稳定但社交化的岗位
        4: 1.5,   # 生活服务
        6: 1.2,   # 生产运输（体力释放）
        1: 0.5,   # 党政（高压不稳定）
        2: 0.6,   # 专业技术（长期专注）
    },
    "N_low_E_high": {
        # 低神+外向 → 管理、社交、专业
        1: 1.8,   # 党政（社交+稳定）
        2: 1.5,   # 专业技术（需社交协作）
        3: 1.3,   # 办事人员
        5: 0.4,   # 农林牧渔（低社交）
        6: 0.5,   # 生产运输
    },
    "N_low_E_low": {
        # 低神+内向 → 专业技术、独立工作
        2: 2.0,   # 专业技术
        3: 1.5,   # 办事人员
        5: 1.3,   # 农林牧渔
        4: 0.4,   # 生活服务（高社交）
        1: 0.5,   # 党政（高社交）
    },
    "O_high_E_high": {
        # 高开+外向 → 创意、社交
        2: 1.8,   # 专业技术（尤其是创意类）
        4: 1.3,   # 生活服务
        1: 1.2,   # 党政
        5: 0.4,   # 农林牧渔
        6: 0.5,   # 生产运输
    },
    "C_low": {
        # 低尽责 → 灵活低结构岗位
        4: 1.8,   # 生活服务
        6: 1.5,   # 生产运输
        5: 1.3,   # 农林牧渔
        2: 0.4,   # 专业技术（需高自律）
        1: 0.3,   # 党政
    },
    "C_high": {
        # 高尽责 → 结构化、专业
        1: 1.8,   # 党政
        2: 1.8,   # 专业技术
        3: 1.5,   # 办事人员
        4: 0.4,   # 生活服务
        6: 0.5,   # 生产运输
    },
    "A_low": {
        # 低宜人 → 独立/竞争性岗位
        6: 1.5,   # 生产运输
        1: 0.4,   # 党政（需协作）
        4: 0.5,   # 生活服务（需高宜人）
    },
    "N_high": {
        3: 1.3,   # 办事人员（低压）
        5: 1.2,   # 农林牧渔
        1: 0.4,   # 党政
        2: 0.6,   # 专业技术
    },
    "N_low": {
        1: 1.5,   # 党政
        2: 1.5,   # 专业技术
        3: 1.3,   # 办事人员
        6: 0.5,   # 生产运输
    },
    "default": {
        # 无显著偏置
    },
}


def adjust_occupation_weights_by_ocean(
    major_weights: dict[int, float],
    ocean: dict[str, int],
) -> dict[int, float]:
    """根据 OCEAN 轮廓调整职业大类权重

    Args:
        major_weights: 原始大类权重 {major: weight}
        ocean: OCEAN 五维分数

    Returns:
        调整后的权重大小
    """
    pattern = classify_ocean_pattern(ocean)
    bias = OCEAN_PROFESSION_BIAS.get(pattern, OCEAN_PROFESSION_BIAS["default"])

    adjusted = {}
    for major, weight in major_weights.items():
        w = weight * bias.get(major, 1.0)
        w = max(w, 0.01)  # 确保不为0
        adjusted[major] = w

    return adjusted


# =====================================================================
# 约束4 — OCEAN→MECE社交关系
# =====================================================================

# 基于 OCEAN E 维度的社交关系调整
# 内向 (E≤4) / 外向 (E≥7) / 中间 (E=5-6) 三种模板
SOCIAL_RELATIONS_E_MODIFIERS: dict[str, dict[str, str | list[str]]] = {
    "low_E": {
        "family_modifier": "家庭关系密切但人际圈子小",
        "friends_modifier": "少数深层友谊，重质量而非数量",
        "network_modifier": "小",
        "template_additions": [
            "我不太喜欢社交场合。",
            "我更喜欢一对一的交流。",
            "独处时我能更好地恢复精力。",
        ],
    },
    "high_E": {
        "family_modifier": "家庭关系开放活跃，经常组织家庭聚会",
        "friends_modifier": "朋友圈广泛，喜欢结交新朋友",
        "network_modifier": "大",
        "template_additions": [
            "周末一起出去玩吧！",
            "我认识一个人可以帮你。",
            "人多热闹才有意思。",
        ],
    },
    "mid_E": {
        "family_modifier": None,  # 保留原始诊断描述
        "friends_modifier": None,
        "network_modifier": None,
        "template_additions": [],
    },
}


def adjust_social_relations_by_ocean(
    social_relations: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 的 E(外向性) 分数调整社会关系特征

    在原始诊断基础上叠加 E 维度影响。

    Args:
        social_relations: 原始社会关系 dict（来自 sample_social_relations）
        ocean: OCEAN 五维分数

    Returns:
        调整后的 social_relations
    """
    e_score = ocean.get("E", 5)

    if e_score <= 4:
        mode = SOCIAL_RELATIONS_E_MODIFIERS["low_E"]
    elif e_score >= 7:
        mode = SOCIAL_RELATIONS_E_MODIFIERS["high_E"]
    else:
        # E=5-6: 仅替换 network_size（中间值改为"偏中等"）
        result = dict(social_relations)
        result["network_size"] = "中等"
        return result

    result = dict(social_relations)

    if mode["family_modifier"]:
        # 合并而不是完全替换
        original_family = result.get("family", "")
        result["family"] = f"{original_family}（{mode['family_modifier']}）"

    if mode["friends_modifier"]:
        original_friends = result.get("friends", "")
        result["friends"] = f"{original_friends}；{mode['friends_modifier']}"

    if mode["network_modifier"]:
        result["network_size"] = mode["network_modifier"]

    # 追加社交模板语句
    additions = list(mode["template_additions"])
    if additions:
        existing_templates = list(result.get("templates", []))
        rng.shuffle(additions)
        # 追加 1-2 条
        n_add = min(len(additions), rng.randint(1, 2))
        existing_templates.extend(additions[:n_add])
        result["templates"] = existing_templates

    return result


# =====================================================================
# 约束5 — 教育→职业
# =====================================================================

# 各教育程度禁止的职业大类
# 基于能力门槛：某些职业大类需要最低教育要求
EDUCATION_OCCUPATION_BLOCKS: dict[str, list[int]] = {
    # 低教育：不能担任党政/专业技术人员/军人
    "未接受正式教育": [1, 2, 7],       # 党政、专业技术、军人
    "小学":            [1, 2, 7],       # 同上
    "初中":            [1, 7],          # 党政、军人（中级专业技术仍可能）
    # 高中及以上无限制
    "高中/中专":       [],
    "大专":            [],
    "本科":            [],
    "硕士及以上":      [],
}

# 高教育→限制低技能职业大类的偏好权重（非禁止，仅降低权重）
EDUCATION_OCCUPATION_PENALTY: dict[str, dict[int, float]] = {
    "硕士及以上": {
        4: 0.3,   # 生活服务
        5: 0.2,   # 农林牧渔
        6: 0.3,   # 生产运输
    },
    "本科": {
        5: 0.4,   # 农林牧渔
        6: 0.5,   # 生产运输
    },
}


def filter_occupations_by_education(
    education: str,
    occupations: list,
    major_weights: dict[int, float] | None = None,
) -> tuple[list, dict[int, float] | None]:
    """根据教育程度过滤/加权职业

    两步：
    1. 硬过滤：移除被禁止的大类
    2. 软加权：高教育降低低技能大类权重

    Args:
        education: 教育程度字符串
        occupations: OccupationCategory 列表
        major_weights: 可选，当前大类权重（用于调整）

    Returns:
        (过滤后的职业列表, 调整后的权重（如果提供了major_weights）)
    """
    # 第一步：硬过滤
    blocked = EDUCATION_OCCUPATION_BLOCKS.get(education, [])
    if blocked:
        filtered = [o for o in occupations if o.major_category not in blocked]
    else:
        filtered = occupations

    # 第二步：如提供了权重，应用高教育惩罚
    adjusted_weights = None
    if major_weights is not None:
        adjusted_weights = dict(major_weights)
        penalty = EDUCATION_OCCUPATION_PENALTY.get(education, {})
        for major, factor in penalty.items():
            if major in adjusted_weights:
                adjusted_weights[major] = max(adjusted_weights[major] * factor, 0.01)

    return filtered, adjusted_weights


# =====================================================================
# 约束6 — OCEAN→价值观信念 (约束8)
# =====================================================================

# OCEAN 轮廓→价值观信念的修饰符
# O(开放性) 影响抽象/探索性 vs 传统价值观
# C(尽责性) 影响秩序/成就 vs 享乐价值观
VALUES_BELIEFS_OCEAN_MODIFIERS: dict[str, dict] = {
    "O_high_C_high": {
        "moral_foundation_appendix": "（理想主义+秩序感兼具）",
        "core_value_additions": ["真理", "自我实现"],
        "worldview_shift": "世界是一幅正在完成的伟大画卷，我愿在其中找到自己的位置",
    },
    "O_high_C_low": {
        "moral_foundation_appendix": "（自由探索倾向）",
        "core_value_additions": ["自由表达", "打破常规"],
        "worldview_shift": "规则是人定的，不一定适合我",
    },
    "O_low_C_high": {
        "moral_foundation_appendix": "（传统保守倾向）",
        "core_value_additions": ["服从", "传统"],
        "worldview_shift": "按规矩办事是最稳妥的生活方式",
    },
    "O_low_C_low": {
        "moral_foundation_appendix": "（当下享乐倾向）",
        "core_value_additions": ["即时满足", "轻松"],
        "worldview_shift": "想那么多干嘛，过好当下就好",
    },
    "N_high": {
        "core_value_additions": ["安全", "控制感"],
        "worldview_shift": "这个世界充满危险，我必须时刻小心",  # 覆盖上述
    },
    "A_low": {
        "core_value_additions": ["权力", "独立"],
        "worldview_shift": "只有强者才能生存",
    },
}


def adjust_values_beliefs_by_ocean(
    values_beliefs: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 轮廓调整价值观与信念"""
    result = dict(values_beliefs)
    o_score = ocean.get("O", 5)
    c_score = ocean.get("C", 5)
    n_score = ocean.get("N", 5)
    a_score = ocean.get("A", 5)
    e_score = ocean.get("E", 5)

    # 确定模式键：优先 O*C 组合
    o_bin = "high" if o_score >= 7 else ("low" if o_score <= 4 else "mid")
    c_bin = "high" if c_score >= 7 else ("low" if c_score <= 4 else "mid")

    if o_bin != "mid" and c_bin != "mid":
        pattern = f"O_{o_bin}_C_{c_bin}"
    elif n_score >= 7:
        pattern = "N_high"
    elif a_score <= 4:
        pattern = "A_low"
    else:
        return result  # 无显著偏置

    mod = VALUES_BELIEFS_OCEAN_MODIFIERS.get(pattern)
    if mod is None:
        return result

    # 叠加 moral_foundation
    if "moral_foundation_appendix" in mod:
        orig = result.get("moral_foundation", "")
        result["moral_foundation"] = f"{orig}{mod['moral_foundation_appendix']}"

    # 追加核心价值观
    additions = list(mod.get("core_value_additions", []))
    if additions:
        existing = list(result.get("core_values", []))
        rng.shuffle(additions)
        existing.extend(additions)
        result["core_values"] = existing

    # 替换 worldview（高优先级覆盖 N_high / A_low ）
    if "worldview_shift" in mod:
        # N_high 和 A_low 的移版覆盖 O*C 移版
        high_priority = pattern in ("N_high", "A_low")
        if high_priority or "worldview_shift" not in values_beliefs.get("worldview", ""):
            result["worldview"] = mod["worldview_shift"]

    return result


# =====================================================================
# 约束7 — OCEAN→沟通风格 (约束6)
# =====================================================================

# E 维度→talkative/直接度偏移
# N 维度→情绪表达度偏移
COMMUNICATION_STYLE_E_MODIFIERS: dict[str, dict[str, int]] = {
    "low_E":  {"talkative": -2, "directness": -1, "formality": +1, "emotional_expression": 0},
    "high_E": {"talkative": +2, "directness": +1, "formality": -1, "emotional_expression": +1},
    "mid_E":  {"talkative": 0,  "directness": 0,  "formality": 0,  "emotional_expression": 0},
}

COMMUNICATION_STYLE_N_MODIFIERS: dict[str, dict[str, int]] = {
    "low_N": {"emotional_expression": -1, "talkative": 0},
    "high_N": {"emotional_expression": +2, "talkative": +1},
    "mid_N": {"emotional_expression": 0, "talkative": 0},
}

# 高 N 者倾向使用负面化典型用语
HIGH_N_TYPICAL_PHRASES: list[str] = [
    "万一出事怎么办", "我不确定", "这样真的行吗",
    "感觉不太对劲", "但愿不会出问题",
]


def adjust_communication_style_by_ocean(
    comm_style: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 的 E(外向性) 和 N(神经质) 调整沟通风格数值"""
    result = dict(comm_style)
    e_score = ocean.get("E", 5)
    n_score = ocean.get("N", 5)

    # E 修饰
    if e_score <= 4:
        e_mode = COMMUNICATION_STYLE_E_MODIFIERS["low_E"]
    elif e_score >= 7:
        e_mode = COMMUNICATION_STYLE_E_MODIFIERS["high_E"]
    else:
        e_mode = COMMUNICATION_STYLE_E_MODIFIERS["mid_E"]

    # N 修饰
    if n_score <= 4:
        n_mode = COMMUNICATION_STYLE_N_MODIFIERS["low_N"]
    elif n_score >= 7:
        n_mode = COMMUNICATION_STYLE_N_MODIFIERS["high_N"]
    else:
        n_mode = COMMUNICATION_STYLE_N_MODIFIERS["mid_N"]

    # 应用偏移（钳制在 1-10）
    for key in ("talkative", "directness", "formality", "emotional_expression"):
        val = result.get(key, 5)
        shift = e_mode.get(key, 0) + n_mode.get(key, 0)
        result[key] = max(1, min(10, val + shift))

    # 高 N 者附加负面典型用语
    if n_score >= 7:
        existing = list(result.get("typical_phrases", []))
        n_phrases = rng.sample(HIGH_N_TYPICAL_PHRASES, min(2, len(HIGH_N_TYPICAL_PHRASES)))
        # 替换 1-2 条
        for i, phrase in enumerate(n_phrases):
            if i < len(existing):
                existing[i] = phrase
        result["typical_phrases"] = existing

    return result


# =====================================================================
# 约束8 — OCEAN→生活习惯 (约束7)
# =====================================================================

# C(尽责性) → 日常节奏结构度
# N(神经质) → 饮食/睡眠紊乱度
LIFESTYLE_HABITS_C_MODIFIERS: dict[str, dict[str, str]] = {
    "low_C": {
        "routine_mod": "（节奏松散，计划经常赶不上变化）",
        "sleep_mod": "睡眠极不规律，经常熬夜",
        "diet_mod": "饮食随心所欲，没有固定时间",
    },
    "high_C": {
        "routine_mod": "（高度自律，每日计划精确到小时）",
        "sleep_mod": "睡眠规律，尽力保证充足休息",
        "diet_mod": "饮食有计划且严格执行",
    },
}

LIFESTYLE_HABITS_N_MODIFIERS: dict[str, dict[str, str]] = {
    "high_N": {
        "diet_mod": "压力大时发生进食紊乱（暴食或食欲全无）",
        "sleep_mod": "入睡困难，脑中反复思虑影响睡眠质量",
    },
}


def adjust_lifestyle_habits_by_ocean(
    habits: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 的 C(尽责性) 和 N(神经质) 调整生活习惯描述"""
    result = dict(habits)
    c_score = ocean.get("C", 5)
    n_score = ocean.get("N", 5)

    # C 修饰
    if c_score <= 4:
        c_mod = LIFESTYLE_HABITS_C_MODIFIERS["low_C"]
        result["daily_routine"] = f"{result.get('daily_routine', '')}{c_mod['routine_mod']}"
        result["sleep"] = c_mod["sleep_mod"]
        result["diet"] = c_mod["diet_mod"]
    elif c_score >= 7:
        c_mod = LIFESTYLE_HABITS_C_MODIFIERS["high_C"]
        result["daily_routine"] = f"{result.get('daily_routine', '')}{c_mod['routine_mod']}"
        result["sleep"] = c_mod["sleep_mod"]
        result["diet"] = c_mod["diet_mod"]

    # N 修饰（叠加在 C 之上）
    if n_score >= 7:
        n_mod = LIFESTYLE_HABITS_N_MODIFIERS["high_N"]
        result["diet"] = n_mod["diet_mod"]
        result["sleep"] = f"{result.get('sleep', '')} —— {n_mod['sleep_mod']}"

    return result


# =====================================================================
# 约束9 — OCEAN→能力技能 (约束9)
# =====================================================================

SKILLS_ABILITIES_OCEAN_MODIFIERS: dict[str, dict] = {
    "O_high": {
        "cognitive_mod": "（思维活跃，富有想象力，擅长发散性思考）",
        "talent_additions": ["创新思维", "跨界联想"],
    },
    "O_low": {
        "cognitive_mod": "（务实保守，偏好熟悉和确定的方法）",
        "talent_additions": ["务实", "执行力"],
    },
    "C_high": {
        "cognitive_mod": "（条理清晰，擅长计划和执行）",
        "talent_additions": ["组织能力", "计划执行力"],
    },
    "C_low": {
        "cognitive_mod": "（注意力容易分散，偏好即兴发挥）",
        "talent_additions": ["临场应变", "即兴创造"],
    },
    "A_high": {
        "cognitive_mod": "（善于理解他人，共情能力强）",
        "talent_additions": ["共情", "协调能力"],
    },
    "A_low": {
        "cognitive_mod": "（独立判断，不受他人意见左右）",
        "talent_additions": ["独立决策", "批判性"],
    },
}


def adjust_skills_abilities_by_ocean(
    skills: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 的 O/C/A 维度调整能力技能描述"""
    result = dict(skills)
    o_score = ocean.get("O", 5)
    c_score = ocean.get("C", 5)
    a_score = ocean.get("A", 5)

    # 依次应用修饰（按优先级 O > C > A）
    for dim_key, score, threshold_high, threshold_low in [
        ("O_high", o_score, 7, 0), ("O_low", o_score, 0, 4),
        ("C_high", c_score, 7, 0), ("C_low", c_score, 0, 4),
        ("A_high", a_score, 7, 0), ("A_low", a_score, 0, 4),
    ]:
        if (threshold_high and score >= threshold_high) or (threshold_low and score <= threshold_low):
            mod = SKILLS_ABILITIES_OCEAN_MODIFIERS.get(dim_key)
            if mod is None:
                continue
            # 叠加认知修饰
            if "cognitive_mod" in mod:
                orig = result.get("cognitive", "")
                result["cognitive"] = f"{orig}{mod['cognitive_mod']}"
            # 追加天赋
            additions = list(mod.get("talent_additions", []))
            if additions:
                existing = list(result.get("talents", []))
                rng.shuffle(additions)
                # 最多加 1 条
                existing.extend(additions[:1])
                result["talents"] = existing

    return result


# =====================================================================
# 约束10 — OCEAN→Erikson阶段 (约束10)
# =====================================================================

ERIKSON_OCEAN_MODIFIERS: dict[str, dict[str, str]] = {
    "N_high": {
        "resolution_mod": "（被高神经质加剧，难以走出）",
    },
    "N_low": {
        "resolution_mod": "（因情绪稳定而相对可调整）",
    },
    "E_high": {
        "strength_mod": "（在社交互动中寻找验证）",
    },
    "E_low": {
        "strength_mod": "（在独处反思中获得）",
    },
}


def adjust_erikson_stage_by_ocean(
    erikson: dict,
    ocean: dict[str, int],
    rng: random.Random,
) -> dict:
    """根据 OCEAN 的 N 和 E 维度微调 Erikson 阶段描述"""
    result = dict(erikson)
    n_score = ocean.get("N", 5)
    e_score = ocean.get("E", 5)

    # 追加 resolution 修饰
    if n_score >= 7:
        mod = ERIKSON_OCEAN_MODIFIERS["N_high"]
        result["resolution"] = f"{result.get('resolution', '')}{mod['resolution_mod']}"
    elif n_score <= 4:
        mod = ERIKSON_OCEAN_MODIFIERS["N_low"]
        result["resolution"] = f"{result.get('resolution', '')}{mod['resolution_mod']}"

    # 追加 strength 修饰
    if e_score >= 7:
        mod = ERIKSON_OCEAN_MODIFIERS["E_high"]
        result["strength"] = f"{result.get('strength', '')}（{mod['strength_mod']}）"
    elif e_score <= 4:
        mod = ERIKSON_OCEAN_MODIFIERS["E_low"]
        result["strength"] = f"{result.get('strength', '')}（{mod['strength_mod']}）"

    return result


# =====================================================================
# 约束11 — OCEAN→触发器类型 (约束11)
# =====================================================================

# 高 N 附加触发器模板
TRIGGERS_HIGH_N_APPEND: list[str] = [
    "突然感到一阵莫名的恐慌",
    "收到意外的坏消息",
    "独自一人在安静环境中思绪开始失控",
    "看到别人过得好而产生自我怀疑",
    "被提醒过去的失败经历",
]
# 高 N 安全行为附加
SAFETY_HIGH_N_APPEND: list[str] = [
    "反复向信任的人确认一切安好",
    "用检查身体指标来缓解焦虑",
    "给自己设计了一套「安全流程」必须完成",
]

# 低 C 附加触发器
TRIGGERS_LOW_C_APPEND: list[str] = [
    "日常琐事堆积到无法忽视的程度",
    "截止日期突然提前",
    "忘记了重要事项后才发现",
]

# 高 E 附加触发器
TRIGGERS_HIGH_E_APPEND: list[str] = [
    "被排除在社交活动之外",
    "看到别人聚会的信息自己没有收到邀请",
    "重要的人不回消息",
]

# 高 A（高宜人性）附加触发器
TRIGGERS_HIGH_A_APPEND: list[str] = [
    "和别人发生冲突后久久不能平静",
    "看到他人受委屈比自己受委屈还难受",
]

# 高 E 安全行为附加
SAFETY_HIGH_E_APPEND: list[str] = [
    "立刻联系朋友寻求陪伴",
    "在社交媒体上发动态寻求关注",
]
# 低 E 安全行为附加
SAFETY_LOW_E_APPEND: list[str] = [
    "彻底切断社交联系直到状态恢复",
    "用酒精或食物独自消化情绪",
]


def adjust_triggers_by_ocean(
    triggers: list[str],
    ocean: dict[str, int],
    rng: random.Random,
    n_triggers: int = 3,
) -> list[str]:
    """根据 OCEAN 轮廓调整触发器列表（追加 OCEAN 相关触发）"""
    result = list(triggers)
    n_score = ocean.get("N", 5)
    c_score = ocean.get("C", 5)
    e_score = ocean.get("E", 5)
    a_score = ocean.get("A", 5)

    additions = []

    if n_score >= 7:
        additions.extend(rng.sample(TRIGGERS_HIGH_N_APPEND, min(2, len(TRIGGERS_HIGH_N_APPEND))))
    if c_score <= 4:
        additions.extend(rng.sample(TRIGGERS_LOW_C_APPEND, min(1, len(TRIGGERS_LOW_C_APPEND))))
    if e_score >= 7:
        additions.extend(rng.sample(TRIGGERS_HIGH_E_APPEND, min(1, len(TRIGGERS_HIGH_E_APPEND))))
    if a_score >= 7:
        additions.extend(rng.sample(TRIGGERS_HIGH_A_APPEND, min(1, len(TRIGGERS_HIGH_A_APPEND))))

    result.extend(additions)
    # 如果超出 n_triggers，随机保留
    rng.shuffle(result)
    return result[:n_triggers]


def adjust_safety_behaviors_by_ocean(
    behaviors: list[str],
    ocean: dict[str, int],
    rng: random.Random,
    n_behaviors: int = 2,
) -> list[str]:
    """根据 OCEAN 轮廓调整安全行为列表"""
    result = list(behaviors)
    n_score = ocean.get("N", 5)
    e_score = ocean.get("E", 5)

    additions = []

    if n_score >= 7:
        additions.extend(rng.sample(SAFETY_HIGH_N_APPEND, min(1, len(SAFETY_HIGH_N_APPEND))))
    if e_score >= 7:
        additions.extend(rng.sample(SAFETY_HIGH_E_APPEND, min(1, len(SAFETY_HIGH_E_APPEND))))
    else:
        additions.extend(rng.sample(SAFETY_LOW_E_APPEND, min(1, len(SAFETY_LOW_E_APPEND))))

    result.extend(additions)
    rng.shuffle(result)
    return result[:n_behaviors]


# =====================================================================
# 约束12 — OCEAN→Storr因果链 (约束15)
# =====================================================================

# 高 N+低 E → 内在性创伤（遗弃、拒绝）
STORR_WOUND_HIGH_N_LOW_E_MODIFIERS: list[str] = [
    "内心深处的恐惧——自己不值得被爱这个念头反复浮现",
    "被最亲近的人背叛后留下的隐性创伤",
    "长期的情感孤独塑造了对人际关系的深刻怀疑",
]
# 低 N+高 E → 外部事件创伤
STORR_WOUND_LOW_N_HIGH_E_MODIFIERS: list[str] = [
    "一次意外的事故虽然已过去，但对安全感的冲击持续至今",
    "亲眼目睹的重大变故让世界观发生了不可逆的改变",
    "一次重大但已被处理的挫折，留下的是反思而非沉溺",
]
# 高 O → 意义/存在层面创伤
STORR_WOUND_HIGH_O_MODIFIERS: list[str] = [
    "对世界本质的追问过早降临，存在主义的困惑成了隐形的负担",
    "体验到宇宙的浩瀚与自身的渺小之间的撕裂感",
]
# 高 E → 社交验证型补偿欲望
STORR_DESIRE_HIGH_E_MODIFIER = "成为群体中不可或缺的人，通过他人的认可确认自己的价值"
# 低 E → 安全型补偿欲望
STORR_DESIRE_LOW_E_MODIFIER = "为自己创造一个完全安全、可控的内心世界"
# 高 O → 意义型补偿欲望
STORR_DESIRE_HIGH_O_MODIFIER = "发现/创造某个超越性的理念或作品，让生命有意义"
# 高 A → 关系型补偿欲望
STORR_DESIRE_HIGH_A_MODIFIER = "建立一种绝对和谐、没有冲突的完美关系"


def adjust_storr_wound_by_ocean(
    wound: str,
    ocean: dict[str, int],
    rng: random.Random,
) -> str:
    """根据 OCEAN 轮廓调整 Storr 形成性创伤描述"""
    n_score = ocean.get("N", 5)
    e_score = ocean.get("E", 5)
    o_score = ocean.get("O", 5)

    if n_score >= 7 and e_score <= 4:
        # 替代一条高 N 低 E 风格的创伤
        return rng.choice(STORR_WOUND_HIGH_N_LOW_E_MODIFIERS)
    elif n_score <= 4 and e_score >= 7:
        return rng.choice(STORR_WOUND_LOW_N_HIGH_E_MODIFIERS)
    elif o_score >= 7:
        return rng.choice(STORR_WOUND_HIGH_O_MODIFIERS)

    return wound  # 保留原始诊断版本


def adjust_storr_desire_by_ocean(
    desire: str,
    ocean: dict[str, int],
    rng: random.Random,
) -> str:
    """根据 OCEAN 轮廓调整 Storr 补偿性欲望"""
    e_score = ocean.get("E", 5)
    o_score = ocean.get("O", 5)
    a_score = ocean.get("A", 5)

    candidates = [desire]

    if e_score >= 7:
        candidates.append(STORR_DESIRE_HIGH_E_MODIFIER)
    else:
        candidates.append(STORR_DESIRE_LOW_E_MODIFIER)
    if o_score >= 7:
        candidates.append(STORR_DESIRE_HIGH_O_MODIFIER)
    if a_score >= 7:
        candidates.append(STORR_DESIRE_HIGH_A_MODIFIER)

    return rng.choice(candidates)


def adjust_storr_need_by_ocean(
    need: str,
    ocean: dict[str, int],
    rng: random.Random,
) -> str:
    """根据 OCEAN 轮廓调整 Storr 内在需要"""
    n_score = ocean.get("N", 5)
    e_score = ocean.get("E", 5)

    # 内在需要对 OCEAN 的依赖较弱，主要在基础上加修饰语
    if n_score >= 7:
        return f"{need}（但高神经质让这个人难以真正接受这一点）"
    elif e_score <= 4:
        return f"{need}（需要在一个安全独处的空间里才能开始面对）"
    elif n_score <= 4 and e_score >= 7:
        return f"{need}（好在有足够的社会支持帮助这个人走向这一步）"

    return need


# =====================================================================
# 约束13 — OCEAN→应激模式 (约束16)
# =====================================================================

# N 分数影响应激模式的冻结/退缩权重
# E 分数影响战斗/逃跑方向
STRESS_N_E_MODIFIERS: dict[str, dict[str, list[str]]] = {
    "N_high_E_low": {
        "primary_addition": ["退缩Withdraw（加剧）"],
        "secondary_addition": ["冻结Freeze（加剧）"],
    },
    "N_high_E_high": {
        "primary_addition": ["战斗Fight（冲动性）"],
        "secondary_addition": ["情绪宣泄Emotional_Dump"],
    },
    "N_low_E_high": {
        "primary_addition": ["战斗Fight（策略性）"],
        "secondary_addition": ["问题解决Problem_Solve"],
    },
    "N_low_E_low": {
        "primary_addition": ["冻结Freeze（控制性）"],
        "secondary_addition": ["接纳Acceptance"],
    },
}


def adjust_stress_response_by_ocean(
    stress: dict[str, list[str]],
    ocean: dict[str, int],
    rng: random.Random,
) -> dict[str, list[str]]:
    """根据 OCEAN 的 N 和 E 调整应激模式"""
    result = {
        "primary": list(stress.get("primary", [])),
        "secondary": list(stress.get("secondary", [])),
    }
    n_score = ocean.get("N", 5)
    e_score = ocean.get("E", 5)

    # 确定模式
    n_bin = "high" if n_score >= 7 else ("low" if n_score <= 4 else "mid")
    e_bin = "high" if e_score >= 7 else ("low" if e_score <= 4 else "mid")

    if n_bin != "mid" and e_bin != "mid":
        pattern = f"N_{n_bin}_E_{e_bin}"
        mod = STRESS_N_E_MODIFIERS.get(pattern)
        if mod:
            for add in mod.get("primary_addition", []):
                if add not in result["primary"]:
                    result["primary"].append(add)
            for add in mod.get("secondary_addition", []):
                if add not in result["secondary"]:
                    result["secondary"].append(add)

    return result


# =====================================================================
# 约束14 — OCEAN→外观特征 (约束13)
# =====================================================================

PHYSICAL_APPEARANCE_N_MODIFIERS: dict[str, list[str]] = {
    "high_N": ["神情紧张", "目光躲闪", "眼神疲惫", "面带倦容"],
    "low_N":  ["表情放松", "目光温和", "平静从容", "神态自然"],
}

PHYSICAL_APPEARANCE_C_MODIFIERS: dict[str, list[str]] = {
    "high_C": ["衣着整洁", "穿戴整齐", "一丝不苟"],
    "low_C":  ["衣着随意", "不修边幅", "穿着凌乱"],
}

PHYSICAL_APPEARANCE_O_MODIFIERS: dict[str, list[str]] = {
    "high_O": ["穿着有个人风格", "发型独特", "个性装扮"],
    "low_O":  ["穿着朴素", "打扮保守", "着装低调"],
}


def adjust_physical_appearance_by_ocean(
    appearance: list[str],
    ocean: dict[str, int],
    rng: random.Random,
) -> list[str]:
    """根据 OCEAN 的 N/C/O 调整外貌描述列表"""
    result = list(appearance)
    n_score = ocean.get("N", 5)
    c_score = ocean.get("C", 5)
    o_score = ocean.get("O", 5)

    additions = []

    if n_score >= 7:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_N_MODIFIERS["high_N"]))
    elif n_score <= 4:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_N_MODIFIERS["low_N"]))

    if c_score >= 7:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_C_MODIFIERS["high_C"]))
    elif c_score <= 4:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_C_MODIFIERS["low_C"]))

    if o_score >= 7:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_O_MODIFIERS["high_O"]))
    elif o_score <= 4:
        additions.append(rng.choice(PHYSICAL_APPEARANCE_O_MODIFIERS["low_O"]))

    result.extend(additions)
    return result


# =====================================================================
# 约束15 — OCEAN→隐藏经历 (约束14)
# =====================================================================

HIDDEN_EXPERIENCES_HIGH_N_APPEND: list[str] = [
    "因为害怕被评判而隐瞒了寻求心理帮助的经历",
    "从未告诉过任何人自己曾经有过的自杀念头",
    "在社交媒体上扮演一个完全不同的、快乐的人",
]
HIDDEN_EXPERIENCES_HIGH_O_APPEND: list[str] = [
    "有一些非常小众甚至怪异的爱好，从不展示给别人",
    "暗中在某个领域进行了大量非主流探索，但从未与人分享",
]
HIDDEN_EXPERIENCES_LOW_N_APPEND: list[str] = [
    "有一件微不足道但不好意思承认的小事",
    "其实偷偷羡慕过某种完全不同的生活方式",
]


def adjust_hidden_experiences_by_ocean(
    experiences: list[str],
    ocean: dict[str, int],
    rng: random.Random,
    n: int = 2,
) -> list[str]:
    """根据 OCEAN 的 N 和 O 调整隐藏经历"""
    result = list(experiences)
    n_score = ocean.get("N", 5)
    o_score = ocean.get("O", 5)

    additions = []

    if n_score >= 7:
        additions.extend(rng.sample(HIDDEN_EXPERIENCES_HIGH_N_APPEND, min(1, len(HIDDEN_EXPERIENCES_HIGH_N_APPEND))))
    elif n_score <= 4:
        additions.extend(rng.sample(HIDDEN_EXPERIENCES_LOW_N_APPEND, min(1, len(HIDDEN_EXPERIENCES_LOW_N_APPEND))))

    if o_score >= 7:
        additions.extend(rng.sample(HIDDEN_EXPERIENCES_HIGH_O_APPEND, min(1, len(HIDDEN_EXPERIENCES_HIGH_O_APPEND))))

    result.extend(additions)
    rng.shuffle(result)
    return result[:n]


# =====================================================================
# 约束16 — OCEAN→事件类型分布 (约束3 extension)
# =====================================================================

# OCEAN 轮廓→事件类型的权重调整
# 事件类型: loss / danger / humiliation / entrapment / positive / neutral
OCEAN_EVENT_TYPE_BIAS: dict[str, dict[str, float]] = {
    "N_high_E_low": {
        "loss": 1.8, "humiliation": 1.5,
        "danger": 0.5, "positive": 0.6,
    },
    "N_high_E_high": {
        "loss": 1.3, "humiliation": 1.5, "danger": 1.3,
        "positive": 0.7,
    },
    "N_low_E_high": {
        "danger": 1.5, "positive": 1.5,
        "loss": 0.5, "entrapment": 0.4,
    },
    "N_low_E_low": {
        "entrapment": 1.5, "positive": 1.3,
        "danger": 0.5, "humiliation": 0.5,
    },
    "C_low": {
        "entrapment": 0.5,
    },
    "C_high": {
        "entrapment": 1.3,
    },
}


def select_event_types_by_ocean(
    base_types: list[str],
    ocean: dict[str, int],
    rng: random.Random,
    n_events: int = 5,
) -> list[str]:
    """根据 OCEAN 轮廓影响事件类型分布的加权采样

    Args:
        base_types: 基础事件类型列表（已有抽样结果中的类型序列）
        ocean: OCEAN 五维分数
        rng: 随机数生成器
        n_events: 需要的事件数

    Returns:
        调整后的事件类型列表（部分替换）
    """
    if not base_types:
        return base_types

    pattern = classify_ocean_pattern(ocean)
    bias = OCEAN_EVENT_TYPE_BIAS.get(pattern, {})

    # 对每个事件类型施加权重
    result = list(base_types)
    for i, etype in enumerate(result):
        if etype in bias:
            # 用加权决定是否保留原类型或替换
            keep_weight = 1.0
            replace_weight = bias.get(etype, 1.0)
            if replace_weight < 0.5:
                # 低权重类型有一定概率被替换
                if rng.random() > keep_weight / (keep_weight + 1.0):
                    # 找替代类型（从权重高的类型中选）
                    candidates = [t for t in bias if bias[t] >= 1.3 and t != etype]
                    if candidates:
                        result[i] = rng.choice(candidates)

    return result
