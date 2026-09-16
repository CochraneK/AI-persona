#!/usr/bin/env python3
"""Compatibility smoke tests for legacy Persona -> PersonaKernel v2."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import generate_persona, generate_persona_kernel, legacy_persona_to_kernel


def main() -> None:
    legacy = generate_persona("重度抑郁障碍", rng_seed=7, event_count=3)
    kernel = legacy_persona_to_kernel(legacy)
    assert kernel.persona_id == legacy.id
    assert "personality_psychology" in kernel.domains
    assert "mental_neurodevelopmental_health" in kernel.domains
    diagnoses = kernel.get_value("mental_neurodevelopmental_health", "diagnoses")
    assert diagnoses and diagnoses[0]["role"] == "primary"
    assert kernel.events

    healthy = generate_persona("无精神障碍（健康）", rng_seed=11, event_count=2)
    healthy_kernel = legacy_persona_to_kernel(healthy)
    assert healthy_kernel.get_value("mental_neurodevelopmental_health", "diagnoses") is None

    direct = generate_persona_kernel("重度抑郁障碍", rng_seed=7, event_count=3)
    assert direct.to_dict()["ontology_version"] == "2.0.0-rc1"
    print("Legacy -> PersonaKernel compatibility: OK")


if __name__ == "__main__":
    main()
