"""
主生成逻辑 — 整合四大模块 + 诊断本体，生成完整 Persona

用法：
  from core import generate_persona
  p = generate_persona(primary_diagnosis="重度抑郁障碍")
  print(p.system_prompt)

=========================================================================
Persona 完整字段
=========================================================================
  id                  — 唯一标识符
  label               — 可读标签（如 "depressive_001"）
  age                 — 当前年龄
  gender              — 性别
  occupation          — 职业中类名
  occupation_code     — 职业中类编码
  education           — 教育程度
  locale              — 地区（城市/农村/城镇，legacy 标签）
  locale_canonical    — 地区 canonical 值（urban/town/rural，Human Ontology v1.3）
  marital_status      — 婚姻状况
  primary_diagnosis   — 主诊断（中文）
  primary_diagnosis_en— 主诊断（英文）
  comorbidities       — 共病列表
  ocean               — OCEAN 五维分数
  ocean_description   — OCEAN 自然语言描述
  personality_tags    — 性格标签列表
  cognitive_styles    — 认知风格
  coping_styles       — 应对方式
  social_relations    — 社会关系特征（v2 增强）
  values_beliefs      — 价值观与信念（v2 增强）
  communication_style — 沟通风格（v2 增强）
  lifestyle_habits    — 生活习惯（v2 增强）
  skills_abilities    — 能力技能（v2 增强）
  erikson_stage       — Erikson 心理发展阶段（v2 增强）
  core_desire         — 核心欲望（Egri）
  core_fear           — 核心恐惧（Egri）
  dysfunctional_beliefs— 功能障碍信念（CBT 认知三角）
  stress_pattern      — 压力应激模式
  formative_wound     — 形成性创伤（Storr Wound）
  compensatory_desire — 补偿性欲望（Storr Desire）
  storr_need          — 内在需要（Storr Need）
  arc_type            — 角色弧线类型（Weiland：positive/negative/flat）
  arc_description     — 角色弧线名称与轨迹描述
  triggers            — 症状触发因素
  safety_behaviors    — 安全行为
  physical_appearance — 外貌描述列表
  hidden_experiences  — 隐藏经历列表
  life_events         — 生活事件时间线
  current_status      — 当前状态摘要
  system_prompt       — 可用于 LLM 评估的完整 System Prompt
=========================================================================
"""

import json
import random
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

from .occupations import (
    OCCUPATIONS,
    get_filtered_occupations,
    get_default_occupation_weights,
    OccupationCategory,
)
from .personality import (
    OCEAN_DIMENSIONS,
    sample_ocean,
    sample_tags_from_ocean,
    describe_ocean,
    sample_cognitive_and_coping,
    sample_core_desires_fears,
    sample_dysfunctional_beliefs,
    sample_stress_response,
    format_stress_response,
    sample_formative_wound,
    sample_compensatory_desire,
    sample_storr_need,
    sample_arc_type,
    _get_diagnosis_key,
    STORR_WOUNDS,
    # --- 6 个 MECE 新维度（v2 增强） ---
    sample_social_relations,
    sample_values_beliefs,
    sample_communication_style,
    sample_lifestyle_habits,
    sample_skills_abilities,
    sample_erikson_stage,
)
from .events import (
    sample_events_for_persona,
    format_events_timeline,
    LifeEvent,
    DOMAIN_CN,
    STAGE_CN,
)
from .triggers import (
    sample_triggers,
    sample_safety_behaviors,
    sample_physical_appearance,
    sample_hidden_experiences,
)
from .stratification import (
    sample_age_from_bands,
    sample_gender_for_diagnosis,
    sample_education_for_diagnosis,
)
from .archetypes import (
    sample_archetype,
    has_archetypes,
    sample_from_archetype,
    apply_archetype_tone,
    apply_ocean_bias,
    get_archetypes,
)
from .cross_constraints import (
    adjust_cognitive_coping_by_ocean,
    adjust_event_ratios_by_ocean,
    adjust_occupation_weights_by_ocean,
    adjust_social_relations_by_ocean,
    filter_occupations_by_education,
)
from .human_ontology import map_legacy_locale


# =====================================================================
# 路径配置
# =====================================================================

_DIAGNOSIS_ONTOLOGY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "diagnosis_ontology.json",
)


# =====================================================================
# 诊断本体缓存
# =====================================================================

_DIAGNOSIS_ONTOLOGY = None

def _load_diagnosis_ontology(path: str | None = None) -> dict:
    """加载诊断本体 JSON"""
    global _DIAGNOSIS_ONTOLOGY
    if _DIAGNOSIS_ONTOLOGY is not None:
        return _DIAGNOSIS_ONTOLOGY

    fp = path or _DIAGNOSIS_ONTOLOGY_PATH
    try:
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # 如果本体不可用，返回最小 Fallback
        _DIAGNOSIS_ONTOLOGY = {"diagnoses": []}
        return _DIAGNOSIS_ONTOLOGY

    diagnoses = data.get("diagnoses", [])
    # 如果没有 "diagnoses" 键，尝试其他顶层结构
    if not diagnoses:
        for key in ["icd11_diagnoses", "items", "records"]:
            if key in data:
                diagnoses = data[key]
                break
        # 如果还是空，可能整个 JSON 就是数组
        if not diagnoses and isinstance(data, list):
            diagnoses = data

    _DIAGNOSIS_ONTOLOGY = {"diagnoses": diagnoses}
    return _DIAGNOSIS_ONTOLOGY


