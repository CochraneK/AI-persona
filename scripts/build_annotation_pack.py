#!/usr/bin/env python3
"""Build a blinded annotation pack from Human Ontology evaluation cases."""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluation"


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotators", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260918)
    parser.add_argument("--out", type=Path, default=EVAL / "generated_annotation_pack.csv")
    args = parser.parse_args()

    if args.annotators < 2:
        raise SystemExit("--annotators must be >= 2")

    adversarial = load(EVAL / "adversarial_cases.json")["cases"]
    rows = []
    for case in adversarial:
        for fact_index, expected in enumerate(case["expected"], start=1):
            fact_label = expected[0]
            for annotator_index in range(1, args.annotators + 1):
                rows.append({
                    "case_id": case["id"],
                    "atomic_fact_id": f"fact-{fact_index:02d}",
                    "vignette": case["vignette"],
                    "fact_prompt": fact_label,
                    "annotator_id": f"annotator-{annotator_index:02d}",
                    "canonical_home": "",
                    "kind": "",
                    "temporal_class": "",
                    "relation_predicate": "",
                    "source_type": "",
                    "confidence": "",
                    "ambiguity_note": "",
                })

    rng = random.Random(args.seed)
    rng.shuffle(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0])
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Wrote {len(rows)} annotation rows "
        f"({len(adversarial)} cases x {args.annotators} annotators, atomic facts expanded) "
        f"to {args.out}"
    )


if __name__ == "__main__":
    main()
