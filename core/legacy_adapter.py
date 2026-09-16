"""Compatibility bridge from legacy flat Persona objects to Human Ontology v2.

This module is intentionally one-way: legacy generator output can be consumed as
an ontology-native PersonaKernel, while v2 consumers must not depend on legacy
field placement.
"""
from __future__ import annotations

from typing import Any

from .persona_kernel import FieldMetadata, PersonaKernel


def _event_to_dict(event: Any) -> dict[str, Any]:
    return {
        "type": "life_event",
        "legacy_domain": getattr(event, "domain", None),
        "legacy_stage": getattr(event, "stage", None),
        "name": getattr(event, "name_cn", "") or getattr(event, "name_en", ""),
        "name_en": getattr(event, "name_en", ""),
        "valence": getattr(event, "valence", None),
        "lcu": getattr(event, "lcu", None),
        "diagnosis_relation": getattr(event, "diagnosis_relation", None),
        "source_type": "generated",
        "provenance": "legacy events.py",
    }


def legacy_persona_to_kernel(persona: Any) -> PersonaKernel:
    """Map a v1.x flat Persona into the v2 canonical semantic homes.

    No information is intentionally discarded. Fields whose old semantics were
    ambiguous are retained under explicit legacy_* keys instead of being
    silently reinterpreted.
    """
    kernel = PersonaKernel(persona_id=str(persona.id))

    def put(domain: str, key: str, value: Any, *, temporal: str = "derived") -> None:
        if value in (None, "", [], {}):
            return
        kernel.set_value(
            domain,
            key,
            value,
            FieldMetadata("generated", 1.0, "legacy PersonaGenerator adapter", temporal),
        )

    put("development", "chronological_age", persona.age, temporal="dynamic_state")
    put("development", "erikson_stage", persona.erikson_stage, temporal="slow_changing")
    put("identity_self_concept", "legacy_gender_label", persona.gender, temporal="slow_changing")

    put("place_mobility", "legacy_residence_context", persona.locale, temporal="dynamic_state")
    put("education_learning", "education_attainment", persona.education, temporal="slow_changing")
    put(
        "education_work_economy",
        "occupation",
        {"label": persona.occupation, "code": persona.occupation_code},
        temporal="role_dependent",
    )
    kernel.relations.append({
        "predicate": "has_role",
        "relation_type": "occupation",
        "value": persona.occupation,
        "code": persona.occupation_code,
        "source_type": "generated",
        "provenance": "legacy PersonaGenerator adapter",
    })

    put("relationships", "legacy_marital_status", persona.marital_status, temporal="relationship_specific")
    put("relationships", "legacy_social_relations_profile", persona.social_relations, temporal="relationship_specific")

    if persona.primary_diagnosis and persona.primary_diagnosis != "无精神障碍（健康）":
        diagnoses = [{
            "label": persona.primary_diagnosis,
            "label_en": persona.primary_diagnosis_en,
            "role": "primary",
        }]
        diagnoses.extend({"label": x, "role": "comorbid"} for x in persona.comorbidities)
        put("mental_neurodevelopmental_health", "diagnoses", diagnoses, temporal="slow_changing")
    else:
        put(
            "mental_neurodevelopmental_health",
            "generated_mental_health_status",
            "no_disorder_generated",
            temporal="dynamic_state",
        )
    put("mental_neurodevelopmental_health", "triggers", persona.triggers, temporal="dynamic_state")
    put("mental_neurodevelopmental_health", "safety_behaviors", persona.safety_behaviors, temporal="dynamic_state")

    put("personality_psychology", "temperament_traits", {
        "ocean": persona.ocean,
        "description": persona.ocean_description,
        "legacy_tags": persona.personality_tags,
    }, temporal="slow_changing")
    put("personality_psychology", "motives_values_goals", {
        "core_desire": persona.core_desire,
        "core_fear": persona.core_fear,
        "legacy_values_beliefs": persona.values_beliefs,
    }, temporal="slow_changing")
    put("personality_psychology", "cognition_beliefs", {
        "cognitive_styles": persona.cognitive_styles,
        "dysfunctional_beliefs": persona.dysfunctional_beliefs,
    }, temporal="slow_changing")
    put("personality_psychology", "emotion_regulation_coping", {
        "coping_styles": persona.coping_styles,
        "stress_pattern": persona.stress_pattern,
    }, temporal="dynamic_state")
    put("personality_psychology", "narrative_identity", {
        "archetype": {
            "key": persona.archetype_key,
            "name": persona.archetype_name,
            "one_liner": persona.archetype_one_liner,
        },
        "formative_wound": persona.formative_wound,
        "compensatory_desire": persona.compensatory_desire,
        "developmental_need": persona.storr_need,
        "character_arc": {
            "type": persona.arc_type,
            "description": persona.arc_description,
        },
        "hidden_experiences": persona.hidden_experiences,
    }, temporal="slow_changing")
    put("personality_psychology", "surface_expression", persona.communication_style, temporal="dynamic_state")

    put("abilities_skills_interests", "legacy_profile", persona.skills_abilities, temporal="slow_changing")
    put("lifestyle_routines", "legacy_profile", persona.lifestyle_habits, temporal="dynamic_state")
    put("body_functioning_health", "physical_appearance", persona.physical_appearance, temporal="dynamic_state")
    put("current_state", "summary", persona.current_status, temporal="dynamic_state")

    kernel.events = [_event_to_dict(e) for e in persona.life_events]
    kernel.validate()
    return kernel


def kernel_compatibility_report(kernel: PersonaKernel) -> dict[str, Any]:
    """Small machine-readable report for migration/testing."""
    return {
        "persona_id": kernel.persona_id,
        "ontology_version": kernel.ontology_version,
        "populated_domains": sorted(kernel.domains),
        "relation_count": len(kernel.relations),
        "event_count": len(kernel.events),
        "metadata_paths": len(kernel.field_metadata),
    }
