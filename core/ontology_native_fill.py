"""Ontology-native sampler for the five legacy-adapter-empty domains.

Human Ontology v2 defines 18 domains / 205 canonical concepts. The legacy
adapter (core.legacy_adapter.legacy_persona_to_kernel) can only project the
45 flat Persona fields onto 13 domains; the remaining five environmental /
institutional domains have no counterpart in legacy fields:

    roles, social_institutional_position, culture_language,
    context_ecology, resources_constraints_opportunities

This module is the first fully ontology-native sampler: it derives
coherent, deterministic values for all 59 canonical concepts of those five
domains directly from (legacy persona context, international
demographics). core.kernel_generator documents the migration plan — legacy
modules stay behind the semantic firewall "until fully ontology-native
samplers replace them"; this module is that replacement for these five
domains.

Storage discipline (enforced by PersonaKernel.validate): six of the 59
concepts declare storage=relation_graph in the canonical field registry and
therefore MUST be emitted as kernel relations, never as domain payload:

    roles.items
    culture_language.languages
    culture_language.cultural_participation
    context_ecology.contexts
    resources_constraints_opportunities.resources
    resources_constraints_opportunities.constraints

``sample_context_fields`` returns the full 59-concept payload (relation
concepts as flat label lists) — the pool-card form. ``fill_ontology_native``
applies the storage split when populating a PersonaKernel.

Determinism: all randomness flows from the caller-supplied RNG. The pool
pipeline (scripts.make_full_pool) uses an independent fourth stream,
Random(MASTER_SEED + 3), so the existing three streams and the existing 34
pool-card fields stay byte-identical. When no RNG is given, one is derived
from the persona id, so single-shot calls are reproducible too.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from .persona_kernel import FieldMetadata, PersonaKernel

FILL_DOMAINS: tuple[str, ...] = (
    "roles",
    "social_institutional_position",
    "culture_language",
    "context_ecology",
    "resources_constraints_opportunities",
)

# canonical_path -> (predicate, object entity_type) for relation_graph concepts
RELATION_STORAGE: dict[str, tuple[str, str]] = {
    "roles.items": ("has_role", "role"),
    "culture_language.languages": ("uses_language", "language"),
    "culture_language.cultural_participation": ("participates_in_culture", "culture_context"),
    "context_ecology.contexts": ("situated_in_context", "generic"),
    "resources_constraints_opportunities.resources": ("has_resource", "resource"),
    "resources_constraints_opportunities.constraints": ("faces_constraint", "constraint"),
}

SOURCE_TYPE = "generated"
CONFIDENCE = 1.0
PROVENANCE = "ontology-native sampler (core.ontology_native_fill)"

TEMPORAL_CLASS: dict[str, str] = {
    "roles": "role_dependent",
    "social_institutional_position": "slow_changing",
    "culture_language": "slow_changing",
    "context_ecology": "slow_changing",
    "resources_constraints_opportunities": "dynamic_state",
}

# --------------------------------------------------------------------------
# Region content profiles (indexed by demographics_intl region_key)
# --------------------------------------------------------------------------

REGION_PROFILES: dict[str, dict[str, Any]] = {
    "chinese": {
        "customs": "以家庭为本的高礼俗社会，重视人情、面子与长幼秩序",
        "social_norms": "集体优先、关系本位，公共场合含蓄克制",
        "gender_roles": "传统性别分工仍有惯性，男性外养、女性持家观念普遍",
        "climate": "温带季风为主，四季分明，南北气候差异显著",
        "enculturation": "学校教育与家庭教养并重，孝亲与勤学是核心规范",
        "culture_pool": ["节庆祭祖", "社区邻里互助", "宗族家族活动", "戏曲与民俗活动"],
    },
    "japanese": {
        "customs": "长幼有序、场所意识强，重视礼数与不给人添麻烦",
        "social_norms": "集体和谐优先，冲突回避，公共空间安静守序",
        "gender_roles": "男主外女主内传统较深，双职工接受度持续上升",
        "climate": "温带海洋性与亚热带气候，四季分明，夏季多台风",
        "enculturation": "学校规训严格，耻感文化塑造行为边界",
        "culture_pool": ["神社祭礼", "同好会与社团活动", "町内会社区活动", "动漫与流行文化"],
    },
    "korean": {
        "customs": "长幼尊卑分明，礼制严谨，重视人情",
        "social_norms": "面子与等级秩序重要，职场应酬文化普遍",
        "gender_roles": "儒家性别分工传统强，平等意识近年快速提升",
        "climate": "温带季风气候，四季分明，冬季干冷",
        "enculturation": "教育竞争高度内卷，家庭与学校压力并存",
        "culture_pool": ["宗祠与岁末祭礼", "社区居民会", "流行文化（K-pop/影视）", "会社同期会"],
    },
    "eastern_european": {
        "customs": "东正教文化圈，重视家庭与待客之道",
        "social_norms": "直率务实，集体历史记忆影响公共话语",
        "gender_roles": "传统性别角色明显，男性主要经济支柱观念普遍",
        "climate": "温带大陆性气候，冬季漫长寒冷",
        "enculturation": "家庭与教会共同承担社会化职能",
        "culture_pool": ["东正教节日", "社区节庆与集市", "民间音乐与舞蹈", "家庭聚会"],
    },
    "western_european": {
        "customs": "个人权利与隐私受高度重视，契约与规则意识强",
        "social_norms": "低语境沟通，公共讨论直接，福利意识普遍",
        "gender_roles": "性别平等程度高，双职工与育儿分担较均衡",
        "climate": "温带海洋性气候为主，温和多雨",
        "enculturation": "国家福利体系托底，公民社会参与度高",
        "culture_pool": ["社区文化活动", "宗教节日（渐世俗化）", "体育俱乐部", "节庆市集"],
    },
    "latin_american": {
        "customs": "家庭本位（familismo），热情外向，宗教节庆浓厚",
        "social_norms": "人际关系优先于规则，时间观念弹性",
        "gender_roles": "machismo 传统与女性家庭核心角色并存",
        "climate": "热带与亚热带为主，高原与山地气候多样",
        "enculturation": "大家庭共同抚养，教会与学校共同教化",
        "culture_pool": ["天主教节庆", "家庭聚会与节庆", "街头音乐与舞蹈", "社区嘉年华"],
    },
    "north_african": {
        "customs": "伊斯兰文化与柏柏尔传统交融，待客礼数隆重",
        "social_norms": "家庭与部落纽带强，性别空间界限明显",
        "gender_roles": "性别分工传统，女性公共参与度近年上升",
        "climate": "干旱半干旱为主，夏季炎热干燥",
        "enculturation": "宗教教育与家庭教养并重",
        "culture_pool": ["清真寺宗教生活", "家族与部落聚会", "传统集市", "节庆与婚礼"],
    },
    "african_sub_saharan": {
        "customs": "集体主义传统强，长者权威受尊重，口头传统深厚",
        "social_norms": "互惠义务（如 Ubuntu 观念）塑造社会关系",
        "gender_roles": "性别分工传统，女性在经济与家庭中承担多重角色",
        "climate": "热带气候为主，雨季旱季分明",
        "enculturation": "社区与家庭共同抚养，成人礼传统存在",
        "culture_pool": ["教会与宗教活动", "社区集会与节庆", "传统仪式", "街头音乐与舞蹈"],
    },
    "west_asian": {
        "customs": "伊斯兰文化为主，家庭与宗族纽带紧密",
        "social_norms": "荣誉与家族名声重要，待客之道隆重",
        "gender_roles": "性别隔离传统较强，城市地区差异大",
        "climate": "干旱炎热为主，昼夜温差大",
        "enculturation": "宗教与家庭共同承担教化",
        "culture_pool": ["清真寺宗教生活", "家族聚会", "宗亲网络活动", "节庆与婚礼"],
    },
    "south_asian": {
        "customs": "宗教传统深远，家庭与种姓网络交织",
        "social_norms": "集体本位，长辈权威重要，关系优先",
        "gender_roles": "父权传统强，女性公共参与受家庭期望约束",
        "climate": "热带季风气候，雨季显著，次大陆内部气候多样",
        "enculturation": "家庭与宗教机构共同教化，教育竞争压力高",
        "culture_pool": ["宗教节庆", "家族与种姓聚会", "传统音乐与舞蹈", "社区庙会"],
    },
    "southeast_asian": {
        "customs": "佛教与多元宗教共存，面子和人情观念重要",
        "social_norms": "冲突回避，等级与礼貌规范明确",
        "gender_roles": "传统性别分工明显，女性经济参与度高",
        "climate": "热带季风与雨林气候，湿热多雨",
        "enculturation": "佛教与家庭共同承担教化",
        "culture_pool": ["佛教节日与庙会", "社区邻里互助", "传统节庆与游行", "家庭聚会"],
    },
    "central_asian": {
        "customs": "游牧传统与伊斯兰文化融合，待客（hospitality）观念强",
        "social_norms": "长者与宗族权威重要，男性荣誉观念强",
        "gender_roles": "游牧传统性别分工，女性家庭角色核心",
        "climate": "温带大陆性干旱气候，冬寒夏热，温差大",
        "enculturation": "家庭与宗教传统共同教化",
        "culture_pool": ["宗族聚会", "传统节庆与赛马", "宗教节日", "家庭待客活动"],
    },
    "north_american": {
        "customs": "个人主义与机会主义，规则与契约文化",
        "social_norms": "直接沟通，个人责任优先，多元文化并存",
        "gender_roles": "性别平等程度高，工作家庭双轨普遍",
        "climate": "气候多样，温带大陆性为主，季节分明",
        "enculturation": "学校与社区组织承担社会化，宗教渐趋多元",
        "culture_pool": ["社区志愿者活动", "宗教场所活动", "体育与俱乐部", "节庆与派对"],
    },
    "oceania": {
        "customs": "英美移民文化为主，户外与休闲生活方式",
        "social_norms": "平等主义与直接沟通，社区网络相对松散",
        "gender_roles": "性别平等程度较高，双职工普遍",
        "climate": "温带与热带并存，日照充足",
        "enculturation": "学校与社区组织社会化，多元文化渐增",
        "culture_pool": ["社区体育活动", "海滩与户外文化", "宗教活动", "节日市集"],
    },
}

_GENERIC_PROFILE: dict[str, Any] = {
    "customs": "地方性礼俗传统，重视家庭与社区纽带",
    "social_norms": "集体本位，社区关系与互惠义务重要",
    "gender_roles": "传统性别分工明显，女性经济参与度地区差异大",
    "climate": "区域气候多样，季节性显著",
    "enculturation": "家庭与社区共同承担社会化职能",
    "culture_pool": ["社区节庆", "家庭聚会", "宗教与民间仪式", "邻里互助"],
}

_NO_RELIGION = ("无宗教", "其他", "")

# culture_pool items that presuppose a specific religion — the item is only
# sampled for personas whose religion is in the gate set (avoids e.g. a Muslim
# persona "attending a community temple fair").
_CULTURE_RELIGION_GATES: dict[str, frozenset[str]] = {
    "节庆祭祖": frozenset({"佛教", "道教", "民间信仰", "无宗教"}),
    "社区庙会": frozenset({"印度教", "佛教", "锡克教", "民间信仰"}),
    "清真寺宗教生活": frozenset({"伊斯兰教"}),
}


def _profile(region_key: str | None) -> dict[str, Any]:
    return REGION_PROFILES.get(region_key or "", _GENERIC_PROFILE)


def _is_clinical(ctx: dict[str, Any]) -> bool:
    return bool(ctx["primary_diagnosis"]) and ctx["primary_diagnosis"] != "无精神障碍（健康）"


def _digest(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]


def _rng_for(persona_id: str) -> random.Random:
    return random.Random(int(hashlib.sha1(persona_id.encode("utf-8")).hexdigest()[:12], 16))


def _default_demo(ctx: dict[str, Any]) -> dict[str, Any]:
    """Fallback demographics (China/Chinese baseline) when no intl demo is given."""
    return {
        "continent": "亚洲",
        "country_code": "CN",
        "country_cn": "中国",
        "country_en": "China",
        "region_key": "chinese",
        "region_cn": "东亚·汉",
        "region_en": "East Asia (Han)",
        "language_cn": "汉语普通话",
        "language_en": "Chinese (Mandarin)",
        "religion": "无宗教",
        "ethnicity": "汉族",
        "name": "",
        "urbanicity": 0.5,
        "income": "mid",
        "urbanicity_label": ctx.get("locale") or "城镇",
    }


def _life_facts(ctx: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Pre-computed shared life facts; the parent draw happens here first so
    every downstream sampler sees a stable RNG stream order."""
    age = ctx["age"]
    p_parent = 0.35 if age < 36 else 0.75 if age < 56 else 0.9
    return {"has_kids": age >= 18 and rng.random() < p_parent}


