#!/usr/bin/env python3
"""Repository-level release gate for Human Ontology v2.

This gate is intentionally standard-library only. It checks structural migration
readiness; GitHub Actions success is the outer gate for promotion.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology"

FORBIDDEN_STALE_TOKENS = (
    "2.0.0-rc1",
    "identity_affiliations",
    "education_work_economy",
)

SCAN_PATHS = (
    ROOT / "README.md",
    ROOT / "CLAUDE.md",
    ROOT / "skill" / "SKILL.md",
    ROOT / "core" / "human_ontology.py",
    ROOT / "core" / "persona_kernel.py",
    ROOT / "core" / "kernel_generator.py",
    ROOT / "core" / "legacy_adapter.py",
    ONTOLOGY / "README.md",
    ONTOLOGY / "HUMAN_ONTOLOGY_V2_ARCHITECTURE.md",
    ONTOLOGY / "HUMAN_ONTOLOGY_REVIEW.md",
    ONTOLOGY / "CONSUMER_CONTRACT.md",
    ONTOLOGY / "V1_V2_OVERLAP_AUDIT.md",
)


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    raise SystemExit(f"Release gate failed: {message}")


def main() -> None:
    v1 = load(ONTOLOGY / "human_ontology.v1.json")
    v2 = load(ONTOLOGY / "human_ontology.v2.json")
    migration = load(ONTOLOGY / "V1_TO_V2_MIGRATION.json")
    field_migration = load(ONTOLOGY / "V1_FIELD_MIGRATION.json")
    registry = load(ONTOLOGY / "CANONICAL_FIELD_REGISTRY.json")
    schema = load(ONTOLOGY / "persona_kernel.schema.json")

    if v2["status"] != "release_candidate":
        fail("rc2 must remain release_candidate until the PR gate is explicitly promoted")
    version = v2["version"]
    for name, other in (
        ("axis migration", migration["to_version"]),
        ("field migration", field_migration["to_version"]),
        ("field registry", registry["version"]),
        ("kernel schema", schema["properties"]["ontology_version"]["const"]),
    ):
        if other != version:
            fail(f"{name} version {other!r} != ontology version {version!r}")

    expected = {
        f"{axis['id']}.{name}"
        for axis in v1["axes"]
        for name in (
            list(axis.get("subaxes", []))
            + [layer["id"] for layer in axis.get("layers", [])]
        )
    }
    actual = {item["legacy_path"] for item in field_migration["entries"]}
    if actual != expected:
        fail(
            f"field migration coverage mismatch: "
            f"missing={sorted(expected-actual)}, extra={sorted(actual-expected)}"
        )

    overlap = (ONTOLOGY / "V1_V2_OVERLAP_AUDIT.md").read_text(encoding="utf-8")
    if "| open |" in overlap.lower():
        fail("overlap audit still contains open rows")

    for path in SCAN_PATHS:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_STALE_TOKENS:
            if token in text:
                fail(f"stale token {token!r} remains in {path.relative_to(ROOT)}")

    required = (
        ONTOLOGY / "CONSUMER_CONTRACT.md",
        ONTOLOGY / "domains" / "psychiatric_diagnosis.module.json",
        ROOT / "core" / "persona_kernel.py",
        ROOT / "core" / "kernel_generator.py",
        ROOT / "core" / "legacy_adapter.py",
    )
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail(f"required v2 artifacts missing: {missing}")

    print(
        "Human Ontology v2 release gate: READY FOR CI "
        f"({version}; {len(v2['canonical_domains'])} domains; "
        f"{len(field_migration['entries'])} migrated v1 fields)"
    )


if __name__ == "__main__":
    main()
