#!/usr/bin/env python3
"""Run the complete Human Ontology v2 quality gate without GitHub Actions.

Standard-library only. Intended for local development, CI runners, Codex/Work
environments, and recovery when hosted Actions are unavailable.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, *args: str) -> None:
    print(f"\n=== {label} ===", flush=True)
    subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    run("Parse ontology JSON assets", "scripts/test_ontology_json_assets.py")
    run("Validate v1 compatibility", "scripts/validate_human_ontology.py")
    run("Validate v2 ontology", "scripts/validate_human_ontology_v2.py")

    print("\n=== Compile core runtime ===", flush=True)
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "core"],
        cwd=ROOT,
        check=True,
    )

    run("Legacy compatibility + psychiatric semantic firewall", "scripts/test_persona_kernel_compat.py")
    run("PersonaKernel typed-graph contract", "scripts/test_persona_kernel_contract.py")
    run("Event sampling regression", "scripts/test_events_sampling.py")
    run("Scientific evaluation machine gate", "scripts/evaluate_human_ontology.py")
    run("Repository release gate", "scripts/check_ontology_release_gate.py")

    print("\nHuman Ontology full local quality gate: OK", flush=True)


if __name__ == "__main__":
    main()
