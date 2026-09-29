#!/usr/bin/env python3
"""Regression-test the Multi-AI benchmark builder/analyzer with synthetic raters."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "multi_ai_benchmark" / "cases.json"


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def build_records(benchmark: dict, *, wrong_first: bool = False) -> dict[str, list[dict]]:
    outputs: dict[str, list[dict]] = {}
    for model_index in range(3):
        model_id = f"synthetic-{model_index + 1}"
        provider = f"synthetic-provider-{model_index + 1}"
        records = []
        for case_index, case in enumerate(benchmark["cases"]):
            annotations = []
            for fact_index, fact in enumerate(case["facts"]):
                gold = fact["gold"]
                domain = gold["canonical_domain"]
                if wrong_first and case_index == 0 and fact_index == 0:
                    domain = "development"
                annotations.append(
                    {
                        "fact_key": fact["fact_key"],
                        "canonical_domain": domain,
                        "knowledge_status": gold["knowledge_status"],
                        "kind": None,
                        "relation_predicate": None,
                        "source_type": None,
                        "confidence": 0.99,
                        "reason_short": "synthetic regression fixture",
                    }
                )
            checks = [
                {
                    "index": index,
                    "entailed": False,
                    "reason_short": "synthetic negative entailment fixture",
                }
                for index, _claim in enumerate(case["forbidden_inferences"])
            ]
            records.append(
                {
                    "benchmark_id": benchmark["benchmark_id"],
                    "ontology_version": benchmark["ontology_version"],
                    "run_id": "synthetic-regression",
                    "model_id": model_id,
                    "provider": "synthetic_adapter",
                    "family": provider,
                    "model": model_id,
                    "case_id": case["case_id"],
                    "theme": case["theme"],
                    "response": {
                        "annotations": annotations,
                        "forbidden_inference_checks": checks,
                    },
                    "error": None,
                }
            )
        outputs[model_id] = records
    return outputs


def write_outputs(directory: Path, outputs: dict[str, list[dict]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for model_id, records in outputs.items():
        path = directory / f"{model_id}.jsonl"
        path.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
            encoding="utf-8",
        )


def analyze(directory: Path, report_path: Path) -> dict:
    run(
        "scripts/analyze_multi_ai_benchmark.py",
        str(directory),
        "--json-out",
        str(report_path),
    )
    return json.loads(report_path.read_text(encoding="utf-8"))


def main() -> None:
    run("scripts/build_multi_ai_benchmark.py", "--check")
    benchmark = json.loads(CASES.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        perfect_dir = tmpdir / "perfect"
        write_outputs(perfect_dir, build_records(benchmark))
        perfect = analyze(perfect_dir, tmpdir / "perfect-report.json")
        assert perfect["tier_b1_passed"] is True
        assert not perfect["agreement_but_wrong"]
        assert perfect["agreement"]["canonical_domain"]["pairwise_agreement"] == 1.0
        assert perfect["agreement"]["canonical_domain"]["fleiss_kappa"] == 1.0

        wrong_dir = tmpdir / "agreement-wrong"
        write_outputs(wrong_dir, build_records(benchmark, wrong_first=True))
        wrong = analyze(wrong_dir, tmpdir / "wrong-report.json")
        assert wrong["tier_b1_passed"] is False
        assert len(wrong["agreement_but_wrong"]) == 1
        assert wrong["agreement_but_wrong"][0]["case_id"] == "ADV-001"
        assert wrong["agreement_but_wrong"][0]["fact_key"] == "birthplace"

    print("Multi-AI benchmark builder/analyzer regression: OK")


if __name__ == "__main__":
    main()
