#!/usr/bin/env python3
"""Static validation for Human Ontology v2 and its migration/MECE contracts."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "human_ontology.v2.json"
MIGRATION = ROOT / "ontology" / "V1_TO_V2_MIGRATION.json"
REGISTRY = ROOT / "ontology" / "CANONICAL_FIELD_REGISTRY.json"
PSYCHIATRIC_MODULE = ROOT / "ontology" / "domains" / "psychiatric_diagnosis.module.json"
KERNEL_SCHEMA = ROOT / "ontology" / "persona_kernel.schema.json"

ALLOWED_KINDS = {"entity", "quality_disposition", "role", "relation", "process_event", "state"}


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def duplicates(values):
    return sorted(k for k, n in Counter(values).items() if n > 1)


def main() -> None:
    o = load(ONTOLOGY)
    m = load(MIGRATION)
    r = load(REGISTRY)
    psychiatric_module = load(PSYCHIATRIC_MODULE)
    kernel_schema = load(KERNEL_SCHEMA)

    assert o["ontology_id"] == "human-ontology"
    assert o["status"] in {"release_candidate", "canonical"}
    assert o["person_root"]["kind"] == "entity"

    domains = o["canonical_domains"]
    ids = [d["id"] for d in domains]
    assert not duplicates(ids), f"duplicate canonical domain ids: {duplicates(ids)}"
    domain_ids = set(ids)

    for d in domains:
        assert d["kind"] in ALLOWED_KINDS, f"invalid kind for {d['id']}"
        assert d.get("question"), f"missing competency question for {d['id']}"
        assert d.get("temporal_class"), f"missing temporal class for {d['id']}"

    mapped = {target for targets in m["axis_map"].values() for target in targets}
    missing_targets = sorted(mapped - domain_ids)
    assert not missing_targets, f"migration points to unknown v2 domains: {missing_targets}"
    assert set(o["semantic_model"]["ontological_kinds"]) == ALLOWED_KINDS

    schema_domains = set(kernel_schema["properties"]["domains"]["properties"])
    assert schema_domains == domain_ids, (
        "Persona Kernel schema/domain drift: "
        f"schema_only={sorted(schema_domains - domain_ids)}, "
        f"ontology_only={sorted(domain_ids - schema_domains)}"
    )
    assert kernel_schema["properties"]["ontology_version"]["const"] == o["version"]

    fields = r["fields"]
    concepts = [f["concept"] for f in fields]
    paths = [f["canonical_path"] for f in fields]
    assert not duplicates(concepts), f"duplicate concepts in registry: {duplicates(concepts)}"
    assert not duplicates(paths), f"duplicate canonical semantic homes: {duplicates(paths)}"

    aliases = []
    for field in fields:
        assert field["kind"] in ALLOWED_KINDS, f"invalid field kind: {field['concept']}"
        root = field["canonical_path"].split(".", 1)[0]
        assert root in domain_ids, f"registry path uses unknown domain: {field['canonical_path']}"
        assert field.get("temporal_class"), f"missing temporal class: {field['concept']}"
        aliases.extend(field.get("legacy_aliases", []))
    assert not duplicates(aliases), f"legacy alias mapped to multiple concepts: {duplicates(aliases)}"

    psychiatric = o["domain_modules"]["psychiatric_diagnosis"]
    assert psychiatric["canonical_home"] == "mental_neurodevelopmental_health"
    assert psychiatric["required"] is False
    assert psychiatric_module["canonical_home"] == "mental_neurodevelopmental_health.diagnoses"
    assert psychiatric_module["required_for_person"] is False
    for key in (
        "diagnosis_is_identity_root",
        "diagnosis_determines_personality",
        "diagnosis_determines_values",
        "diagnosis_determines_morality",
        "diagnosis_determines_life_outcome",
    ):
        assert psychiatric_module["semantics"][key] is False, f"unsafe psychiatric semantic flag: {key}"

    print(
        "Human Ontology v2 validation: OK "
        f"({len(ids)} domains, {len(fields)} canonical fields, {len(aliases)} legacy aliases)"
    )


if __name__ == "__main__":
    main()
