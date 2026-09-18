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
- [ ] actual SHACL execution has passed in an environment with the pinned semantic-web dependencies.

This tier does **not** justify the claim “scientifically validated ontology”.

## Tier B — Scientifically supported

Allowed claim:

> Human Ontology v2 has independent semantic-reliability and coverage evidence in addition to machine validation.

Requirements:
- [ ] independent competency-question set authored/adjudicated by reviewers not limited to ontology authors;
- [ ] >= 3 independent annotators where feasible;
- [ ] semantic mapping reliability reported by dimension;
- [ ] critical boundary concepts meet preregistered agreement target or are revised;
- [ ] adversarial cases independently adjudicated;
- [ ] diversity stress cases independently adjudicated;
- [ ] zero unresolved critical deterministic inference from sensitive/proxy facts;
- [ ] reviewed first-class concepts have explicit external mapping decisions.

## Tier C — Application / external validation

Allowed claim:

> Human Ontology v2 has evidence of practical utility and external reproducibility.

Requirements:
- [ ] P003 before/after task evaluation completed;
- [ ] AI-Ques before/after mapping evaluation completed;
- [ ] at least one external reviewer/team reproduces a subset of the semantic-mapping study;
- [ ] RDF/OWL semantic projection reasoner checks completed;
- [ ] SHACL instance-graph validation completed;
- [ ] dated FAIR semantic-artefact assessment archived when a web-published RDF/OWL artefact exists.

## Current status

**Tier A: achieved for the reviewed runtime contract at the machine-regression level.**

Important scope limit: 56 `provisional_migrated` relation leaves have accepted canonical homes but do not yet have reviewed predicate/runtime contracts. Tier A does not claim those provisional leaves are stable APIs.  
**Tier B: not yet achieved.**  
**Tier C: not yet achieved.**

The repository must not collapse these tiers into one numerical score.