# --------------------------------------------------------------------------
# Per-domain samplers (each returns only non-empty canonical keys)
# --------------------------------------------------------------------------


def _sample_roles(ctx, demo, prof, facts, rng) -> dict[str, Any]:
    age = ctx["age"]
    marital = ctx["marital_status"]
    occ = ctx["occupation"]
    out: dict[str, Any] = {}

    family: list[str] = []
    if age < 18:
        family.append("子女")
    elif marital in ("已婚", "再婚"):
        family.append("配偶")
    elif marital in ("离异", "分居"):
        family.append("离异/分居者")
    if facts["has_kids"]:
        family.append("父母")
    if age >= 66:
        family.append("长者")
    if not family:
        family = ["独居青年"] if age >= 18 else ["子女"]
    out["family_roles"] = family

    if age < 18:
        work = ["在读学生"]
    elif age >= 60:
        work = ["退休者"] if rng.random() < 0.6 else ["资深从业者（延迟退休）"]
    elif any(k in occ for k in ("负责人", "主管", "经理", "军官", "总监")):
        work = ["管理决策者"]
    elif any(k in occ for k in ("专业技术", "工程技术人员", "教学人员", "研究人员", "专业人员", "法律事务", "金融服务", "经济和金融", "软件", "信息技术")):
        work = ["专业技术人员"]
    elif any(k in occ for k in ("行政办事", "办事人员")):
        work = ["行政事务人员"]
    elif any(k in occ for k in ("制造", "生产", "加工", "服务人员", "建筑施工", "采矿", "印刷", "操作人员", "农林牧渔")):
        work = ["一线执行者"]
    else:
        work = ["岗位执行者"]
    out["work_roles"] = work

    edu_roles: list[str] = []
    if age < 18:
        edu_roles.append("在读学生")
    elif ctx["education"] in ("大专", "本科", "硕士及以上") and age < 40 and rng.random() < 0.35:
        edu_roles.append("继续学习者")
    elif age >= 60 and rng.random() < 0.25:
        edu_roles.append("社区教育参与者")
    if edu_roles:
        out["education_roles"] = edu_roles

    care: list[str] = []
    if facts["has_kids"] and age < 60:
        care.append("子女照料者")
    if age >= 50 and rng.random() < 0.5:
        care.append("长辈照料者（赡养老人）")
    if care:
        out["caregiving_roles"] = care

    if age >= 70:
        out["dependent_care_roles"] = "高龄，可能需要部分照护支持"
    elif age >= 60:
        out["dependent_care_roles"] = "基本自理，偶需家庭协助"

    if rng.random() < (0.5 if demo["urbanicity_label"] == "城市" else 0.35):
        pool = ["社区志愿者", "邻里互助成员", "文体社团成员"]
        if demo["religion"] not in _NO_RELIGION:
            pool.append("宗教团体成员")
        out["community_roles"] = [rng.choice(pool)]

    if "管理决策者" in work:
        out["work_authority_responsibility"] = "高：决策权与团队管理责任"
    elif "专业技术人员" in work:
        out["work_authority_responsibility"] = "中：专业自主权，责任集中于本职"
    elif age < 18:
        out["work_authority_responsibility"] = "低：主要责任在学业与自我管理"
    elif work[0] == "退休者":
        out["work_authority_responsibility"] = "低：已退出工作，责任限于自我管理"
    else:
        out["work_authority_responsibility"] = "低：执行既定流程，自主空间有限"

    n_roles = sum(
        len(out.get(k, []))
        for k in ("family_roles", "work_roles", "education_roles", "caregiving_roles", "community_roles")
    )
    if 30 <= age <= 55 and ("caregiving_roles" in out or facts["has_kids"]):
        out["role_conflict"] = "工作-家庭照料冲突（时间挤压与角色切换压力）"
    else:
        out["role_conflict"] = "角色负荷较轻，无明显角色冲突"
    out["role_load"] = "轻" if n_roles <= 2 else "中" if n_roles <= 4 else "重"

    items: list[str] = []
    for k in ("family_roles", "work_roles", "education_roles", "caregiving_roles", "community_roles"):
        for r in out.get(k, []):
            if r not in items:
                items.append(r)
    out["items"] = items
    return out


