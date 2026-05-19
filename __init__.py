"""C — scripture-grounded reasoning kernel, in code.

Reading order:
  1. AGENTS.md / IN_THE_BEGINNING.md  (single-file entrance)
  2. README.md
  3. kernel.md  (the constant this folder is derived from)
  4. ARCHITECTURE.md  (module ↔ kernel clause map)
  5. CROSS_TRADITIONS.md  (non-Christian agent mapping)
  6. self.py — the integrator (AX₂)

Public surface:
  - word: C, the corpus  (read-only)
  - Self: the integrator (AX₂)
  - receive: Mode-3 input gate (T 2.4)
  - eps: ε measurement (T₃)
  - witness: Deut 19:15 two-witness
  - fruit: emit if derivable + witnessed (T₂, T₄)
  - convergence: derive_from_kernel / verify_witness / cite (T_word, T_bridge)
"""
from . import word, gospel, convergence
from .self import Self
from .receive import receive, Reception
from .eps import measure, Eps
from .witness import witness, Verdict
from .fruit import fruit, Fruit

__all__ = [
    "word", "gospel", "convergence",
    "Self",
    "receive", "Reception",
    "measure", "Eps",
    "witness", "Verdict",
    "fruit", "Fruit",
]
