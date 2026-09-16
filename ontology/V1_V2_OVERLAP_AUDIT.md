# Human Ontology v1 → v2 overlap audit

This register prevents a cosmetic rename from being mistaken for MECE.

**rc2 rule:** domains are semantic namespaces; ontological kind belongs to the concept. A duplicated v1 fact is resolved by one canonical home, typed relation, split concept, or explicitly derived projection.

| v1 overlap | rc2 decision | Evidence / canonical treatment | Status |
|---|---|---|---|
| partner/spouse vs romantic relationships | one Person↔Person relation; spouse/partner obligations are roles | `relationships.*`, `roles.*`, field migration | resolved |
| household membership vs housing context | household membership is social relation; dwelling/residence is place relation; environmental properties are context | `relationships.household_membership`, `place_mobility.*`, `context_ecology.*` | resolved |
| income/wealth/material security vs material resources | economic facts remain work/economic facts; current usable resources are time-indexed projections | `work_economic_participation.*` + `resources_constraints_opportunities.*` | resolved_split |
| learning access vs learning opportunities | learning access history and current feasible opportunities are separate | field migration splits into `education_learning.learning_access_history` and `resources_constraints_opportunities.learning_opportunities` | resolved_split |
| occupation/status vs work role | labour participation and role obligations are different kinds | `work_economic_participation.*` + `roles.*` | resolved |
| family relation vs family/caregiving role | kinship/relation and role are represented separately | `relationships.*` + `roles.*` | resolved |
| relationship quality vs relational pattern | dyad-specific observation ≠ person-level disposition | `relationships.relationship_quality` + `personality_psychology.relational_dispositions` | resolved |
| health sleep vs sleep routine | functioning/problem ≠ recurring behavior | `body_functioning_health.sleep_functioning` + `lifestyle_routines.sleep_routine` | resolved |
| self-presentation vs grooming routine | expression ≠ behavior/routine | `personality_psychology.surface_expression.self_presentation` + `lifestyle_routines.appearance_grooming_routine` | resolved |
| household context vs family/household graph | context describes external conditions; membership remains a relationship | `context_ecology.household_context` references relationship/household entities | resolved_reference |
| school/work institutions vs education/work/social structural views | institution is not duplicated; domains hold typed relations/projections | context institution references + education/work/social institutional relations | resolved_reference |
| institutional memberships vs roles/education/work | membership relation is canonical; role/education/work views reference it | `social_institutional_position.institutional_memberships` | resolved_reference |
| life events vs migration/education/work/health histories | event is canonical process/event; domain histories are projections/references | `life_events.*`; migration manifest relationizes histories | resolved_reference |
| current_state vs health/work/resources/personality | current state is a timestamped projection, not second source-of-truth for enduring facts | `current_state.*` with derived action where source facts live elsewhere | resolved_derived |
| self-efficacy vs ability | self-efficacy is a belief about capability, not the capability itself | `personality_psychology.cognition_beliefs.self_efficacy`; removed from ability-domain question | resolved |
| religion/spirituality vs values | participation/affiliation/exposure ≠ personally endorsed value/meaning | `culture_language.religion_spirituality` vs `personality_psychology.motives_values_goals` | resolved |

## Machine-checkable migration

- `V1_TO_V2_MIGRATION.json` maps all 19 v1 coverage axes.
- `V1_FIELD_MIGRATION.json` maps **every v1 subaxis/personality layer** to rc2.
- `CANONICAL_FIELD_REGISTRY.json` owns canonical concept paths and legacy aliases.
- `scripts/validate_human_ontology_v2.py` fails if any v1 field disappears from the field-level migration manifest, if a target domain does not exist, or if canonical/legacy identifiers collide.

## Decision rule

For every future overlap:

1. Same concept? → one canonical definition, references elsewhere.
2. Different ontological kinds? → type them rather than merge them.
3. Same fact at different times? → model temporality.
4. Derived view? → mark derived/projection, never a second source of truth.
5. Legacy field conflates multiple concepts? → split with explicit migration.
6. Unsupported distinction? → deprecate with compatibility mapping.

## rc2 disposition

The original v1 overlap register has no remaining unresolved row at the architecture level. This does **not** mean Human Ontology is permanently closed: new counterexamples can reopen a boundary through `HUMAN_ONTOLOGY_REVIEW.md`. Canonical promotion still depends on CI, migration coverage, semantic-firewall tests, stale-reference checks and final PR review.