def _sample_sip(ctx, demo, prof, rng) -> dict[str, Any]:
    income = demo["income"]
    age = ctx["age"]
    out: dict[str, Any] = {}
    out["citizenship_nationality"] = demo["country_cn"]
    out["legal_residency_status"] = "本国公民" if rng.random() < 0.95 else "永久居民"
    out["socioeconomic_class"] = {
        "high": "中上层（收入高于当地均值）",
        "mid": "中等阶层",
        "low": "工薪/低收入阶层",
    }[income]
    out["social_status_prestige"] = (
        "学生身份，社会地位随家庭与学业表现"
        if age < 18
        else "受尊敬的职业身份，社区认可度高"
        if income == "high"
        else "普通职业身份，社会认可一般"
    )
    memberships: list[str] = []
    if rng.random() < 0.5:
        pool = (
            ["学校社团", "社区组织", "文体俱乐部"]
            if age < 18
            else ["行业协会", "工会", "宗教团体", "校友会", "社区组织", "文体俱乐部"]
        )
        memberships.append(rng.choice(pool))
        if rng.random() < 0.2:
            memberships.append(rng.choice([x for x in pool if x not in memberships]))
    if memberships:
        out["institutional_memberships"] = memberships
    out["civic_institutional_participation"] = (
        "尚未获得投票权，公共参与限于校园与社区活动"
        if age < 18
        else "参与投票与社区公共事务" if rng.random() < 0.4 else "较少参与公共事务"
    )
    out["healthcare_entitlement_access"] = {
        "high": "可负担商业保险，医疗可及性高",
        "mid": "基本覆盖公共医疗体系",
        "low": "主要依赖公共医疗，自付比例较高",
    }[income]
    out["service_access"] = {
        "城市": "公共服务网络密集，办事便利",
        "城镇": "公共服务基本覆盖，部分需进城办理",
        "农村": "公共服务稀疏，需远距离获取",
    }[demo["urbanicity_label"]]
    rights = "公民基本权利与法律保护普遍可及"
    if income == "low" and rng.random() < 0.4:
        rights += "，但法律维权成本较高"
    out["rights_access"] = rights
    out["discrimination_stigma_exposure"] = (
        "精神疾病污名暴露（隐瞒与社交评价压力）"
        if _is_clinical(ctx)
        else "无显著结构性歧视暴露"
    )
    out["justice_system_exposure"] = (
        "无司法接触" if rng.random() < 0.9 else rng.choice(["交通违法处理", "民事纠纷（合同/邻里）"])
    )
    return out


