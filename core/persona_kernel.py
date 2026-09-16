"""Ontology-native Persona Kernel v2.

The kernel is deliberately diagnosis-neutral. It stores canonical domain payloads
and provenance separately, allowing AI-persona, P003 and AI-Ques to share one
human representation without sharing one application model.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Mapping

V2_DOMAIN_IDS = frozenset({
    "development", "body_functioning_health", "mental_neurodevelopmental_health",
    "personality_psychology", "abilities_skills_interests", "identity_affiliations",
    "roles", "relationships", "place_mobility", "education_work_economy",
    "social_institutional_position", "culture_language", "life_events",
    "context_ecology", "resources_constraints_opportunities", "lifestyle_routines",
    "current_state",
})

SOURCE_TYPES = frozenset({
    "user_provided", "observed", "measured", "inferred", "generated", "derived",
    "external_reference",
})


@dataclass(frozen=True)
class FieldMetadata:
    source_type: str
    confidence: float | None = None
    provenance: str | None = None
    temporal_class: str | None = None

    def __post_init__(self) -> None:
        if self.source_type not in SOURCE_TYPES:
            raise ValueError(f"Unknown source_type: {self.source_type}")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.source_type in {"inferred", "generated"}:
            if self.confidence is None or not self.provenance or not self.temporal_class:
                raise ValueError(
                    "inferred/generated values require confidence, provenance and temporal_class"
                )


@dataclass
class PersonaKernel:
    persona_id: str
    ontology_version: str = "2.0.0-rc1"
    domains: dict[str, dict[str, Any]] = field(default_factory=dict)
    field_metadata: dict[str, FieldMetadata] = field(default_factory=dict)
    relations: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        unknown = sorted(set(self.domains) - V2_DOMAIN_IDS)
        if unknown:
            raise ValueError(f"Unknown Human Ontology v2 domains: {unknown}")
        if "person" in self.domains:
            raise ValueError("Person root is identity, not a domain payload")
        for path, meta in self.field_metadata.items():
            domain = path.split(".", 1)[0]
            if domain not in V2_DOMAIN_IDS:
                raise ValueError(f"Metadata path has unknown domain: {path}")
            if not isinstance(meta, FieldMetadata):
                raise TypeError(f"Metadata for {path} must be FieldMetadata")

    def set_value(self, domain: str, key: str, value: Any, metadata: FieldMetadata) -> None:
        if domain not in V2_DOMAIN_IDS:
            raise ValueError(f"Unknown Human Ontology v2 domain: {domain}")
        self.domains.setdefault(domain, {})[key] = value
        self.field_metadata[f"{domain}.{key}"] = metadata

    def get_value(self, domain: str, key: str, default: Any = None) -> Any:
        return self.domains.get(domain, {}).get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "ontology_version": self.ontology_version,
            "domains": self.domains,
            "field_metadata": {k: asdict(v) for k, v in self.field_metadata.items()},
            "relations": self.relations,
            "events": self.events,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "PersonaKernel":
        metadata = {
            path: value if isinstance(value, FieldMetadata) else FieldMetadata(**value)
            for path, value in payload.get("field_metadata", {}).items()
        }
        return cls(
            persona_id=str(payload["persona_id"]),
            ontology_version=str(payload.get("ontology_version", "2.0.0-rc1")),
            domains={k: dict(v) for k, v in payload.get("domains", {}).items()},
            field_metadata=metadata,
            relations=list(payload.get("relations", [])),
            events=list(payload.get("events", [])),
        )
