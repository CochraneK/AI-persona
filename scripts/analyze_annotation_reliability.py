#!/usr/bin/env python3
"""Analyze inter-rater agreement for Human Ontology semantic annotations.

Standard-library only. Reports exact pairwise agreement for all designs and
Fleiss' kappa when every item has the same number of non-missing ratings.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

DIMENSIONS = (
    "canonical_home",
    "kind",
    "temporal_class",
    "relation_predicate",
    "source_type",
)


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def item_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("case_id", "").strip(), row.get("atomic_fact_id", "").strip()


def nonmissing(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def pairwise_agreement(groups: dict[tuple[str, str], list[str]]) -> tuple[int, int, float | None]:
    agree = 0
    total = 0
    for values in groups.values():
        for a, b in itertools.combinations(values, 2):
            total += 1
            agree += int(a == b)
    return agree, total, (agree / total if total else None)


def fleiss_kappa(groups: dict[tuple[str, str], list[str]]) -> float | None:
    usable = [values for values in groups.values() if len(values) >= 2]
    if not usable:
        return None
    n_values = {len(values) for values in usable}
    if len(n_values) != 1:
        return None
    n = next(iter(n_values))
    if n < 2:
        return None

    categories = sorted({value for values in usable for value in values})
    if len(categories) < 2:
        return 1.0

    N = len(usable)
    category_totals = Counter(value for values in usable for value in values)
    p = {cat: category_totals[cat] / (N * n) for cat in categories}
    P_e = sum(value * value for value in p.values())

    P_i = []
    for values in usable:
        counts = Counter(values)
        numerator = sum(count * count for count in counts.values()) - n
        P_i.append(numerator / (n * (n - 1)))
    P_bar = sum(P_i) / N

    if P_e == 1.0:
        return 1.0
    return (P_bar - P_e) / (1.0 - P_e)


def analyze(rows: list[dict[str, str]]) -> dict:
    result = {
        "rows": len(rows),
        "annotators": sorted({row.get("annotator_id", "").strip() for row in rows if row.get("annotator_id", "").strip()}),
        "dimensions": {},
        "interpretation_note": (
            "Fleiss' kappa is reported only for balanced items with equal non-missing rater counts. "
            "Project thresholds are engineering review targets, not universal psychometric laws."
        ),
    }

    for dimension in DIMENSIONS:
        groups: dict[tuple[str, str], list[str]] = defaultdict(list)
        for row in rows:
            value = nonmissing(row.get(dimension))
            key = item_key(row)
            if value is not None and all(key):
                groups[key].append(value)

        agree, total, pairwise = pairwise_agreement(groups)
        kappa = fleiss_kappa(groups)
        result["dimensions"][dimension] = {
            "items_with_ratings": len(groups),
            "pairwise_agree_pairs": agree,
            "pairwise_total_pairs": total,
            "pairwise_agreement": None if pairwise is None else round(pairwise, 6),
            "fleiss_kappa": None if kappa is None else round(kappa, 6),
            "balanced_for_fleiss": kappa is not None,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = analyze(load_rows(args.csv_path))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    print(f"Rows: {report['rows']}; annotators: {len(report['annotators'])}")
    for dimension, stats in report["dimensions"].items():
        pa = stats["pairwise_agreement"]
        fk = stats["fleiss_kappa"]
        print(
            f"{dimension}: pairwise={('NA' if pa is None else f'{pa:.3f}')}; "
            f"Fleiss kappa={('NA' if fk is None else f'{fk:.3f}')}; "
            f"items={stats['items_with_ratings']}"
        )


if __name__ == "__main__":
    main()