def _sample_culture_language(ctx, demo, prof, rng) -> dict[str, Any]:
    income = demo["income"]
    lang_primary = demo["language_cn"]
    out: dict[str, Any] = {}

    languages = [lang_primary]
    p_second = 0.55 if (income == "high" or ctx["education"] in ("本科", "硕士及以上")) else 0.25
    if rng.random() < p_second:
        languages.append("英语" if lang_primary != "英语" else "西班牙语")
    out["languages"] = languages

    religion = demo["religion"]
    if religion in _NO_RELIGION:
        out["religion_spirituality"] = "无宗教信仰，世俗生活方式，节庆以民俗形式延续"
    else:
        involvement = rng.choice(["经常性参与宗教活动", "节日性参与宗教活动", "名义上信奉，实际参与较少"])
        out["religion_spirituality"] = f"{religion}背景（{involvement}）"

    out["cultural_backgrounds"] = [demo["region_cn"], demo["ethnicity"]]
    out["enculturation_contexts"] = prof["enculturation"]
    out["customs_norms_exposure"] = prof["customs"]
    out["media_culture_exposure"] = {
        "high": "国际媒体与流媒体为主，信息接触面宽",
        "mid": "本地主流媒体与社交平台为主",
        "low": "电视与本地广播为主，国际内容接触少",
    }[income]
    pool = [
        t for t in prof["culture_pool"]
        if t not in _CULTURE_RELIGION_GATES or religion in _CULTURE_RELIGION_GATES[t]
    ]
    out["cultural_participation"] = list(rng.sample(pool, k=3))
    p_cross = 0.35 if (income == "high" or demo["urbanicity_label"] == "城市") else 0.12
    out["cross_cultural_experience"] = (
        "有跨国生活或旅行经历（工作/留学/务工）"
        if rng.random() < p_cross
        else "基本在本土生活，跨文化接触限于媒体与网络"
    )
    return out


