# Human Ontology v1 → v2 overlap audit

This register prevents a cosmetic rename from being mistaken for MECE. Each item must be resolved by definition, relation modeling, or migration before v2 becomes canonical.

| Area A | Area B | Risk | Proposed resolution | Status |
|---|---|---|---|---|
| `family_household.partner_spouse` | `relationships_networks.romantic_relationships` | same relationship/person can be duplicated | represent Person↔Person relation once; family/household and romantic views reference it | open |
| `family_household.household_membership` | `place_mobility.housing_context` | household composition vs dwelling context blurred | household = social relation/group; housing = physical tenure/dwelling context | open |
| `work_economic_position.income/wealth_assets/material_security` | `resources_constraints_opportunities.material_resources` | economic facts copied into resource snapshot | economic axis owns source facts; resources module derives time-indexed accessible resources | open |
| `education_learning.learning_access` | `resources_constraints_opportunities.learning_opportunities` | access/opportunity duplication | education owns participation/history; opportunity module owns current feasible option set | open |
| `work_economic_position` | `roles_responsibilities.work_roles` | occupation/status vs role duplicated | work owns labor-market facts; Role entity references work context and responsibilities | open |
| `family_household` | `roles_responsibilities.family_roles/caregiving_roles` | kinship relation vs role confused | kinship relation and social role are separate typed objects linked to same actors | open |
| `relationships_networks.relationship_quality` | `personality_psychology.relational_patterns` | actual dyadic state vs person tendency confused | relationship quality is relation-specific observation; relational pattern is disposition/summary with evidence | open |
| `body_health.sleep` | `lifestyle_routines.sleep_routine` | health outcome vs behavior duplicated | health owns sleep functioning/problems; lifestyle owns routine/behavior | open |
| `body_health.self_presentation` | `lifestyle_routines.appearance_grooming_routine` | presentation state vs grooming behavior overlap | define self-presentation as observed expression; grooming as process/routine | open |
| `ecology_macro_context.household_context` | `family_household` | same household represented twice | household entity belongs to relational/social model; ecology references contextual properties of household | open |
| `ecology_macro_context.school_work_institutions` | education/work/social-structural axes | institution duplicated | Organization/Institution entities are canonical; domains link via typed relations | open |
| `social_structural_position.institutional_memberships` | roles / education / work | membership duplicated | one membership relation; domain views reference it | open |
| `life_events_history` | migration/education/work/health histories | event copied into domain histories | canonical Event object with domain tags/relations; domain histories become projections | open |
| `current_state` | health/work/resources/personality fields | snapshot vs persistent fact ambiguity | every dynamic value is timestamped; current_state is a projection, not a second canonical home | open |
| `abilities_skills_interests.self_efficacy` | personality cognition/beliefs | construct placement ambiguity | define self-efficacy as domain-specific belief; move to cognition/beliefs or explicitly reference it | open |
| `culture_language.religion_spirituality` | personality values | affiliation/exposure vs personally endorsed values | culture owns affiliation/exposure; personality owns personally endorsed values/meaning | open |

## Decision rule

For every overlap, ask in order:

1. Are these actually the same entity/concept? → keep one canonical definition and reference it.
2. Are they different ontological kinds? → type them (role, relation, state, disposition, event, context).
3. Are they the same fact at different times? → model temporality instead of duplicate fields.
4. Is one a derived view? → mark it derived/projection, never a second source of truth.
5. Is the distinction scientifically or operationally unsupported? → deprecate with compatibility mapping.

The register is complete only when every row is resolved and the automated ontology audit passes.