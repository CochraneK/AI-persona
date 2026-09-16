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
V1 = ROOT / "ontology" / "human_ontology.v1.json"
FIELD_MIGRATION = ROOT / "ontology" / "V1_FIELD_MIGRATION.json"

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
    v1 = load(V1)
    field_migration = load(FIELD_MIGRATION)

    assert o["ontology_id"] == "human-ontology"
    assert o["status"] in {"release_candidate", "canonical"}
    assert o["person_root"]["kind"] == "entity"

    domains = o["canonical_domains"]
    ids = [d["id"] for d in domains]
    assert not duplicates(ids), f"duplicate canonical domain ids: {duplicates(ids)}"
    domain_ids = set(ids)

    for d in domains:
        assert d.get("domain_type") == "semantic_namespace", f"invalid domain type for {d['id']}"
        allowed = set(d.get("allowed_kinds", []))
        assert allowed, f"missing allowed_kinds for {d['id']}"
        assert allowed <= ALLOWED_KINDS, f"invalid allowed_kinds for {d['id']}: {sorted(allowed - ALLOWED_KINDS)}"
        assert d.get("question"), f"missing competency question for {d['id']}"
        assert d.get("default_temporal_class"), f"missing default temporal class for {d['id']}"

    # Axis-level migration targets must exist.
    mapped = {target for targets in m["axis_map"].values() for target in targets}
    missing_targets = sorted(mapped - domain_ids)
    assert not missing_targets, f"migration points to unknown v2 domains: {missing_targets}"
    assert set(o["semantic_model"]["ontological_kinds"]) == ALLOWED_KINDS

    # Field-level migration must cover every v1 subaxis/personality layer exactly once.
    expected_v1_paths = []
    for axis in v1["axes"]:
        expected_v1_paths.extend(
            f"{axis['id']}.{name}" for name in axis.get("subaxes", [])
        )
        expected_v1_paths.extend(
            f"{axis['id']}.{layer['id']}" for layer in axis.get("layers", [])
        )
    migration_entries = field_migration["entries"]
    migrated_paths = [item["legacy_path"] for item in migration_entries]
    assert not duplicates(migrated_paths), (
        f"duplicate v1 field migration entries: {duplicates(migrated_paths)}"
    )
    assert set(migrated_paths) == set(expected_v1_paths), (
        f"v1 field migration coverage mismatch: "
        f"missing={sorted(set(expected_v1_paths)-set(migrated_paths))}, "
        f"extra={sorted(set(migrated_paths)-set(expected_v1_paths))}"
    )
    assert field_migration["to_version"] == o["version"]
    allowed_actions = set(field_migration["allowed_actions"])
    for item in migration_entries:
        assert item["action"] in allowed_actions
        assert item.get("canonical_targets"), f"no target for {item['legacy_path']}"
        for target in item["canonical_targets"]:
            root = target.split(".", 1)[0]
            assert root in domain_ids, (
                f"field migration target uses unknown domain: {item['legacy_path']} -> {target}"
            )

    schema_domains = set(kernel_schema["properties"]["domains"]["properties"])
    assert schema_domains == domain_ids, (
        "Persona Kernel schema/domain drift: "
        f"schema_only={sorted(schema_domains - domain_ids)}, "
        f"ontology_only={sorted(domain_ids - schema_domains)}"
    )
    assert kernel_schema["properties"]["ontology_version"]["const"] == o["version"]
    schema_source_types = set(
        kernel_schema["$defs"]["fieldMetadata"]["properties"]["source_type"]["enum"]
    )
    ontology_source_types = set(o["field_metadata_contract"]["source_type_values"])
    assert schema_source_types == ontology_source_types, (
        f"metadata source-type drift: schema_only={sorted(schema_source_types-ontology_source_types)}, "
        f"ontology_only={sorted(ontology_source_types-schema_source_types)}"
    )
    schema_relation_families = set(
        kernel_schema["$defs"]["relationRecord"]["properties"]["predicate"]["enum"]
    )
    assert schema_relation_families == set(o["relation_families"]), (
        "relation-family drift between ontology and Kernel schema"
    )

    assert r["version"] == o["version"], "field registry version must match ontology version"
    domain_by_id = {d["id"]: d for d in domains}

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
        assert field.get("cardinality"), f"missing cardinality: {field['concept']}"
        assert field["kind"] in set(domain_by_id[root]["allowed_kinds"]), (
            f"field kind {field['kind']} not allowed by domain {root}: {field['concept']}"
        )
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
