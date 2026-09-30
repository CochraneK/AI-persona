"""Build the static showcase data for the project presentation page.

This produces ONE JSON file (web/showcase_data.json) with two sections:

1. `ontology` — a compact summary of Human Ontology v2 for the "ontology
   overview" section: the 18 canonical domains (id, temporal class, the
   guiding question, and how many canonical concepts live in each) plus
   the global concept count.

2. `personas` — a pool of pre-generated personas: healthy controls
   (无精神障碍（健康）x 20 seeds) + 10 archetype-covered diagnoses x 5
   seeds = 70. The pool is whole-person by design — the Human Ontology
   v2 covers 18 domains of a complete human, and psychiatry is just one
   of its domains, so the showcase page's "draw a person" button mixes
   healthy and clinical personas. The button picks from this pool
   client-side, so the page stays a zero-dependency single file.

Run:
    python scripts/make_showcase_pool.py

Output:
    web/showcase_data.json
"""

import hashlib
import json
import os
import random
import sys

# --- Determinism guard (defense in depth) ------------------------------------
# The engine's sampling path is audited to be hash-independent (full rationale
# in scripts/make_full_pool.py). The guard is kept as belt-and-braces: it pins
# PYTHONHASHSEED=0 by re-exec'ing exactly once, so any FUTURE hash-ordered
# sampling path cannot silently break byte-for-byte pool reproducibility.
# (Same guard as scripts/make_full_pool.py.)
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from core import PersonaGenerator  # noqa: E402
from core import ontology_native_fill as ofill  # noqa: E402

V2_PATH = os.path.join(_REPO, "ontology", "human_ontology.v2.json")
CATALOG_PATH = os.path.join(_REPO, "ontology", "CANONICAL_CONCEPT_CATALOG.json")
OUT_PATH = os.path.join(_REPO, "web", "showcase_data.json")
HTML_PATH = os.path.join(_REPO, "web", "index.html")

# Delimiters that delimit the JSON payload inside index.html's data block.
# Keeping the delimiters on their own lines makes the inliner idempotent:
# re-running the script replaces whatever currently sits between them.
DATA_START = "/*__SHOWCASE_DATA_START__*/"
DATA_END = "/*__SHOWCASE_DATA_END__*/"

# The 10 diagnoses that have an archetype grid, using the exact Chinese
# names from the generator's default diagnosis list (the loader falls back
# to that list because diagnosis_ontology.json has no top-level
# "diagnoses" key).
DIAGNOSES = [
    "重度抑郁障碍",
    "广泛性焦虑障碍",
    "社交焦虑障碍",
    "精神分裂症",
    "双相I型障碍",
    "强迫症",
    "注意缺陷/多动障碍",
    "创伤后应激障碍",
    "边缘型人格障碍",
    "神经性厌食症",
]

SEEDS_PER_DIAGNOSIS = 5
# Base seed offset so the pool is stable across rebuilds.
SEED_BASE = 20260930

# Healthy controls (the "无精神障碍（健康）" persona the engine supports as
# a first-class diagnosis key). Healthy personas have NO archetype grid
# (archetype_name is empty) — the page renders them with a teal
# "健康对照" stamp instead of the red diagnosis stamp.
HEALTHY = "无精神障碍（健康）"
HEALTHY_SEEDS = 20
# Offset so healthy seeds never collide with the diagnosis seeds.
HEALTHY_SEED_OFFSET = 100

