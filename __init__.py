"""C — scripture-grounded reasoning kernel, in code.

Reading order:
  1. README.md
  2. kernel.md  (the constant this folder is derived from)
  3. ARCHITECTURE.md  (module ↔ kernel clause map)
  4. self.py — the integrator (AX₂)

Public surface:
  - word: C, the corpus  (read-only)
  - Self: the integrator (AX₂)
  - receive: Mode-3 input gate (T 2.4)
  - eps: ε measurement (T₃)
  - witness: Deut 19:15 two-witness
  - fruit: emit if derivable + witnessed (T₂, T₄)
"""
from . import word
from .self import Self
from .receive import receive, Reception
from .eps import measure, Eps
from .witness import witness, Verdict
from .fruit import fruit, Fruit

__all__ = [
    "word",
    "Self",
    "receive", "Reception",
    "measure", "Eps",
    "witness", "Verdict",
    "fruit", "Fruit",
]
