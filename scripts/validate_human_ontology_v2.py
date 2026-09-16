#!/usr/bin/env python3
"""Static validation for Human Ontology v2 and its migration contract."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "human_ontology.v2.json"
MIGRATION = ROOT / "ontology" / "V1_TO_V2_MIGRATION.json"
ALLOWED_KINDS = {"entity", "quality_disposition", "role", "relation", "process_event", "state"}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    o = load(ONTOLOGY)
    m = load(MIGRATION)
    assert o["ontology_id"] == "human-ontology"
    assert o["status"] in {"release_candidate", "canonical"}
    assert o["person_root"]["kind"] == "entity"
    domains = o["canonical_domains"]
    ids = [d["id"] for d in domains]
    assert len(ids) == len(set(ids)), "duplicate canonical domain id"
    for d in domains:
        assert d["kind"] in ALLOWED_KINDS, f"invalid kind for {d['id']}"
        assert d.get("question"), f"missing competency question for {d['id']}"
        assert d.get("temporal_class"), f"missing temporal class for {d['id']}"
    mapped = {target for targets in m["axis_map"].values() for target in targets}
    missing_targets = sorted(mapped - set(ids))
    assert not missing_targets, f"migration points to unknown v2 domains: {missing_targets}"
    assert set(o["semantic_model"]["ontological_kinds"]) == ALLOWED_KINDS
    psychiatric = o["domain_modules"]["psychiatric_diagnosis"]
    assert psychiatric["canonical_home"] == "mental_neurodevelopmental_health"
    assert psychiatric["required"] is False
    print(f"Human Ontology v2 validation: OK ({len(ids)} canonical domains)")


if __name__ == "__main__":
    main()