def _parse_diagnosis_info(diag: dict) -> dict:
    """从诊断本体的单个条目提取关键信息"""
    # ICD-11 代码
    icd_code = diag.get("icd11_code", diag.get("code", diag.get("icd_code", "")))

    # 中文/英文名称
    name_cn = diag.get("name_cn", diag.get("chinese_name", diag.get("cn_name", "")))
    name_en = diag.get("name_en", diag.get("english_name", diag.get("en_name", "")))
    if not name_cn:
        name_cn = diag.get("name", "")

    # 发病年龄范围
    onset = diag.get("typical_onset_age", diag.get("onset_age", {}))
    if isinstance(onset, dict):
        onset_min = onset.get("min", onset.get("start", 0))
        onset_max = onset.get("max", onset.get("end", 99))
    else:
        onset_min, onset_max = 0, 99

    # 性别比
    gender_ratio = diag.get("gender_ratio", diag.get("sex_ratio", "1:1"))

    # 共病
    comorbidities = diag.get("common_comorbidities", diag.get("comorbidities", []))
    if isinstance(comorbidities, dict):
        comorbidities = list(comorbidities.keys())

    # 严重度维度
    severity = diag.get("severity_dimensions", diag.get("severity", None))

    return {
        "icd_code": icd_code,
        "name_cn": name_cn,
        "name_en": name_en,
        "onset_min": onset_min,
        "onset_max": onset_max,
        "gender_ratio": gender_ratio,
        "comorbidities": comorbidities,
        "severity": severity,
    }


# =====================================================================
# Persona 数据类型
# =====================================================================

@dataclass
class Persona:
    """完整的 Persona 对象"""
    id: str                                              # 唯一标识
    label: str                                           # 可读标签
    age: int                                             # 当前年龄
    gender: str                                          # 性别
    occupation: str                                      # 职业中类名
    occupation_code: str                                 # 职业中类编码
    education: str                                       # 教育程度
    locale: str                                          # 地区（legacy 标签）：城市/农村/城镇
    marital_status: str                                  # 婚姻状况

    primary_diagnosis: str                               # 主诊断（中文）
    primary_diagnosis_en: str                            # 主诊断（英文）
    locale_canonical: str = ""                           # 地区 canonical 值（Human Ontology）：urban/town/rural
    comorbidities: list[str] = field(default_factory=list)  # 共病列表

    # --- 人设元类型（Archetype Grid，v1.2 新增） ---
    archetype_key: str = ""                              # 元类型英文键（如 "hidden_sufferer"）
    archetype_name: str = ""                             # 元类型中文名（如 "隐忍承担型"）
    archetype_one_liner: str = ""                        # 元类型一句话描述

    # --- 性格（已有） ---
    ocean: dict[str, int] = field(default_factory=dict)  # OCEAN 五维分数
    ocean_description: str = ""                          # OCEAN 自然语言描述
    personality_tags: list[str] = field(default_factory=list)  # 性格标签
    cognitive_styles: list[str] = field(default_factory=list)  # 认知风格
    coping_styles: list[str] = field(default_factory=list)    # 应对方式

    # --- MECE 六维度扩展（v2 增强） ---
    social_relations: dict = field(default_factory=dict)       # 社会关系特征
    values_beliefs: dict = field(default_factory=dict)         # 价值观与信念
    communication_style: dict = field(default_factory=dict)    # 沟通风格
    lifestyle_habits: dict = field(default_factory=dict)       # 生活习惯
    skills_abilities: dict = field(default_factory=dict)       # 能力技能
    erikson_stage: dict = field(default_factory=dict)          # Erikson 发展阶段

    # --- Egri 心理维增强 ---
    core_desire: str = ""                                # 核心欲望
    core_fear: str = ""                                  # 核心恐惧
    dysfunctional_beliefs: dict[str, str] = field(default_factory=dict)  # 功能障碍信念（about_self / about_world / about_future）
    stress_pattern: dict[str, list[str]] = field(default_factory=dict)   # 压力应激模式（primary / secondary）

    # --- Storr 叙事因果链 ---
    formative_wound: str = ""                            # 形成性创伤（Wound）
    compensatory_desire: str = ""                        # 补偿性欲望（Storr Desire）
    storr_need: str = ""                                 # 内在需要（Need）

    # --- Weiland 角色弧线 ---
    arc_type: str = ""                                   # 弧线类型：positive/negative/flat
    arc_description: str = ""                            # 弧线名称+轨迹描述

    # --- 触发器系统 ---
    triggers: list[str] = field(default_factory=list)    # 症状触发器
    safety_behaviors: list[str] = field(default_factory=list)  # 安全行为

    # --- 生理 & 隐藏经历 ---
    physical_appearance: list[str] = field(default_factory=list)  # 外貌描述
    hidden_experiences: list[str] = field(default_factory=list)   # 隐藏经历

    # --- 生活事件 & 状态 ---
    life_events: list[LifeEvent] = field(default_factory=list)      # 生活事件
    life_events_text: str = ""                              # 格式化事件文本

    current_status: str = ""                             # 当前状态

    system_prompt: str = ""                              # 组装后的 System Prompt

    # 额外保留的原始诊断信息
    _diagnosis_info: dict = field(default_factory=dict)


# =====================================================================
# PersonaGenerator 主类
# =====================================================================

