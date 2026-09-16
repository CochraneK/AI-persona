#!/usr/bin/env python3
"""Validate PersonaKernel exchange and single-home graph invariants."""
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
    except ValueError as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError(f"Expected ValueError containing {contains!r}")


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

    duplicate = PersonaKernel.from_dict(payload)
    duplicate.set_value(
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
        duplicate.validate,
        "duplicates domain payload at culture_language.languages",
    )

    duplicate_relation_id = deepcopy(payload)
    duplicate_relation_id["relations"].append(deepcopy(duplicate_relation_id["relations"][0]))
    expect_value_error(
        lambda: PersonaKernel.from_dict(duplicate_relation_id),
        "duplicate relation_id",
    )

    duplicate_event_id = deepcopy(payload)
    duplicate_event_id["events"].append(deepcopy(duplicate_event_id["events"][0]))
    expect_value_error(
        lambda: PersonaKernel.from_dict(duplicate_event_id),
        "duplicate event_id",
    )

    print("PersonaKernel contract + single-home invariants: OK")


if __name__ == "__main__":
    main()
