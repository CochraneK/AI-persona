# Human Ontology v2 Scientific Evaluation Protocol

## Objective

Evaluate whether Human Ontology v2 is internally coherent, semantically robust across heterogeneous AI systems, interoperable with external standards, and useful in downstream person-centered AI systems.

## Non-equivalence rule

The following are different claims and must remain separate:

- internally consistent;
- passes machine regression tests;
- multiple AI models agree;
- multiple AI models are accurate against adversarial boundary gold;
- humans/experts independently agree;
- aligns with external standards;
- represents diverse people without distortion;
- improves downstream systems.

No single result proves all of them.

## E1 — Formal / structural validity

Machine gates check JSON/schema/runtime consistency, canonical-home uniqueness, complete reviewed concept contracts, graph target constraints, provenance completeness and single-home storage.

Pass criterion: 100% critical machine invariants.

A reproducible RDF/OWL + SHACL projection is maintained separately. Actual reasoner/SHACL execution is additional formal evidence, not a substitute for semantic validation.

## E2 — Machine competency-question validity

The current regression suite contains 184 critical competency questions covering domain presence, domain competency questions, first-class concept homes/kinds/storage, reviewed graph representability, typed relations, epistemic source distinctions and semantic boundaries.

Pass criterion:
- 100% critical CQs;
- >= 95% all CQs.

Automatically generated or ontology-author-maintained CQs are regression evidence, not independent validation.

## E3 — Multi-AI semantic robustness (Tier B1)

Different AI model/provider families receive the same blinded adversarial mapping task.

Each case asks the model to:
- map named atomic facts to one of the 18 semantic namespaces;
- assign ontological kind;
- choose a relation predicate where appropriate;
- identify epistemic source type when inferable;
- distinguish known / unknown / absent / insufficient information;
- judge whether candidate forbidden inferences are actually entailed.

Primary metrics:
- response completeness;
- domain accuracy against hidden adversarial gold;
- pairwise agreement by semantic dimension;
- Fleiss' kappa when balanced;
- forbidden-inference false-positive rate;
- consensus domain accuracy;
- agreement-but-wrong cases.

Predeclared Tier-B1 project targets:
- >= 3 distinct providers/families;
- >= 95% mean response completeness;
- domain pairwise agreement >= .80;
- domain Fleiss' kappa >= .80;
- every model domain accuracy >= .90;
- every model forbidden-inference FP rate <= .05;
- 0 agreement-but-wrong critical items.

High agreement is never sufficient by itself: correlated model error is explicitly tested through gold accuracy and agreement-but-wrong detection.

Exact model IDs, provider, date, prompt hash and case hash must be archived for every evidence-producing run.

## E4 — Human / expert corroboration (Tier B2, optional stronger evidence)

Human annotation is retained as an optional stronger corroboration path rather than a current prerequisite.

If used, report:
- annotator backgrounds;
- independent mapping before adjudication;
- exact agreement and Fleiss' kappa;
- disagreement classification;
- ontology changes caused by human review.

Human and AI evidence must remain separate.

## E5 — External alignment

For each reviewed concept, record one of:
- exact/close/broad/narrow/related mapping;
- design reference only;
- no suitable external concept found;
- intentional divergence.

Every positive mapping requires source/version/date/reviewer or reviewer-agent provenance. External alignment supports interoperability, not truth by authority.

## E6 — Diversity / coverage validity

Use synthetic cases spanning migration, multilingualism, legal status, gender/sex distinctions, family structures, disability/functioning, chronic illness, neurodivergence, work/education combinations, religion, socioeconomic resources and life transitions.

Review:
- representability;
- distortion;
- false inference;
- cultural assumption;
- sensitive-attribute handling.

Critical criterion: zero unresolved false deterministic inference from sensitive/proxy facts.

## E7 — Epistemic validity

The same proposition must remain distinguishable when it is user_provided, observed, measured, inferred, generated, derived, external_reference or input_constraint.

Critical criterion: no input constraint or generated value may collapse into observed/measured evidence.

## E8 — Pragmatic / downstream validity

Evaluate at least P003 and AI-Ques.

Recommended before/after metrics:
- duplicate semantic fields;
- schema conflicts;
- invalid state transitions;
- adapter code required;
- mapping errors;
- successful competency queries;
- time/changes required to add a new person concept;
- provenance loss.

## E9 — FAIR / governance

Assess identifiers, metadata, versioning, provenance, licensing, accessibility, reuse and deprecation policy. After a public semantic artefact exists, archive a dated external FAIR assessment.

## Evidence states

Use:
- `passed_machine`
- `passed_multi_ai`
- `passed_human`
- `passed_application`
- `partial`
- `not_tested`
- `failed`
- `external_blocked`

Never convert `not_tested` into pass.
