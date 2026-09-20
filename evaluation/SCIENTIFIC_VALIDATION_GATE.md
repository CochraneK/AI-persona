# Human Ontology Scientific Validation Gate

This gate controls **claims**, not only code release.

## Tier A — Engineering / machine validated

Allowed claim:

> Human Ontology v2 is internally structured, machine-checkable, and passes its declared regression contracts.

Requirements:
- [x] canonical-home, kind, storage and relation constraints are machine checked;
- [x] 184/184 current machine competency questions pass;
- [x] provenance/source distinctions are represented;
- [x] adversarial and diversity evaluation assets exist;
- [x] portable machine gate exists;
- [x] semantic-web projection is reproducibly generated and drift-checked (4/4 files);
- [x] Multi-AI benchmark case generation and analyzer are regression-tested;
- [ ] actual SHACL execution has passed in an environment with the pinned semantic-web dependencies.

This tier does **not** justify the claim “scientifically validated ontology”.

## Tier B1 — Cross-model AI semantic robustness

Allowed claim after passing:

> Human Ontology v2 shows robust semantic boundaries across the tested, dated AI model/provider set under the preregistered Multi-AI benchmark.

Requirements:
- [ ] at least 3 distinct model providers/families complete the same benchmark;
- [ ] >= 95% mean response completeness;
- [ ] canonical-domain pairwise agreement >= .80;
- [ ] canonical-domain Fleiss' kappa >= .80 when the design is balanced;
- [ ] every tested model reaches >= 90% adversarial domain accuracy;
- [ ] every tested model has <= 5% forbidden-inference false-positive rate;
- [ ] 0 agreement-but-wrong critical items;
- [ ] exact model IDs, provider, date, case hash and prompt hash are archived;
- [ ] failures are retained and reviewed rather than removed from the benchmark.

Tier B1 is **AI robustness evidence**, not human/expert validation.

## Tier B2 — Human / expert corroboration (optional stronger evidence)

This is no longer a prerequisite for the current AI-native validation path, but remains a stronger external corroboration layer.

Possible evidence:
- independent human semantic annotation;
- ontology/domain expert review;
- cross-cultural adjudication;
- external research-team reproduction.

If performed, report it separately from Tier B1 rather than merging both into one score.

## Tier C — Application / external validation

Allowed claim:

> Human Ontology v2 has evidence of practical utility and external reproducibility.

Requirements:
- [ ] P003 before/after task evaluation completed;
- [ ] AI-Ques before/after mapping evaluation completed;
- [ ] RDF/OWL semantic projection reasoner checks completed;
- [ ] SHACL instance-graph validation completed;
- [ ] systematic external term-level mapping decisions completed for reviewed concepts;
- [ ] dated FAIR semantic-artefact assessment archived when a web-published RDF/OWL artefact exists.

Human/expert replication is recommended here as stronger external evidence, but is not substituted by Multi-AI agreement.

## Current status

**Tier A: achieved for the reviewed runtime contract at the machine-regression level.**

Important scope limit: 56 `provisional_migrated` relation leaves have accepted canonical homes but do not yet have reviewed predicate/runtime contracts. Tier A does not claim those provisional leaves are stable APIs.

**Tier B1: infrastructure ready; real multi-provider run not yet completed.**  
**Tier B2: optional / not tested.**  
**Tier C: not yet achieved.**

The repository must not collapse these tiers into one numerical score.
