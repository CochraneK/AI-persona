#!/usr/bin/env python3
"""Validate the canonical Human Ontology and print compatibility coverage."""

from __future__ import annotations

import json
from core.human_ontology import (
    canonical_axis_ids,
    canonical_developmental_stage_ids,
    canonical_event_pressure_shapes,
    canonical_life_domains,
    load_human_ontology,
    ontology_summary,
)


def main() -> None:
    ontology = load_human_ontology()
    summary = ontology_summary()

    print("Human Ontology validation: OK")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\nAxes:")
    for axis in canonical_axis_ids():
        print(f"  - {axis}")
    print("\nShared classifications:")
    print(f"  life domains: {len(canonical_life_domains())}")
    print(f"  developmental stages: {len(canonical_developmental_stage_ids())}")
    print(f"  event pressure shapes: {len(canonical_event_pressure_shapes())}")

    legacy = ontology.get("legacy_mappings", {})
    print("\nLegacy compatibility maps:")
    for name, mapping in legacy.items():
        print(f"  - {name}: {len(mapping)} entries")


if __name__ == "__main__":
    main()
