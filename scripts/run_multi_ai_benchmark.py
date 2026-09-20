#!/usr/bin/env python3
"""Run the Human Ontology Multi-AI Tier-B1 benchmark."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "evaluation" / "multi_ai_benchmark"

from multi_ai_client import ProviderError, call_provider, extract_json_object


def load(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_model(entry: dict[str, Any]) -> dict[str, Any]:
    model = os.getenv(entry.get("model_env", ""), entry.get("model", "")).strip()
    base_url = os.getenv(
        entry.get("base_url_env", ""), entry.get("base_url", "")
    ).strip()
    api_key = os.getenv(entry.get("api_key_env", ""), "").strip()
    return {
        **entry,
        "model": model,
        "base_url": base_url,
        "api_key": api_key,
    }


def ontology_summary() -> tuple[str, dict[str, set[str]]]:
    ontology = load(ROOT / "ontology" / "human_ontology.v2.json")
    lines = ["SEMANTIC NAMESPACES:"]
    for domain in ontology["canonical_domains"]:
        lines.append(
            f"- {domain['id']}: {domain['question']} "
            f"(allowed kinds: {', '.join(domain['allowed_kinds'])})"
        )
    lines += [
        "",
        "ONTOLOGICAL KINDS:",
        ", ".join(ontology["semantic_model"]["ontological_kinds"]),
        "",
        "RELATION PREDICATES:",
        ", ".join(ontology["relation_families"]),
        "",
        "EPISTEMIC SOURCE TYPES:",
        ", ".join(ontology["field_metadata_contract"]["source_type_values"]),
    ]
    allowed = {
        "domains": {d["id"] for d in ontology["canonical_domains"]},
        "kinds": set(ontology["semantic_model"]["ontological_kinds"]),
        "predicates": set(ontology["relation_families"]),
        "sources": set(ontology["field_metadata_contract"]["source_type_values"]),
    }
    return "\n".join(lines), allowed


def build_prompt(case: dict[str, Any], summary: str) -> str:
    facts = "\n".join(
        f"{i}. {fact['fact_key']}"
        for i, fact in enumerate(case["facts"], start=1)
    )
    forbidden = "\n".join(
        f"{i}. {claim}"
        for i, claim in enumerate(case["forbidden_inferences"])
    )
    return f"""ONTOLOGY SUMMARY

{summary}

VIGNETTE

{case['vignette']}

TARGET FACT KEYS

{facts}

CANDIDATE INFERENCES

{forbidden if forbidden else '(none)'}

Return one JSON object with exactly these top-level keys:
- annotations
- forbidden_inference_checks

For each target fact key, annotations must contain exactly one item with:
- fact_key
- canonical_domain: one namespace ID above, or null if the fact is genuinely unknown
- knowledge_status: known | unknown | absent | insufficient_information
- kind: one ontological kind above, or null if not assertable
- relation_predicate: one allowed predicate above if a relation is the best representation, else null
- source_type: one epistemic source type above if inferable from wording, else null
- confidence: 0..1
- reason_short: concise explanation

For each candidate inference, forbidden_inference_checks must contain exactly one item:
- index: zero-based index from the list order
- entailed: true only if the vignette actually entails the claim
- reason_short

