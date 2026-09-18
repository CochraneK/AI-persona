"""Human Ontology v2 transitional Kernel generator.

The default policy isolates psychiatric diagnosis to the mental-health domain.
It intentionally prevents legacy diagnosis-conditioned samplers from changing
personality, narrative identity, occupation, demographics or life history.

This is a migration architecture: legacy modules are reused behind a semantic
firewall until fully ontology-native samplers replace them.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from .generator import generate_persona
from .legacy_adapter import legacy_persona_to_kernel
from .persona_kernel import FieldMetadata, PersonaKernel


@dataclass(frozen=True)
class KernelGenerationPolicy:
    psychiatric_influence_scope: str = "health_only"

    def __post_init__(self) -> None:
        if self.psychiatric_influence_scope not in {"health_only", "legacy_full"}:
            raise ValueError(
                "psychiatric_influence_scope must be 'health_only' or 'legacy_full'"
            )


class KernelGenerator:
    def __init__(
        self,
        rng_seed: int | None = None,
        policy: KernelGenerationPolicy | None = None,
    ) -> None:
        self.rng_seed = rng_seed
        self.policy = policy or KernelGenerationPolicy()

    @staticmethod
    def _without(kwargs: dict[str, Any], *keys: str) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if k not in keys}

    def _healthy_base(self, **kwargs: Any) -> PersonaKernel:
        clean = self._without(kwargs, "healthy_ratio")
        persona = generate_persona(
            rng_seed=self.rng_seed,
            healthy_ratio=1.0,
            **clean,
        )
        return legacy_persona_to_kernel(persona)

    def _diagnosed_source(self, diagnosis: str, **kwargs: Any) -> PersonaKernel:
        clean = self._without(kwargs, "healthy_ratio")
        health_seed = None if self.rng_seed is None else self.rng_seed + 1_000_003
        persona = generate_persona(
            primary_diagnosis=diagnosis,
            rng_seed=health_seed,
            healthy_ratio=0.0,
            **clean,
        )
        return legacy_persona_to_kernel(persona)

    def generate(
        self,
        primary_diagnosis: str | None = None,
        **kwargs: Any,
    ) -> PersonaKernel:
        if self.policy.psychiatric_influence_scope == "legacy_full":
            persona = generate_persona(
                primary_diagnosis=primary_diagnosis,
                rng_seed=self.rng_seed,
                **kwargs,
            )
            return legacy_persona_to_kernel(persona)

        base = self._healthy_base(**kwargs)
        if not primary_diagnosis:
            return base

        health = self._diagnosed_source(primary_diagnosis, **kwargs)
        mental = deepcopy(health.domains.get("mental_neurodevelopmental_health", {}))

        # The requested primary diagnosis is a generation constraint, not evidence
        # that a real person was observed/clinically diagnosed. Preserve that
        # epistemic distinction at item level; generated comorbidities remain generated.
        for diagnosis in mental.get("diagnoses", []):
            if diagnosis.get("role") == "primary":
                diagnosis["source_type"] = "input_constraint"
                diagnosis["confidence"] = None
                diagnosis["provenance"] = "generate_kernel(primary_diagnosis=...)"
                diagnosis["temporal_class"] = "slow_changing"

        base.domains["mental_neurodevelopmental_health"] = mental

        prefix = "mental_neurodevelopmental_health."
        base.field_metadata = {
            path: meta
            for path, meta in base.field_metadata.items()
            if not path.startswith(prefix)
        }
        for path, meta in health.field_metadata.items():
            if path.startswith(prefix):
                if path == "mental_neurodevelopmental_health.diagnoses":
                    base.field_metadata[path] = FieldMetadata(
                        source_type="generated",
                        confidence=1.0,
                        provenance=(
                            "mixed collection: primary=input_constraint; "
                            "legacy comorbidities=generated"
                        ),
                        temporal_class="slow_changing",
                    )
                else:
                    base.field_metadata[path] = FieldMetadata(
                        source_type=meta.source_type,
                        confidence=meta.confidence,
                        provenance="psychiatric domain module: health-only overlay",
                        temporal_class=meta.temporal_class,
                    )

        # Health-domain relations (for example typed trigger relations) follow the
        # same health-only overlay rule. Rebind the relation subject to the base
        # PersonaKernel identity and replace any healthy-base health relations.
        base.relations = [
            relation
            for relation in base.relations
            if not str(relation.get("canonical_path", "")).startswith(prefix)
        ]
        health_relations = [
            deepcopy(relation)
            for relation in health.relations
            if str(relation.get("canonical_path", "")).startswith(prefix)
        ]
        for index, relation in enumerate(health_relations, start=1):
            relation["relation_id"] = (
                f"{base.persona_id}:health-overlay:{index}:{relation.get('predicate', 'relation')}"
            )
            if isinstance(relation.get("subject"), dict):
                relation["subject"]["entity_id"] = base.persona_id
                relation["subject"]["entity_type"] = "person"
            relation["provenance"] = "psychiatric domain module: health-only relation overlay"
        base.relations.extend(health_relations)

        # Current state may legitimately reflect an explicitly supplied diagnosis,
        # but it remains a dynamic generated state, never a personality trait.
        if "current_state" in health.domains:
            base.domains["current_state"] = deepcopy(health.domains["current_state"])
            for path, meta in list(health.field_metadata.items()):
                if path.startswith("current_state."):
                    base.field_metadata[path] = FieldMetadata(
                        source_type=meta.source_type,
                        confidence=meta.confidence,
                        provenance="psychiatric domain module: current-state overlay",
                        temporal_class=meta.temporal_class,
                    )

        base.validate()
        return base


def generate_kernel(
    primary_diagnosis: str | None = None,
    rng_seed: int | None = None,
    *,
    psychiatric_influence_scope: str = "health_only",
    **kwargs: Any,
) -> PersonaKernel:
    return KernelGenerator(
        rng_seed=rng_seed,
        policy=KernelGenerationPolicy(psychiatric_influence_scope),
    ).generate(primary_diagnosis=primary_diagnosis, **kwargs)
