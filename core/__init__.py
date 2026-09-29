"""Public API for AI-Persona.

Legacy Persona generation remains available for backwards compatibility.
New integrations should prefer generate_persona_kernel / KernelGenerator, which
apply the Human Ontology v2 semantic firewall by default.
"""
from .generator import Persona, PersonaGenerator, batch_generate, generate_persona
from .kernel_generator import KernelGenerationPolicy, KernelGenerator, generate_kernel
from .legacy_adapter import kernel_compatibility_report, legacy_persona_to_kernel
from .persona_kernel import EntityRef, FieldMetadata, PersonaKernel
from .personality import DIAGNOSIS_OCEAN_RANGES


def generate_persona_kernel(primary_diagnosis=None, rng_seed=None, **kwargs):
    """Generate an ontology-native PersonaKernel with health-only diagnosis influence."""
    return generate_kernel(
        primary_diagnosis=primary_diagnosis,
        rng_seed=rng_seed,
        psychiatric_influence_scope="health_only",
        **kwargs,
    )


__all__ = [
    "Persona",
    "PersonaGenerator",
    "PersonaKernel",
    "EntityRef",
    "FieldMetadata",
    "KernelGenerator",
    "KernelGenerationPolicy",
    "generate_persona",
    "batch_generate",
    "generate_persona_kernel",
    "generate_kernel",
    "legacy_persona_to_kernel",
    "kernel_compatibility_report",
    "DIAGNOSIS_OCEAN_RANGES",
]
