#!/usr/bin/env python3
"""Validate the checked-in PersonaKernel exchange example against runtime rules."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.persona_kernel import PersonaKernel

EXAMPLE = ROOT / "ontology" / "examples" / "persona_kernel.example.json"


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
    print("PersonaKernel contract example round-trip: OK")


if __name__ == "__main__":
    main()
