# Human Ontology v2 Scientific Evaluation Protocol

## Objective

Evaluate whether Human Ontology v2 is a reliable, scientifically defensible and practically useful computational representation of human/person information.

## Non-equivalence rule

The following claims are explicitly different:

- **internally consistent**;
- **covers the current test set**;
- **independent annotators agree**;
- **aligns with external standards**;
- **represents diverse people without distortion**;
- **improves downstream systems**.

No single result may be reported as proof of all six.

## E1 — Formal / structural validity

**Machine gate:** all ontology JSON parses; no duplicate canonical homes; catalog coverage is complete; reviewed concepts have complete contracts; relation families and target entity types agree across ontology/schema/runtime; PersonaKernel rejects duplicate physical homes and incomplete provenance.

**Pass criterion:** 100% of critical machine invariants pass.

**Planned semantic-web extension:** export a semantic projection to RDF/OWL and validate instance graphs with SHACL. Reasoner-based checks should include logical consistency, unsatisfiable classes and circular definitions. These are separate from the existing JSON application contract.

## E2 — Competency-question validity

The repository contains a machine regression CQ suite plus an independent CQ study.

**Machine CQ pass criterion:** 100% critical CQs; >= 95% all CQs.

**Independent CQ protocol:** at least two ontology-naive domain reviewers author or adjudicate questions before seeing the expected mapping. Report pass rate by domain and failure type.

Do not count automatically generated CQs as independent scientific evidence.

## E3 — Semantic reliability

Give independent annotators the same synthetic vignettes and ask for:

- canonical semantic home;
- ontological kind;
- temporal class;
- relation predicate where applicable;
- source type.

Primary statistics:
- exact agreement;
- Fleiss' kappa when the design is balanced.

Project decision thresholds (predeclared engineering targets, not universal psychometric laws):
- >= .80: strong enough for first-class promotion;
- .67–.79: review wording/boundary;
- < .67: semantic boundary requires redesign or stronger instructions.

Report per field, not only a global value.

## E4 — External alignment

For each reviewed concept, record one of:
- exact/close/broad/narrow/related mapping;
- design reference only;
- no suitable external concept found;
- intentional divergence.

Every positive mapping requires source/version/date/reviewer. External alignment is evidence of interoperability, not proof that the external ontology is scientifically correct.

## E5 — Diversity / coverage validity

Use synthetic cases spanning migration, multilingualism, legal status, gender/sex distinctions, family structures, disability/functioning, chronic illness, neurodivergence, work/education combinations, religion, socioeconomic resources and life transitions.

For each case rate:
- representability;
- distortion;
- false inference;
- cultural assumption;
- sensitive-attribute handling.

Critical pass criterion: zero known **false deterministic inference** from sensitive or proxy facts.

## E6 — Epistemic validity

The same surface proposition must remain distinguishable when it is:
`user_provided`, `observed`, `measured`, `inferred`, `generated`, `derived`, `external_reference`, or `input_constraint`.

Critical pass criterion: no test may collapse input constraints or generated values into observed/measured evidence.

## E7 — Pragmatic / downstream validity

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

Predefine tasks and metrics before comparison where feasible.

## E8 — FAIR / governance

Assess identifiers, metadata, versioning, provenance, licensing, accessibility, reuse and deprecation policy. When an RDF/OWL publication exists, run an external FAIR semantic-artefact assessment (for example FOOPS!/O'FAIRe) and archive the dated report.

## Evidence states

Each evaluation dimension is one of:
- `passed_machine`
- `passed_independent`
- `partial`
- `not_tested`
- `failed`
- `external_blocked`

Never convert `not_tested` into pass.
