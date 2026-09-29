#!/usr/bin/env python3
"""Build/check the deterministic Multi-AI Tier-B1 benchmark cases."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evaluation" / "adversarial_cases.json"
OUT = ROOT / "evaluation" / "multi_ai_benchmark" / "cases.json"


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build() -> dict:
    source = load(SOURCE)
    cases = []
    atomic_count = 0
    for case in source["cases"]:
        facts = []
        for index, pair in enumerate(case["expected"], start=1):
            fact_key, expected_domain = pair
            atomic_count += 1
            if expected_domain == "unknown":
                gold_domain = None
                gold_knowledge_status = "unknown"
            else:
                gold_domain = expected_domain
                gold_knowledge_status = "known"
            facts.append(
                {
                    "fact_id": f"{case['id']}-F{index:02d}",
                    "fact_key": fact_key,
                    "gold": {
                        "canonical_domain": gold_domain,
                        "knowledge_status": gold_knowledge_status,
                    },
                }
            )
        cases.append(
            {
                "case_id": case["id"],
                "theme": case["theme"],
                "vignette": case["vignette"],
                "facts": facts,
                "forbidden_inferences": list(case["forbidden_inferences"]),
            }
        )
    return {
        "benchmark_id": "human-ontology-multi-ai-tier-b1",
        "ontology_version": source["version"],
        "source_asset": "evaluation/adversarial_cases.json",
        "protocol": {
            "gold_hidden_from_models": True,
            "same_prompt_contract_across_models": True,
            "forbidden_inferences_are_candidate_entailment_checks": True,
            "primary_unit": "case",
        },
        "counts": {
            "cases": len(cases),
            "atomic_facts": atomic_count,
            "forbidden_inferences": sum(len(c["forbidden_inferences"]) for c in cases),
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        actual = OUT.read_text(encoding="utf-8") if OUT.exists() else None
        if actual != expected:
            raise SystemExit(
                "Multi-AI benchmark cases are stale; "
                "run scripts/build_multi_ai_benchmark.py"
            )
        print("Multi-AI benchmark case drift check: OK")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(expected, encoding="utf-8")
    payload = build()
    print(
        f"Wrote {payload['counts']['cases']} cases / "
        f"{payload['counts']['atomic_facts']} atomic facts / "
        f"{payload['counts']['forbidden_inferences']} forbidden-inference checks"
    )


if __name__ == "__main__":
    main()
