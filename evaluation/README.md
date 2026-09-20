# Human Ontology Scientific Evaluation

This directory separates **engineering conformance** from **scientific validity evidence**.

A green CI run proves that the current contracts are internally consistent. It does **not** prove that the ontology is scientifically adequate, culturally portable, complete, or useful for downstream systems.

## Evidence layers

1. **Formal / structural validity** — internal consistency, schema/runtime agreement, single-home storage, typed graph constraints.
2. **Competency questions** — can the ontology represent and distinguish the questions it claims to answer?
3. **Semantic reliability** — do heterogeneous AI raters independently choose the same canonical home/kind/relation, and are they accurate against adversarial gold?
4. **External alignment** — are relationships to established ontologies/standards explicit and justified?
5. **Diversity / coverage validity** — can difficult real-world person configurations be represented without distortion?
6. **Epistemic validity** — observed/measured/inferred/generated/derived/input-constraint values remain distinct.
7. **Pragmatic validity** — does using the ontology improve P003, AI-Ques and other consumers?
8. **FAIR / governance** — stable identifiers, versioning, provenance, reuse and change control.

## Current assets

- `competency_questions.json` — 184 machine-checkable structural/regression CQs, including reviewed graph-predicate representability.
- `adversarial_cases.json` — 24 hand-authored semantic boundary cases.
- `diversity_cases.json` — 30 synthetic diversity stress-test cases.
- `external_alignment_matrix.json` — external-standard evaluation registry and evidence sources.
- `multi_ai_benchmark/` — Tier B1 multi-provider AI benchmark, runner, analyzer, prompts and API references.
- `ANNOTATION_PROTOCOL.md` / `annotation_template.csv` — optional Tier B2 human corroboration assets.
- `EVALUATION_PROTOCOL.md` — preregistration-style evaluation plan.
- `EVALUATION_REPORT.md` — evidence report; unknown evidence stays unknown.

## Run

```bash
python scripts/evaluate_human_ontology.py
python scripts/build_multi_ai_benchmark.py --check
python scripts/test_multi_ai_benchmark.py
# real Tier-B1 run requires your provider API keys; see evaluation/multi_ai_benchmark/README.md
```

The machine evaluation is intentionally a **regression baseline**. Current reviewed runtime contract baseline: **184/184 critical CQs pass**. The catalog still contains **56 provisional relation leaves** whose semantic homes are accepted but whose predicate/runtime contracts remain under review. Tier B1 claims require a real run across multiple different AI providers/models; human review remains an optional stronger Tier B2 layer. Downstream empirical tests are still required for Tier C.
