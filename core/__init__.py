"""
Persona Generator — 精神病学评估用全量 Persona 生成引擎

模块结构：
  occupations.py     — 职业分类（《职业分类大典2022》79中类）
  personality.py     — 性格系统（OCEAN 大五人格 + MECE 标签库 + 诊断映射 + Egri 增强）
  events.py          — 生活事件（6领域×4阶段 2D 矩阵，143 事件模板）
  triggers.py        — 触发器系统（症状触发 + 安全行为 + 生理特征 + 隐藏经历）
  stratification.py  — 分层压缩系统（普查校准的人口学联合分布约束）
  generator.py       — 主生成逻辑（整合以上所有模块 + 诊断本体）
  human_ontology.py  — canonical Human Ontology 加载器（ontology/human_ontology.v1.json）
"""

from .occupations import (
    OccupationCategory,
    OCCUPATIONS,
    get_occupation_by_code,
    get_occupations_by_major,
    get_filtered_occupations,
    get_default_occupation_weights,
    list_occupations_summary,
)

from .personality import (
    OCEAN_DIMENSIONS,
    PERSONALITY_TAGS,
    DIAGNOSIS_OCEAN_RANGES,
    CORE_DESIRES_FEARS,
    DYSFUNCTIONAL_BELIEFS,
    STRESS_RESPONSE_PATTERNS,
    STORR_WOUNDS,
    STORR_COMPENSATORY_DESIRES,
    STORR_NEEDS,
    WEILAND_ARC_TYPES,
    DIAGNOSIS_ARC_MAPPINGS,
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
    # --- MECE 六维度（v2 增强） ---
    sample_social_relations,
    sample_values_beliefs,
    sample_communication_style,
    sample_lifestyle_habits,
    sample_skills_abilities,
    sample_erikson_stage,
    SOCIAL_RELATIONS_MAP,
    VALUES_BELIEFS_MAP,
    COMMUNICATION_STYLES_MAP,
    LIFESTYLE_HABITS_MAP,
    SKILLS_ABILITIES_MAP,
    ERIKSON_STAGES_MAP,
)

from .events import (
    LifeEvent,
    LIFE_EVENTS,
    sample_events_for_persona,
    format_events_timeline,
    get_events_by_domain_stage,
    get_events_by_diagnosis,
    DOMAIN_CN,
    STAGE_CN,
)

from .triggers import (
    TRIGGERS_AND_SAFETY,
    PHYSICAL_APPEARANCE_TEMPLATES,
    HIDDEN_EXPERIENCES,
    sample_triggers,
    sample_safety_behaviors,
    sample_physical_appearance,
    sample_hidden_experiences,
)

from .stratification import (
    AGE_BANDS,
    EDUCATION_LEVELS,
    DIAGNOSIS_GENDER_DIST,
    DIAGNOSIS_AGE_BANDS,
    EDUCATION_DIAGNOSIS_MODIFIERS,
    sample_age_from_bands,
    sample_gender_for_diagnosis,
    sample_education_for_diagnosis,
    classify_ocean_pattern,
    compute_event_valence_weights,
    calculate_total_compression,
)

from .archetypes import (
    ARCHETYPES,
    sample_archetype,
    has_archetypes,
    get_archetypes,
    sample_from_archetype,
    apply_archetype_tone,
    apply_ocean_bias,
    calculate_archetype_compression,
)

from .generator import (
    Persona,
    PersonaGenerator,
    generate_persona,
    batch_generate,
)

from .human_ontology import (
    load_human_ontology,
    validate_human_ontology,
    ontology_version,
    canonical_axis_ids,
    canonical_life_domains,
    canonical_developmental_stage_ids,
    canonical_event_pressure_shapes,
    map_legacy_event_domain,
    map_legacy_event_stage,
    map_legacy_locale,
    ontology_summary,
)

__version__ = "1.3.0"
