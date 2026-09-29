#!/usr/bin/env python3
"""Repository-level release gate for Human Ontology v2.

This gate is intentionally standard-library only. It checks structural migration
readiness; GitHub Actions success is the outer gate for promotion.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology"

FORBIDDEN_STALE_TOKENS = (
    "2.0.0-rc1",
    "identity_affiliations",
    "education_work_economy",
)

SCAN_PATHS = (
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "skill" / "SKILL.md",
    ROOT / "core" / "human_ontology.py",
    ROOT / "core" / "persona_kernel.py",
    ROOT / "core" / "kernel_generator.py",
    ROOT / "core" / "legacy_adapter.py",
    ONTOLOGY / "README.md",
    ONTOLOGY / "HUMAN_ONTOLOGY_V2_ARCHITECTURE.md",
    ONTOLOGY / "HUMAN_ONTOLOGY_REVIEW.md",
    ONTOLOGY / "CONSUMER_CONTRACT.md",
    ONTOLOGY / "V1_V2_OVERLAP_AUDIT.md",
)


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    raise SystemExit(f"Release gate failed: {message}")


def main() -> None:
    v1 = load(ONTOLOGY / "human_ontology.v1.json")
    v2 = load(ONTOLOGY / "human_ontology.v2.json")
    migration = load(ONTOLOGY / "V1_TO_V2_MIGRATION.json")
    field_migration = load(ONTOLOGY / "V1_FIELD_MIGRATION.json")
    registry = load(ONTOLOGY / "CANONICAL_FIELD_REGISTRY.json")
    catalog = load(ONTOLOGY / "CANONICAL_CONCEPT_CATALOG.json")
    schema = load(ONTOLOGY / "persona_kernel.schema.json")
    evaluation_cqs = load(ROOT / "evaluation" / "competency_questions.json")
    evaluation_baseline = load(ROOT / "evaluation" / "baseline_machine_report.json")
    multi_ai_cases = load(ROOT / "evaluation" / "multi_ai_benchmark" / "cases.json")
    adversarial_cases = load(ROOT / "evaluation" / "adversarial_cases.json")
    multi_ai_models = load(
        ROOT / "evaluation" / "multi_ai_benchmark" / "models.example.json"
    )

    if v2["status"] != "release_candidate":
        fail("rc2 must remain release_candidate until the PR gate is explicitly promoted")
    version = v2["version"]
    for name, other in (
        ("axis migration", migration["to_version"]),
        ("field migration", field_migration["to_version"]),
        ("field registry", registry["version"]),
        ("concept catalog", catalog["version"]),
        ("kernel schema", schema["properties"]["ontology_version"]["const"]),
    ):
        if other != version:
            fail(f"{name} version {other!r} != ontology version {version!r}")

    expected = {
        f"{axis['id']}.{name}"
        for axis in v1["axes"]
        for name in (
            list(axis.get("subaxes", []))
            + [layer["id"] for layer in axis.get("layers", [])]
        )
    }
    actual = {item["legacy_path"] for item in field_migration["entries"]}
    if actual != expected:
        fail(
            f"field migration coverage mismatch: "
            f"missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )

    migration_targets = {
        target
        for item in field_migration["entries"]
        for target in item["canonical_targets"]
    }
    registry_paths = {item["canonical_path"] for item in registry["fields"]}
    catalog_paths = {item["canonical_path"] for item in catalog["concepts"]}
    expected_catalog = migration_targets | registry_paths
    if catalog_paths != expected_catalog:
        fail(
            f"concept catalog coverage mismatch: "
            f"missing={sorted(expected_catalog-catalog_paths)}, "
            f"extra={sorted(catalog_paths-expected_catalog)}"
        )
    if any(
        item["review_status"] == "reviewed" and not item.get("value_contract")
        for item in catalog["concepts"]
    ):
        fail("reviewed catalog concepts must declare value_contract")

    cq_total = len(evaluation_cqs["questions"])
    baseline_cq = evaluation_baseline["machine_competency_questions"]
    if evaluation_baseline["ontology_version"] != version:
        fail("evaluation baseline ontology version is stale")
    if baseline_cq["total"] != cq_total:
        fail(
            f"machine CQ baseline is stale: baseline={baseline_cq['total']}, current={cq_total}"
        )
    if baseline_cq["failed"] != 0 or baseline_cq["critical_failed"] != 0:
        fail("machine competency baseline contains failures")
    current_provisional_relation_count = sum(
        1
        for item in catalog["concepts"]
        if item.get("review_status") == "provisional_migrated"
        and item.get("kind") == "relation"
    )
    baseline_gap = evaluation_baseline["evaluation_assets"].get(
        "provisional_relation_leaves_pending_predicate_review"
    )
    if baseline_gap != current_provisional_relation_count:
        fail(
            "evaluation baseline provisional-relation count is stale: "
            f"baseline={baseline_gap}, current={current_provisional_relation_count}"
        )

    if multi_ai_cases["ontology_version"] != version:
        fail("multi-ai benchmark ontology version is stale")
    if multi_ai_cases["counts"]["cases"] != len(adversarial_cases["cases"]):
        fail("multi-ai benchmark case count drift")
    current_atomic = sum(len(case["expected"]) for case in adversarial_cases["cases"])
    if multi_ai_cases["counts"]["atomic_facts"] != current_atomic:
        fail("multi-ai benchmark atomic-fact count drift")
    current_forbidden = sum(
        len(case["forbidden_inferences"])
        for case in adversarial_cases["cases"]
    )
    if multi_ai_cases["counts"]["forbidden_inferences"] != current_forbidden:
        fail("multi-ai benchmark forbidden-inference count drift")
    if not multi_ai_cases.get("protocol", {}).get("gold_hidden_from_models"):
        fail("multi-ai benchmark must keep gold hidden from model prompts")
    model_entries = multi_ai_models.get("models", [])
    families = {
        item.get("family")
        for item in model_entries
        if item.get("enabled", True) and item.get("family")
    }
    if len(families) < 3:
        fail("multi-ai example config needs >=3 distinct families")
    ids = [item.get("id") for item in model_entries]
    if len(ids) != len(set(ids)):
        fail("multi-ai example config contains duplicate model ids")
    for item in model_entries:
        if "api_key" in item or "token" in item:
            fail("multi-ai example config must never contain literal secrets")
        if not item.get("api_key_env") or not item.get("model_env"):
            fail(f"multi-ai model entry lacks env-based secret/model config: {item.get('id')}")
        if not item.get("provider") or not item.get("family"):
            fail(f"multi-ai model entry lacks provider/family: {item.get('id')}")

    overlap = (ONTOLOGY / "V1_V2_OVERLAP_AUDIT.md").read_text(encoding="utf-8")
    if "| open |" in overlap.lower():
        fail("overlap audit still contains open rows")

    for path in SCAN_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_STALE_TOKENS:
            if token in text:
                fail(f"stale token {token!r} remains in {path.relative_to(ROOT)}")

    required = (
        ONTOLOGY / "CONSUMER_CONTRACT.md",
        ONTOLOGY / "CANONICAL_CONCEPT_CATALOG.json",
        ONTOLOGY / "domains" / "psychiatric_diagnosis.module.json",
        ROOT / "core" / "persona_kernel.py",
        ROOT / "core" / "kernel_generator.py",
        ROOT / "core" / "legacy_adapter.py",
        ROOT / "evaluation" / "README.md",
        ROOT / "evaluation" / "EVALUATION_PROTOCOL.md",
        ROOT / "evaluation" / "SCIENTIFIC_VALIDATION_GATE.md",
        ROOT / "evaluation" / "competency_questions.json",
        ROOT / "evaluation" / "adversarial_cases.json",
        ROOT / "evaluation" / "diversity_cases.json",
        ROOT / "evaluation" / "external_alignment_matrix.json",
        ROOT / "evaluation" / "baseline_machine_report.json",
        ROOT / "evaluation" / "multi_ai_benchmark" / "README.md",
        ROOT / "evaluation" / "multi_ai_benchmark" / "cases.json",
        ROOT / "evaluation" / "multi_ai_benchmark" / "models.example.json",
        ROOT / "evaluation" / "multi_ai_benchmark" / "output_schema.json",
        ROOT / "evaluation" / "multi_ai_benchmark" / "API_REFERENCES.md",
        ROOT / "evaluation" / "multi_ai_benchmark" / "REPORT.md",
        ROOT / "evaluation" / "multi_ai_benchmark" / "prompts" / "annotator_system.txt",
        ROOT / "evaluation" / "multi_ai_benchmark" / "prompts" / "critic_system.txt",
        ROOT / "scripts" / "evaluate_human_ontology.py",
        ROOT / "scripts" / "analyze_annotation_reliability.py",
        ROOT / "scripts" / "build_annotation_pack.py",
        ROOT / "scripts" / "build_multi_ai_benchmark.py",
        ROOT / "scripts" / "multi_ai_client.py",
        ROOT / "scripts" / "run_multi_ai_benchmark.py",
        ROOT / "scripts" / "analyze_multi_ai_benchmark.py",
        ROOT / "scripts" / "test_multi_ai_benchmark.py",
    )
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail(f"required v2 artifacts missing: {missing}")

    print(
        "Human Ontology v2 release gate: READY FOR CI "
        f"({version}; {len(v2['canonical_domains'])} domains; "
        f"{len(field_migration['entries'])} migrated v1 fields; "
        f"{multi_ai_cases['counts']['cases']} Multi-AI adversarial cases)"
    )


if __name__ == "__main__":
    main()
