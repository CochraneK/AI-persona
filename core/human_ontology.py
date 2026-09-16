"""Canonical Human Ontology loader for AI-persona.

The JSON file is the source of truth. Python code should reference canonical ids
through this module instead of redefining shared life stages/domains locally.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_ONTOLOGY_PATH = Path(__file__).resolve().parents[1] / "ontology" / "human_ontology.v1.json"


@lru_cache(maxsize=1)
def load_human_ontology() -> dict[str, Any]:
    with _ONTOLOGY_PATH.open("r", encoding="utf-8") as f:
        ontology = json.load(f)
    validate_human_ontology(ontology)
    return ontology


def validate_human_ontology(ontology: dict[str, Any]) -> None:
    required = {
        "ontology_id",
        "version",
        "status",
        "design_principles",
        "axes",
        "canonical_shared_classifications",
        "legacy_mappings",
    }
    missing = sorted(required - ontology.keys())
    if missing:
        raise ValueError(f"Human Ontology missing keys: {missing}")

    if ontology["status"] != "canonical":
        raise ValueError("Human Ontology loaded by production code must be canonical")

    axes = ontology["axes"]
    axis_ids = [axis["id"] for axis in axes]
    if len(axis_ids) != len(set(axis_ids)):
        raise ValueError("Human Ontology contains duplicate top-level axis ids")

    shared = ontology["canonical_shared_classifications"]
    for key in ("life_domains", "developmental_stages", "event_pressure_shapes"):
        if key not in shared or not shared[key]:
            raise ValueError(f"Human Ontology missing canonical classification: {key}")


def ontology_version() -> str:
    return str(load_human_ontology()["version"])


def canonical_axis_ids() -> tuple[str, ...]:
    return tuple(axis["id"] for axis in load_human_ontology()["axes"])


def canonical_life_domains() -> tuple[str, ...]:
    return tuple(
        load_human_ontology()["canonical_shared_classifications"]["life_domains"]
    )


def canonical_developmental_stage_ids() -> tuple[str, ...]:
    return tuple(
        item["id"]
        for item in load_human_ontology()["canonical_shared_classifications"][
            "developmental_stages"
        ]
    )


def canonical_event_pressure_shapes() -> tuple[str, ...]:
    return tuple(
        load_human_ontology()["canonical_shared_classifications"][
            "event_pressure_shapes"
        ]
    )


def map_legacy_event_domain(domain: str) -> str | None:
    return (
        load_human_ontology()
        .get("legacy_mappings", {})
        .get("ai_persona_event_domains_v1", {})
        .get(domain)
    )


def map_legacy_event_stage(stage: str) -> tuple[str, ...]:
    values = (
        load_human_ontology()
        .get("legacy_mappings", {})
        .get("ai_persona_event_stages_v1", {})
        .get(stage, [])
    )
    return tuple(values)


def ontology_summary() -> dict[str, Any]:
    ontology = load_human_ontology()
    return {
        "ontology_id": ontology["ontology_id"],
        "version": ontology["version"],
        "axes": len(ontology["axes"]),
        "life_domains": len(
            ontology["canonical_shared_classifications"]["life_domains"]
        ),
        "developmental_stages": len(
            ontology["canonical_shared_classifications"]["developmental_stages"]
        ),
        "event_pressure_shapes": len(
            ontology["canonical_shared_classifications"]["event_pressure_shapes"]
        ),
    }


if __name__ == "__main__":
    print(json.dumps(ontology_summary(), ensure_ascii=False, indent=2))