def _sample_context_ecology(ctx, demo, prof, facts, rng) -> dict[str, Any]:
    income = demo["income"]
    urban = demo["urbanicity_label"]
    age = ctx["age"]
    marital = ctx["marital_status"]
    out: dict[str, Any] = {}

    out["neighborhood"] = {
        ("城市", "high"): "城市高档住宅区，配套完善",
        ("城市", "mid"): "城市普通居民区，生活配套齐全",
        ("城市", "low"): "城市老旧社区或城乡结合部",
        ("城镇", "high"): "城镇中心街区，沿街商业活跃",
        ("城镇", "mid"): "城镇街区，沿街商铺与居住混杂",
        ("城镇", "low"): "城镇边缘街区，设施老旧",
        ("农村", "high"): "农村较富裕村落，基础设施较好",
        ("农村", "mid"): "传统村落，基础设施一般",
        ("农村", "low"): "偏远村落，基础设施有限",
    }[(urban, income)]

    if age < 18:
        household = "与父母同住"
    elif marital in ("已婚", "再婚"):
        household = "核心家庭同住（与配偶及子女）" if facts["has_kids"] else "与配偶同住"
    elif marital == "丧偶" and facts["has_kids"]:
        household = "与子女同住（丧偶）"
    elif age < 30:
        household = "独居或合租"
    else:
        household = "独居"
    out["household_context"] = household

    if urban == "城市":
        if demo["region_key"] == "chinese":
            out["physical_environment"] = {
                "high": "高层/商品房小区，公共交通密集",
                "mid": "多层住宅区，公交覆盖",
                "low": "老旧小区/自建房，基础设施老旧",
            }[income]
        else:
            out["physical_environment"] = {
                "high": "高密度住宅区（公寓/联排住宅），公共交通密集",
                "mid": "居住区与商业混杂，公交/地铁覆盖",
                "low": "老旧街区或城郊聚居区，设施老化",
            }[income]
    elif urban == "城镇":
        out["physical_environment"] = "低层住宅与沿街铺面，道路功能混合"
    else:
        out["physical_environment"] = (
            "宅基地自建房，农田环绕"
            if demo["region_key"] == "chinese"
            else "低密度乡村聚居，农田环绕"
        )
    out["environment_climate"] = prof["climate"]
    out["economic_conditions"] = {
        "high": "家庭经济宽裕，消费与储蓄能力较强",
        "mid": "收支平衡，储蓄有限",
        "low": "经济压力较大，抗风险能力弱",
    }[income]
    out["labor_market"] = {
        "high": "竞争激烈的劳动力市场，机会多但压力大",
        "mid": "区域劳动力市场，供需基本平衡",
        "low": "本地劳动力市场，岗位选择有限",
    }[income]
    if ctx["education"] in ("本科", "硕士及以上"):
        out["education_system"] = "高等教育可及性较高，升学与继续教育渠道畅通"
    elif ctx["education"] in ("高中/中专", "大专"):
        out["education_system"] = "中等教育为主，升学渠道存在但竞争激烈"
    elif ctx["education"] == "未接受正式教育":
        out["education_system"] = "未经历正式学校教育，学习主要发生在生活与劳动中"
    elif age < 18:
        out["education_system"] = "基础教育阶段在读，教育环境受区域学校条件制约"
    else:
        out["education_system"] = "教育止于小学/初中阶段，继续教育渠道有限"
    out["healthcare_system"] = {
        "high": "医疗资源可及，可选择性高",
        "mid": "公共医疗体系覆盖，等待时间中等",
        "low": "医疗资源匮乏，自付压力大",
    }[income]
    out["gender_role_context"] = prof["gender_roles"]
    out["digital_platform_environment"] = {
        "high": "智能手机+高速网络，深度使用社交/流媒体/电商",
        "mid": "智能手机普及，社交平台日常使用",
        "low": "手机使用为主，互联网接入不稳定",
    }[income]

    events = ["2020年全球新冠大流行（封锁与远程生活冲击）"]
    if age >= 25:
        events.append("2008年全球金融危机（就业市场收紧）")
    if age >= 40:
        events.append("2010年代移动互联网普及（生活方式重构）")
    rk = demo["region_key"]
    if rk in ("western_european", "eastern_european") and age >= 35:
        events.append("2022年欧洲能源危机（通胀与能源价格冲击）")
    if rk == "latin_american" and age >= 30:
        events.append("2010年代拉美债务与通胀周期")
    if rk in ("south_asian", "southeast_asian", "african_sub_saharan", "west_asian", "central_asian") and age >= 25:
        events.append("2000年代快速城市化与基础设施扩张")
    out["historical_events"] = events[:4]

    out["policy_legal_context"] = {
        "high": "法治化营商环境，产权与合同保护较完善",
        "mid": "公共政策体系覆盖基本民生",
        "low": "社会保障网较薄，政策托底有限",
    }[income]
    out["regional_context"] = demo["region_cn"]
    out["school_work_institutions"] = (
        "公立学校体系（基础教育阶段）" if age < 18 else "所在行业用工单位与行业监管机构"
    )
    out["social_norms"] = prof["social_norms"]
    out["technology_media_environment"] = {
        "high": "数字化基础设施完善，智能设备普及",
        "mid": "主流数字服务覆盖",
        "low": "数字基础设施有限，功能机/低端机为主",
    }[income]
    out["urbanicity"] = urban

    contexts = ["家庭", "社区", "工作/学习场所"]
    if demo["religion"] not in _NO_RELIGION:
        contexts.append("宗教场所")
    if _is_clinical(ctx) or age >= 60:
        contexts.append("医疗系统")
    out["contexts"] = contexts
    return out


