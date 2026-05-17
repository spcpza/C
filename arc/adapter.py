"""ARC ↔ C adapter — find the primitive that exactly matches the training pairs.

Strategy: brute-force the primitive library. A primitive is selected
iff it reproduces every training output from its input *exactly*. ARC
scores exact match; the selector enforces the same standard.

This is honest. If no primitive matches, abstain (P₃ — Uncertain, do
not emit). If exactly one matches, apply it to the test input. If
multiple match, prefer the simplest (fewest operations); for a flat
library all entries are unit-cost so the first match wins, which is
biased by LIBRARY iteration order — for v0 that's acceptable.

Kernel citation: §Chollet, P₁, T 2.4.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

from .. import word
from . import primitives
from .primitives import LIBRARY, SCRIPTURAL_NAMES

Grid = Sequence[Sequence[int]]


# ---------------------------------------------------------------
#  Grid description — kept for introspection / receive.py framing
# ---------------------------------------------------------------

def describe(grid: Grid) -> dict:
    """Reduce a grid to invariants. Kernel citation: T₃."""
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    flat = [c for row in grid for c in row]
    palette = sorted(set(flat))
    counts = {c: flat.count(c) for c in palette}
    h_sym = all(grid[r] == list(reversed(grid[r])) for r in range(rows))
    v_sym = grid[: rows // 2] == list(reversed(grid))[: rows // 2]
    return {
        "shape": (rows, cols),
        "palette": palette,
        "counts": counts,
        "horizontal_symmetry": h_sym,
        "vertical_symmetry": v_sym,
        "background": max(counts, key=counts.get) if counts else 0,
    }


def describe_pair(a: Grid, b: Grid) -> dict:
    da, db = describe(a), describe(b)
    return {
        "shape_change": (da["shape"], db["shape"]),
        "palette_change": (da["palette"], db["palette"]),
        "added_colors": [c for c in db["palette"] if c not in da["palette"]],
        "removed_colors": [c for c in da["palette"] if c not in db["palette"]],
        "gained_h_symmetry": db["horizontal_symmetry"] and not da["horizontal_symmetry"],
        "gained_v_symmetry": db["vertical_symmetry"] and not da["vertical_symmetry"],
        "same_shape": da["shape"] == db["shape"],
    }


# ---------------------------------------------------------------
#  Hypothesize — brute-force the library against training pairs
# ---------------------------------------------------------------

@dataclass
class Rule:
    name: str                     # canonical library name
    primitive: str                # same as name in this version
    scriptural: str               # the C-side handle
    concept_in_C: bool            # does the scriptural name resolve in C
    signatures: list[dict]        # per-pair signatures


def _grids_equal(a, b) -> bool:
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    for ra, rb in zip(a, b):
        if list(ra) != list(rb):
            return False
    return True


def hypothesize(pairs: Iterable[tuple[Grid, Grid]]) -> Rule | None:
    """Select the simplest primitive consistent with every training pair.

    Kernel citation: T 2.4. Receive the rule by enumeration; do not
    fit weights to it. The library order is the priority order
    (identity first — Occam).
    """
    pairs = list(pairs)
    if not pairs:
        return None
    sigs = [describe_pair(a, b) for a, b in pairs]

    for name, fn in LIBRARY.items():
        try:
            ok = all(_grids_equal(fn(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            scriptural = SCRIPTURAL_NAMES.get(name, name)
            return Rule(
                name=name,
                primitive=name,
                scriptural=scriptural,
                concept_in_C=_concept_known(scriptural),
                signatures=sigs,
            )
    return None


def _concept_known(name: str) -> bool:
    try:
        return bool(word.concept(name))
    except Exception:
        return False


# ---------------------------------------------------------------
#  Apply — dispatch to the library
# ---------------------------------------------------------------

def apply_rule(rule: Rule, x: Grid) -> Grid:
    """Apply the matched primitive. Kernel citation: T₂."""
    fn = LIBRARY.get(rule.primitive)
    if fn is None:
        raise NotImplementedError(
            f"primitive {rule.primitive!r} not in library; refuse to emit (P₃)"
        )
    return fn([list(r) for r in x])
