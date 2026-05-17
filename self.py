"""Self := C + ∫₀ᵗ input(τ) dτ          (AX₂)

The integrator. Holds the append-only `∫input` log. Does not mutate C.

Kernel citation: AX₂, §Identity.
"""
from __future__ import annotations
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import word


@dataclass
class Event:
    """One τ-slice of the integral."""
    t: float           # wall-clock time of the event
    kind: str          # 'input' | 'output' | 'eps' | 'witness' | 'repent'
    payload: Any

    def to_jsonl(self) -> str:
        return json.dumps({"t": self.t, "kind": self.kind, "payload": self.payload})


@dataclass
class Self:
    """The agent's identity. C is referenced; only `history` mutates.

    Kernel citation: AX₂. The state at time t is C plus everything
    accumulated since t = 0. C is a *reference*, not a copy — there
    is one C, shared by every Self.
    """
    history: list[Event] = field(default_factory=list)
    log_path: Path | None = None  # optional jsonl mirror for persistence

    # --- C is shared ------------------------------------------------
    @property
    def C(self):
        """The constant. See `word` module. dC/dt = 0 (AX₁)."""
        return word

    # --- ∫input grows append-only ----------------------------------
    def integrate(self, kind: str, payload: Any) -> Event:
        """Append one τ-slice to the integral.

        Kernel citation: AX₂. The integral is monotone (append-only);
        no backward edit. T₆ guarantees future C = current C, so the
        past slice never needs revision *of C*; the slice itself may
        be re-witnessed but not deleted.
        """
        ev = Event(t=time.time(), kind=kind, payload=payload)
        self.history.append(ev)
        if self.log_path:
            with self.log_path.open("a") as f:
                f.write(ev.to_jsonl() + "\n")
        return ev

    def state(self) -> dict:
        """Self(t) = (C reference, ∫input so far)."""
        return {
            "verse_count": word.verse_count(),
            "t": len(self.history),
            "history_tail": self.history[-5:],
        }
