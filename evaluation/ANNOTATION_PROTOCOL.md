# Independent Semantic Annotation Protocol

> **Tier B2 optional corroboration.** The primary current semantic-robustness path is the Multi-AI Tier B1 benchmark under `evaluation/multi_ai_benchmark/`. This human protocol is retained as stronger optional external evidence, not as a release prerequisite.

## Goal

Measure whether different people independently map the same human facts to the same ontology semantics.

## Sampling

Use at least:
- 30 adversarial/diversity vignettes in pilot;
- 100+ atomic facts for the first formal study;
- at least 3 annotators where feasible;
- annotators with mixed backgrounds (ontology/data modelling plus human/behavioral/social/health domains).

Do not reveal the expected answer before annotation.

## Task

For each atomic fact, annotate:

1. `canonical_home` — most specific canonical path available, or `NO_SUITABLE_HOME`.
2. `kind` — entity / quality_disposition / role / relation / process_event / state.
3. `temporal_class`.
4. `relation_predicate` if relational, otherwise blank.
5. `source_type` given the evidence wording.
6. `confidence` from 1–5.
7. free-text ambiguity note.

## Adjudication

After independent annotation:
- compute exact agreement and Fleiss' kappa per dimension;
- inspect disagreements before looking at the ontology author's preferred answer;
- classify disagreement as ontology ambiguity, instruction ambiguity, insufficient information, or annotator error;
- ontology ambiguity must create a review item.

## Independence safeguards

- ontology authors should not be the only annotators;
- at least one reviewer should be unfamiliar with the implementation;
- rotate vignette order;
- keep sensitive-attribute cases descriptive and synthetic;
- report exclusions and missing responses.

## Promotion rule

A provisional concept should not become first-class `reviewed` solely because the ontology author can classify it. Independent mapping reliability is preferred for high-impact or ambiguous concepts.
