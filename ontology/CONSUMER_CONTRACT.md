# Human Ontology v2 Consumer Contract

Human Ontology is the semantic authority. Applications consume it; applications do not redefine what a person is.

## Roles

| Consumer | Responsibility | Must not do |
|---|---|---|
| AI-Persona | instantiate/generate a Persona Kernel | make diagnosis the root identity; invent competing canonical fields |
| AI-Ques | observe/measure a real person and map evidence into canonical paths | turn an inference into an observed fact; store questionnaire names as ontology roots |
| P003 | simulate choices, relationships, events, consequences and state transitions | redefine person semantics inside the simulation engine |
| Future Self / Avatar | render or transform a person representation | overwrite source/provenance or confuse generated futures with observations |
| Research agents / games | use a bounded projection of the Kernel | silently add incompatible person schemas |

## Envelope

Every consumer-facing record must identify:
- `ontology_version`;
- a stable `persona_id` / subject identifier;
- canonical domain payloads;
- field-level provenance/temporality metadata for **every stored domain value**;
- typed relations and events when applicable. Relation/event records carry stable IDs and a `canonical_path` back to their semantic namespace;
- relations with typed `subject` / `object` `EntityRef` endpoints; predicate-specific target types must be respected.

## Epistemic contract

`user_provided`, `observed`, `measured`, `inferred`, `generated`, `derived`, `external_reference`, and `input_constraint` are not interchangeable.

Unknown is not false. Missing is not absent. Generated is not measured. An `input_constraint` is a condition requested by a generator/simulation caller; it is **not evidence that the represented person was observed to have that property**.

Every stored domain value requires provenance and temporal class. Inferred/generated values additionally require confidence. Input constraints require provenance and temporal class; do not assign an epistemic confidence score merely because the caller requested the condition. Collections with mixed origins should carry item-level provenance. Sensitive inferences require a purpose-specific policy in the consuming application.

## Update contract

Consumers may update values in their canonical homes. They may not create a second semantic home for convenience. A UI may project the same value in several screens, but all views must reference one canonical path. When a fact is represented as a top-level `relations` or `events` record, the same fact must **not** also be copied into the domain payload; the graph record carries its `canonical_path`, and domain views may hold only references/projections.

## Cross-repository interoperability

P003 and AI-Ques should depend on Human Ontology versioned contracts rather than copy the JSON and edit it independently. If a consumer needs a new concept:
1. search the first-class registry and exhaustive concept catalog;
2. prefer a relation/reference to an existing concept;
3. propose a canonical change only if no existing home is semantically correct;
4. run ontology review before promotion.

## Compatibility

During migration, legacy AI-Persona fields are supported by `core/legacy_adapter.py`. Compatibility aliases are transitional and must not become new canonical semantics.
