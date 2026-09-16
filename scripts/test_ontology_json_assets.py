#!/usr/bin/env python3
"""Parse every ontology JSON asset and fail with an actionable path/line."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology"


def main() -> None:
    paths = sorted(ONTOLOGY.rglob("*.json"))
    if not paths:
        raise SystemExit("No ontology JSON assets found")
    for path in paths:
        try:
            with path.open(encoding="utf-8") as f:
                json.load(f)
        except json.JSONDecodeError as exc:
            rel = path.relative_to(ROOT)
            raise SystemExit(
                f"Invalid JSON: {rel}:{exc.lineno}:{exc.colno}: {exc.msg}"
            ) from exc
    print(f"Ontology JSON parse check: OK ({len(paths)} files)")


if __name__ == "__main__":
    main()
