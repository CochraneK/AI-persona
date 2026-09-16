# Human Ontology v2 Release Gate

Human Ontology v2 may move from `release_candidate` to `canonical` only when every gate below is satisfied.

## Semantic gates

- [x] Person is the root entity; diagnosis/occupation/nationality/personality are not root identities.
- [x] Domains are semantic namespaces; ontological kind belongs to concepts/fields.
- [x] One canonical semantic home rule is documented and machine checked for the canonical registry.
- [x] MECE is local to sibling classifications, not falsely global.
- [x] v1 overlap register has no unresolved architecture row.
- [x] Self-efficacy is separated from underlying ability and lives under cognition/beliefs.
- [x] Relationship observation is separated from person-level relational disposition.
- [x] Current-state projections are separated from enduring source facts.

## Migration gates

- [x] All 19 v1 coverage axes have rc2 targets.
- [x] Every v1 subaxis/personality layer has a field-level migration entry.
- [x] Legacy flat Persona can be adapted to PersonaKernel.
- [x] Psychiatric ontology is preserved as an optional health domain module.
- [x] Archetype assets are preserved as narrative-generation assets.
- [x] Legacy v1 generator remains available for reproducibility.

## Epistemic/safety gates

- [x] Generated/inferred values require confidence, provenance and temporal class.
- [x] Unknown/absent and generated/observed are explicitly distinct.
- [x] Psychiatric module declares that diagnosis does not determine personality, values, morality, competence or life outcome.
- [x] Default v2 KernelGenerator applies a health-only psychiatric semantic firewall.
- [x] Same-seed cross-diagnosis test verifies non-health personality/abilities/education/work/identity/life-events remain unchanged.

## Engineering gates

- [x] v1 validator retained.
- [x] v2 semantic validator added.
- [x] All ontology JSON assets parse in CI.
- [x] JSON Schema domain/version drift is checked.
- [x] Field registry version/domain/kind/cardinality consistency is checked.
- [x] 100% v1 field migration coverage is machine checked.
- [x] Event-allocation negative-count bug has a regression test.
- [x] Diagnosis-linked event count is capped by requested event count.
- [x] Repository stale rc1/removed-domain tokens are checked by release gate.
- [ ] Latest PR head GitHub Actions is green.
- [ ] Final PR diff/self-review has no unresolved issue.
- [ ] PR body reflects final architecture and compatibility implications.

## Promotion rule

Do not edit `human_ontology.v2.json.status` to `canonical` merely because the design looks complete.

Promotion is a separate commit after:
1. latest-head CI passes;
2. final PR diff review passes;
3. compatibility/safety regressions are green;
4. no unresolved review thread remains.

Until then, v1 is the compatibility canonical and v2 is the release candidate.