class PersonaGenerator:
    """Persona 生成器

    通过构造函数配置参数，调用 generate() 生成单个 Persona，
    调用 batch() 批量生成。
    """

    def __init__(
        self,
        rng_seed: int | None = None,
        # --- 职业参数 ---
        occupation_major_weights: dict[int, float] | None = None,
        occupation_major_filter: list[int] | None = None,
        occupation_stress_filter: list[str] | None = None,
        # --- 性格参数 ---
        personality_tag_count: int = 4,
        cognitive_count: int = 2,
        coping_count: int = 2,
        # --- 事件参数 ---
        event_count: int = 6,
        event_positive_ratio: float = 0.3,
        event_negative_ratio: float = 0.4,
        event_neutral_ratio: float = 0.3,
        # --- 触发器参数 ---
        trigger_count: int = 3,
        safety_behavior_count: int = 2,
        # --- 隐藏经历参数 ---
        hidden_experience_count: int = 2,
        # --- 人口学参数 ---
        age_range: tuple[int, int] = (18, 75),
        healthy_ratio: float = 0.2,     # 健康人群占生成总体的比例
    ):
        self.rng = random.Random(rng_seed)
        self.occupation_major_weights = occupation_major_weights or get_default_occupation_weights()
        self.occupation_major_filter = occupation_major_filter
        self.occupation_stress_filter = occupation_stress_filter
        self.personality_tag_count = personality_tag_count
        self.cognitive_count = cognitive_count
        self.coping_count = coping_count
        self.event_count = event_count
        self.event_positive_ratio = event_positive_ratio
        self.event_negative_ratio = event_negative_ratio
        self.event_neutral_ratio = event_neutral_ratio
        self.trigger_count = trigger_count
        self.safety_behavior_count = safety_behavior_count
        self.hidden_experience_count = hidden_experience_count
        self.age_range = age_range
        self.healthy_ratio = healthy_ratio

        # 加载诊断本体
        self.diagnosis_ontology = _load_diagnosis_ontology()
        self._diagnosis_cache: list[dict] = []  # parsed diagnosis info cache

        # 初始化诊断缓存
        self._build_diagnosis_cache()

        # 计数器
        self._counter = 0

    # ======================== 初始化 ========================

    def _build_diagnosis_cache(self):
        """解析诊断本体，构建可搜索的诊断缓存"""
        diagnoses = self.diagnosis_ontology.get("diagnoses", [])
        for diag in diagnoses:
            info = _parse_diagnosis_info(diag)
            if info["name_cn"]:
                self._diagnosis_cache.append(info)

        # 如果没有找到诊断，添加默认
        if not self._diagnosis_cache:
            # 创建有代表性的诊断列表
            default_diagnoses = [
                {"name_cn": "重度抑郁障碍", "name_en": "Major Depressive Disorder", "icd_code": "6A70"},
                {"name_cn": "广泛性焦虑障碍", "name_en": "Generalized Anxiety Disorder", "icd_code": "6B00"},
                {"name_cn": "社交焦虑障碍", "name_en": "Social Anxiety Disorder", "icd_code": "6B04"},
                {"name_cn": "精神分裂症", "name_en": "Schizophrenia", "icd_code": "6A20"},
                {"name_cn": "双相I型障碍", "name_en": "Bipolar I Disorder", "icd_code": "6A60"},
                {"name_cn": "强迫症", "name_en": "Obsessive-Compulsive Disorder", "icd_code": "6B20"},
                {"name_cn": "注意缺陷/多动障碍", "name_en": "ADHD", "icd_code": "6A05"},
                {"name_cn": "创伤后应激障碍", "name_en": "PTSD", "icd_code": "6B40"},
                {"name_cn": "边缘型人格障碍", "name_en": "Borderline Personality Disorder", "icd_code": "6D10"},
                {"name_cn": "酒精使用障碍", "name_en": "Alcohol Use Disorder", "icd_code": "6C40"},
                {"name_cn": "神经性厌食症", "name_en": "Anorexia Nervosa", "icd_code": "6B80"},
                {"name_cn": "失眠障碍", "name_en": "Insomnia Disorder", "icd_code": "7A00"},
            ]
            for dd in default_diagnoses:
                info = _parse_diagnosis_info(dd)
                self._diagnosis_cache.append(info)

    # ======================== 人口学采样（委托到 stratification） ========================

    def _sample_gender(self, diagnosis_key: str) -> str:
        """根据诊断的流行病学性别比加权采样"""
        return sample_gender_for_diagnosis(diagnosis_key, rng=self.rng)

    def _sample_age(self, diagnosis_key: str) -> int:
        """从普查校准的年龄带中按权重采样（诊断约束有效带）"""
        age, _ = sample_age_from_bands(diagnosis_key, rng=self.rng)
        return age

    def _sample_education(self, diagnosis_key: str, age: int) -> str:
        """根据诊断+年龄+普查分布加权采样教育程度"""
        return sample_education_for_diagnosis(diagnosis_key, age, rng=self.rng)

    def _sample_marital_status(self, age: int) -> str:
        """根据年龄、随机采样婚姻状况"""
        if age < 20:
            return self.rng.choice(["未婚"])
        elif age < 30:
            return self.rng.choice(["未婚", "已婚", "未婚"])
        elif age < 45:
            return self.rng.choice(["已婚", "未婚", "离异", "已婚", "已婚", "分居"])
        elif age < 60:
            return self.rng.choice(["已婚", "离异", "丧偶", "已婚", "分居", "再婚"])
        else:
            return self.rng.choice(["已婚", "丧偶", "离异", "再婚", "未婚"])

    def _sample_locale(self) -> str:
        return self.rng.choice(["城市", "农村", "城镇"])

    def _sample_occupation(self, stress_preference: str | None = None,
                           occ_pool: list | None = None,
                           major_weights_override: dict[int, float] | None = None,
                           ) -> OccupationCategory:
        """按大类权重采样职业中类

        如果指定 stress_preference，倾向于匹配压力水平的中类
        occ_pool: 可选，过滤后的职业池
        major_weights_override: 可选，覆盖的大类权重
        """
        # 优先使用大类权重
        majors = list(major_weights_override or self.occupation_major_weights)
        weights = [(major_weights_override or self.occupation_major_weights)[m] for m in majors]
        major = self.rng.choices(majors, weights=weights, k=1)[0]

        # 在该大类内找中类
        pool = occ_pool or OCCUPATIONS
        pool_by_major = [o for o in pool if o.major_category == major]
        if not pool_by_major:
            pool_by_major = [o for o in OCCUPATIONS if o.major_category == major]
        if not pool_by_major:
            pool_by_major = OCCUPATIONS

        if stress_preference and self.rng.random() < 0.6:
            stress_pool = [o for o in pool if o.stress_level == stress_preference]
            if stress_pool:
                return self.rng.choice(stress_pool)

        return self.rng.choice(pool)

    # ======================== 诊断采样 ========================

    def _sample_primary_diagnosis(self) -> tuple[dict, str]:
        """从诊断本体采样主诊断
        
        Returns:
            (diagnosis_info, diagnosis_key)
        """
        is_healthy = self.rng.random() < self.healthy_ratio

        if is_healthy:
            return {
                "name_cn": "无精神障碍（健康）",
                "name_en": "No Mental Disorder (Healthy)",
                "icd_code": "",
                "onset_min": 0,
                "onset_max": 99,
                "gender_ratio": "1:1",
                "comorbidities": [],
                "severity": None,
            }, "healthy"

        # 从诊断缓存中随机选一个
        info = self.rng.choice(self._diagnosis_cache)
        key = _get_diagnosis_key(info["name_en"] or info["name_cn"])
        return info, key

    def _sample_comorbidities(self, primary_info: dict,
                               primary_key: str,
                               max_comorbid: int = 2) -> list[dict]:
        """采样共病"""
        if primary_key == "healthy":
            return []

        existing_comorbid_names = set()
        existing_comorbid_names.add(primary_info["name_cn"])
        result = []

        # 从诊断本体记录的共病中采样
        ontology_comorbid_names = primary_info.get("comorbidities", [])
        comorbid_candidates = []

        if ontology_comorbid_names:
            for cn_name in ontology_comorbid_names:
                if cn_name not in existing_comorbid_names:
                    comorbid_candidates.append(cn_name)

        # 也随机从缓存中抽取
        for info in self._diagnosis_cache:
            if info["name_cn"] not in existing_comorbid_names:
                if info["name_cn"] not in comorbid_candidates:
                    comorbid_candidates.append(info["name_cn"])

        n = self.rng.randint(0, min(max_comorbid, len(comorbid_candidates)))
        if n == 0:
            return []

        selected_names = self.rng.sample(comorbid_candidates, n)
        for name in selected_names:
            # 从缓存找对应信息
            info = {"name_cn": name, "name_en": name, "icd_code": ""}
            for ci in self._diagnosis_cache:
                if ci["name_cn"] == name:
                    info = ci
                    break
            result.append(info)

        return result

    # ======================== 状态摘要 ========================

    def _generate_current_status(self, persona_dict: dict) -> str:
        """根据 Persona 信息生成当前状态摘要"""
        diagnosis = persona_dict["primary_diagnosis"]
        ocean = persona_dict["ocean"]
        events = persona_dict.get("life_events", [])

        parts = []

        if diagnosis != "无精神障碍（健康）":
            severity = "轻度" if ocean.get("N", 5) < 6 else "中度" if ocean.get("N", 5) < 8 else "重度"
            parts.append(f"当前处于{severity}{diagnosis}发作期" if self.rng.random() < 0.6
                         else f"{diagnosis}缓解期，但仍有一定残余症状" if self.rng.random() < 0.5
                         else f"诊断为{diagnosis}，目前正在接受治疗")
        else:
            parts.append("目前精神状态健康，无明显心理困扰")

        # 近况
        recent_events = [e for e in events if e.stage in ["adulthood", "mid_older"]]
        if recent_events:
            last_event = recent_events[-1] if len(recent_events) < 4 else recent_events[0]
            if last_event.valence == "negative":
                parts.append(f"近期经历了「{last_event.name_cn}」事件")
            elif last_event.valence == "positive":
                parts.append(f"近期经历了「{last_event.name_cn}」，整体状态尚可")

        parts.append(f"当前{Ocean_to_work_status(ocean)}")

        return "，".join(parts)


    # ======================== System Prompt 组装 ========================

    def _build_system_prompt(self, p: Persona) -> str:
        """组装可用于 LLM 评估的完整 System Prompt"""
        lines = []

        # 基本信息
        lines.append("# Persona 档案")
        lines.append("")

        gender_noun = "男性" if p.gender == "男" else "女性"
        lines.append(f"## 基本信息")
        lines.append(f"- 年龄：{p.age}岁")
        lines.append(f"- 性别：{gender_noun}")
        lines.append(f"- 职业：{p.occupation}")
        lines.append(f"- 教育程度：{p.education}")
        lines.append(f"- 居住地：{p.locale}")
        lines.append(f"- 婚姻状况：{p.marital_status}")

        # 诊断信息
        if p.primary_diagnosis != "无精神障碍（健康）":
            lines.append(f"\n## 精神科诊断")
            lines.append(f"- 主诊断：{p.primary_diagnosis}")
            if p.comorbidities:
                lines.append(f"- 共病诊断：{'、'.join(p.comorbidities)}")
        else:
            lines.append(f"\n## 精神状态")
            lines.append(f"- 无精神障碍，属于健康人群")

        # 人设元类型（Archetype Grid，v1.2）
        if p.archetype_name:
            lines.append(f"\n## 人设元类型（本角色的心理内核组织方式）")
            lines.append(f"- 类型：{p.archetype_name}")
            if p.archetype_one_liner:
                lines.append(f"- 特征：{p.archetype_one_liner}")

        # 性格特征
        lines.append(f"\n## 性格特征")
        lines.append(f"- 大五人格(OCEAN)：{p.ocean_description}")
        if p.personality_tags:
            lines.append(f"- 性格标签：{'，'.join(p.personality_tags)}")
        if p.cognitive_styles:
            lines.append(f"- 典型认知风格：{'、'.join(p.cognitive_styles)}")
        if p.coping_styles:
            lines.append(f"- 常用应对方式：{'、'.join(p.coping_styles)}")

        # MECE 六维度
        if p.social_relations:
            sr = p.social_relations
            lines.append(f"\n## 社会关系")
            lines.append(f"- 家庭关系：{sr.get('family', '')}")
            lines.append(f"- 友谊模式：{sr.get('friends', '')}")
            lines.append(f"- 社交网络规模：{sr.get('network_size', '')}")
            templates = sr.get('templates', [])
            if templates:
                lines.append(f"- 典型社交语句：{'；'.join(templates)}")

        if p.values_beliefs:
            vb = p.values_beliefs
            lines.append(f"\n## 价值观与信念")
            lines.append(f"- 道德基础倾向：{vb.get('moral_foundation', '')}")
            lines.append(f"- 核心价值观：{'、'.join(vb.get('core_values', []))}")
            taboos = vb.get('taboo', [])
            if taboos:
                lines.append(f"- 心理禁忌：{'、'.join(taboos)}")
            lines.append(f"- 世界观：{vb.get('worldview', '')}")

        if p.communication_style:
            cs = p.communication_style
            lines.append(f"\n## 沟通风格")
            lines.append(f"- 健谈度：{cs.get('talkative', '')}/10")
            lines.append(f"- 直接度：{cs.get('directness', '')}/10")
            lines.append(f"- 情绪表达度：{cs.get('emotional_expression', '')}/10")
            lines.append(f"- 正式度：{cs.get('formality', '')}/10")
            phrases = cs.get('typical_phrases', [])
            if phrases:
                lines.append(f"- 常用语：{'；'.join(phrases)}")

        if p.lifestyle_habits:
            lh = p.lifestyle_habits
            lines.append(f"\n## 生活习惯")
            lines.append(f"- 日常节奏：{lh.get('daily_routine', '')}")
            lines.append(f"- 饮食特点：{lh.get('diet', '')}")
            lines.append(f"- 睡眠模式：{lh.get('sleep', '')}")
            hobbies = lh.get('hobbies', [])
            if hobbies:
                lines.append(f"- 兴趣爱好：{'、'.join(hobbies)}")

        if p.skills_abilities:
            sa = p.skills_abilities
            lines.append(f"\n## 能力与技能")
            lines.append(f"- 认知能力：{sa.get('cognitive', '')}")
            talents = sa.get('talents', [])
            if talents:
                lines.append(f"- 天赋特长：{'、'.join(talents)}")
            vocational = sa.get('vocational', [])
            if vocational:
                lines.append(f"- 擅长领域：{'、'.join(vocational)}")
            lines.append(f"- 日常生活能力：{sa.get('daily_living', '')}")

        if p.erikson_stage:
            es = p.erikson_stage
            lines.append(f"\n## 心理发展阶段（Erikson）")
            lines.append(f"- 当前阶段：{es.get('stage', '')}")
            lines.append(f"- 核心冲突：{es.get('crisis', '')}")
            lines.append(f"- 解决状态：{es.get('resolution', '')}")
            if es.get('strength'):
                lines.append(f"- 正向品质：{es['strength']}")

        # 核心动机（Egri）
        if p.core_desire or p.core_fear:
            lines.append(f"\n## 核心动机")
            if p.core_desire:
                lines.append(f"- 最深层的渴望：{p.core_desire}")
            if p.core_fear:
                lines.append(f"- 最深层的恐惧：{p.core_fear}")

        # 叙事因果链（Storr）—— Lie 展开为 CBT 认知三角（about_self / about_world / about_future）
        if p.formative_wound or p.compensatory_desire or p.storr_need:
            lines.append(f"\n## 人物叙事链（造成今日之他的因果路径）")
            if p.formative_wound:
                lines.append(f"- **形成性创伤**：{p.formative_wound}")
            if p.dysfunctional_beliefs:
                lines.append(f"- **错误信念**（关于自己/世界/未来）：")
                label_map = {"about_self": "关于自己", "about_world": "关于世界", "about_future": "关于未来"}
                for key in ["about_self", "about_world", "about_future"]:
                    val = p.dysfunctional_beliefs.get(key)
                    if val:
                        lines.append(f"  - {label_map[key]}：{val}")
            if p.compensatory_desire:
                lines.append(f"- **补偿性欲望（想要）**：{p.compensatory_desire}")
            if p.storr_need:
                lines.append(f"- **内在需要（真正需要）**：{p.storr_need}")

        # 角色弧线（Weiland）
        if p.arc_type:
            lines.append(f"\n## 角色弧线（K.M. Weiland — Creating Character Arcs）")
            arc_label = {
                "positive": "正弧（Positive Change Arc）",
                "negative": "负弧（Negative Change Arc）",
                "flat": "平坦弧（Flat Arc）",
            }.get(p.arc_type, p.arc_type)
            lines.append(f"- 弧线类型：{arc_label}")
            if p.arc_description:
                lines.append(f"- 轨迹描述：{p.arc_description}")
            lines.append(f"- 角色的潜力方向：在叙事中沿着这条弧线前进，ta 要么成长（正弧）、要么堕落（负弧）、要么坚持自我并影响周围（平坦弧）")

        # 压力应激模式
        if p.stress_pattern:
            lines.append(f"\n## 压力应激模式")
            primary = p.stress_pattern.get("primary", [])
            secondary = p.stress_pattern.get("secondary", [])
            if primary:
                lines.append(f"- 主要应激反应：{'、'.join(primary)}")
            if secondary:
                lines.append(f"- 次要应激反应：{'、'.join(secondary)}")

        # 触发器
        if p.triggers:
            lines.append(f"\n## 症状触发因素")
            for t in p.triggers:
                lines.append(f"- {t}")

        # 安全行为
        if p.safety_behaviors:
            lines.append(f"\n## 安全行为（应对症状的策略）")
            for b in p.safety_behaviors:
                lines.append(f"- {b}")

        # 外貌
        if p.physical_appearance:
            lines.append(f"\n## 外貌特征")
            lines.append(f"{'，'.join(p.physical_appearance)}。")

        # 隐藏经历
        if p.hidden_experiences:
            lines.append(f"\n## 隐藏经历（他/她不会主动告诉别人的事）")
            for h in p.hidden_experiences:
                lines.append(f"- {h}")

        # 人生经历
        if p.life_events_text:
            lines.append(f"\n## 人生经历")
            lines.append(f"以下是从出生到现在的关键事件：")
            lines.append(p.life_events_text)

        # 当前状态
        lines.append(f"\n## 当前状态")
        lines.append(p.current_status)

        # 评估指示
        lines.append(f"\n## 评估指示")
        if p.primary_diagnosis != "无精神障碍（健康）":
            lines.append("请以精神科临床评估的方式，对上述人物进行访谈和量表施测。")
            lines.append("评估目标：验证诊断、评估当前严重程度、了解功能损害。")
        else:
            lines.append("请以精神科临床评估的方式，对上述健康人群代表进行访谈。")
            lines.append("评估目标：确认无精神障碍、了解心理韧性和应对资源。")

        return "\n".join(lines)

    # ======================== 单次生成 ========================

    def generate(
        self,
        primary_diagnosis: str | None = None,
        *,
        gender: str | None = None,
        age: int | None = None,
        education: str | None = None,
        locale: str | None = None,
        marital_status: str | None = None,
    ) -> Persona:
        """生成一个完整 Persona

        Args:
            primary_diagnosis: 主诊断中文名，None 则随机
            gender: 固定性别，None 则随机采样
            age: 固定年龄，None 则随机采样
            education: 固定教育程度，None 则随机采样
            locale: 固定地区，None 则随机采样
            marital_status: 固定婚姻状况，None 则随机采样
        """
        self._counter += 1

        # ---- 1. 采样诊断 ----
        if primary_diagnosis:
            # 如果指定了诊断，尝试在缓存中找到
            info = None
            for ci in self._diagnosis_cache:
                if primary_diagnosis in ci["name_cn"] or primary_diagnosis in ci["name_en"]:
                    info = ci
                    break
            if info is None:
                # 找不到，创建虚拟诊断
                info = {
                    "name_cn": primary_diagnosis,
                    "name_en": primary_diagnosis,
                    "icd_code": "",
                    "onset_min": 10,
                    "onset_max": 50,
                    "gender_ratio": "1:1",
                    "comorbidities": [],
                    "severity": None,
                }
            diag_info = info
            diag_key = _get_diagnosis_key(diag_info.get("name_en", diag_info["name_cn"]))
        else:
            diag_info, diag_key = self._sample_primary_diagnosis()

        # ---- 2. 人口学（可选覆盖） ----
        # 委托到 stratification 模块：流行病学性别比 + 普查校准年龄带 + 诊断-教育联动
        age = age if age is not None else self._sample_age(diag_key)
        gender = gender if gender is not None else self._sample_gender(diag_key)
        education = education if education is not None else self._sample_education(diag_key, age)
        marital = marital_status if marital_status is not None else self._sample_marital_status(age)
        locale = locale if locale is not None else self._sample_locale()
        locale_canonical = (map_legacy_locale(locale) or {}).get("value", "")

        # ---- 3. 共病（先做，OCEAN 需要共病信息）----
        comorb_infos = self._sample_comorbidities(diag_info, diag_key)
        comorb_keys = [_get_diagnosis_key(ci.get("name_en", ci["name_cn"])) for ci in comorb_infos]
        comorb_names = [ci["name_cn"] for ci in comorb_infos]

        # ---- 3b. 人设元类型（Archetype Grid，v1.2）----
        # 型决定心理内核（wound→desire→need 因果链），诊断只决定症状学外壳。
        # 未定义网格的诊断返回 None，回退旧采样逻辑（向后兼容）。
        archetype = sample_archetype(diag_key, rng=self.rng)

        # ---- 4. OCEAN 性格（先做，职业/认知/事件/社交都依赖它）----
        ocean = sample_ocean(
            diag_info.get("name_en", diag_info["name_cn"]),
            comorbidity_names=[ci.get("name_en", ci["name_cn"]) for ci in comorb_infos],
            rng=self.rng,
        )
        # v1.2: 施加 archetype 的 OCEAN 偏置（型优先，使同诊断不同型人格轮廓可区分）
        ocean = apply_ocean_bias(ocean, archetype, self.rng)
        ocean_desc = describe_ocean(ocean)
        tags = sample_tags_from_ocean(ocean, count=self.personality_tag_count, rng=self.rng)

        # ---- 5. 职业（OCEAN→职业加权 + 教育→职业过滤）----
        stress_lookup = {
            "depressive": "high", "anxiety": "high", "psychotic": "high",
            "bipolar": "medium", "ocd": "medium", "adhd": "low",
            "ptsd": "high", "substance": "low", "healthy": "medium",
        }
        stress_pref = stress_lookup.get(diag_key, None)

        # 教育→职业硬过滤（约束5）
        occ_filtered, edu_adj_weights = filter_occupations_by_education(
            education, OCCUPATIONS, self.occupation_major_weights,
        )
        # OCEAN→职业大类加权（约束3）
        if edu_adj_weights is not None:
            occ_weights = edu_adj_weights
        else:
            occ_weights = dict(self.occupation_major_weights)
        occ_weights = adjust_occupation_weights_by_ocean(occ_weights, ocean)

        occ = self._sample_occupation(
            stress_pref,
            occ_pool=occ_filtered,
            major_weights_override=occ_weights,
        )

        # ---- 6. 认知与应对（OCEAN→认知应对加权，约束1）----
        raw_cognitive, raw_coping = sample_cognitive_and_coping(
            diag_info.get("name_en", diag_info["name_cn"]),
            rng=self.rng,
            n_cognitive=self.cognitive_count,
            n_coping=self.coping_count,
        )
        # 用 OCEAN 轮廓对认知/应对做加权重采样
        cognitive, coping = adjust_cognitive_coping_by_ocean(
            raw_cognitive, raw_coping, ocean, self.rng,
            n_cognitive=self.cognitive_count,
            n_coping=self.coping_count,
        )

        # ---- 5b. MECE 六维度（v2 增强）----
        # v1.2: 先用 archetype 基调覆盖诊断默认（型专属优先，列表字段合并去重）
        _raw_social = sample_social_relations(diag_key, rng=self.rng)
        _raw_social = apply_archetype_tone(_raw_social, archetype, "social_tone")
        # OCEAN→社交关系调整（约束4）
        social_relations = adjust_social_relations_by_ocean(_raw_social, ocean, self.rng)
        _raw_values = sample_values_beliefs(diag_key, rng=self.rng, ocean=ocean)
        values_beliefs = apply_archetype_tone(_raw_values, archetype, "values_tone")
        communication_style = sample_communication_style(diag_key, rng=self.rng, ocean=ocean)
        lifestyle_habits = sample_lifestyle_habits(diag_key, rng=self.rng, ocean=ocean)
        skills_abilities = sample_skills_abilities(diag_key, rng=self.rng, ocean=ocean)
        erikson_stage = sample_erikson_stage(diag_key, rng=self.rng, ocean=ocean)

        # ---- 6. Egri 核心欲望/恐惧 ----
        desires_fears = sample_core_desires_fears(diag_key, rng=self.rng)
        # v1.2: archetype 专属的核心欲望/恐惧优先
        if archetype:
            if archetype.get("core_desire"):
                desires_fears["core_desire"] = archetype["core_desire"]
            if archetype.get("core_fear"):
                desires_fears["core_fear"] = archetype["core_fear"]

        # ---- 6b. Storr 叙事因果链 ----
        # v1.2: 优先使用 archetype 专属的 wound/desire/need 池。
        # 注意不传 ocean 给 adjust_*_by_ocean —— 那些函数在极端 OCEAN 下会
        # **整体替换**文本（丢弃型专属内容），此处刻意保持型的完整性。
        fmt_wound = sample_from_archetype(
            archetype, "wounds", self.rng,
            fallback_pool=STORR_WOUNDS.get(diag_key) or STORR_WOUNDS.get("healthy"),
        ) or sample_formative_wound(diag_key, rng=self.rng)
        comp_desire = sample_from_archetype(
            archetype, "compensatory_desires", self.rng,
        ) or sample_compensatory_desire(diag_key, rng=self.rng)
        storr_need = sample_from_archetype(
            archetype, "storr_needs", self.rng,
        ) or sample_storr_need(diag_key, rng=self.rng)

        # ---- 6c. Weiland 角色弧线 ----
        arc_info = sample_arc_type(diag_key, rng=self.rng)

        # ---- 7. 功能障碍信念 ----
        beliefs = sample_dysfunctional_beliefs(diag_key, rng=self.rng)

        # ---- 8. 压力应激模式 ----
        stress = sample_stress_response(diag_key, rng=self.rng, ocean=ocean)

        # ---- 9. 触发器 & 安全行为 ----
        trigs = sample_triggers(diag_key, rng=self.rng, n_triggers=self.trigger_count, ocean=ocean)
        sbehaviors = sample_safety_behaviors(diag_key, rng=self.rng, n_behaviors=self.safety_behavior_count, ocean=ocean)

        # ---- 10. 生理特征 ----
        appearance = sample_physical_appearance(gender=gender, age=age, rng=self.rng, ocean=ocean)

        # ---- 11. 隐藏经历 ----
        secrets = sample_hidden_experiences(diag_key, rng=self.rng, n=self.hidden_experience_count, ocean=ocean)

        # ---- 12. 生活事件（OCEAN→效价调整，约束2）----
        pos_r, neg_r, neu_r = adjust_event_ratios_by_ocean(
            ocean,
            base_positive=self.event_positive_ratio,
            base_negative=self.event_negative_ratio,
            base_neutral=self.event_neutral_ratio,
        )
        events = sample_events_for_persona(
            age=age,
            primary_diagnosis_key=diag_key if diag_key != "healthy" else None,
            comorbidity_keys=comorb_keys if comorb_keys else None,
            positive_ratio=pos_r,
            negative_ratio=neg_r,
            neutral_ratio=neu_r,
            # 预留一个事件槽给 formative_wound
            n_events=self.event_count - 1 if fmt_wound else self.event_count,
            rng=self.rng,
        )

        # ---- 12b. 强制注入 formative_wound 到 life_events（确保一致性）----
        if fmt_wound:
            events = _inject_wound_into_events(fmt_wound, events, self.rng)

        events_text = format_events_timeline(events)
        event_names = [e.name_cn for e in events]

        # ---- 7. 构造 Persona ----
        label = f"{diag_key}_{self._counter:04d}"
        pid = f"P-{self._counter:06d}"

        current_status = self._generate_current_status({
            "primary_diagnosis": diag_info["name_cn"],
            "ocean": ocean,
            "life_events": events,
        })

        p = Persona(
            id=pid,
            label=label,
            age=age,
            gender=gender,
            occupation=occ.name_cn,
            occupation_code=occ.code,
            education=education,
            locale=locale,
            locale_canonical=locale_canonical,
            marital_status=marital,
            primary_diagnosis=diag_info["name_cn"],
            primary_diagnosis_en=diag_info.get("name_en", diag_info["name_cn"]),
            comorbidities=comorb_names,

            # 人设元类型（Archetype Grid，v1.2）
            archetype_key=archetype.get("key", "") if archetype else "",
            archetype_name=archetype.get("name_cn", "") if archetype else "",
            archetype_one_liner=archetype.get("one_liner", "") if archetype else "",
            ocean=ocean,
            ocean_description=ocean_desc,
            personality_tags=tags,
            cognitive_styles=cognitive,
            coping_styles=coping,

            # MECE 六维度
            social_relations=social_relations,
            values_beliefs=values_beliefs,
            communication_style=communication_style,
            lifestyle_habits=lifestyle_habits,
            skills_abilities=skills_abilities,
            erikson_stage=erikson_stage,

            core_desire=desires_fears.get("core_desire", ""),
            core_fear=desires_fears.get("core_fear", ""),
            dysfunctional_beliefs=beliefs,
            stress_pattern=stress,
            formative_wound=fmt_wound,
            compensatory_desire=comp_desire,
            storr_need=storr_need,
            arc_type=arc_info.get("arc_type", ""),
            arc_description=f"{arc_info.get('arc_name', '')}：{arc_info.get('trajectory', '')}",
            triggers=trigs,
            safety_behaviors=sbehaviors,
            physical_appearance=appearance,
            hidden_experiences=secrets,
            life_events=events,
            life_events_text=events_text,
            current_status=current_status,
            _diagnosis_info=diag_info,
        )

        p.system_prompt = self._build_system_prompt(p)
        return p

    # ======================== 批量生成 ========================

    def batch(self, n: int, seed_pool: list[str] | None = None) -> list[Persona]:
        """批量生成 Persona

        Args:
            n: 生成的 Persona 数量
            seed_pool: 可选，指定诊断种子列表，循环使用
        """
        result = []
        for i in range(n):
            if seed_pool:
                diag = seed_pool[i % len(seed_pool)]
                p = self.generate(primary_diagnosis=diag)
            else:
                p = self.generate()
            result.append(p)
        return result


