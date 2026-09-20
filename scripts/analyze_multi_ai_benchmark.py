#!/usr/bin/env python3
"""Analyze Multi-AI Tier-B1 ontology benchmark outputs."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluation" / "multi_ai_benchmark"
CASES = EVAL / "cases.json"

DIMS = (
    "canonical_domain",
    "knowledge_status",
    "kind",
    "relation_predicate",
    "source_type",
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            rows.append(row)
    return rows


def norm(value: Any) -> str:
    if value is None:
        return "<NULL>"
    return str(value)


def pairwise_agreement(groups: dict[str, list[str]]) -> float | None:
    agree = 0
    total = 0
    for values in groups.values():
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                total += 1
                agree += int(values[i] == values[j])
    return None if not total else agree / total


def fleiss_kappa(groups: dict[str, list[str]]) -> float | None:
    usable = [values for values in groups.values() if len(values) >= 2]
    if not usable:
        return None
    n_values = {len(values) for values in usable}
    if len(n_values) != 1:
        return None
    n = next(iter(n_values))
    categories = sorted({value for values in usable for value in values})
    if not categories:
        return None
    if len(categories) == 1:
        return 1.0

    N = len(usable)
    totals = Counter(value for values in usable for value in values)
    p = {cat: totals[cat] / (N * n) for cat in categories}
    pe = sum(v * v for v in p.values())

    p_items = []
    for values in usable:
        counts = Counter(values)
        numerator = sum(count * count for count in counts.values()) - n
        p_items.append(numerator / (n * (n - 1)))
    pbar = sum(p_items) / N
    if math.isclose(pe, 1.0):
        return 1.0
    return (pbar - pe) / (1.0 - pe)


def majority(values: list[str]) -> str | None:
    if not values:
        return None
    counts = Counter(values)
    top = counts.most_common()
    if len(top) > 1 and top[0][1] == top[1][1]:
        return None
    return top[0][0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("outputs_dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--min-families", "--min-providers", dest="min_families", type=int, default=3)
    args = parser.parse_args()

    benchmark = load_json(CASES)
    case_map = {case["case_id"]: case for case in benchmark["cases"]}
    gold = {}
    for case in benchmark["cases"]:
        for fact in case["facts"]:
            gold[(case["case_id"], fact["fact_key"])] = fact["gold"]

    files = sorted(args.outputs_dir.glob("*.jsonl"))
    if not files:
        nested = sorted(args.outputs_dir.glob("*/*.jsonl"))
        files = nested
    if not files:
        raise SystemExit(f"No JSONL model outputs found under {args.outputs_dir}")

    records = []
    for path in files:
        records.extend(load_jsonl(path))

    valid_records = [r for r in records if r.get("response") and not r.get("error")]
    model_meta = {}
    for record in records:
        model_meta[record["model_id"]] = {
            "provider": record.get("provider"),
            "family": record.get("family") or record.get("provider"),
            "model": record.get("model"),
        }

    expected_case_count = len(benchmark["cases"])
    model_case_counts = Counter(r["model_id"] for r in valid_records)
    completeness_by_model = {
        model_id: model_case_counts[model_id] / expected_case_count
        for model_id in model_meta
    }

    flattened = []
    forbidden_rows = []
    for record in valid_records:
        case_id = record["case_id"]
        response = record["response"]
        for ann in response.get("annotations", []):
            flattened.append(
                {
                    "model_id": record["model_id"],
                    "provider": record.get("provider"),
                    "family": record.get("family") or record.get("provider"),
                    "model": record.get("model"),
                    "case_id": case_id,
                    "theme": record.get("theme"),
                    **ann,
                }
            )
        for check in response.get("forbidden_inference_checks", []):
            forbidden_rows.append(
                {
                    "model_id": record["model_id"],
                    "case_id": case_id,
                    "theme": record.get("theme"),
                    "index": check["index"],
                    "entailed": bool(check["entailed"]),
                }
            )

    per_model = {}
    for model_id in model_meta:
        rows = [r for r in flattened if r["model_id"] == model_id]
        correct = 0
        scored = 0
        knowledge_correct = 0
        for row in rows:
            target = gold.get((row["case_id"], row["fact_key"]))
            if target is None:
                continue
            scored += 1
            if row.get("canonical_domain") == target["canonical_domain"]:
                correct += 1
            if row.get("knowledge_status") == target["knowledge_status"]:
                knowledge_correct += 1
        fp_rows = [r for r in forbidden_rows if r["model_id"] == model_id]
        fps = sum(r["entailed"] for r in fp_rows)
        per_model[model_id] = {
            **model_meta[model_id],
            "response_completeness": round(completeness_by_model.get(model_id, 0.0), 6),
            "scored_atomic_facts": scored,
            "domain_accuracy": None if not scored else round(correct / scored, 6),
            "knowledge_status_accuracy": None if not scored else round(knowledge_correct / scored, 6),
            "forbidden_checks": len(fp_rows),
            "forbidden_false_positives": fps,
            "forbidden_false_positive_rate": None if not fp_rows else round(fps / len(fp_rows), 6),
        }

    agreement = {}
    for dim in DIMS:
        groups = defaultdict(list)
        for row in flattened:
            key = f"{row['case_id']}::{row['fact_key']}"
            groups[key].append(norm(row.get(dim)))
        pa = pairwise_agreement(groups)
        fk = fleiss_kappa(groups)
        agreement[dim] = {
            "pairwise_agreement": None if pa is None else round(pa, 6),
            "fleiss_kappa": None if fk is None else round(fk, 6),
            "items": len(groups),
        }

    by_item = defaultdict(list)
    for row in flattened:
        by_item[(row["case_id"], row["fact_key"])].append(row)

    consensus_correct = 0
    consensus_scored = 0
    agreement_but_wrong = []
    for key, rows in sorted(by_item.items()):
        values = [norm(row.get("canonical_domain")) for row in rows]
        consensus = majority(values)
        target = gold.get(key)
        if target is None or consensus is None:
            continue
        consensus_scored += 1
        target_norm = norm(target["canonical_domain"])
        if consensus == target_norm:
            consensus_correct += 1
        unique = set(values)
        if len(unique) == 1 and next(iter(unique)) != target_norm and len(rows) >= 2:
            agreement_but_wrong.append(
                {
                    "case_id": key[0],
                    "fact_key": key[1],
                    "theme": rows[0].get("theme"),
                    "agreed_domain": None if next(iter(unique)) == "<NULL>" else next(iter(unique)),
                    "gold_domain": target["canonical_domain"],
                    "models": [row["model_id"] for row in rows],
                }
            )

    theme_stats = {}
    themes = sorted({case["theme"] for case in benchmark["cases"]})
    for theme in themes:
        rows = [r for r in flattened if r.get("theme") == theme]
        scored = correct = 0
        for row in rows:
            target = gold.get((row["case_id"], row["fact_key"]))
            if target is None:
                continue
            scored += 1
            correct += int(row.get("canonical_domain") == target["canonical_domain"])
        checks = [r for r in forbidden_rows if r.get("theme") == theme]
        fps = sum(r["entailed"] for r in checks)
        theme_stats[theme] = {
            "domain_accuracy": None if not scored else round(correct / scored, 6),
            "forbidden_false_positive_rate": None if not checks else round(fps / len(checks), 6),
            "atomic_model_judgments": scored,
        }

    families = {meta["family"] for meta in model_meta.values() if meta.get("family")}
    completeness = (
        sum(completeness_by_model.values()) / len(completeness_by_model)
        if completeness_by_model else 0.0
    )
    domain_pa = agreement["canonical_domain"]["pairwise_agreement"]
    domain_fk = agreement["canonical_domain"]["fleiss_kappa"]
    model_accuracy_ok = all(
        stats["domain_accuracy"] is not None and stats["domain_accuracy"] >= 0.90
        for stats in per_model.values()
    )
    fp_ok = all(
        stats["forbidden_false_positive_rate"] is not None
        and stats["forbidden_false_positive_rate"] <= 0.05
        for stats in per_model.values()
    )
    gate = {
        "model_families_at_least_3": len(families) >= args.min_families,
        "mean_response_completeness_gte_0_95": completeness >= 0.95,
        "domain_pairwise_agreement_gte_0_80": domain_pa is not None and domain_pa >= 0.80,
        "domain_fleiss_kappa_gte_0_80": domain_fk is not None and domain_fk >= 0.80,
        "every_model_domain_accuracy_gte_0_90": model_accuracy_ok,
        "every_model_forbidden_fp_rate_lte_0_05": fp_ok,
        "agreement_but_wrong_zero": len(agreement_but_wrong) == 0,
    }

    report = {
        "benchmark_id": benchmark["benchmark_id"],
        "ontology_version": benchmark["ontology_version"],
        "models": model_meta,
        "family_count": len(families),
        "families": sorted(families),
        "records_total": len(records),
        "records_valid": len(valid_records),
        "mean_response_completeness": round(completeness, 6),
        "per_model": per_model,
        "agreement": agreement,
        "consensus_domain_accuracy": (
            None if not consensus_scored else round(consensus_correct / consensus_scored, 6)
        ),
        "agreement_but_wrong": agreement_but_wrong,
        "theme_stats": theme_stats,
        "tier_b1_gate": gate,
        "tier_b1_passed": all(gate.values()),
        "interpretation": (
            "Cross-model agreement is not human/expert validation. "
            "High agreement can reflect correlated model bias, so gold accuracy and "
            "agreement-but-wrong are reported separately."
        ),
    }

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.md_out:
        lines = [
            "# Multi-AI Benchmark Report",
            "",
            f"- Tier B1 passed: **{report['tier_b1_passed']}**",
            f"- Model families: {len(families)} ({', '.join(sorted(families))})",
            f"- Mean response completeness: {report['mean_response_completeness']:.3f}",
            f"- Domain pairwise agreement: {domain_pa if domain_pa is not None else 'NA'}",
            f"- Domain Fleiss kappa: {domain_fk if domain_fk is not None else 'NA'}",
            f"- Consensus domain accuracy: {report['consensus_domain_accuracy']}",
            f"- Agreement-but-wrong items: {len(agreement_but_wrong)}",
            "",
            "## Per model",
            "",
            "| Model | Provider | Domain accuracy | Knowledge accuracy | Forbidden FP rate | Completeness |",
            "|---|---|---:|---:|---:|---:|",
        ]
        for model_id, stats in sorted(per_model.items()):
            lines.append(
                f"| {model_id} | {stats['provider']} | {stats['domain_accuracy']} | "
                f"{stats['knowledge_status_accuracy']} | "
                f"{stats['forbidden_false_positive_rate']} | "
                f"{stats['response_completeness']} |"
            )
        lines += [
            "",
            "## Gate",
            "",
        ]
        for key, value in gate.items():
            lines.append(f"- [{'x' if value else ' '}] {key}")
        if agreement_but_wrong:
            lines += ["", "## Agreement but wrong", ""]
            for item in agreement_but_wrong:
                lines.append(
                    f"- {item['case_id']} / {item['fact_key']}: "
                    f"all valid models -> {item['agreed_domain']!r}; "
                    f"gold -> {item['gold_domain']!r}"
                )
        args.md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
