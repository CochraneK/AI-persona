# Human Ontology — Canonical Human/Persona Ontology

AI-Persona hosts the canonical Human Ontology intended for AI-Persona, P003, AI-Ques and future person-centered systems.

## Current status

- `human_ontology.v1.json` remains the **canonical compatibility schema** while v2 is being migrated.
- `HUMAN_ONTOLOGY_V2_ARCHITECTURE.md` is the normative architecture contract for the refactor.
- `V1_V2_OVERLAP_AUDIT.md` records unresolved semantic overlaps; v2 cannot become canonical while material overlaps remain unresolved.
- `EXTERNAL_ONTOLOGY_REGISTRY.json` records external standards/ontologies considered for alignment or mapping.

This avoids a flag day: existing generators and psychiatric assets keep working while the ontology is made structurally cleaner.

## Core rule

> **Orthogonal semantic homes + local MECE + typed cross-axis relations.**

The older shorthand, “orthogonal axes across the system; MECE within each axis,” remains useful but is insufficient on its own. Real humans contain multi-valued, temporal, continuous and relational facts that should not be forced into false mutual exclusivity.

### One canonical home
A concept is defined once. Other modules reference it rather than creating competing copies.

### Local MECE
Closed single-valued classifications should be mutually exclusive and collectively exhaustive at their declared abstraction level. Multi-valued, continuous, fuzzy and culturally local constructs must explicitly declare those semantics instead of pretending to be MECE.

### Typed relations
A person, partner, organization, place or event can participate in multiple domains without being duplicated. Cross-domain facts should increasingly be represented through typed relations and projections.

## Ontological kinds introduced for v2

v2 explicitly distinguishes:

1. entity;
2. quality / disposition;
3. role;
4. relation;
5. process / event;
6. state.

This is informed by upper-ontology practice such as BFO, while remaining a pragmatic application ontology for computational person representation.

## v1 top-level coverage

v1 currently covers 19 practical axes:

1. Time & development
2. Place, residence & mobility
3. Culture & language environment
4. Sex, gender & intimate orientation
5. Body, functioning & physical health
6. Mental / neurodevelopmental health
7. Education & learning
8. Work & economic position
9. Social structural & institutional position
10. Family, kinship & household
11. Relationships & social networks
12. Personality & psychological organization
13. Abilities, skills & interests
14. Lifestyle & routines
15. Life events & history
16. Ecology & macro context
17. Resources, constraints & opportunities
18. Roles & responsibilities
19. Current state

These are now treated as **coverage views**, not proof that all 19 are perfectly orthogonal ontological primitives. The v2 audit may retain, relationize, move or deprecate individual fields while preserving compatibility mappings.

## Psychiatry is retained, not deleted

The existing diagnosis ontology, ICD/DSM mappings, symptom logic, archetypes, events and psychiatric persona assets remain project assets.

The architectural change is that diagnosis becomes an optional domain module under mental/neurodevelopmental health rather than the root identity of a persona:

```text
Person
  └─ Mental / neurodevelopmental health
       ├─ symptoms & experiences
       ├─ functioning / impairment
       ├─ diagnoses (optional)
       ├─ treatment & support
       ├─ course / recovery
       └─ risk & protective factors
```

Healthy and diagnosed personas must use the same Person/Persona Kernel. Diagnosis must never be required to make a persona richly specified.

## Personality

The seven-layer model remains:

1. temperament & stable traits;
2. motives, values & goals;
3. cognition & beliefs;
4. emotion regulation & coping;
5. relational patterns;
6. narrative identity;
7. surface expression.

Archetypes remain useful as a **narrative/generative model** under narrative identity, not as a universal psychometric taxonomy.

## Important separations

- birthplace ≠ culture ≠ citizenship;
- diagnosis ≠ symptom ≠ impairment ≠ treatment ≠ identity;
- trait ≠ motive ≠ coping ≠ current state;
- relationship-specific observation ≠ global personality disposition;
- role ≠ person;
- event ≠ enduring attribute;
- structural constraint ≠ personality weakness;
- source fact ≠ derived current-resource projection.

## External alignment

Human Ontology should reuse or map established semantics rather than reinventing domain vocabularies. Candidate references include BFO/RO, Mental Functioning Ontology, Emotion Ontology, HPO, ICF, ICD/DSM, FHIR Person and Schema.org Person. See `EXTERNAL_ONTOLOGY_REGISTRY.json`.

External semantics are never silently copied: mappings require provenance and review.

## Shared classifications

v1 defines canonical IDs for 10 life domains, 9 lifespan stages and 13 event pressure/affordance shapes. AI-Persona's older 6-domain × 4-stage event matrix is retained as a legacy source and maps into the canonical scheme.

## Governance

Ontology changes must follow `HUMAN_ONTOLOGY_REVIEW.md` and the v2 quality gates. New personas/events may expand easily; new canonical concepts should be comparatively difficult to add.

Before v2 is marked canonical, the project must have:

- resolved or explicitly accepted the overlap register;
- unique canonical concept IDs and homes;
- explicit ontological kind/cardinality/temporality where applicable;
- provenance for external mappings and empirical priors;
- complete v1 migration mappings;
- automated checks against diagnosis-as-identity and deterministic sensitive inference.
