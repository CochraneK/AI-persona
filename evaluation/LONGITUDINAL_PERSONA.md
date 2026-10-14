# Dynamic Persona Modeling — Evidence, Ambiguity, Time and Agency

> Experimental, synthetic-persona research module (2026-10-14).  
> **Not** a clinical tool, a validated psychological change theory, or a way to infer real people's motives.  
> The existing Human Ontology v2 and PersonaKernel schema remain canonical and unchanged.

## Why this exists

An internally valid ontology and a static, richly described persona are useful, but neither alone demonstrates that a person-like agent can change over time while retaining agency. A single action should not mechanically reveal a stable trait. A relationship-specific behavior should not silently become a global disposition. Two participants may experience the same interaction differently.

The optional `core/persona_trace.py` sidecar adds an explicit record of **what happened, alternative readings, what changed (if anything), and how an alternate future branches**. It is a trace bookkeeping and validation mechanism, **not** an autonomous psychology or event-transition engine.

## Boundaries

- **Structured framework, flexible individual content.** Trace events have identifiers, source metadata, before/after hashes and change types, but `narrative`, `context`, `perspectives` and competing explanations remain open text. There is no universal “wound/desire/need” requirement.
- **Variation is not a schema defect.** Different synthetic personas may have different levels of detail, salient domains, ways of speaking, values, or unfolding narratives. “Unknown” and “no change” are valid.
- **Partial overlap is legitimate.** Stable disposition, relationship context, current state, cultural circumstance and lived event may overlap causally without collapsing into one canonical field. Assign each stored fact one semantic home and reference others.
- **Do not infer inner motives from one episode.** `CompetingHypothesis` may preserve multiple readings and a question that could discriminate them. It does not choose truth or update trait scores automatically.
- **Agency and dyads.** Perspectives are keyed by actor. One actor's interpretation is not another's consent, commitment or preference; two-person interactions must not auto-produce romantic attachment.
- **Counterfactual safety.** Branches and generated observations remain synthetic possibilities, never empirical population probabilities or facts about a real person.
- **Provenance.** The caller must supply event IDs, event/record times, provenance and source type. This API validates presence and the v2 kernel; it cannot verify honesty of the caller.
- **No diagnosis determinism.** Optional psychiatric information does not force goals, ethics, education, romance, competence or a life outcome. The legacy generator's diagnosis-conditioned content remains legacy only.

## API (standard library, deterministic bookkeeping)

```python
from core import PersonaKernel, PersonaTrace, CompetingHypothesis, FieldMetadata

initial = PersonaKernel(persona_id="fiction-001")
trace = PersonaTrace(initial)

trace.append(
    step_id="s1",
    event_id="ordinary-conversation",
    event_time="fictional-day-1",
    recorded_at="simulation-run-1",
    provenance="synthetic script",
    source_type="generated",
    hypotheses=[
        CompetingHypothesis("H1", "The character enjoys this particular task"),
        CompetingHypothesis("H2", "The character values the partner's company"),
    ],
    actor_id="fiction-001",
    other_id="fiction-002",
    context="ordinary collaboration",
    perspectives={
        "fiction-001": "I was curious.",
        "fiction-002": "I enjoyed our talk, but did not make a promise.",
    },
    narrative="No long-term personality conclusion is warranted.",
)
assert trace.steps[-1].change_kind == "no_change"

later = trace.current_kernel()
later.set_value(
    "current_state", "mood", "rested",
    FieldMetadata("generated", confidence=0.7,
                  provenance="fictional episode", temporal_class="dynamic_state"),
)
trace.append(
    step_id="s2", event_id="good-sleep", event_time="fictional-day-2",
    recorded_at="simulation-run-1", provenance="synthetic script",
    source_type="generated", change_kind="parameter_update",
    after=later, narrative="Current state changes; no forced trait update.",
)

alternate_future = trace.fork()
print(trace.to_dict())                  # metadata and hashes; no full snapshots
print(trace.to_dict(include_snapshots=True))  # explicit full-kernel export
```

### Change kinds

| Value | Meaning | Kernel changes allowed? |
|---|---|---|
| `no_change` | Event recorded; insufficient or irrelevant information for updating current representation | No |
| `parameter_update` | Explicit value/state adjustment, already validated against existing PersonaKernel v2 | Required |
| `model_revision` | Explanation or working model changes, with or without an underlying representation change | Optional |
| `ontology_proposal` | Proposed schema inadequacy; does not silently mutate canonical Human Ontology v2 | No |

`PersonaTrace` does **not** pick which update is appropriate; the simulation or reviewer must supply that choice. Even a formally valid trace is not empirical evidence of realistic human change.

## Recommended evaluation

The runnable synthetic regression is `python scripts/test_persona_trace.py`, also added to `scripts/run_ontology_ci.py`.

Current regression scope:
- existing v2 PersonaKernel contracts preserved;
- new state recorded without changing person identity;
- competing explanations survive without arbitrary forced selection;
- no-change and revision-without-trait-change survive;
- dyad perspectives stay separate;
- independent branches do not rewrite previous history;
- export defaults to omitting full persona snapshots.

Recommended *future* adversarial studies (not implemented by these regressions):
- narrator accuracy vs true simulator state; misinformation about another person's feelings;
- contradictory evidence over multiple simulated months;
- ordinary, low-drama trajectories vs implausibly perpetual crisis;
- multiple valid paths after the same event;
- cultural and demographic fairness, non-determinism;
- human-expert review of whether dynamics are plausible;
- downstream gains vs static generator and non-trace baselines.

### Scientific claim limit

Passing a regression **only** supports contract behavior. It does not establish causal realism, psychometric validity, naturalistic relationship quality, or cross-cultural generalizability.

## Relationship to upstream semantics

- Human Ontology v2 remains the authority for `domains`, canonical paths and typed relations.
- PersonaTrace is an **optional temporal sidecar** and does not alter `ontology/persona_kernel.schema.json`.
- Consumers can ignore this feature without migration.
- Each generated character can have an individual organization and narrative: the common contract organizes evidence, **not the essence of a person**.
