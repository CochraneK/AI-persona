"""Human Ontology loaders and compatibility helpers.

The JSON documents under ontology/ are the semantic source of truth. Python
runtime code must consume canonical IDs from this module rather than redeclare
ontology structure independently.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_V1_PATH = _ROOT / "ontology" / "human_ontology.v1.json"
_V2_PATH = _ROOT / "ontology" / "human_ontology.v2.json"
_FIELD_REGISTRY_PATH = _ROOT / "ontology" / "CANONICAL_FIELD_REGISTRY.json"


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_human_ontology() -> dict[str, Any]:
    """Load stable/canonical v1 for backwards-compatible production callers."""
    ontology = _read_json(_V1_PATH)
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
        raise ValueError(f"Human Ontology v1 missing keys: {missing}")
    if ontology["status"] != "canonical":
        raise ValueError("Human Ontology loaded by the v1 production API must be canonical")

    axis_ids = [axis["id"] for axis in ontology["axes"]]
    if len(axis_ids) != len(set(axis_ids)):
        raise ValueError("Human Ontology v1 contains duplicate top-level axis ids")

    shared = ontology["canonical_shared_classifications"]
    for key in ("life_domains", "developmental_stages", "event_pressure_shapes"):
        if key not in shared or not shared[key]:
            raise ValueError(f"Human Ontology v1 missing canonical classification: {key}")


@lru_cache(maxsize=1)
def load_human_ontology_v2(*, require_canonical: bool = False) -> dict[str, Any]:
    """Load Human Ontology v2 release candidate.

    require_canonical=True is intended for future production consumers after the
    migration gate is complete.
    """
    ontology = _read_json(_V2_PATH)
    validate_human_ontology_v2(ontology, require_canonical=require_canonical)
    return ontology


def validate_human_ontology_v2(
    ontology: dict[str, Any], *, require_canonical: bool = False
) -> None:
    required = {
        "ontology_id",
        "version",
        "status",
        "semantic_model",
        "person_root",
        "canonical_domains",
        "relation_families",
        "domain_modules",
        "field_metadata_contract",
        "consumer_contract",
        "migration",
    }
    missing = sorted(required - ontology.keys())
    if missing:
        raise ValueError(f"Human Ontology v2 missing keys: {missing}")

    allowed_status = {"canonical"} if require_canonical else {"release_candidate", "canonical"}
    if ontology["status"] not in allowed_status:
        raise ValueError(
            f"Human Ontology v2 status {ontology['status']!r} not in {sorted(allowed_status)}"
        )
    if ontology["person_root"].get("kind") != "entity":
        raise ValueError("Human Ontology v2 Person root must be an entity")

    domains = ontology["canonical_domains"]
    domain_ids = [item["id"] for item in domains]
    if len(domain_ids) != len(set(domain_ids)):
        raise ValueError("Human Ontology v2 contains duplicate canonical domain ids")


@lru_cache(maxsize=1)
def load_canonical_field_registry() -> dict[str, Any]:
    registry = _read_json(_FIELD_REGISTRY_PATH)
    fields = registry.get("fields", [])
    paths = [item["canonical_path"] for item in fields]
    concepts = [item["concept"] for item in fields]
    if len(paths) != len(set(paths)):
        raise ValueError("Canonical field registry contains duplicate semantic homes")
    if len(concepts) != len(set(concepts)):
        raise ValueError("Canonical field registry contains duplicate concepts")
    return registry


def ontology_version() -> str:
    """Backwards-compatible v1 version accessor."""
    return str(load_human_ontology()["version"])


def ontology_v2_version() -> str:
    return str(load_human_ontology_v2()["version"])


def canonical_axis_ids() -> tuple[str, ...]:
    return tuple(axis["id"] for axis in load_human_ontology()["axes"])


def canonical_v2_domain_ids() -> tuple[str, ...]:
    return tuple(item["id"] for item in load_human_ontology_v2()["canonical_domains"])


def canonical_relation_families() -> tuple[str, ...]:
    return tuple(load_human_ontology_v2()["relation_families"])


def canonical_entity_types() -> tuple[str, ...]:
    return tuple(item["id"] for item in load_human_ontology_v2()["entity_types"])


def canonical_field_paths() -> tuple[str, ...]:
    return tuple(
        item["canonical_path"] for item in load_canonical_field_registry()["fields"]
    )


def resolve_legacy_alias(alias: str) -> str | None:
    """Return the v2 canonical path for a v1/legacy field alias."""
    for item in load_canonical_field_registry()["fields"]:
        if alias in item.get("legacy_aliases", []):
            return str(item["canonical_path"])
    return None


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


def ontology_v2_summary() -> dict[str, Any]:
    ontology = load_human_ontology_v2()
    return {
        "ontology_id": ontology["ontology_id"],
        "version": ontology["version"],
        "status": ontology["status"],
        "canonical_domains": len(ontology["canonical_domains"]),
        "canonical_fields": len(load_canonical_field_registry()["fields"]),
        "domain_modules": sorted(ontology["domain_modules"]),
    }


if __name__ == "__main__":
    print(json.dumps({
        "v1": ontology_summary(),
        "v2": ontology_v2_summary(),
    }, ensure_ascii=False, indent=2))
