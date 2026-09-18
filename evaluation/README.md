# Human Ontology Scientific Evaluation

This directory separates **engineering conformance** from **scientific validity evidence**.

A green CI run proves that the current contracts are internally consistent. It does **not** prove that the ontology is scientifically adequate, culturally portable, complete, or useful for downstream systems.

## Evidence layers

1. **Formal / structural validity** — internal consistency, schema/runtime agreement, single-home storage, typed graph constraints.
2. **Competency questions** — can the ontology represent and distinguish the questions it claims to answer?
3. **Semantic reliability** — do independent annotators choose the same canonical home/kind/relation?
4. **External alignment** — are relationships to established ontologies/standards explicit and justified?
5. **Diversity / coverage validity** — can difficult real-world person configurations be represented without distortion?
6. **Epistemic validity** — observed/measured/inferred/generated/derived/input-constraint values remain distinct.
7. **Pragmatic validity** — does using the ontology improve P003, AI-Ques and other consumers?
8. **FAIR / governance** — stable identifiers, versioning, provenance, reuse and change control.

## Current assets

- `competency_questions.json` — 172 machine-checkable structural/regression CQs.
- `adversarial_cases.json` — 24 hand-authored semantic boundary cases.
- `diversity_cases.json` — 30 synthetic diversity stress-test cases.
- `external_alignment_matrix.json` — external-standard evaluation registry and evidence sources.
- `ANNOTATION_PROTOCOL.md` — blinded human semantic-mapping study protocol.
- `annotation_template.csv` — annotation data template.
- `EVALUATION_PROTOCOL.md` — preregistration-style evaluation plan.
- `EVALUATION_REPORT.md` — evidence report; unknown evidence stays unknown.

## Run

```bash
python scripts/evaluate_human_ontology.py
python scripts/analyze_annotation_reliability.py evaluation/annotation_template.csv
```

The machine evaluation is intentionally a **regression baseline**. Scientific claims require independent human review and downstream empirical tests.
