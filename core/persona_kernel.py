"""Ontology-native Persona Kernel v2.

The kernel is diagnosis-neutral. It stores canonical domain payloads and
field-level provenance separately so AI-Persona, P003 and AI-Ques can share one
human representation without sharing application-specific semantics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .human_ontology import (
    canonical_relation_families,
    canonical_v2_domain_ids,
    load_human_ontology_v2,
    ontology_v2_version,
)

SOURCE_TYPES = frozenset(
    load_human_ontology_v2()["field_metadata_contract"]["source_type_values"]
)


def _validate_provenance_record(record: Mapping[str, Any], *, context: str) -> None:
    source_type = record.get("source_type")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"{context} has invalid source_type: {source_type!r}")
    if source_type in {"inferred", "generated"}:
        confidence = record.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(f"{context} generated/inferred confidence must be 0..1")
        if not record.get("provenance") or not record.get("temporal_class"):
            raise ValueError(
                f"{context} generated/inferred record requires provenance and temporal_class"
            )
    if source_type == "input_constraint":
        if not record.get("provenance") or not record.get("temporal_class"):
            raise ValueError(
                f"{context} input_constraint requires provenance and temporal_class"
            )


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
        if self.source_type == "input_constraint":
            if not self.provenance or not self.temporal_class:
                raise ValueError(
                    "input_constraint values require provenance and temporal_class"
                )


@dataclass
class PersonaKernel:
    persona_id: str
    ontology_version: str = field(default_factory=ontology_v2_version)
    domains: dict[str, dict[str, Any]] = field(default_factory=dict)
    field_metadata: dict[str, FieldMetadata] = field(default_factory=dict)
    relations: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    @staticmethod
    def allowed_domain_ids() -> frozenset[str]:
        return frozenset(canonical_v2_domain_ids())

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        allowed = self.allowed_domain_ids()
        unknown = sorted(set(self.domains) - allowed)
        if unknown:
            raise ValueError(f"Unknown Human Ontology v2 domains: {unknown}")
        if "person" in self.domains:
            raise ValueError("Person root is identity, not a domain payload")
        if self.ontology_version != ontology_v2_version():
            raise ValueError(
                f"Kernel ontology_version={self.ontology_version!r} does not match "
                f"runtime ontology={ontology_v2_version()!r}"
            )
        for path, meta in self.field_metadata.items():
            domain = path.split(".", 1)[0]
            if domain not in allowed:
                raise ValueError(f"Metadata path has unknown domain: {path}")
            if not isinstance(meta, FieldMetadata):
                raise TypeError(f"Metadata for {path} must be FieldMetadata")

        allowed_relations = set(canonical_relation_families())
        relation_ids: set[str] = set()
        for index, relation in enumerate(self.relations):
            if not isinstance(relation, dict):
                raise TypeError(f"relation[{index}] must be a dict")
            relation_id = relation.get("relation_id")
            if not relation_id:
                raise ValueError(f"relation[{index}] requires relation_id")
            if relation_id in relation_ids:
                raise ValueError(f"duplicate relation_id: {relation_id}")
            relation_ids.add(str(relation_id))
            canonical_path = relation.get("canonical_path")
            if not canonical_path or "." not in canonical_path:
                raise ValueError(f"relation[{index}] requires canonical_path")
            domain, key = canonical_path.split(".", 1)
            if domain not in allowed:
                raise ValueError(
                    f"relation[{index}] canonical_path has unknown domain: {canonical_path}"
                )
            if key in self.domains.get(domain, {}):
                raise ValueError(
                    f"relation[{index}] duplicates domain payload at {canonical_path}"
                )
            predicate = relation.get("predicate")
            if predicate not in allowed_relations:
                raise ValueError(
                    f"relation[{index}] has unknown predicate {predicate!r}"
                )
            _validate_provenance_record(relation, context=f"relation[{index}]")

        event_ids: set[str] = set()
        for index, event in enumerate(self.events):
            if not isinstance(event, dict):
                raise TypeError(f"event[{index}] must be a dict")
            event_id = event.get("event_id")
            if not event_id:
                raise ValueError(f"event[{index}] requires event_id")
            if event_id in event_ids:
                raise ValueError(f"duplicate event_id: {event_id}")
            event_ids.add(str(event_id))
            canonical_path = event.get("canonical_path")
            if not canonical_path or "." not in canonical_path:
                raise ValueError(f"event[{index}] requires canonical_path")
            domain, key = canonical_path.split(".", 1)
            if domain not in allowed:
                raise ValueError(
                    f"event[{index}] canonical_path has unknown domain: {canonical_path}"
                )
            if key in self.domains.get(domain, {}):
                raise ValueError(
                    f"event[{index}] duplicates domain payload at {canonical_path}"
                )
            if not event.get("type"):
                raise ValueError(f"event[{index}] requires type")
            _validate_provenance_record(event, context=f"event[{index}]")

    def set_value(
        self, domain: str, key: str, value: Any, metadata: FieldMetadata
    ) -> None:
        if domain not in self.allowed_domain_ids():
            raise ValueError(f"Unknown Human Ontology v2 domain: {domain}")
        self.domains.setdefault(domain, {})[key] = value
        self.field_metadata[f"{domain}.{key}"] = metadata

    def get_value(self, domain: str, key: str, default: Any = None) -> Any:
        return self.domains.get(domain, {}).get(key, default)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
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
            ontology_version=str(payload.get("ontology_version", ontology_v2_version())),
            domains={k: dict(v) for k, v in payload.get("domains", {}).items()},
            field_metadata=metadata,
            relations=list(payload.get("relations", [])),
            events=list(payload.get("events", [])),
        )
