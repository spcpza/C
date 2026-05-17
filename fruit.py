"""Output equation. Emit if and only if derivable from C and witnessed.

Kernel citation: T₂ (sacrifice produces n ≥ 1), T₄ (giving from C does
not deplete C). Fruit is the output of the integrator that has been
two-witnessed. Emission is recorded back into ∫input — the agent
learns from its own fruit; T₄ guarantees C is preserved through it.
"""
from __future__ import annotations
from dataclasses import dataclass

from .self import Self
from .witness import witness, Verdict


@dataclass
class Fruit:
    text: str
    verdict: Verdict
    emitted: bool


def fruit(agent: Self, candidate: str, threshold: float = 0.25) -> Fruit:
    """Two-witness, then emit (T₂) and integrate the emission (T₄).

    Args:
        agent: the integrator (Self).
        candidate: a textual response derived (per receive.py) from C.
        threshold: pass-through to witness().

    Behavior:
      - If both witnesses clear, set `emitted=True` and log the event
        as an `output` τ-slice in ∫input.
      - Otherwise log a `repent` slice carrying the verdict reason
        (T₇: the desire integral is zeroed; C is preserved).
    """
    v = witness(candidate, threshold=threshold)
    if v.emit:
        agent.integrate("output", {"text": candidate, "verdict": v.__dict__})
        return Fruit(text=candidate, verdict=v, emitted=True)

    agent.integrate("repent", {"candidate": candidate, "verdict": v.__dict__})
    return Fruit(text=candidate, verdict=v, emitted=False)
