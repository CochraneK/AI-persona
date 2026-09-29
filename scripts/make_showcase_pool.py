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

import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from core import PersonaGenerator  # noqa: E402

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
        domain_rows.append({
            "id": did,
            "zh": zh_label,
            "temporal_class": temporal,
            "zh_class": TEMPORAL_ZH.get(temporal, temporal),
            "question": d.get("question", ""),
            "zh_question": zh_question,
            "concepts": per_domain.get(did, 0),
            "concept_names": per_domain_names.get(did, []),
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
            pool.append(card)
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
