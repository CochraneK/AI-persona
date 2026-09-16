# AI-Persona — Human Ontology + Persona Engine

AI-Persona hosts the shared Human Ontology and the engines/adapters that instantiate it into computational Persona representations.

## Architecture

```
Human Ontology v2
   ├─ canonical semantic homes
   ├─ typed roles / relations / events / states
   ├─ provenance + temporality contract
   └─ optional domain ontologies
              ↓
        PersonaKernel
        ↙    ↓     ↘
   AI-Ques   P003   Persona/Future-Self/Avatar consumers
```

The old psychiatric Persona generator is retained for backwards compatibility and research reproduction. It is not the ontology.

## Normative files

- `ontology/human_ontology.v2.json` — v2 release-candidate semantic model.
- `ontology/CANONICAL_FIELD_REGISTRY.json` — one canonical home per semantic concept.
- `ontology/V1_TO_V2_MIGRATION.json` — migration from the v1 coverage model.
- `ontology/persona_kernel.schema.json` — exchange envelope.
- `ontology/CONSUMER_CONTRACT.md` — cross-project contract.
- `ontology/HUMAN_ONTOLOGY_REVIEW.md` — ontology governance.
- `ontology/domains/psychiatric_diagnosis.module.json` — psychiatric module mounted under mental health.

Runtime:
- `core/human_ontology.py` — v1/v2 loaders and canonical-ID helpers.
- `core/persona_kernel.py` — ontology-native runtime model.
- `core/kernel_generator.py` — v2 transitional generator with health-only psychiatric influence by default.
- `core/legacy_adapter.py` — flat v1 Persona → PersonaKernel migration bridge.
- `core/generator.py` — legacy v1.x generator.
- `core/archetypes.py` — legacy narrative-generation assets.
- `core/personality.py` — trait/generation utilities; Big Five is one trait model, not the ontology.

## Non-negotiable semantic rules

1. **One canonical semantic home.** UI duplication is allowed; ontology duplication is not.
2. **Local MECE only.** Apply MECE to sibling classifications answering the same question, not to every human fact globally.
3. Distinguish **entity / quality-disposition / role / relation / process-event / state**.
4. **Diagnosis is optional health information, never the Person root.**
5. Diagnosis must not deterministically define personality, values, morality, competence, relationships, biography or life outcome.
6. Archetypes are `narrative_identity` generation assets, not clinical personality types or psychometric truth.
7. Big Five/OCEAN belongs to `personality_psychology.temperament_traits`; it is not a MECE Human Ontology.
8. Place ≠ culture ≠ citizenship; role ≠ identity; relationship observation ≠ global disposition; state ≠ trait.
9. Unknown ≠ absent. Generated ≠ observed. Inferred ≠ measured.
10. Inferred/generated values require provenance, confidence and temporal class.

## Public APIs

Preferred v2 API:

```python
from core import generate_persona_kernel

kernel = generate_persona_kernel(
    primary_diagnosis="重度抑郁障碍",
    rng_seed=42,
)
```

By default, psychiatric diagnosis is isolated to the mental-health/current-state payload. For the same seed, diagnosis must not change non-health personality or life history.

Legacy compatibility API:

```python
from core import generate_persona

persona = generate_persona(
    primary_diagnosis="重度抑郁障碍",
    rng_seed=42,
)
print(persona.system_prompt)
```

Use the legacy API only when reproducing v1.x behavior or legacy datasets.

## Psychiatry migration

`diagnosis_ontology.json` is preserved. Do not delete it merely because Human Ontology v2 exists.

Its role is now a domain asset:

```
Person
  └─ mental_neurodevelopmental_health
       ├─ symptoms / experiences
       ├─ functional impact
       ├─ diagnoses (optional)
       ├─ treatment / support
       ├─ course / recovery
       └─ risk / protective factors
```

Legacy diagnosis-conditioned personality/archetype/event generation is compatibility behavior behind the v2 semantic firewall and should not be expanded into new canonical logic.

## Tests / quality gate

Run:

```bash
python scripts/validate_human_ontology.py
python scripts/validate_human_ontology_v2.py
python scripts/test_persona_kernel_compat.py
python scripts/test_events_sampling.py
python -m py_compile core/*.py
```

The GitHub Actions workflow `.github/workflows/ontology-ci.yml` must pass before v2 is promoted from release candidate to canonical.

## Change policy

Before adding a new human concept:
1. search `CANONICAL_FIELD_REGISTRY.json`;
2. decide its ontological kind;
3. verify it is not a relation/view of an existing concept;
4. define cardinality and temporality;
5. review sensitivity and inference risk;
6. add migration mapping if replacing a legacy field;
7. update schema/validators/tests;
8. follow `HUMAN_ONTOLOGY_REVIEW.md`.

Content libraries can grow freely. Canonical ontology changes are governed.