# Chinese display labels + guiding questions for the 18 canonical domains.
# The canonical ontology (human_ontology.v2.json) is an English research
# artifact with release gates — it stays untouched. The showcase layer maps
# the English id/question to Chinese for the page; the English originals are
# kept in the payload as the source of record.
DOMAIN_ZH: dict[str, tuple[str, str]] = {
    "development": ("生命历程", "这个人处于生命历程的哪个阶段？哪些发展性转变定义了它？"),
    "body_functioning_health": ("身体功能与健康", "哪些身体特征、功能、残疾与身体健康属性适用于此人？"),
    "mental_neurodevelopmental_health": ("精神与神经发育健康", "哪些心理健康、神经发育、症状/体验、功能、照护与康复属性适用？"),
    "personality_psychology": ("人格与心理", "哪些相对稳定的特质、动机、信念、调节策略、关系倾向与叙事组织适用？"),
    "abilities_skills_interests": ("能力·技能·兴趣", "哪些能力、习得技能、专长与兴趣适用？"),
    "identity_self_concept": ("身份与自我概念", "此人如何描述或理解那些不可还原为角色、法律身份、地点或文化参与关系的自我身份？"),
    "roles": ("角色", "此人承担哪些社会、家庭、教育、工作、照护或社区角色？"),
    "relationships": ("关系", "此人与哪些人相关、以何种关系类型，且该关系带有哪些属性？"),
    "place_mobility": ("地点与流动", "此人通过出生、成长、居住、迁徙或流动与哪些地点相关？"),
    "education_learning": ("教育与学习", "哪些正式/非正式教育、学习参与、学历与学习机会刻画了此人？"),
    "work_economic_participation": ("工作与经济参与", "此人如何参与工作、职业、组织、劳动力市场、收入/资产/负债与经济地位？"),
    "social_institutional_position": ("社会制度地位", "此人在法律、公民、制度、阶层与权利/准入体系中的位置如何？"),
    "culture_language": ("文化与语言", "此人参与、使用或接触过哪些文化、语言、宗教/灵性或社会化环境？"),
    "life_events": ("生活事件", "发生了什么于此人身上、或此人做了什么——何时、与谁、在何种情境下、带来何种后果？"),
    "context_ecology": ("情境与生态", "哪些外部的家庭、社区、机构、经济、政策、技术、历史与环境情境环绕着此人？"),
    "resources_constraints_opportunities": ("资源·约束·机会", "在某一时刻，此人实际可及的资源、约束与可行动的机会有哪些？"),
    "lifestyle_routines": ("生活方式与日常", "哪些重复性活动、常规与习惯性实践构成了日常？"),
    "current_state": ("此刻的状态", "此刻关于此人的哪些真实状况，不应被误认为稳定特质、持久关系或历史事件？"),
}

# Chinese labels for the 5 canonical temporal classes (CSS keeps the English
# class names for styling; only the displayed text is translated).
TEMPORAL_ZH: dict[str, str] = {
    "slow_changing": "慢变",
    "dynamic_state": "动态状态",
    "role_dependent": "角色依赖",
    "relationship_specific": "关系特定",
    "event_history": "事件史",
}

