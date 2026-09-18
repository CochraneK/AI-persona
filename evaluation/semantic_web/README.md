# Semantic-web validation projection

This directory is a **standards-based validation projection**, not a replacement for the JSON Human Ontology / PersonaKernel application contract.

Files:
- `human_ontology.ttl` — OWL/SKOS projection of entity types, relation families, namespaces and reviewed concepts.
- `human_ontology_shapes.ttl` — SHACL target-type constraints for Person relations.
- `positive_person.ttl` — fixture that must conform.
- `negative_wrong_target.ttl` — fixture that must fail because relation targets use the wrong entity classes.

Run:

```bash
python -m pip install -r evaluation/requirements-semantic-web.txt
python scripts/validate_semantic_web.py
```

Pinned evaluation dependencies (checked 2026-09-18):
- RDFLib 7.6.0
- pySHACL 0.40.1

Passing this test supports standards-based **graph constraint validity**. It is not equivalent to a full OWL-DL scientific ontology review or proof of empirical validity.
