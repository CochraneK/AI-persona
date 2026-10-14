"""Versioned, non-deterministic longitudinal trace for PersonaKernel v2.

An OPTIONAL sidecar, not another human ontology or a personality theory.
No real-world observations are synthesized by this module. The caller supplies
events, candidate explanations and explicitly chosen kernel state changes.

A trace may preserve contradictions, interpret one interaction in multiple
ways, and record a no-change result. Current Kernel schema is unchanged.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from json import dumps
from typing import Mapping, Sequence

from .persona_kernel import PersonaKernel, SOURCE_TYPES


CHANGE_KINDS = frozenset({
    "no_change", "parameter_update", "model_revision", "ontology_proposal"
})


def _snapshot(kernel: PersonaKernel) -> dict:
    if not isinstance(kernel, PersonaKernel):
        raise TypeError("A valid PersonaKernel is required")
    # to_dict() validates v2 provenance and typed-graph contracts.
    return deepcopy(kernel.to_dict())


def _digest(snapshot: dict) -> str:
    payload = dumps(snapshot, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CompetingHypothesis:
    """Candidate explanation, NOT a statement of the person's true motive."""

    hypothesis_id: str
    explanation: str
    support_refs: tuple[str, ...] = ()
    counterevidence_refs: tuple[str, ...] = ()
    discriminating_question: str = ""

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not self.explanation:
            raise ValueError("Hypothesis requires an id and an explanation")


@dataclass(frozen=True)
class TraceStep:
    step_id: str
    event_id: str
    event_time: str
    recorded_at: str
    source_type: str
    provenance: str
    change_kind: str
    before_hash: str
    after_hash: str
    context: str = ""
    actor_id: str = ""
    other_id: str = ""
    perspectives: dict[str, str] = field(default_factory=dict)
    hypotheses: tuple[CompetingHypothesis, ...] = ()
    narrative: str = ""


class PersonaTrace:
    """Append-only history with optional narrative and immutable state snapshots.

    The framework is structured; character content and narration are *not*
    forced into a fixed set of traits, motivations, or stages.
    """

    def __init__(self, initial: PersonaKernel) -> None:
        first = _snapshot(initial)
        self.persona_id = initial.persona_id
        self._snapshots = [first]
        self._steps: list[TraceStep] = []
        self._step_ids: set[str] = set()

    @property
    def steps(self) -> tuple[TraceStep, ...]:
        return tuple(self._steps)

    def current_kernel(self) -> PersonaKernel:
        return PersonaKernel.from_dict(deepcopy(self._snapshots[-1]))

    def snapshot(self, index: int = -1) -> dict:
        """Get a defensive copy: 0=initial, 1=after first step, ..."""
        return deepcopy(self._snapshots[index])

    def append(
        self,
        *,
        step_id: str,
        event_id: str,
        event_time: str,
        recorded_at: str,
        provenance: str,
        change_kind: str = "no_change",
        source_type: str = "generated",
        after: PersonaKernel | None = None,
        hypotheses: Sequence[CompetingHypothesis] = (),
        actor_id: str = "",
        other_id: str = "",
        context: str = "",
        perspectives: Mapping[str, str] | None = None,
        narrative: str = "",
    ) -> TraceStep:
        """Append one explicitly authored episode; never auto-infer traits.

        For parameter_update a changed, validated Kernel must be provided.
        model_revision may change just the interpretation (no Kernel change).
        ontology_proposal does not mutate the versioned v2 Kernel.
        no_change means identical states; it is a meaningful outcome.
        """
        if not step_id or step_id in self._step_ids:
            raise ValueError("step_id must be nonempty and unique")
        if not event_id or not event_time or not recorded_at or not provenance:
            raise ValueError("event_id, event_time, recorded_at and provenance are required")
        if source_type not in SOURCE_TYPES:
            raise ValueError(f"invalid source_type: {source_type}")
        if change_kind not in CHANGE_KINDS:
            raise ValueError(f"invalid change_kind: {change_kind}")

        before = self._snapshots[-1]
        new_state = _snapshot(after) if after is not None else deepcopy(before)
        if new_state["persona_id"] != self.persona_id:
            raise ValueError("trace cannot replace a person with another person")
        old_hash, new_hash = _digest(before), _digest(new_state)
        if change_kind in {"no_change", "ontology_proposal"} and old_hash != new_hash:
            raise ValueError(f"{change_kind} cannot change the Kernel")
        if change_kind == "parameter_update" and old_hash == new_hash:
            raise ValueError("parameter_update requires a changed Kernel")
        if change_kind == "model_revision" and not (hypotheses or narrative):
            raise ValueError("model_revision requires hypotheses or a narrative explanation")

        hypotheses = tuple(hypotheses)
        if any(not isinstance(h, CompetingHypothesis) for h in hypotheses):
            raise TypeError("hypotheses must contain CompetingHypothesis values")
        ids = [h.hypothesis_id for h in hypotheses]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate hypothesis_id in a trace step")
        views = dict(perspectives or {})
        if any(not k or not isinstance(v, str) for k, v in views.items()):
            raise ValueError("perspectives must map nonempty actor IDs to text")

        step = TraceStep(
            step_id=step_id, event_id=event_id,
            event_time=event_time, recorded_at=recorded_at,
            source_type=source_type, provenance=provenance,
            change_kind=change_kind, before_hash=old_hash, after_hash=new_hash,
            actor_id=actor_id, other_id=other_id, context=context,
            perspectives=deepcopy(views), hypotheses=hypotheses,
            narrative=narrative,
        )
        self._steps.append(step)
        self._snapshots.append(deepcopy(new_state))
        self._step_ids.add(step_id)
        return step

    def fork(self) -> "PersonaTrace":
        """Independent alternate future; never overwrites original history."""
        branch = PersonaTrace(PersonaKernel.from_dict(deepcopy(self._snapshots[0])))
        branch._snapshots = deepcopy(self._snapshots)
        branch._steps = deepcopy(self._steps)
        branch._step_ids = set(self._step_ids)
        return branch

    def to_dict(self, *, include_snapshots: bool = False) -> dict:
        """Minimal export by default: omit full person data unless requested.

        This is a trace export, NOT PersonaKernel schema-compatible JSON.
        Sensitive-data policy/consent is the caller's responsibility.
        """
        payload = {
            "format": "persona-trace-v1",
            "persona_id": self.persona_id,
            "kernel_version": self._snapshots[0]["ontology_version"],
            "initial_hash": _digest(self._snapshots[0]),
            "steps": [asdict(step) for step in self._steps],
        }
        if include_snapshots:
            payload["snapshots"] = deepcopy(self._snapshots)
        return payload
