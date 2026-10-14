#!/usr/bin/env python3
"""Regression tests for the optional longitudinal PersonaTrace sidecar."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.persona_kernel import PersonaKernel, FieldMetadata
from core.persona_trace import PersonaTrace, CompetingHypothesis


def rejects(fn, fragment: str) -> None:
    try:
        fn()
    except (ValueError, TypeError) as exc:
        assert fragment in str(exc), str(exc)
    else:
        raise AssertionError("Should have rejected: " + fragment)


def main() -> None:
    a = PersonaKernel(persona_id="synthetic-person-A")
    trace = PersonaTrace(a)
    hypotheses = (
        CompetingHypothesis("H1", "Prefers helping across contexts",
                            ("sim-event-1",), (), "Does helping persist with less time?"),
        CompetingHypothesis("H2", "Helps in a specific role",
                            (), (), "What happens outside the role?"),
    )
    trace.append(step_id="step-1", event_id="sim-event-1",
                 event_time="day-1", recorded_at="run-1",
                 provenance="entirely synthetic fixture",
                 hypotheses=hypotheses, actor_id="synthetic-person-A",
                 other_id="synthetic-person-B", context="collaboration",
                 perspectives={"synthetic-person-A": "I can help.",
                               "synthetic-person-B": "I may decline."},
                 narrative="Help occurred; motive remains uncertain.")
    assert trace.steps[0].change_kind == "no_change"
    assert len(trace.steps[0].hypotheses) == 2
    assert trace.snapshot(0) == trace.snapshot(1)

    # Same interaction may be interpreted differently; no coercive relation.
    trace.append(step_id="step-2", event_id="sim-event-2",
                 event_time="day-2", recorded_at="run-1",
                 provenance="synthetic competing interpretation",
                 change_kind="model_revision",
                 hypotheses=(hypotheses[1],),
                 narrative="New event weakens H1, but no global trait is overwritten.")
    assert trace.snapshot(2) == trace.snapshot(1)

    changed = trace.current_kernel()
    changed.set_value("current_state", "mood", "tired",
                      FieldMetadata("generated", confidence=0.8,
                                    provenance="synthetic day-3 event",
                                    temporal_class="dynamic_state"))
    trace.append(step_id="step-3", event_id="sim-event-3",
                 event_time="day-3", recorded_at="run-1",
                 provenance="synthetic event", after=changed,
                 change_kind="parameter_update",
                 narrative="Current state changed, stable traits remain unassigned.")
    assert trace.current_kernel().get_value("current_state", "mood") == "tired"
    assert "personality_psychology" not in trace.current_kernel().domains
    assert "snapshots" not in trace.to_dict()
    assert len(trace.to_dict(include_snapshots=True)["snapshots"]) == 4

    # Alternate futures stay separate and make no universal predictions.
    branch = trace.fork()
    branch.append(step_id="step-4", event_id="sim-choice-X",
                  event_time="day-4", recorded_at="run-1",
                  provenance="synthetic branch X")
    assert len(trace.steps) == 3
    assert len(branch.steps) == 4

    rejects(lambda: trace.append(step_id="step-3", event_id="x",
                                 event_time="d", recorded_at="r",
                                 provenance="synthetic"), "unique")
    rejects(lambda: trace.append(step_id="wrong-person", event_id="x",
                                 event_time="d", recorded_at="r",
                                 provenance="synthetic", after=PersonaKernel("person-B")),
            "another person")
    rejects(lambda: trace.append(step_id="step-invalid-no-change", event_id="x",
                                 event_time="d", recorded_at="r",
                                 provenance="synthetic", after=PersonaKernel("synthetic-person-A")),
            "cannot change")
    rejects(lambda: trace.append(step_id="step-invalid-update", event_id="x",
                                 event_time="d", recorded_at="r",
                                 provenance="synthetic", change_kind="parameter_update"),
            "requires a changed")
    rejects(lambda: trace.append(step_id="step-invalid-origin", event_id="x",
                                 event_time="d", recorded_at="r",
                                 provenance="", change_kind="no_change"), "provenance")
    assert len(trace.steps) == 3, "Failed validation must not append history"
    print("PersonaTrace longitudinal, ambiguity, no-change and branching: OK")


if __name__ == "__main__":
    main()