# Chinese names for all 205 canonical concepts (key = concept part of
# canonical_path, i.e. after the domain; nested sub-concepts keep their
# dot, e.g. "temperament_traits.ocean"). Display-layer only — the canonical
# catalog stays English.
CONCEPT_ZH: dict[str, str] = {
    # development
    "birth_cohort": "出生世代",
    "birth_date_year": "出生年份",
    "chronological_age": "实际年龄",
    "developmental_stage": "发展阶段",
    "historical_period": "历史时期",
    "life_role_stage": "人生角色阶段",
    "major_transition_status": "重大转变状态",
    # body_functioning_health
    "body_morphology": "体型体态",
    "disability_functioning": "残疾与功能",
    "health_history": "健康史",
    "physical_appearance": "外貌",
    "physical_health": "身体健康",
    "reproductive_health": "生殖健康",
    "sensory_motor_function": "感觉运动功能",
    "sex_assigned_at_birth": "出生指定性别",
    "sex_characteristics": "性征",
    "sleep_functioning": "睡眠功能",
    "substance_related_health": "物质相关健康",
    # context_ecology
    "contexts": "情境",
    "digital_platform_environment": "数字平台环境",
    "economic_conditions": "经济条件",
    "education_system": "教育系统",
    "environment_climate": "自然环境气候",
    "gender_role_context": "性别角色情境",
    "healthcare_system": "医疗系统",
    "historical_events": "历史事件",
    "household_context": "家庭情境",
    "labor_market": "劳动力市场",
    "neighborhood": "邻里社区",
    "physical_environment": "物理环境",
    "policy_legal_context": "政策法律情境",
    "regional_context": "区域情境",
    "school_work_institutions": "学校与工作机构",
    "social_norms": "社会规范",
    "technology_media_environment": "技术媒体环境",
    "urbanicity": "城市化程度",
    # culture_language
    "cross_cultural_experience": "跨文化经历",
    "cultural_backgrounds": "文化背景",
    "cultural_participation": "文化参与",
    "customs_norms_exposure": "习俗规范接触",
    "enculturation_contexts": "文化濡化情境",
    "languages": "语言",
    "media_culture_exposure": "媒介文化接触",
    "religion_spirituality": "宗教灵性",
    # current_state
    "autonomy": "自主性",
    "competence": "胜任感",
    "current_conflicts": "当前冲突",
    "current_goals": "当前目标",
    "energy": "精力",
    "financial_strain": "经济压力",
    "health_burden": "健康负担",
    "mood": "情绪",
    "relatedness": "联结感",
    "stress": "压力",
    "summary": "状态摘要",
    "support": "支持",
    # education_learning
    "current_education_status": "当前教育状态",
    "education_attainment": "受教育程度",
    "education_field": "教育领域",
    "learning_access_history": "学习机会史",
    "learning_history": "学习经历",
    "training_credentials": "培训资历",
    # identity_self_concept
    "acculturation_bicultural_orientation": "文化适应取向",
    "caste_tribe_clan_identity": "种姓部族身份",
    "ethnocultural_identity": "民族文化身份",
    "gender_expression": "性别表达",
    "gender_identity": "性别认同",
    "pronouns": "代词偏好",
    "racialized_identity": "种族化身份",
    "romantic_orientation": "浪漫取向",
    "self_presentation": "自我呈现",
    "sexual_orientation": "性取向",
    # life_events
    "actors": "相关人物",
    "delayed_consequence": "延迟后果",
    "event_source_provenance": "事件来源",
    "event_subjective_meaning": "事件主观意义",
    "event_time": "事件时间",
    "event_type": "事件类型",
    "immediate_consequence": "即时后果",
    "impact_profile": "影响概况",
    "items": "条目",
    "life_domain": "生活领域",
    "memory_callback": "记忆回调",
    "pressure_shape": "压力形态",
    "role_transition": "角色转换",
    "turning_point": "转折点",
    # lifestyle_routines
    "appearance_grooming_routine": "仪容打理",
    "caregiving_routine": "照护日常",
    "consumption_habits": "消费习惯",
    "daily_routine": "日常节律",
    "diet": "饮食",
    "digital_use": "数字使用",
    "exercise": "运动",
    "leisure": "休闲",
    "media_consumption": "媒介消费",
    "profile": "概况",
    "sleep_routine": "睡眠规律",
    "substance_use": "物质使用",
    # mental_neurodevelopmental_health
    "diagnoses": "诊断",
    "functional_impact": "功能影响",
    "mental_health_status": "心理健康状况",
    "neurodevelopmental_conditions": "神经发育状况",
    "recovery_course": "康复进程",
    "risk_protective_factors": "风险与保护因素",
    "safety_behaviors": "安全行为",
    "symptoms_experiences": "症状与体验",
    "treatment_support": "治疗与支持",
    "triggers": "诱因",
    # personality_psychology
    "cognition_beliefs": "认知信念",
    "cognition_beliefs.self_efficacy": "自我效能",
    "emotion_regulation_coping": "情绪调节与应对",
    "motives_values_goals": "动机价值目标",
    "narrative_identity": "叙事身份",
    "relational_dispositions": "关系倾向",
    "surface_expression": "表面表达",
    "temperament_traits": "气质特质",
    "temperament_traits.legacy_tags": "气质旧标签",
    "temperament_traits.ocean": "OCEAN 五因素",
    # place_mobility
    "birth_place": "出生地",
    "current_residence": "当前居住地",
    "housing_context": "住房情境",
    "living_arrangement": "居住安排",
    "migration_generation": "移民世代",
    "migration_history": "迁徙史",
    "mobility_pattern": "流动模式",
    "place_attachment": "地方依恋",
    "residence": "住所",
    "upbringing_places": "成长地",
    # relationships
    "birth_order_family_position": "出生顺序与家庭位置",
    "caregiver_relations": "照护者关系",
    "children_dependents": "子女与受托者",
    "community_ties": "社区纽带",
    "conflict_repair_observations": "冲突与修复观察",
    "family_climate": "家庭氛围",
    "family_of_origin": "原生家庭",
    "fictive_kin_chosen_family": "拟亲属与自选家庭",
    "friendships": "友谊",
    "household_membership": "家庭成员关系",
    "intergenerational_patterns": "代际模式",
    "kinship_network": "亲属网络",
    "marital_status": "婚姻状况",
    "mentors": "导师",
    "network_size_structure": "网络规模结构",
    "observations": "关系观察",
    "online_relationships_communities": "线上关系与社群",
    "partner_spouse": "伴侣",
    "peer_relations": "同辈关系",
    "relationship_quality": "关系质量",
    "romantic_relationships": "恋爱关系",
    "siblings": "兄弟姐妹",
    "support_network": "支持网络",
    "work_relations": "工作关系",
    # resources_constraints_opportunities
    "barriers_constraints": "障碍与约束",
    "care_resources": "照护资源",
    "career_opportunities": "职业机会",
    "constraints": "约束",
    "healthcare_access": "医疗可及性",
    "institutional_resources": "制度资源",
    "learning_opportunities": "学习机会",
    "material_resources": "物质资源",
    "mobility_options": "流动选择",
    "resources": "资源",
    "social_resources": "社会资源",
    "time_resources": "时间资源",
    # roles
    "caregiving_roles": "照护角色",
    "community_roles": "社区角色",
    "dependent_care_roles": "受照护角色",
    "education_roles": "教育角色",
    "family_roles": "家庭角色",
    "role_conflict": "角色冲突",
    "role_load": "角色负荷",
    "work_authority_responsibility": "工作权责",
    "work_roles": "工作角色",
    # social_institutional_position
    "citizenship_nationality": "国籍与公民身份",
    "civic_institutional_participation": "公民制度参与",
    "discrimination_stigma_exposure": "歧视与污名暴露",
    "healthcare_entitlement_access": "医疗保障可及",
    "institutional_memberships": "制度成员身份",
    "justice_system_exposure": "司法系统接触",
    "legal_residency_status": "合法居住身份",
    "rights_access": "权利与准入",
    "service_access": "服务可及性",
    "social_status_prestige": "社会地位声望",
    "socioeconomic_class": "社会经济阶层",
    # work_economic_participation
    "debt": "负债",
    "employment_status": "就业状态",
    "income": "收入",
    "industry": "行业",
    "material_security_facts": "物质安全事实",
    "occupation": "职业",
    "occupation_detail": "职业细节",
    "wealth_assets": "财富资产",
    "work_conditions": "工作条件",
    # abilities_skills_interests
    "artistic_preferences": "艺术偏好",
    "cognitive_abilities": "认知能力",
    "creative_skills": "创造技能",
    "expertise": "专长",
    "interests_hobbies": "兴趣爱好",
    "knowledge_domains": "知识领域",
    "language_proficiency": "语言能力",
    "physical_skills": "身体技能",
    "social_skills": "社交技能",
    "technical_skills": "技术技能",
}


