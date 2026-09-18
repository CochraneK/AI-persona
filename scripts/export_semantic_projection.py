#!/usr/bin/env python3
"""Generate/check the RDF/OWL + SHACL semantic-web projection.

The JSON Human Ontology and CANONICAL_FIELD_REGISTRY remain the v2 RC source of
truth. This script deterministically projects their reviewed graph semantics into
Turtle for standards-based validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "ontology" / "human_ontology.v2.json"
REGISTRY = ROOT / "ontology" / "CANONICAL_FIELD_REGISTRY.json"
SEM = ROOT / "evaluation" / "semantic_web"


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def cls(entity_type: str) -> str:
    return "ho:" + "".join(part[:1].upper() + part[1:] for part in entity_type.split("_"))


def lit(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{text}"'


def build_ontology_ttl(ontology: dict, registry: dict) -> str:
    out = [
        "@prefix ho: <https://w3id.org/human-ontology/> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "ho:HumanOntology a owl:Ontology ;",
        f"  owl:versionInfo {lit(ontology['version'])} ;",
        "  rdfs:comment " + lit(
            "Semantic-web projection of the Human Ontology application contract. "
            "The JSON ontology/PersonaKernel remain the executable source of truth during v2 RC."
        ) + " .",
        "",
        "ho:canonicalPath a owl:AnnotationProperty .",
        "ho:ontologicalKind a owl:AnnotationProperty .",
        "ho:storageMode a owl:AnnotationProperty .",
        "ho:temporalClass a owl:AnnotationProperty .",
        "ho:reviewStatus a owl:AnnotationProperty .",
        "ho:relationPredicate a owl:AnnotationProperty .",
        "",
        "ho:SemanticNamespaceScheme a skos:ConceptScheme ;",
        '  skos:prefLabel "Human Ontology semantic namespaces" .',
        "",
        "ho:CanonicalConceptScheme a skos:ConceptScheme ;",
        '  skos:prefLabel "Human Ontology reviewed canonical concepts" .',
        "",
    ]

    for entity in ontology["entity_types"]:
        out.extend([
            f"{cls(entity['id'])} a owl:Class ;",
            f"  rdfs:label {lit(entity['id'])} ;",
            f"  rdfs:comment {lit(entity['definition'])} .",
            "",
        ])

    for domain in ontology["canonical_domains"]:
        out.extend([
            f"ho:domain_{domain['id']} a skos:Concept ;",
            "  skos:inScheme ho:SemanticNamespaceScheme ;",
            f"  skos:notation {lit(domain['id'])} ;",
            f"  skos:prefLabel {lit(domain['id'])} ;",
            f"  skos:definition {lit(domain['question'])} .",
            "",
        ])

    for predicate in ontology["relation_families"]:
        object_types = ontology["relation_constraints"][predicate]["object_entity_types"]
        out.extend([
            f"ho:{predicate} a owl:ObjectProperty ;",
            f"  rdfs:label {lit(predicate)} ;",
            "  rdfs:domain ho:Person ;",
        ])
        if len(object_types) == 1:
            out.append(f"  rdfs:range {cls(object_types[0])} .")
        else:
            union = " ".join(cls(item) for item in object_types)
            out.append(
                f"  rdfs:range [ a owl:Class ; owl:unionOf ( {union} ) ] ."
            )
        out.append("")

    for field in registry["fields"]:
        lines = [
            f"ho:concept_{field['concept']} a skos:Concept ;",
            "  skos:inScheme ho:CanonicalConceptScheme ;",
            f"  skos:prefLabel {lit(field['concept'])} ;",
            f"  skos:notation {lit(field['canonical_path'])} ;",
            f"  skos:definition {lit(field['definition'])} ;",
            f"  ho:canonicalPath {lit(field['canonical_path'])} ;",
            f"  ho:ontologicalKind {lit(field['kind'])} ;",
            f"  ho:storageMode {lit(field['storage'])} ;",
            f"  ho:temporalClass {lit(field['temporal_class'])} ;",
        ]
        if field.get("relation_predicate"):
            lines.extend([
                f"  ho:reviewStatus {lit(field['review_status'])} ;",
                f"  ho:relationPredicate ho:{field['relation_predicate']} .",
            ])
        else:
            lines.append(f"  ho:reviewStatus {lit(field['review_status'])} .")
        out.extend(lines + [""])

    return "\n".join(out)


def build_shapes_ttl(ontology: dict) -> str:
    out = [
        "@prefix ho: <https://w3id.org/human-ontology/> .",
        "@prefix sh: <http://www.w3.org/ns/shacl#> .",
        "",
        "ho:PersonShape a sh:NodeShape ;",
        "  sh:targetClass ho:Person",
    ]
    relations = ontology["relation_families"]
    for index, predicate in enumerate(relations):
        object_types = ontology["relation_constraints"][predicate]["object_entity_types"]
        out.extend([
            "  ;" if index > 0 else "  ;",
            "  sh:property [",
            f"    sh:path ho:{predicate} ;",
        ])
        if len(object_types) == 1:
            out.append(f"    sh:class {cls(object_types[0])}")
        else:
            options = " ".join(f"[ sh:class {cls(item)} ]" for item in object_types)
            out.append(f"    sh:or ( {options} )")
        out.append("  ]")
    out[-1] = out[-1] + " ."
    return "\n".join(out) + "\n"


def build_positive_fixture() -> str:
    return """@prefix ho: <https://w3id.org/human-ontology/> .
@prefix ex: <https://example.org/human-ontology-test/> .

ex:person-1 a ho:Person ;
  ho:has_role ex:role-professor ;
  ho:uses_language ex:language-en ;
  ho:resides_in ex:place-manchester ;
  ho:situated_in_context ex:org-university .

ex:role-professor a ho:Role .
ex:language-en a ho:Language .
ex:place-manchester a ho:Place .
ex:org-university a ho:Organization .
"""


def build_negative_fixture() -> str:
    return """@prefix ho: <https://w3id.org/human-ontology/> .
@prefix ex: <https://example.org/human-ontology-test/> .

ex:person-bad a ho:Person ;
  ho:uses_language ex:not-a-language ;
  ho:has_role ex:not-a-role .

ex:not-a-language a ho:Place .
ex:not-a-role a ho:Organization .
"""


def outputs() -> dict[Path, str]:
    ontology = load(ONTOLOGY)
    registry = load(REGISTRY)
    return {
        SEM / "human_ontology.ttl": build_ontology_ttl(ontology, registry),
        SEM / "human_ontology_shapes.ttl": build_shapes_ttl(ontology),
        SEM / "positive_person.ttl": build_positive_fixture(),
        SEM / "negative_wrong_target.ttl": build_negative_fixture(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed semantic-web projection differs from generated output.",
    )
    args = parser.parse_args()

    generated = outputs()
    if args.check:
        stale = []
        for path, expected in generated.items():
            actual = path.read_text(encoding="utf-8") if path.exists() else None
            if actual != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise SystemExit(
                "Semantic-web projection is stale; regenerate: " + ", ".join(stale)
            )
        print(f"Semantic-web projection drift check: OK ({len(generated)} files)")
        return

    SEM.mkdir(parents=True, exist_ok=True)
    for path, content in generated.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
