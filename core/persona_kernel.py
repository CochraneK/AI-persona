"""Ontology-native Persona Kernel v2.

The kernel enforces Human Ontology's runtime invariants:
- one canonical semantic home;
- complete field-level provenance for domain values;
- typed relation endpoints;
- stable relation/event IDs;
- versioned ontology semantics shared across consumers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .human_ontology import (
    canonical_entity_types,
    canonical_relation_families,
    canonical_v2_domain_ids,
    load_human_ontology_v2,
    ontology_v2_version,
)

_ONTOLOGY = load_human_ontology_v2()
SOURCE_TYPES = frozenset(_ONTOLOGY["field_metadata_contract"]["source_type_values"])
RELATION_CONSTRAINTS = _ONTOLOGY["relation_constraints"]


def _validate_provenance_record(record: Mapping[str, Any], *, context: str) -> None:
    source_type = record.get("source_type")
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"{context} has invalid source_type: {source_type!r}")
    if not record.get("provenance"):
        raise ValueError(f"{context} requires provenance")
    if not record.get("temporal_class"):
        raise ValueError(f"{context} requires temporal_class")
    confidence = record.get("confidence")
    if confidence is not None and (
        not isinstance(confidence, (int, float))
        or not 0.0 <= float(confidence) <= 1.0
    ):
        raise ValueError(f"{context} confidence must be 0..1")
    if source_type in {"inferred", "generated"} and confidence is None:
        raise ValueError(f"{context} generated/inferred confidence must be 0..1")


@dataclass(frozen=True)
class EntityRef:
    entity_id: str
    entity_type: str
    label: str | None = None
    source_system: str | None = None
    source_id: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("EntityRef.entity_id is required")
        if self.entity_type not in set(canonical_entity_types()):
            raise ValueError(f"Unknown entity_type: {self.entity_type}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "EntityRef":
        return cls(
            entity_id=str(value["entity_id"]),
            entity_type=str(value["entity_type"]),
            label=value.get("label"),
            source_system=value.get("source_system"),
            source_id=value.get("source_id"),
        )


@dataclass(frozen=True)
class FieldMetadata:
    source_type: str
    confidence: float | None = None
    provenance: str | None = None
    temporal_class: str | None = None

    def __post_init__(self) -> None:
        _validate_provenance_record(asdict(self), context="FieldMetadata")


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

    def _validate_domain_metadata_completeness(self) -> None:
        allowed = self.allowed_domain_ids()
        expected_paths = {
            f"{domain}.{key}"
            for domain, payload in self.domains.items()
            for key in payload
        }
        actual_paths = set(self.field_metadata)

        missing = sorted(expected_paths - actual_paths)
        if missing:
            raise ValueError(f"Domain values missing field_metadata: {missing}")

        orphan = sorted(actual_paths - expected_paths)
        if orphan:
            raise ValueError(f"field_metadata has no matching domain value: {orphan}")

        for path, meta in self.field_metadata.items():
            domain = path.split(".", 1)[0]
            if domain not in allowed:
                raise ValueError(f"Metadata path has unknown domain: {path}")
            if not isinstance(meta, FieldMetadata):
                raise TypeError(f"Metadata for {path} must be FieldMetadata")

    def _validate_entity_ref(
        self,
        value: Mapping[str, Any],
        *,
        context: str,
    ) -> EntityRef:
        if not isinstance(value, Mapping):
            raise TypeError(f"{context} must be an EntityRef object")
        try:
            return EntityRef.from_mapping(value)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{context} invalid EntityRef: {exc}") from exc

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

        self._validate_domain_metadata_completeness()

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

            subject = self._validate_entity_ref(
                relation.get("subject"),
                context=f"relation[{index}].subject",
            )
            obj = self._validate_entity_ref(
                relation.get("object"),
                context=f"relation[{index}].object",
            )
            if subject.entity_type != "person" or subject.entity_id != self.persona_id:
                raise ValueError(
                    f"relation[{index}] subject must reference PersonaKernel person "
                    f"{self.persona_id!r}"
                )

            allowed_object_types = set(
                RELATION_CONSTRAINTS[predicate]["object_entity_types"]
            )
            if obj.entity_type not in allowed_object_types:
                raise ValueError(
                    f"relation[{index}] predicate {predicate!r} does not allow "
                    f"object entity_type {obj.entity_type!r}; "
                    f"expected one of {sorted(allowed_object_types)}"
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

            participants = event.get("participants", [])
            if not isinstance(participants, list):
                raise TypeError(f"event[{index}].participants must be a list")
            for participant_index, participant in enumerate(participants):
                self._validate_entity_ref(
                    participant,
                    context=f"event[{index}].participants[{participant_index}]",
                )
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

    def person_ref(self, label: str | None = None) -> EntityRef:
        return EntityRef(self.persona_id, "person", label=label)

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