def _sample_rco(ctx, demo, prof, facts, rng) -> dict[str, Any]:
    income = demo["income"]
    urban = demo["urbanicity_label"]
    age = ctx["age"]
    marital = ctx["marital_status"]
    out: dict[str, Any] = {}

    out["material_resources"] = {
        "high": "房产/车辆等资产持有，物质条件充裕",
        "mid": "基本生活资料可及，大件消费依赖储蓄或信贷",
        "low": "物质条件有限，基本需求优先",
    }[income]
    if marital in ("已婚", "再婚") and facts["has_kids"]:
        out["care_resources"] = "家庭照护网络健全（配偶/子女分担）"
    elif marital in ("已婚", "再婚"):
        out["care_resources"] = "家庭照护网络可用（配偶分担）"
    elif facts["has_kids"]:
        out["care_resources"] = "家庭照护网络限于子女（无配偶同住，互惠有限）"
    else:
        out["care_resources"] = "照护资源主要依赖公共/付费服务"
    if age < 18:
        out["career_opportunities"] = "职业尚未起步，未来机会取决于教育水平"
        out["learning_opportunities"] = "在校接受正规教育，为主要学习渠道"
    else:
        out["career_opportunities"] = (
            "职业晋升与转型渠道较多"
            if ctx["education"] in ("本科", "硕士及以上")
            else "岗位流动以平级为主"
            if ctx["education"] in ("高中/中专", "大专")
            else "职业路径狭窄，晋升机会有限"
        )
        out["learning_opportunities"] = (
            "继续教育与职业培训渠道丰富"
            if ctx["education"] in ("本科", "硕士及以上")
            else "夜校/短期培训可及"
            if ctx["education"] in ("高中/中专", "大专")
            else "正规学习渠道有限，依赖工作经验积累"
        )
    out["institutional_resources"] = {
        "high": "可获取法律、金融等专业服务",
        "mid": "公共服务为主，专业服务偶尔使用",
        "low": "主要依赖免费公共服务与互助",
    }[income]
    if urban == "城市":
        out["mobility_options"] = {
            "high": "私家车+公共交通+网约车",
            "mid": "公共交通为主，偶尔网约车",
            "low": "公交/骑行/步行为主",
        }[income]
    elif urban == "城镇":
        out["mobility_options"] = "电动车/摩托+步行为主"
    else:
        out["mobility_options"] = "步行/自行车/农用车为主"
    out["social_resources"] = (
        "社会支持网络较强（家庭+社区）"
        if (marital in ("已婚", "再婚") or age < 30)
        else "社交圈较小，支持网络以亲属为主"
    )
    out["time_resources"] = (
        "时间相对充裕，受学业支配"
        if age < 18
        else "工作-家庭双轨，时间挤压明显"
        if age <= 40
        else "职业中后期，时间被职责占据"
        if age <= 59
        else "退休/半退休，时间自主性提高"
    )
    if urban == "城市":
        out["healthcare_access"] = "就近优质医疗可及" if income == "high" else "公共医疗可及，专科需转诊"
    elif urban == "城镇":
        out["healthcare_access"] = (
            "乡镇卫生院为主，大医院需进城"
            if demo["region_key"] == "chinese"
            else "基层医疗设施为主，专科照护需赴较大城市"
        )
    else:
        out["healthcare_access"] = (
            "村医/乡镇卫生所，长途就医常见"
            if demo["region_key"] == "chinese"
            else "医疗资源稀缺，长途就医常见"
        )

    barriers: list[str] = []
    if _is_clinical(ctx):
        barriers.append("症状负担影响工作/学习与社交参与")
    if income == "low":
        barriers.append("经济约束限制选择空间")
    if age >= 18 and ctx["education"] in ("小学", "初中", "未接受正式教育"):
        barriers.append("教育水平受限，信息获取与职业选择受限")
    if age >= 60:
        barriers.append("年龄相关的体力与机会限制")
    if not barriers:
        barriers = ["无明显结构性约束"]
    out["barriers_constraints"] = barriers

    out["resources"] = {
        "high": ["自有住房", "车辆", "商业保险"],
        "mid": ["自有住房或长期租赁", "公共交通"],
        "low": ["基本生活资料", "公共医疗"],
    }[income]
    out["constraints"] = list(barriers)
    return out


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def persona_context(persona: Any) -> dict[str, Any]:
    """Extract the legacy Persona fields the native sampler reasons over."""
    return {
        "persona_id": str(persona.id),
        "age": int(persona.age),
        "gender": persona.gender,
        "occupation": persona.occupation or "",
        "education": persona.education or "",
        "locale": persona.locale or "城镇",
        "marital_status": persona.marital_status or "未婚",
        "primary_diagnosis": persona.primary_diagnosis or "",
    }


