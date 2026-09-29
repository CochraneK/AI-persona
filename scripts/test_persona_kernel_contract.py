#!/usr/bin/env python3
"""Validate PersonaKernel exchange and hard runtime invariants."""
from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.persona_kernel import FieldMetadata, PersonaKernel

EXAMPLE = ROOT / "ontology" / "examples" / "persona_kernel.example.json"


def expect_value_error(fn, contains: str) -> None:
    try:
        fn()
    except (ValueError, TypeError) as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError(f"Expected error containing {contains!r}")


def main() -> None:
    with EXAMPLE.open(encoding="utf-8") as f:
        payload = json.load(f)

    kernel = PersonaKernel.from_dict(payload)
    roundtrip = kernel.to_dict()
    assert roundtrip["persona_id"] == payload["persona_id"]
    assert roundtrip["ontology_version"] == payload["ontology_version"]
    assert roundtrip["domains"] == payload["domains"]
    assert roundtrip["relations"] == payload["relations"]
    assert roundtrip["events"] == payload["events"]

    # First-class relation_graph fields must not sit in a domain payload.
    misplaced_storage = PersonaKernel.from_dict(payload)
    misplaced_storage.set_value(
        "culture_language",
        "languages",
        ["en"],
        FieldMetadata(
            "user_provided",
            provenance="negative contract fixture",
            temporal_class="dynamic_state",
        ),
    )
    expect_value_error(
        misplaced_storage.validate,
        "culture_language.languages must be stored in relation_graph, not domain payload",
    )

    # Duplicate physical home: a relation whose canonical_path is already a
    # domain payload key is rejected.
    duplicate_home = deepcopy(payload)
    duplicate_relation = deepcopy(duplicate_home["relations"][0])
    duplicate_relation["relation_id"] = "example-001:relation:mood:neutral"
    duplicate_relation["canonical_path"] = "current_state.mood"
    duplicate_home["relations"].append(duplicate_relation)
    expect_value_error(
        lambda: PersonaKernel.from_dict(duplicate_home),
        "duplicates domain payload at current_state.mood",
    )

    missing_metadata = deepcopy(payload)
    del missing_metadata["field_metadata"]["current_state.mood"]
    expect_value_error(
        lambda: PersonaKernel.from_dict(missing_metadata),
        "Domain values missing field_metadata",
    )

    orphan_metadata = deepcopy(payload)
    orphan_metadata["field_metadata"]["current_state.fake"] = deepcopy(
        orphan_metadata["field_metadata"]["current_state.mood"]
    )
    expect_value_error(
        lambda: PersonaKernel.from_dict(orphan_metadata),
        "field_metadata has no matching domain value",
    )

    duplicate_relation_id = deepcopy(payload)
    duplicate_relation_id["relations"].append(deepcopy(duplicate_relation_id["relations"][0]))
    expect_value_error(
        lambda: PersonaKernel.from_dict(duplicate_relation_id),
        "duplicate relation_id",
    )

    bad_target_type = deepcopy(payload)
    bad_target_type["relations"][0]["object"]["entity_type"] = "place"
    expect_value_error(
        lambda: PersonaKernel.from_dict(bad_target_type),
        "does not allow object entity_type",
    )

    wrong_subject = deepcopy(payload)
    wrong_subject["relations"][0]["subject"]["entity_id"] = "someone-else"
    expect_value_error(
        lambda: PersonaKernel.from_dict(wrong_subject),
        "subject must reference PersonaKernel person",
    )

    duplicate_event_id = deepcopy(payload)
    duplicate_event_id["events"].append(deepcopy(duplicate_event_id["events"][0]))
    expect_value_error(
        lambda: PersonaKernel.from_dict(duplicate_event_id),
        "duplicate event_id",
    )

    no_provenance = deepcopy(payload)
    no_provenance["field_metadata"]["current_state.mood"]["provenance"] = ""
    expect_value_error(
        lambda: PersonaKernel.from_dict(no_provenance),
        "requires provenance",
    )

    print("PersonaKernel typed graph + metadata completeness invariants: OK")


if __name__ == "__main__":
    main()