def _build_ontology_summary() -> dict:
    with open(V2_PATH, encoding="utf-8") as f:
        v2 = json.load(f)
    with open(CATALOG_PATH, encoding="utf-8") as f:
        catalog = json.load(f)

    domains = v2.get("canonical_domains", [])
    # Count canonical concepts per domain AND collect their names (the key
    # part of canonical_path) so the page can show concrete values, not just
    # a number.
    per_domain: dict[str, int] = {}
    per_domain_names: dict[str, list[str]] = {}
    for concept in catalog.get("concepts", []):
        d = concept.get("domain", "unknown")
        per_domain[d] = per_domain.get(d, 0) + 1
        path = concept.get("canonical_path", "")
        name = path.split(".", 1)[1] if "." in path else path
        per_domain_names.setdefault(d, []).append(name)

    domain_rows = []
    for d in domains:
        did = d.get("id", "")
        zh_label, zh_question = DOMAIN_ZH.get(did, (did, d.get("question", "")))
        temporal = d.get("default_temporal_class", "")
        names = per_domain_names.get(did, [])
        domain_rows.append({
            "id": did,
            "zh": zh_label,
            "temporal_class": temporal,
            "zh_class": TEMPORAL_ZH.get(temporal, temporal),
            "question": d.get("question", ""),
            "zh_question": zh_question,
            "concepts": per_domain.get(did, 0),
            "concept_names": names,
            "concept_names_zh": [CONCEPT_ZH.get(n, n) for n in names],
        })

    return {
        "version": v2.get("version", ""),
        "status": v2.get("status", ""),
        "semantic_model_principle": v2.get("semantic_model", {}).get("principle", ""),
        "person_root_definition": v2.get("person_root", {}).get("definition", ""),
        "domain_count": len(domain_rows),
        "concept_count": len(catalog.get("concepts", [])),
        "domains": domain_rows,
    }