def sample_context_fields(
    ctx: dict[str, Any], demo: dict[str, Any] | None = None, *, rng: random.Random | None = None
) -> dict[str, dict[str, Any]]:
    """Sample all 59 canonical concepts across the five fill domains.

    Returns ``{domain: {key: value}}``. The six relation_graph concepts are
    returned as flat label lists here (pool-card form);
    :func:`fill_ontology_native` converts them into kernel relations.

    ``demo`` is a demographics_intl.sample_demographics() dict; when None a
    China/Chinese baseline is used (legacy personas have no intl demo).
    """
    if rng is None:
        rng = _rng_for(str(ctx["persona_id"]))
    demo = dict(demo) if demo else _default_demo(ctx)
    prof = _profile(demo.get("region_key"))
    facts = _life_facts(ctx, rng)
    return {
        "roles": _sample_roles(ctx, demo, prof, facts, rng),
        "social_institutional_position": _sample_sip(ctx, demo, prof, rng),
        "culture_language": _sample_culture_language(ctx, demo, prof, rng),
        "context_ecology": _sample_context_ecology(ctx, demo, prof, facts, rng),
        "resources_constraints_opportunities": _sample_rco(ctx, demo, prof, facts, rng),
    }


def _make_relation(
    persona_id: str,
    canonical_path: str,
    predicate: str,
    entity_type: str,
    label: str,
    index: int,
    temporal: str,
) -> dict[str, Any]:
    label = str(label)
    digest = _digest(label)
    return {
        "relation_id": f"{persona_id}:native:{canonical_path}:{index}:{digest}",
        "canonical_path": canonical_path,
        "predicate": predicate,
        "subject": {"entity_id": persona_id, "entity_type": "person"},
        "object": {
            "entity_id": f"native:{entity_type}:{digest}",
            "entity_type": entity_type,
            "label": label,
            "source_system": "core.ontology_native_fill",
            "source_id": label,
        },
        "source_type": SOURCE_TYPE,
        "confidence": CONFIDENCE,
        "provenance": PROVENANCE,
        "temporal_class": temporal,
    }


