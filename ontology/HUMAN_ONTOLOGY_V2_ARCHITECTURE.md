# Human Ontology v2 — Architecture

Status: **architecture contract for the v2 refactor**. Human Ontology v1 remains the machine-readable compatibility schema until the v2 migration is complete.

## Goal

Represent a human without making diagnosis, occupation, nationality, personality, or any other single domain the root identity.

The v2 model separates six ontological kinds that v1 sometimes mixes:

1. **Entity** — relatively persistent things: person, body, organization, place.
2. **Quality / disposition** — properties borne by an entity: traits, abilities, relatively stable tendencies.
3. **Role** — context-dependent positions: student, employee, caregiver, spouse.
4. **Relation** — links between entities: lives-in, partner-of, works-for, member-of.
5. **Process / event** — things that happen through time: migration, education, illness episode, job loss.
6. **State** — time-indexed conditions: current mood, fatigue, employment state, acute symptoms.

This distinction is inspired by upper-ontology practice (especially BFO) but Human Ontology is an application ontology for computational person representation, not a fork or replacement of BFO.

## MECE contract

Human Ontology does **not** claim that every real-world fact is globally mutually exclusive. Instead it uses three rules:

### 1. Orthogonal semantic homes
Every concept has exactly one canonical definition/home. Other modules reference that concept instead of redefining it.

### 2. MECE where classification semantics permit it
A closed, single-valued classification SHOULD be mutually exclusive and collectively exhaustive at its declared abstraction level. Multi-valued, continuous, fuzzy, temporal, or culturally local concepts MUST NOT be forced into false exclusivity.

### 3. Relations instead of duplication
If the same entity participates in several domains, represent one entity plus typed relations. Example: a partner may simultaneously be a household member and caregiver; do not create three incompatible copies of the person.

Therefore the project-level invariant is:

> **Orthogonal semantic homes + local MECE + typed cross-axis relations.**

## Canonical layers

### A. Person core
Identity-independent anchors and relatively persistent characteristics.

- temporal/developmental identity
- embodiment and functioning
- psychological organization
- abilities and skills

### B. Social and cultural positioning
How the person is situated in human systems.

- culture and language
- sex/gender/orientation
- education
- work/economic position
- social/institutional position

### C. Relations and roles
Represented explicitly rather than embedded as duplicate attributes.

- family/kinship/household relations
- interpersonal/social-network relations
- roles and responsibilities
- organization/institution relations

### D. Life course
Time-indexed processes and events.

- migration
- education/work transitions
- relationship transitions
- health episodes
- major life events

### E. Context and affordances
Properties of the environment and the person's accessible option set.

- place and physical environment
- ecology/macro context
- resources
- constraints
- opportunities

### F. Current state
A timestamped snapshot, explicitly separated from stable traits and history.

## Health architecture

Health is a domain module, not the root of Person.

```text
Person
  ├─ body/functioning/physical-health
  └─ mental/neurodevelopmental-health
       ├─ symptoms & experiences
       ├─ functioning / impairment
       ├─ diagnoses (optional)
       ├─ treatment & support
       ├─ course / recovery
       └─ risk & protective factors
```

The existing psychiatric knowledge assets are **retained** and migrated behind this module. Diagnosis terms may map to external code systems (for example ICD/DSM) while symptoms/functioning remain separate concepts. A persona without a diagnosis must be representable with the same richness as any other persona.

## External ontology strategy

Do not copy an external ontology wholesale into Human Ontology. Use mappings/import manifests with provenance.

Candidate references:

- **BFO** — upper-level distinctions such as continuant/occurrent, role and disposition.
- **OBO / Relation Ontology practices** — interoperable identifiers and typed relations.
- **Mental Functioning Ontology / Emotion Ontology** — mental functioning and affective concepts.
- **HPO** — abnormal human phenotypes where medically appropriate.
- **ICF-like concepts** — functioning/disability framing.
- **ICD / DSM** — diagnosis coding/mapping, not person identity.
- **FHIR Person** — engineering precedent for separating a person from context-specific healthcare roles.
- **Schema.org Person** — pragmatic interoperability for common person metadata.

Every external mapping MUST record source ontology/system, source identifier, version/date when available, mapping relation, and review status.

## Personality architecture

Keep the existing seven-layer model, but type each layer:

| Layer | Ontological treatment |
|---|---|
| temperament & traits | quality/disposition |
| motives, values & goals | disposition / intentional structure |
| cognition & beliefs | informational/psychological state or disposition, explicitly typed |
| emotion regulation & coping | disposition + context-sensitive strategy/process |
| relational patterns | disposition plus relationship-specific observations |
| narrative identity | narrative/generative model; **not psychometric truth** |
| surface expression | observed/generated behavior and communication style |

Archetypes therefore remain useful, but live under narrative identity and generation logic rather than serving as a universal scientific taxonomy of people.

## v1 → v2 migration rule

Do not delete v1 fields merely because their top-level grouping changes. Each v1 field receives one of four dispositions:

- `retain` — same canonical meaning;
- `move` — same concept, new canonical home;
- `relationize` — convert duplicated embedded data into an entity/relation representation;
- `deprecate` — genuinely redundant or scientifically unsupported; preserve a compatibility mapping until a major-version boundary.

No psychiatric dataset or generator asset is deleted as part of ontology restructuring unless it is independently shown to be invalid or redundant.

## Quality gates

A v2 release cannot be marked canonical until automated review checks:

- unique IDs and definitions;
- exactly one canonical home per concept;
- explicit ontological kind for canonical concepts;
- cardinality (`single`, `multi`, continuous, relation, event) where applicable;
- temporal class;
- sensitivity class;
- provenance for external mappings and empirical priors;
- no diagnosis-as-identity dependency;
- no deterministic inference of sensitive attributes;
- v1 compatibility mapping coverage;
- unresolved overlap register is empty or explicitly accepted.

## Consumer contract

AI-Persona owns the canonical Human Ontology and Persona Kernel. Downstream projects consume versioned representations rather than redefine person concepts.

```text
Human Ontology
      ↓
Persona Specification
      ↓
Persona Kernel
      ↓
Persona Generator
      ↓
Concrete Person
      ├─ P003 / simulation & life dynamics
      ├─ AI-Ques / measurement & observation
      ├─ Future Self
      └─ other agents, games and research applications
```

The ontology defines what can be represented. The generator decides how a concrete persona is instantiated. A simulation decides what happens to that person. A measurement product estimates selected properties from observations.