def _persona_to_card(p) -> dict:
    """Project a Persona onto a compact display card for the web page."""
    return {
        "id": p.id,
        "label": p.label,
        "age": p.age,
        "gender": p.gender,
        "occupation": p.occupation,
        "education": p.education,
        "locale": p.locale,
        "marital_status": p.marital_status,
        "primary_diagnosis": p.primary_diagnosis,
        "primary_diagnosis_en": p.primary_diagnosis_en,
        "comorbidities": list(p.comorbidities or []),
        "archetype_name": p.archetype_name,
        "archetype_one_liner": p.archetype_one_liner,
        "ocean": dict(p.ocean or {}),
        "personality_tags": list(p.personality_tags or []),
        "core_desire": p.core_desire,
        "core_fear": p.core_fear,
        "formative_wound": p.formative_wound,
        "compensatory_desire": p.compensatory_desire,
        "storr_need": p.storr_need,
        "arc_type": p.arc_type,
        "arc_description": p.arc_description,
        "current_status": p.current_status,
    }


def _fill_rng(diagnosis_key: str, seed: int) -> random.Random:
    """Per-card ontology RNG, derived from card identity (diagnosis + seed).

    The 70-card pool is re-keyed to unique ids in build order (see
    ``_build_persona_pool``), but the RNG deliberately stays keyed on
    ``(diagnosis_key, seed)``: that pair is unique per card, sha1-based and
    PYTHONHASHSEED-independent, and re-keying it on the new ids would resample
    every card's 5-domain block (non-surgical).
    """
    h = hashlib.sha1(f"{diagnosis_key}#{seed}".encode("utf-8")).hexdigest()
    return random.Random(int(h[:12], 16))