# =====================================================================
# 辅助函数
# =====================================================================

def _inject_wound_into_events(
    wound_text: str,
    events: list[LifeEvent],
    rng: random.Random,
) -> list[LifeEvent]:
    """确保形成性创伤在 life_events 中有对应条目

    检查 formative_wound 是否已在 events 中体现，若否则创建一个对应的 LifeEvent 插入。
    """
    # 检查是否已有对应事件（前 12 个字符匹配即可）
    wound_short = wound_text[:12]
    for e in events:
        if wound_short in e.name_cn or e.name_cn[:12] in wound_text:
            return events  # 已有对应事件，无需重复

    # 根据创伤文本推断人生阶段
    stage = "childhood"
    if any(kw in wound_text for kw in ["青少年", "学生", "学校", "同学", "校园"]):
        stage = "adolescence"
    elif any(kw in wound_text for kw in ["成年", "工作", "职场", "婚姻", "配偶", "伴侣"]):
        stage = "adulthood"
    elif any(kw in wound_text for kw in ["中年", "老年", "退休"]):
        stage = "mid_older"

    # 根据创伤文本推断领域
    domain = "family"
    if any(kw in wound_text for kw in ["社交", "人际", "朋友", "被排", "孤立", "公众"]):
        domain = "interpersonal"
    elif any(kw in wound_text for kw in ["学业", "学校", "老师", "成绩", "考试"]):
        domain = "education"
    elif any(kw in wound_text for kw in ["工作", "职场", "上司", "同事", "失业", "职场"]):
        domain = "occupation"
    elif any(kw in wound_text for kw in ["健康", "疾病", "医院", "病", "伤害", "住院"]):
        domain = "health"

    wound_event = LifeEvent(
        domain=domain,
        stage=stage,
        name_cn=wound_text[:35] + "…" if len(wound_text) > 35 else wound_text,
        name_en=wound_text,
        valence="negative",
    )
    result = list(events)
    result.append(wound_event)
    return result


