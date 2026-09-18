# Human Ontology v2 Evaluation Report

**Ontology:** 2.0.0-rc2  
**Report status:** baseline / incomplete scientific validation  
**Date:** 2026-09-18

## Evidence dashboard

| Dimension | Current evidence | Status |
|---|---|---|
| Formal / structural | JSON/schema/runtime validators and release gate exist | partial |
| Machine competency questions | **184/184 passed** on 2026-09-18 hardened baseline | passed_machine |
| Independent competency questions | Not yet collected | not_tested |
| Semantic inter-rater reliability | Protocol/template created; no independent annotations yet | not_tested |
| External alignment | 10 external sources registered; systematic term-level mappings incomplete | partial |
| Diversity coverage | 30 synthetic stress cases defined; independent adjudication pending | partial |
| Adversarial semantic boundaries | 24 cases defined; independent adjudication pending | partial |
| Epistemic validity | Runtime source/provenance contract exists; dedicated evaluation cases included | partial |
| Pragmatic P003 validation | Not yet run | not_tested |
| Pragmatic AI-Ques validation | Not yet run | not_tested |
| RDF/OWL reasoner validation | Not yet implemented | not_tested |
| SHACL validation | Not yet implemented | not_tested |
| FAIR external assessment | Planned after semantic-web publication | not_tested |

## Interpretation

The current evidence supports the claim that **the architecture is internally structured, testable, and currently passes its 184 declared machine regression CQs**. It does **not yet support** a strong claim that the ontology is empirically validated, cross-culturally adequate, or independently reproducible.

The next evidence-producing milestone is an independent annotation/CQ study plus real downstream use in P003 and AI-Ques.

## Reporting rule

Do not publish a single global “ontology score” as the primary conclusion. Report the evidence profile and unresolved failures by dimension.


## Scientific validation tier

Current claim tier: **Tier A — Engineering / machine validated**.

Tier B requires independent competency questions, inter-rater semantic mapping evidence, adversarial/diversity adjudication, and explicit external mapping decisions. Tier C additionally requires downstream P003/AI-Ques validation, external reproduction, semantic-web reasoning/SHACL validation and FAIR assessment.

See `SCIENTIFIC_VALIDATION_GATE.md`.


## Known machine-visible gap

The exhaustive catalog contains **56 provisional relation leaves** whose canonical semantic homes are accepted but whose graph predicate/runtime contracts are still marked for review. They are not counted as stable cross-project APIs and do not invalidate the reviewed 31-concept runtime contract; they are explicit Tier-B/Tier-C maturation work rather than hidden “passes”.