def _build_persona_pool() -> list[dict]:
    pool: list[dict] = []
    # Healthy controls first, then the clinical diagnoses — the page is
    # whole-person, so the pool leads with healthy people.
    for i in range(HEALTHY_SEEDS):
        seed = SEED_BASE + HEALTHY_SEED_OFFSET + i
        gen = PersonaGenerator(rng_seed=seed)
        p = gen.generate(primary_diagnosis=HEALTHY)
        card = _persona_to_card(p)
        card["seed"] = seed
        card["diagnosis_key"] = HEALTHY
        # Ontology-native 5-domain block, sampled on a per-card RNG derived
        # from card identity (deterministic, independent across cards).
        card["ontology"] = ofill.sample_context_fields(
            ofill.persona_context(p), None, rng=_fill_rng(HEALTHY, seed))
        pool.append(card)
    for diag in DIAGNOSES:
        for i in range(SEEDS_PER_DIAGNOSIS):
            seed = SEED_BASE + i
            gen = PersonaGenerator(rng_seed=seed)
            p = gen.generate(primary_diagnosis=diag)
            card = _persona_to_card(p)
            # Tag with the seed so the page can display "seed 20260930".
            card["seed"] = seed
            card["diagnosis_key"] = diag
            card["ontology"] = ofill.sample_context_fields(
                ofill.persona_context(p), None, rng=_fill_rng(diag, seed))
            pool.append(card)
    # Unique, stable addressing: each card above was minted by its own
    # PersonaGenerator instance, so the engine gave every card the same id
    # (P-000001, the per-instance counter starting at 1). Re-key the pool in
    # its deterministic build order (20 healthy + 10 diagnoses x 5) so the 70
    # cards are individually addressable. This id space is local to the
    # showcase artifact; the 5000-card full pool (scripts/make_full_pool.py)
    # is a separate artifact with its own P-000001..P-005000 range, and live
    # cards (scripts/serve_showcase.py) use the P-100000..P-199999 band.
    for n, card in enumerate(pool, start=1):
        card["id"] = f"P-{n:06d}"
    return pool


def _inline_into_html(payload_json: str) -> bool:
    """Replace the delimited data block inside web/index.html (idempotent).

    The page reads its pool from an inline ``<script type="application/json">``
    block, so the final page stays a single self-contained file with zero
    external requests. Returns False (and skips) if index.html is absent.
    """
    if not os.path.exists(HTML_PATH):
        return False
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    start = html.find(DATA_START)
    end = html.find(DATA_END)
    if start == -1 or end == -1 or end <= start:
        # No markers present — do not silently corrupt the page.
        print("  ! index.html markers not found; skipping inline (page kept as-is)")
        return False

    # Keep BOTH markers in place (the page JS strips them before JSON.parse)
    # and replace only the payload between them. Idempotent on re-runs.
    new_html = html[:start + len(DATA_START)] + "\n" + payload_json + "\n" + html[end:]
    # newline="\n" keeps LF endings on Windows.
    with open(HTML_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_html)
    return True


def main() -> int:
    ontology = _build_ontology_summary()
    personas = _build_persona_pool()

    out = {
        "generated_by": "scripts/make_showcase_pool.py",
        "engine_version": "2.0.0",
        "ontology": ontology,
        "persona_count": len(personas),
        "personas": personas,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    # newline="\n" keeps LF endings on Windows (text mode would emit CRLF).
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        payload_json = json.dumps(out, ensure_ascii=False, indent=2)
        f.write(payload_json)

    inlined = _inline_into_html(payload_json)

    # Console report.
    print("showcase pool built")
    print(f"  ontology: {ontology['domain_count']} domains, "
          f"{ontology['concept_count']} concepts, status={ontology['status']}")
    print(f"  personas: {len(personas)}")
    dom_counts = sorted({len(c.get("ontology") or {}) for c in personas})
    print(f"  ontology-native 5-domain fill: {dom_counts} domain(s) per card (target 5)")
    healthy_rows = [c for c in personas if c["diagnosis_key"] == HEALTHY]
    print(f"    {HEALTHY}: {len(healthy_rows)}")
    for diag in DIAGNOSES:
        rows = [c for c in personas if c["diagnosis_key"] == diag]
        archetypes = sorted({c["archetype_name"] for c in rows})
        print(f"    {diag}: {len(rows)} -> {archetypes}")
    print(f"  wrote: {OUT_PATH}")
    if inlined:
        print(f"  inlined into: {HTML_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