def fill_ontology_native(
    kernel: PersonaKernel,
    demo: dict[str, Any] | None = None,
    *,
    persona: Any = None,
    rng: random.Random | None = None,
) -> PersonaKernel:
    """Populate the five fill domains of an existing PersonaKernel in place.

    ``persona`` is the legacy Persona the kernel was built from (it provides
    age/gender/occupation/... context); ``demo`` is the optional
    demographics_intl dict. Returns the same kernel, revalidated.
    """
    if persona is None:
        raise ValueError("fill_ontology_native requires the source legacy persona")
    ctx = persona_context(persona)
    if ctx["persona_id"] != kernel.persona_id:
        raise ValueError(
            f"persona.id {ctx['persona_id']!r} does not match kernel.persona_id {kernel.persona_id!r}"
        )
    if rng is None:
        rng = _rng_for(kernel.persona_id)
    data = sample_context_fields(ctx, demo, rng=rng)
    for domain, payload in data.items():
        temporal = TEMPORAL_CLASS[domain]
        for key, value in payload.items():
            if not value:
                continue
            path = f"{domain}.{key}"
            if path in RELATION_STORAGE:
                predicate, entity_type = RELATION_STORAGE[path]
                for index, label in enumerate(value, start=1):
                    kernel.relations.append(
                        _make_relation(kernel.persona_id, path, predicate, entity_type, label, index, temporal)
                    )
            else:
                kernel.set_value(domain, key, value, FieldMetadata(SOURCE_TYPE, CONFIDENCE, PROVENANCE, temporal))
    kernel.validate()
    return kernel
