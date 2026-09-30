"""Build the full international persona pool for the table + dashboard pages.

Produces ONE JSON file (web/pool.json) — a large, stratified, deterministic
pool intended as a "whole-human, all-industry" database:

  * 11 diagnoses: 无精神障碍（健康）(~30%) + 10 archetype-covered clinical
    diagnoses (~7% each). Age/gender/education are sampled by the engine per
    diagnosis (realistic epidemiology), not forced.
  * 52 countries, all covered (>= 1 each) with realistic population weighting.
  * Per persona: the 23-field display card + an international demographics
    block (name / country / continent / region / language / religion /
    ethnicity / income / urbanicity) so the pool is genuinely global.
  * Per persona: an "ontology" block — the five ontology-native sampled
    domains (roles / social_institutional_position / culture_language /
    context_ecology / resources_constraints_opportunities, 59 canonical
    concepts) from core.ontology_native_fill, sampled on an independent
    fourth RNG stream so the existing card + demo fields stay byte-identical.

Deterministic: given the master seed and N the pool is byte-for-byte
reproducible.  Pure stdlib.

Run:
    python scripts/make_full_pool.py            # default N = 5000
    python scripts/make_full_pool.py --n 8000    # custom size

Output:
    web/pool.json
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

# --- Determinism guard (defense in depth) ------------------------------------
# The engine's sampling path is audited to be hash-independent: the only
# order-sensitive set iteration (personality.sample_tags_from_ocean) sorts
# before shuffling, and every other set() in core/ is membership-only. The
# guard is kept as belt-and-braces: it pins PYTHONHASHSEED=0 by re-exec'ing
# exactly once, so any FUTURE hash-ordered sampling path cannot silently break
# byte-for-byte pool reproducibility on any machine / CI.
if os.environ.get("PYTHONHASHSEED") != "0":
    os.environ["PYTHONHASHSEED"] = "0"
    os.execv(sys.executable, [sys.executable] + sys.argv)

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from core import PersonaGenerator  # noqa: E402
from core import demographics_intl as demo  # noqa: E402
from core import ontology_native_fill as ofill  # noqa: E402

OUT_PATH = os.path.join(_REPO, "web", "pool.json")

# ---------------------------------------------------------------------------
# Stratification config
# ---------------------------------------------------------------------------
HEALTHY = "无精神障碍（健康）"
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
ALL_DIAGNOSES = [HEALTHY] + DIAGNOSES
HEALTHY_WEIGHT = 0.30
CLINICAL_WEIGHT = 0.07  # x10 -> 0.70 ; total = 1.00
DIAG_WEIGHTS = [HEALTHY_WEIGHT] + [CLINICAL_WEIGHT] * len(DIAGNOSES)

MASTER_SEED = 20260930
DEFAULT_N = 5000

# Demographics keys attached to each card (authoritative, country-based).
_DEMO_KEYS = (
    "name", "country_code", "country_cn", "country_en", "continent",
    "region_cn", "language_cn", "religion", "ethnicity", "income",
    "urbanicity",
)


def _persona_to_card(p) -> dict:
    """Project a Persona onto a compact display card (same fields as showcase)."""
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


def _build_sequences(n: int):
    """Deterministic (diagnosis, country_code) assignment for the pool.

    * diagnosis: weighted sample (healthy 30%, clinical 7% each).
    * country: every one of the 52 countries appears at least once (first pass),
      the rest are population-weighted; the result is shuffled for a natural mix.
    """
    rng_seq = random.Random(MASTER_SEED + 2)
    diag_seq = rng_seq.choices(ALL_DIAGNOSES, weights=DIAG_WEIGHTS, k=n)

    codes = [c["code"] for c in demo.COUNTRIES]
    weights = [c["w"] for c in demo.COUNTRIES]
    country_seq = list(codes)  # guarantee full coverage (>= 1 each)
    if n > len(codes):
        country_seq += rng_seq.choices(codes, weights=weights, k=n - len(codes))
    rng_seq.shuffle(country_seq)
    return diag_seq, country_seq


def _tally(values) -> dict:
    out: dict = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], str(kv[0]))))


def build_pool(n: int) -> dict:
    gen = PersonaGenerator(rng_seed=MASTER_SEED)
    rng_demo = random.Random(MASTER_SEED + 1)
    rng_fill = random.Random(MASTER_SEED + 3)  # independent stream for the 5 ontology-native domains
    diag_seq, country_seq = _build_sequences(n)

    personas = []
    for i in range(n):
        p = gen.generate(primary_diagnosis=diag_seq[i])
        d = demo.sample_demographics(rng_demo, country_code=country_seq[i], gender=p.gender)
        card = _persona_to_card(p)
        for k in _DEMO_KEYS:
            card[k] = d[k]
        ctx = ofill.persona_context(p)
        card["ontology"] = ofill.sample_context_fields(ctx, d, rng=rng_fill)
        personas.append(card)

    age_bins: dict = {}
    for c in personas:
        b = (c["age"] // 10) * 10
        age_bins[b] = age_bins.get(b, 0) + 1
    age_bins = dict(sorted(age_bins.items()))

    coverage = {
        "diagnoses": _tally([c["primary_diagnosis"] for c in personas]),
        "genders": _tally([c["gender"] for c in personas]),
        "continents": _tally([c["continent"] for c in personas]),
        "countries": _tally([c["country_code"] for c in personas]),
        "occupations": _tally([c["occupation"] for c in personas]),
        "education": _tally([c["education"] for c in personas]),
        "income": _tally([c["income"] for c in personas]),
        "locale": _tally([c["locale"] for c in personas]),
        "age_bins": age_bins,
        "ontology_domains": sorted({d for c in personas for d in c["ontology"]}),
        "ontology_concepts_covered": len(
            {f"{d}.{k}" for c in personas for d, pl in c["ontology"].items() for k in pl}
        ),
        "ontology_concept_total": 59,
    }

    return {
        "generated_by": "make_full_pool.py",
        "engine_version": "2.0.0",
        "master_seed": MASTER_SEED,
        "persona_count": n,
        "country_count": len(demo.COUNTRIES),
        "diagnosis_count": len(ALL_DIAGNOSES),
        "stratification": {
            "healthy_weight": HEALTHY_WEIGHT,
            "clinical_weight_each": CLINICAL_WEIGHT,
            "age_gender_education": "sampled by engine per diagnosis (not forced)",
        },
        "coverage": coverage,
        "personas": personas,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build web/pool.json (full international pool)")
    ap.add_argument("--n", type=int, default=DEFAULT_N, help="pool size (default 5000)")
    args = ap.parse_args()

    payload = build_pool(args.n)
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

    cov = payload["coverage"]
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"pool.json written: {payload['persona_count']} personas "
          f"({size_kb:.0f} KB) -> {os.path.relpath(OUT_PATH, _REPO)}")
    print(f"  diagnoses  : {len(cov['diagnoses'])} (healthy={cov['diagnoses'].get(HEALTHY, 0)})")
    print(f"  countries  : {len(cov['countries'])} / {payload['country_count']}")
    print(f"  genders    : {cov['genders']}")
    print(f"  top5 cc    : {list(cov['countries'].items())[:5]}")
    print(f"  age bins   : {cov['age_bins']}")
    print(f"  ontology   : {len(cov['ontology_domains'])}/5 domains, "
          f"{cov['ontology_concepts_covered']}/{cov['ontology_concept_total']} concepts")


if __name__ == "__main__":
    main()
