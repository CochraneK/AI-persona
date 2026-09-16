# Human Ontology Review Policy

Human Ontology is the single canonical ontology for AI-persona, P003 and future BJTU human/persona systems.

## Core rule

**Multiple orthogonal axes; MECE within each axis.**

A concept has one canonical home. Other modules reference that concept by ID rather than redefining it.

Examples:
- birthplace belongs to `place_mobility`;
- cultural exposure belongs to `culture_language`;
- nationality/citizenship belongs to `social_structural_position`;
- OCEAN belongs to `personality_psychology.temperament_traits`;
- coping belongs to `emotion_regulation_coping`;
- diagnosis belongs to `mental_neurodevelopmental_health`;
- an archetype belongs to `narrative_identity`;
- today's stress belongs to `current_state`.

## Why birthplace and culture are separate

A person may:
- be born in one country;
- grow up in another;
- speak several languages;
- belong to more than one cultural community;
- have a citizenship that differs from both birthplace and current residence.

Therefore the ontology must never infer culture from geography.

## Change classes

### PATCH
- wording/description;
- adding an alias;
- correcting a mapping;
- adding provenance;
- adding a non-semantic example.

Does not change canonical meaning.

### MINOR
- adding a new leaf/subaxis;
- adding an enum value that does not alter existing meaning;
- adding an external code-system mapping.

Requires ontology review + compatibility tests.

### MAJOR
- adding/removing a top-level axis;
- moving a concept between axes;
- changing semantic meaning;
- replacing a canonical classification;
- changing an ID.

Requires migration plan and major version bump.

## Required review questions

Every ontology change must answer:

1. **Canonical home** — Which single axis owns this concept?
2. **Orthogonality** — Is it actually distinct from existing axes, or a duplicate description?
3. **MECE** — At this abstraction level, are categories non-overlapping and sufficiently exhaustive?
5. **Cardinality** — single value, multi-select, ordered history, graph/relationship, or continuous measure?
6. **Temporality** — origin-fixed, slow-changing, role-dependent, relationship-specific, event history, dynamic state, or derived?
7. **Level** — trait, motive, cognition, strategy, relationship pattern, narrative identity, surface expression, health, context, role, or state?
8. **Cross-cultural portability** — Is this a universal concept or a region-specific code system?
9. **Sensitivity** — Is this health, race/ethnicity, religion, orientation, legal status or another sensitive attribute?
10. **Non-determinism** — Could the proposed rule accidentally turn correlation into destiny?
11. **Provenance** — What source/version/population supports any empirical prior?
12. **Interoperability** — What happens to AI-persona, P003, AI-Ques admin data and persona-kernel schemas?
13. **Migration** — How are old IDs/fields mapped?
14. **Coverage** — Which valid people/lives cannot be represented after this change?
15. **Counterexamples** — Give at least two people who would break a naive version of the classification.

## Review outcomes

- `accepted`
- `accepted_with_mapping`
- `experimental`
- `deprecated`
- `rejected_duplicate`
- `rejected_non_mece`
- `rejected_deterministic`

## Governance rule

Content libraries are open-ended; the ontology is governed.

Writers/generators may add:
- personas;
- occupations/details;
- events;
- storylets;
- names;
- dialogue;
- cultural examples.

They may **not** invent new top-level domains, life stages, personality layers or pressure shapes without ontology review.

## Personality layering

The canonical personality stack is:

1. **Temperament / traits** — relatively stable distributions.
2. **Motives / values / goals** — what matters and is pursued.
3. **Cognition / beliefs / appraisal** — how the world is interpreted.
4. **Emotion regulation / coping strategies** — learned and situational responses.
5. **Relational patterns** — trust, attachment expression, rejection sensitivity, boundaries.
6. **Narrative identity** — archetype, formative pressure, compensatory strategy, developmental need, arc.
7. **Surface expression** — communication, disclosure, conflict style, manner.

Mental-health diagnosis and current mood/stress are **not** personality layers.

## Sensitive dimensions

Sensitive dimensions may exist because a comprehensive Human Ontology must represent real human diversity. But:
- do not infer them when unknown;
- do not use them as moral/value proxies;
- do not deterministically infer personality/diagnosis/outcomes;
- expose only where product/research purpose justifies it;
- keep source/provenance and privacy classification.

## Canonical location

For now the canonical files are physically hosted in **AI-persona**:
- `ontology/human_ontology.v1.json`
- `ontology/HUMAN_ONTOLOGY_REVIEW.md`

This is a neutral shared ontology despite living in the AI-persona repository. If multiple projects later need independent release/versioning, extract these files into a dedicated shared package/repository without changing IDs.
