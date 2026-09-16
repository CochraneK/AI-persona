"""Public API for AI-Persona.

The legacy Persona generator remains supported while Human Ontology v2 is
adopted. New consumers should prefer generate_persona_kernel.
"""
from .generator import Persona, PersonaGenerator, batch_generate, generate_persona
from .legacy_adapter import kernel_compatibility_report, legacy_persona_to_kernel
from .persona_kernel import FieldMetadata, PersonaKernel
from .personality import DIAGNOSIS_OCEAN_RANGES


def generate_persona_kernel(primary_diagnosis=None, rng_seed=None, **kwargs):
    """Generate a legacy-compatible persona and return its v2 PersonaKernel."""
    return legacy_persona_to_kernel(
        generate_persona(primary_diagnosis=primary_diagnosis, rng_seed=rng_seed, **kwargs)
    )


__all__ = [
    "Persona",
    "PersonaGenerator",
    "PersonaKernel",
    "FieldMetadata",
    "generate_persona",
    "batch_generate",
    "generate_persona_kernel",
    "legacy_persona_to_kernel",
    "kernel_compatibility_report",
    "DIAGNOSIS_OCEAN_RANGES",
]
