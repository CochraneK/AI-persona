#!/usr/bin/env python3
"""Evaluate Human Ontology v2 scientific-evaluation assets.

This script intentionally evaluates only machine-checkable regression evidence.
It does not convert missing independent human evidence into a pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = ROOT / "ontology"
EVAL_DIR = ROOT / "evaluation"


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _domain_map(ontology: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in ontology["canonical_domains"]}


def _registry_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["concept"]: item for item in registry["fields"]}


def _catalog_path_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["canonical_path"]: item for item in catalog["concepts"]}


def evaluate_question(
    question: dict[str, Any],
    *,
    ontology: dict[str, Any],
    registry: dict[str, Any],
    catalog: dict[str, Any],
) -> tuple[bool, str]:
    assertion = question["assertion"]
    kind = assertion["type"]
    domains = _domain_map(ontology)
    fields = _registry_map(registry)
    catalog_paths = _catalog_path_map(catalog)

    if kind == "domain_exists":
        ok = assertion["domain"] in domains
        return ok, "domain exists" if ok else "missing domain"

    if kind == "domain_question_nonempty":
        domain = domains.get(assertion["domain"])
        ok = bool(domain and str(domain.get("question", "")).strip())
        return ok, "competency question present" if ok else "missing domain competency question"

    if kind == "concept_path":
        field = fields.get(assertion["concept"])
        ok = bool(field and field.get("canonical_path") == assertion["path"])
        return ok, (
            "canonical path matches"
            if ok
            else f"expected {assertion['path']!r}, got {None if field is None else field.get('canonical_path')!r}"
        )

    if kind == "concept_kind":
        field = fields.get(assertion["concept"])
        ok = bool(field and field.get("kind") == assertion["kind"])
        return ok, (
            "kind matches"
            if ok
            else f"expected {assertion['kind']!r}, got {None if field is None else field.get('kind')!r}"
        )

    if kind == "concept_storage":
        field = fields.get(assertion["concept"])
        ok = bool(field and field.get("storage") == assertion["storage"])
        return ok, (
            "storage matches"
            if ok
            else f"expected {assertion['storage']!r}, got {None if field is None else field.get('storage')!r}"
        )

    if kind == "concept_relation_predicate":
        field = fields.get(assertion["concept"])
        actual = None if field is None else field.get("relation_predicate")
        ok = actual == assertion["predicate"]
        return ok, (
            "relation predicate matches"
            if ok
            else f"expected {assertion['predicate']!r}, got {actual!r}"
        )

    if kind == "relation_targets":
        rule = ontology.get("relation_constraints", {}).get(assertion["predicate"])
        actual = sorted(rule.get("object_entity_types", [])) if rule else []
        expected = sorted(assertion["object_entity_types"])
        ok = actual == expected
        return ok, "target types match" if ok else f"expected {expected}, got {actual}"

    if kind == "source_type_exists":
        actual = set(ontology["field_metadata_contract"]["source_type_values"])
        ok = assertion["source_type"] in actual
        return ok, "source type represented" if ok else "source type missing"

    if kind == "catalog_path_domain":
        item = catalog_paths.get(assertion["path"])
        actual = None if item is None else item.get("domain")
        ok = actual == assertion["domain"]
        return ok, "semantic home matches" if ok else f"expected domain {assertion['domain']!r}, got {actual!r}"

    raise ValueError(f"Unsupported competency-question assertion type: {kind}")


def evaluate_assets() -> dict[str, Any]:
    ontology = load(ONTOLOGY_DIR / "human_ontology.v2.json")
    registry = load(ONTOLOGY_DIR / "CANONICAL_FIELD_REGISTRY.json")
    catalog = load(ONTOLOGY_DIR / "CANONICAL_CONCEPT_CATALOG.json")
    cqs = load(EVAL_DIR / "competency_questions.json")
    adversarial = load(EVAL_DIR / "adversarial_cases.json")
    diversity = load(EVAL_DIR / "diversity_cases.json")
    external = load(EVAL_DIR / "external_alignment_matrix.json")

    results = []
    for question in cqs["questions"]:
        passed, detail = evaluate_question(
            question,
            ontology=ontology,
            registry=registry,
            catalog=catalog,
        )
        results.append(
            {
                "id": question["id"],
                "category": question["category"],
                "critical": question["critical"],
                "passed": passed,
                "detail": detail,
            }
        )

    total = len(results)
    passed = sum(item["passed"] for item in results)
    critical = [item for item in results if item["critical"]]
    critical_passed = sum(item["passed"] for item in critical)
    critical_failures = [item for item in critical if not item["passed"]]

    categories: dict[str, dict[str, int]] = {}
    for item in results:
        bucket = categories.setdefault(item["category"], {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(item["passed"])

    adversarial_cases = adversarial["cases"]
    diversity_cases = diversity["cases"]
    adv_ids = [item["id"] for item in adversarial_cases]
    div_ids = [item["id"] for item in diversity_cases]
    assert len(adv_ids) == len(set(adv_ids)), "duplicate adversarial case IDs"
    assert len(div_ids) == len(set(div_ids)), "duplicate diversity case IDs"

    for case in adversarial_cases:
        assert case.get("theme")
        assert case.get("vignette")
        assert case.get("expected")
        assert case.get("forbidden_inferences")
    for case in diversity_cases:
        assert case.get("theme")
        assert case.get("vignette")
        assert case.get("required_review")
        assert case.get("status")

    external_ids = [item["id"] for item in external["sources"]]
    assert len(external_ids) == len(set(external_ids)), "duplicate external source IDs"

    reviewed = [item for item in catalog["concepts"] if item["review_status"] == "reviewed"]
    provisional = [item for item in catalog["concepts"] if item["review_status"] == "provisional_migrated"]
    provisional_relations = [
        item for item in provisional
        if item.get("kind") == "relation"
    ]

    machine_pass_rate = passed / total if total else 0.0
    critical_pass_rate = critical_passed / len(critical) if critical else 0.0

    return {
        "ontology_version": ontology["version"],
        "evidence_scope": "machine_regression_only",
        "machine_competency_questions": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(machine_pass_rate, 6),
            "critical_total": len(critical),
            "critical_passed": critical_passed,
            "critical_failed": len(critical_failures),
            "critical_pass_rate": round(critical_pass_rate, 6),
            "categories": categories,
            "failures": [item for item in results if not item["passed"]],
        },
        "evaluation_assets": {
            "adversarial_cases": len(adversarial_cases),
            "diversity_cases": len(diversity_cases),
            "external_sources": len(external_ids),
            "reviewed_concepts": len(reviewed),
            "provisional_concepts": len(provisional),
            "provisional_relation_leaves_pending_predicate_review": len(provisional_relations),
        },
        "scientific_evidence_state": {
            "formal_structural": "partial",
            "machine_cq": "passed_machine" if not critical_failures and machine_pass_rate >= 0.95 else "failed",
            "independent_cq": "not_tested",
            "semantic_interrater_reliability": "not_tested",
            "external_term_alignment": "partial",
            "diversity_independent_adjudication": "not_tested",
            "pragmatic_p003": "not_tested",
            "pragmatic_ai_ques": "not_tested",
            "rdf_owl_reasoner": "not_tested",
            "shacl": "not_tested",
            "fair_external_assessment": "not_tested",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Print machine report as JSON.")
    parser.add_argument("--out", type=Path, help="Write report JSON to this path.")
    args = parser.parse_args()

    report = evaluate_assets()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        cq = report["machine_competency_questions"]
        assets = report["evaluation_assets"]
        print(
            "Human Ontology scientific-evaluation machine gate: "
            f"{cq['passed']}/{cq['total']} CQs passed; "
            f"{cq['critical_passed']}/{cq['critical_total']} critical; "
            f"{assets['adversarial_cases']} adversarial cases; "
            f"{assets['diversity_cases']} diversity cases."
        )
        print("Independent scientific evidence remains explicitly NOT TESTED where applicable.")

    cq = report["machine_competency_questions"]
    if cq["critical_failed"] or cq["pass_rate"] < 0.95:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