# =====================================================================
# 便利函数
# =====================================================================

def generate_persona(
    primary_diagnosis: str | None = None,
    rng_seed: int | None = None,
    **kwargs,
) -> Persona:
    """快速生成一个 Persona

    Args:
        primary_diagnosis: 主诊断中文名，None 则随机
        rng_seed: 随机种子
        **kwargs: 可包含两类参数：
            - 传给构造器的：trigger_count, safety_behavior_count, event_count 等
            - 传给 generate() 的：gender, age, education, locale, marital_status

    Returns:
        Persona 对象
    """
    # 分离构造器参数和 generate 参数
    gen_kwargs = {}
    generate_kwargs = {}
    generate_params = {"gender", "age", "education", "locale", "marital_status"}
    for k, v in kwargs.items():
        if k in generate_params:
            generate_kwargs[k] = v
        else:
            gen_kwargs[k] = v
    gen = PersonaGenerator(rng_seed=rng_seed, **gen_kwargs)
    return gen.generate(primary_diagnosis=primary_diagnosis, **generate_kwargs)


def batch_generate(
    n: int,
    seed_pool: list[str] | None = None,
    rng_seed: int | None = None,
    **kwargs,
) -> list[Persona]:
    """批量生成 Persona"""
    gen = PersonaGenerator(rng_seed=rng_seed, **kwargs)
    return gen.batch(n, seed_pool=seed_pool)


def Ocean_to_work_status(ocean: dict[str, int]) -> str:
    """从 OCEAN 推断大致工作/社会功能状态"""
    n = ocean.get("N", 5)
    c = ocean.get("C", 5)
    e = ocean.get("E", 5)

    if n >= 8 and c <= 3:
        return "社会功能明显受损，可能需要病休或住院治疗"
    elif n >= 7 and c <= 4:
        return "社会功能受损，日常工作和社交受影响"
    elif n >= 6:
        return "社会功能轻度受损，仍可维持基本日常活动"
    else:
        return "社会功能基本正常"
