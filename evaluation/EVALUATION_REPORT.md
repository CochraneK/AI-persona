# Human Ontology v2 Evaluation Report

**Ontology:** 2.0.0-rc2  
**Report status:** baseline / incomplete scientific validation  
**Date:** 2026-09-21

## Evidence dashboard

| Dimension | Current evidence | Status |
|---|---|---|
| Formal / structural | JSON/schema/runtime validators and release gate exist | partial |
| Machine competency questions | **184/184 passed** on 2026-09-18 hardened baseline | passed_machine |
| Multi-AI Tier B1 | Runner/analyzer/cases/provider adapters implemented; real multi-provider run not yet executed | not_tested |
| Human/expert Tier B2 | Optional corroboration protocol exists; not run | not_tested |
| External alignment | 10 external sources registered; systematic term-level mappings incomplete | partial |
| Diversity coverage | 30 synthetic stress cases defined; independent adjudication pending | partial |
| Adversarial semantic boundaries | 24 cases defined; independent adjudication pending | partial |
| Epistemic validity | Runtime source/provenance contract exists; dedicated evaluation cases included | partial |
| Pragmatic P003 validation | Not yet run | not_tested |
| Pragmatic AI-Ques validation | Not yet run | not_tested |
| Semantic projection drift | RDF/OWL + SHACL projection regenerates **4/4 identical files** from canonical JSON | passed_machine |
| RDF/OWL reasoner validation | Projection exists; full reasoner validation not yet run | not_tested |
| SHACL validation | Shapes + positive/negative fixtures + pinned validator exist; pySHACL execution not yet run | not_tested |
| FAIR external assessment | Planned after semantic-web publication | not_tested |

## Interpretation

The current evidence supports the claim that **the architecture is internally structured, testable, and currently passes its 184 declared machine regression CQs**. It does **not yet support** a strong claim that the ontology is empirically validated, cross-culturally adequate, or independently reproducible.

The next evidence-producing milestone is a dated Multi-AI Tier-B1 run using at least three distinct provider/model families, followed by downstream P003 and AI-Ques validation.

## Reporting rule

Do not publish a single global “ontology score” as the primary conclusion. Report the evidence profile and unresolved failures by dimension.


## Scientific validation tier

Current claim tier: **Tier A — Engineering / machine validated**.

Tier B1 requires cross-model agreement plus adversarial gold accuracy, low forbidden-inference false positives, and zero agreement-but-wrong critical items. Tier B2 human/expert review is optional stronger corroboration. Tier C additionally requires downstream P003/AI-Ques validation, semantic-web reasoning/SHACL validation and FAIR assessment.

See `SCIENTIFIC_VALIDATION_GATE.md`.


## Known machine-visible gap

The exhaustive catalog contains **56 provisional relation leaves** whose canonical semantic homes are accepted but whose graph predicate/runtime contracts are still marked for review. They are not counted as stable cross-project APIs and do not invalidate the reviewed 31-concept runtime contract; they are explicit Tier-B/Tier-C maturation work rather than hidden “passes”.
