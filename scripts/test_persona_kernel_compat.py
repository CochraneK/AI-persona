#!/usr/bin/env python3
"""Compatibility and semantic-firewall tests for PersonaKernel v2."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import (
    KernelGenerationPolicy,
    KernelGenerator,
    generate_persona,
    generate_persona_kernel,
    legacy_persona_to_kernel,
)


def main() -> None:
    legacy = generate_persona("重度抑郁障碍", rng_seed=7, event_count=3)
    kernel = legacy_persona_to_kernel(legacy)
    assert kernel.persona_id == legacy.id
    assert "personality_psychology" in kernel.domains
    assert "mental_neurodevelopmental_health" in kernel.domains
    assert "education_learning" in kernel.domains
    assert "work_economic_participation" not in kernel.domains
    occupation_relations = [
        r for r in kernel.relations
        if r["canonical_path"] == "work_economic_participation.occupation"
    ]
    assert len(occupation_relations) == 1
    diagnoses = kernel.get_value("mental_neurodevelopmental_health", "diagnoses")
    assert diagnoses and diagnoses[0]["role"] == "primary"
    assert kernel.events
    assert all(e["source_type"] == "generated" for e in kernel.events)
    assert all("provenance" in e and "temporal_class" in e for e in kernel.events)
    assert all(r["predicate"] for r in kernel.relations)
    assert all(r["relation_id"] and r["canonical_path"] for r in kernel.relations)
    assert all(e["event_id"] and e["canonical_path"] for e in kernel.events)
    assert "triggers" not in kernel.domains.get("mental_neurodevelopmental_health", {})
    trigger_relations = [
        r for r in kernel.relations
        if r["canonical_path"] == "mental_neurodevelopmental_health.triggers"
    ]
    assert all(r["predicate"] == "has_trigger" for r in trigger_relations)

    safe_dep = generate_persona_kernel("重度抑郁障碍", rng_seed=19, event_count=3)
    safe_gad = generate_persona_kernel("广泛性焦虑障碍", rng_seed=19, event_count=3)
    dep_dx = safe_dep.get_value("mental_neurodevelopmental_health", "diagnoses")
    gad_dx = safe_gad.get_value("mental_neurodevelopmental_health", "diagnoses")
    assert dep_dx and gad_dx and dep_dx[0]["label"] != gad_dx[0]["label"]
    assert dep_dx[0]["source_type"] == "input_constraint"
    assert gad_dx[0]["source_type"] == "input_constraint"
    assert dep_dx[0]["provenance"] == "generate_kernel(primary_diagnosis=...)"

    # Sensitive diagnosis may alter health/current-state payloads, but under the
    # default health-only policy it must not determine non-health person semantics.
    invariant_domains = (
        "personality_psychology",
        "abilities_skills_interests",
        "education_learning",
        "work_economic_participation",
        "identity_self_concept",
        "relationships",
        "place_mobility",
        "lifestyle_routines",
    )
    for domain in invariant_domains:
        assert safe_dep.domains.get(domain) == safe_gad.domains.get(domain), domain
    dep_non_health_relations = [
        r for r in safe_dep.relations
        if not r["canonical_path"].startswith("mental_neurodevelopmental_health.")
    ]
    gad_non_health_relations = [
        r for r in safe_gad.relations
        if not r["canonical_path"].startswith("mental_neurodevelopmental_health.")
    ]
    assert dep_non_health_relations == gad_non_health_relations
    assert safe_dep.events == safe_gad.events

    direct = safe_dep.to_dict()
    assert direct["ontology_version"] == "2.0.0"

    legacy_full = KernelGenerator(
        rng_seed=19,
        policy=KernelGenerationPolicy("legacy_full"),
    ).generate("重度抑郁障碍", event_count=2)
    assert legacy_full.get_value("mental_neurodevelopmental_health", "diagnoses")
    print("PersonaKernel compatibility + psychiatric semantic firewall: OK")


if __name__ == "__main__":
    main()
