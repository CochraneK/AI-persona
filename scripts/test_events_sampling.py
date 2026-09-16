#!/usr/bin/env python3
"""Regression tests for life-event allocation and uniqueness."""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.events import sample_events_for_persona


def main() -> None:
    cases = [
        (1, 0.3, 0.4, 0.3),
        (2, 0.3, 0.4, 0.3),
        (3, 0.8, 0.8, 0.0),
        (4, 0.0, 0.0, 0.0),
        (5, 1.0, 0.0, 0.0),
        (7, 0.1, 0.8, 0.1),
    ]
    for seed in range(20):
        for n, pos, neg, neu in cases:
            events = sample_events_for_persona(
                age=35,
                primary_diagnosis_key="depressive",
                positive_ratio=pos,
                negative_ratio=neg,
                neutral_ratio=neu,
                n_events=n,
                rng=random.Random(seed),
            )
            assert len(events) <= n
            names = [e.name_cn for e in events]
            assert len(names) == len(set(names)), (
                f"duplicate events for seed={seed}, n={n}: {names}"
            )
    print("Event sampling regression tests: OK")


if __name__ == "__main__":
    main()
