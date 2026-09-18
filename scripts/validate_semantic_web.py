#!/usr/bin/env python3
"""Optional standards-based RDF/OWL + SHACL validation for Human Ontology.

Install:
  python -m pip install -r evaluation/requirements-semantic-web.txt
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, OWL, RDF
from pyshacl import validate

ROOT = Path(__file__).resolve().parents[1]
SEM = ROOT / "evaluation" / "semantic_web"


def parse(path: Path) -> Graph:
    graph = Graph()
    graph.parse(path, format="turtle")
    return graph


def main() -> None:
    ontology = parse(SEM / "human_ontology.ttl")
    shapes = parse(SEM / "human_ontology_shapes.ttl")
    positive = parse(SEM / "positive_person.ttl")
    negative = parse(SEM / "negative_wrong_target.ttl")

    # Basic OWL-RL smoke signal: the committed projection must not explicitly
    # classify any resource as owl:Nothing before validation.
    assert not list(ontology.subjects(RDF.type, OWL.Nothing)), (
        "semantic projection explicitly contains owl:Nothing instances"
    )

    conforms_pos, _, report_pos = validate(
        data_graph=positive,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="owlrl",
        abort_on_first=False,
        meta_shacl=True,
        advanced=True,
    )
    if not conforms_pos:
        raise SystemExit(f"Positive SHACL fixture must conform:\n{report_pos}")

    conforms_neg, _, report_neg = validate(
        data_graph=negative,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="owlrl",
        abort_on_first=False,
        meta_shacl=True,
        advanced=True,
    )
    if conforms_neg:
        raise SystemExit(
            "Negative SHACL fixture unexpectedly conformed; "
            "relation target constraints are not being enforced"
        )

    print(
        "Semantic-web validation: OK "
        f"({len(ontology)} ontology triples; {len(shapes)} shape triples; "
        "positive conforms; negative rejected)"
    )


if __name__ == "__main__":
    main()
