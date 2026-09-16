# Human Ontology v1 — Canonical Human/Persona Ontology

This repository now hosts the canonical Human Ontology used by AI-persona and intended for P003 / AI-Ques interoperability.

## Design

The ontology uses **orthogonal dimensions** rather than one giant tree.

> **Orthogonal axes across the system; MECE within each axis.**

This matters because one person can simultaneously have:
- a birthplace;
- a different upbringing place;
- several cultural environments;
- one or more languages;
- citizenship/legal status;
- a gender identity;
- education and occupation;
- family/household roles;
- personality traits;
- motives and values;
- coping strategies;
- relationship-specific patterns;
- health conditions;
- life events;
- current state.

These facts answer different questions and should not compete for one branch.

## Canonical top-level axes

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

The machine-readable definitions live in `human_ontology.v1.json`.

## Important separations

### Birthplace ≠ culture
Birthplace, upbringing place, residence, migration, language, culture, ethnicity and citizenship are separate concepts.

### Diagnosis ≠ identity
Mental and physical health are health layers. They do not define the whole person.

### Trait ≠ motive ≠ coping ≠ relationship ≠ narrative ≠ surface
See the 7-layer personality model in the ontology.

### Context ≠ personality
Poverty, discrimination, housing constraints, policy restrictions or limited education access are structural context/resources, not personality weakness.

### State ≠ trait
Today's stress, mood, energy and financial strain are dynamic state.

## Shared classifications

Human Ontology v1 defines canonical IDs for:
- 10 life domains;
- 9 lifespan stages;
- 13 event pressure/affordance shapes.

AI-persona's existing 6-domain × 4-stage event matrix is retained only as a legacy source and maps into the canonical scheme.

## Governance

Ontology changes must follow `HUMAN_ONTOLOGY_REVIEW.md`.

The ontology is deliberately harder to change than content. New personas and events should be easy; new canonical dimensions should be rare and reviewed.