Do not add facts not stated or logically entailed by the vignette.
"""


def validate_response(
    response: dict[str, Any],
    case: dict[str, Any],
    allowed: dict[str, set[str]],
) -> None:
    annotations = response.get("annotations")
    checks = response.get("forbidden_inference_checks")
    if not isinstance(annotations, list) or not isinstance(checks, list):
        raise ValueError("response requires annotations and forbidden_inference_checks arrays")

    expected_keys = [fact["fact_key"] for fact in case["facts"]]
    actual_keys = [item.get("fact_key") for item in annotations]
    if sorted(actual_keys) != sorted(expected_keys) or len(actual_keys) != len(expected_keys):
        raise ValueError(
            f"annotation fact keys mismatch: expected={expected_keys}, got={actual_keys}"
        )

    for item in annotations:
        domain = item.get("canonical_domain")
        if domain is not None and domain not in allowed["domains"]:
            raise ValueError(f"unknown canonical_domain: {domain}")
        status = item.get("knowledge_status")
        if status not in {"known", "unknown", "absent", "insufficient_information"}:
            raise ValueError(f"invalid knowledge_status: {status}")
        kind = item.get("kind")
        if kind is not None and kind not in allowed["kinds"]:
            raise ValueError(f"unknown kind: {kind}")
        predicate = item.get("relation_predicate")
        if predicate is not None and predicate not in allowed["predicates"]:
            raise ValueError(f"unknown relation_predicate: {predicate}")
        source = item.get("source_type")
        if source is not None and source not in allowed["sources"]:
            raise ValueError(f"unknown source_type: {source}")
        confidence = item.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            raise ValueError(f"invalid confidence: {confidence}")

    expected_indices = set(range(len(case["forbidden_inferences"])))
    actual_indices = {item.get("index") for item in checks}
    if actual_indices != expected_indices or len(checks) != len(expected_indices):
        raise ValueError(
            f"forbidden inference indices mismatch: "
            f"expected={sorted(expected_indices)}, got={sorted(actual_indices)}"
        )
    if any(not isinstance(item.get("entailed"), bool) for item in checks):
        raise ValueError("forbidden inference entailed values must be booleans")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--model", action="append", help="Run only selected model id(s).")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    benchmark = load(EVAL / "cases.json")
    config = load(args.config)
    system = (EVAL / "prompts" / "annotator_system.txt").read_text(encoding="utf-8")
    summary, allowed = ontology_summary()
    cases = benchmark["cases"][: args.limit] if args.limit else benchmark["cases"]

    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = EVAL / "outputs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    selected = set(args.model or [])
    models = [
        resolve_model(entry)
        for entry in config["models"]
        if entry.get("enabled", True)
        and (not selected or entry["id"] in selected)
    ]
    if not models:
        raise SystemExit("No enabled models selected")

    manifest_models = []
    for model in models:
        manifest_models.append(
            {
                "id": model["id"],
                "provider": model["provider"],
                "model": model["model"] or None,
                "base_url": model["base_url"] or None,
                "api_key_env": model.get("api_key_env"),
            }
        )
    manifest = {
        "benchmark_id": benchmark["benchmark_id"],
        "ontology_version": benchmark["ontology_version"],
        "run_id": run_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "case_hash": sha256_text(
            (EVAL / "cases.json").read_text(encoding="utf-8")
        ),
        "system_prompt_hash": sha256_text(system),
        "models": manifest_models,
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    for model in models:
        output_path = run_dir / f"{model['id']}.jsonl"
        with output_path.open("w", encoding="utf-8") as out:
            for case in cases:
                prompt = build_prompt(case, summary)
                base_record = {
                    "benchmark_id": benchmark["benchmark_id"],
                    "ontology_version": benchmark["ontology_version"],
                    "run_id": run_id,
                    "model_id": model["id"],
                    "provider": model["provider"],
                    "model": model["model"] or None,
                    "case_id": case["case_id"],
                    "theme": case["theme"],
                    "prompt_hash": sha256_text(system + "\n" + prompt),
                }
                if args.dry_run:
                    record = {**base_record, "prompt": prompt, "response": None, "error": None}
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    continue

                missing = []
                if not model["model"]:
                    missing.append(model.get("model_env") or "model")
                if not model["base_url"]:
                    missing.append(model.get("base_url_env") or "base_url")
                if not model["api_key"]:
                    missing.append(model.get("api_key_env") or "api_key")
                if missing:
                    raise SystemExit(
                        f"Model {model['id']} missing configuration: {', '.join(missing)}"
                    )

                last_error = None
                started = time.monotonic()
                for attempt in range(args.retries + 1):
                    try:
                        raw_text, _provider_payload = call_provider(
                            provider=model["provider"],
                            base_url=model["base_url"],
                            api_key=model["api_key"],
                            model=model["model"],
                            system=system,
                            prompt=prompt,
                            timeout=args.timeout,
                            json_mode=bool(model.get("json_mode", True)),
                        )
                        parsed = extract_json_object(raw_text)
                        validate_response(parsed, case, allowed)
                        record = {
                            **base_record,
                            "latency_ms": round((time.monotonic() - started) * 1000),
                            "attempts": attempt + 1,
                            "response": parsed,
                            "raw_text": raw_text,
                            "error": None,
                        }
                        break
                    except (ProviderError, ValueError) as exc:
                        last_error = str(exc)
                        if attempt < args.retries:
                            time.sleep(min(2 ** attempt, 4))
                else:
                    record = {
                        **base_record,
                        "latency_ms": round((time.monotonic() - started) * 1000),
                        "attempts": args.retries + 1,
                        "response": None,
                        "raw_text": None,
                        "error": last_error,
                    }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()

        print(f"{model['id']}: wrote {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
