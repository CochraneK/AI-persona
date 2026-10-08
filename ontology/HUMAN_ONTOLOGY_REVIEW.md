# Human Ontology Review Policy

Human Ontology is the shared semantic authority for AI-Persona, P003, AI-Ques and future person-centered systems. v2.0.0 is the canonical semantic authority (promoted 2026-09-30); v1 remains the compatibility schema for legacy consumers.

## Core rule

> **One canonical semantic home + local MECE + typed relations.**

Canonical domains are semantic namespaces, not ontological kinds. Concrete concepts must be typed as one of:
- entity;
- quality / disposition;
- role;
- relation;
- process / event;
- state.

MECE applies only when sibling categories answer the same question at the same abstraction level. Multi-valued, continuous, temporal, fuzzy or relational facts must not be forced into false exclusivity.

Examples:
- birthplace → `place_mobility.birth_place` as a place relation;
- cultural exposure → `culture_language.*`;
- citizenship/legal status → `social_institutional_position.*`;
- OCEAN → `personality_psychology.temperament_traits.ocean`;
- self-efficacy → `personality_psychology.cognition_beliefs.self_efficacy`;
- coping → `personality_psychology.emotion_regulation_coping`;
- diagnosis → `mental_neurodevelopmental_health.diagnoses`;
- archetype → `personality_psychology.narrative_identity`;
- relationship quality → `relationships.*`, not a global personality trait;
- today's stress → `current_state.stress`;
- role transition → `life_events.role_transition`, while the resulting role belongs under `roles`.

## Why place, culture, identity and legal status are separate

A person may:
- be born in one country;
- grow up in another;
- live in a third;
- speak several languages;
- participate in several cultural communities;
- identify in ways not reducible to those communities;
- hold citizenship/legal status that differs from birthplace, residence or cultural participation.

Therefore:
- geography must not infer culture;
- culture must not infer citizenship;
- citizenship must not infer identity;
- any cross-domain inference needs explicit evidence/provenance.

## Provisional migrated concepts

`CANONICAL_CONCEPT_CATALOG.json` distinguishes two review states:

- `reviewed` — first-class concepts with reviewed definition, kind, cardinality, temporality, sensitivity, storage mode and value contract;
- `provisional_migrated` — legacy leaf concepts whose **canonical semantic home is accepted**, but whose leaf-level kind/cardinality/value contract may still be refined.

A provisional concept may be used for migration, archival compatibility and bounded internal representation. It should not be treated as a stable cross-project API contract until promoted to `reviewed`.

Promotion to `reviewed` requires:
1. definition and counterexample review;
2. ontological kind review;
3. cardinality and temporal semantics;
4. sensitivity/inference review;
5. storage mode and value contract;
6. consumer compatibility check;
7. validator/schema updates where applicable.

Promotion may refine leaf semantics without moving its canonical semantic home. Moving the home remains a MAJOR ontology change.

## Change classes


### PATCH
- wording/description;
- adding an alias;
- correcting a non-semantic mapping;
- adding provenance;
- adding a non-semantic example.

Does not change canonical meaning.

### MINOR
- adding a first-class canonical concept inside an existing semantic namespace;
- adding an enum/classification value without changing existing meaning;
- adding an external code-system mapping;
- adding a new relation subtype compatible with current semantics.

Requires ontology review + compatibility/schema tests.

### MAJOR
- adding/removing/renaming a canonical domain;
- moving a concept between canonical semantic homes;
- changing concept meaning or ontological kind;
- replacing a canonical classification;
- changing stable IDs;
- changing consumer-visible Kernel semantics.

Requires migration plan and major version bump.

## Required review questions

Every ontology change must answer:

1. **Canonical home** — What single canonical path owns this concept?
2. **Ontological kind** — entity, quality/disposition, role, relation, process/event, or state?
3. **Duplicate check** — Is this actually new, or a view/relation/projection of an existing concept?
4. **MECE scope** — Does this belong to a sibling classification answering one question? If yes, is that classification mutually exclusive and sufficiently exhaustive? If not, do not force MECE.
5. **Cardinality** — single value, multi-value, continuous measure, ordered history, relation graph, or event collection?
6. **Temporality** — origin-fixed, slow-changing, role-dependent, relationship-specific, event history, dynamic state, or derived?
7. **Canonical vs derived** — Is this a source fact or a projection computed from facts that live elsewhere?
8. **Level** — trait, motive, cognition, strategy, relationship observation, narrative identity, health, context, role, event, or state?
9. **Cross-cultural portability** — universal concept, locally scoped concept, or external code system?
10. **Sensitivity** — health, race/ethnicity, religion, orientation, legal status, disability, or another sensitive attribute?
11. **Non-determinism** — Could this rule turn correlation or a generation constraint into destiny/fact?
12. **Epistemic source** — user-provided, observed, measured, inferred, generated, derived, external reference, or input constraint?
13. **Provenance** — What source/version/population supports empirical priors or mappings?
14. **Interoperability** — What changes for AI-Persona, P003, AI-Ques and PersonaKernel exchange?
15. **Migration** — How do old IDs/fields map, including split/derived cases?
16. **Coverage** — Which valid people/lives become unrepresentable?
17. **Counterexamples** — Give at least two examples that would break a naive classification.

## Review outcomes

- `accepted`
- `accepted_with_mapping`
- `experimental`
- `deprecated`
- `rejected_duplicate`
- `rejected_non_mece`
- `rejected_deterministic`

## Governance rule

Content libraries are open-ended; canonical ontology is governed.

Writers/generators may freely add:
- personas;
- occupation examples/details;
- events/storylets;
- names/dialogue;
- cultural examples;
- generation templates.

They may **not** create a new canonical domain, concept home, relation family, personality layer, life-stage classification or event-pressure classification without ontology review.

## Personality layering

The canonical personality stack is:

1. **Temperament / traits** — relatively stable distributions.
2. **Motives / values / goals** — what matters and is pursued.
3. **Cognition / beliefs / appraisal** — how the world is interpreted.
4. **Emotion regulation / coping** — dispositions plus context-sensitive strategies.
5. **Relational dispositions** — person-level tendencies, distinct from relationship-specific observations.
6. **Narrative identity** — narrative/generative organization; archetypes are not psychometric truth.
7. **Surface expression** — communication and expression patterns.

Mental-health diagnosis, current mood/stress and relationship-specific quality are not personality layers.

## Sensitive dimensions

Sensitive dimensions may be represented when a legitimate product/research purpose requires them, but:
- unknown must remain unknown;
- do not infer sensitive properties by default;
- do not use them as moral/value/competence proxies;
- do not deterministically infer personality, diagnosis or outcome;
- distinguish `input_constraint` from observed/measured evidence;
- preserve source/provenance, temporality and privacy handling.

## Canonical location and release state

The shared ontology is physically hosted in **AI-Persona**.

Compatibility:
- `ontology/human_ontology.v1.json` — current compatibility canonical.

v2.0.0 (canonical, promoted 2026-09-30):
- `ontology/human_ontology.v2.json`
- `ontology/CANONICAL_FIELD_REGISTRY.json`
- `ontology/V1_TO_V2_MIGRATION.json`
- `ontology/V1_FIELD_MIGRATION.json`
- `ontology/persona_kernel.schema.json`
- `ontology/CONSUMER_CONTRACT.md`
- `ontology/RELEASE_GATE.md`
- `ontology/HUMAN_ONTOLOGY_REVIEW.md`

If multiple projects later need independent packaging/versioning, extract the shared ontology into a dedicated package/repository **without changing stable semantic IDs**.
