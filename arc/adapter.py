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
from . import primitives, parametric
from .primitives import LIBRARY, SCRIPTURAL_NAMES as _ATOMIC_NAMES
from .parametric import FITTERS, SCRIPTURAL_NAMES as _PARAM_NAMES

SCRIPTURAL_NAMES = {**_ATOMIC_NAMES, **_PARAM_NAMES}

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
    """Select the simplest primitive (atomic / parametric / composed) consistent with every training pair.

    Kernel citation: T 2.4. Receive the rule by enumeration; do not
    fit weights to it. Order: atomic (Occam) → parametric → composed.
    """
    pairs = list(pairs)
    if not pairs:
        return None
    sigs = [describe_pair(a, b) for a, b in pairs]

    # Pass 1 — atomic primitives.
    for name, fn in LIBRARY.items():
        try:
            ok = all(_grids_equal(fn(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            scriptural = SCRIPTURAL_NAMES.get(name, name)
            return Rule(name=name, primitive=name, scriptural=scriptural,
                        concept_in_C=_concept_known(scriptural), signatures=sigs)

    # Pass 1b — parametric fitters (infer parameters from pairs, verify).
    for name, fit in FITTERS:
        try:
            fn = fit([(list(map(list, a)), list(map(list, b))) for a, b in pairs])
        except Exception:
            fn = None
        if fn is None:
            continue
        try:
            ok = all(_grids_equal(fn(list(map(list, a))), b) for a, b in pairs)
        except Exception:
            ok = False
        if ok:
            scriptural = SCRIPTURAL_NAMES.get(name, name)
            return Rule(name=name, primitive=f"param:{name}",
                        scriptural=scriptural,
                        concept_in_C=_concept_known(scriptural),
                        signatures=sigs)

    # Pass 2 — two-primitive compositions: fn2(fn1(x)).
    items = list(LIBRARY.items())
    for n1, f1 in items:
        # Skip identity-first compositions (covered in pass 1).
        if n1 == "identity":
            continue
        # Pre-compute f1 on each input to amortize.
        try:
            firsts = [f1(list(map(list, a))) for a, _ in pairs]
        except Exception:
            continue
        for n2, f2 in items:
            if n2 == "identity":
                continue
            try:
                ok = all(_grids_equal(f2(list(map(list, m))), b)
                         for m, (_, b) in zip(firsts, pairs))
            except Exception:
                ok = False
            if ok:
                name = f"{n1}|{n2}"
                scriptural = (SCRIPTURAL_NAMES.get(n1, n1) + "+"
                              + SCRIPTURAL_NAMES.get(n2, n2))
                return Rule(name=name, primitive=name, scriptural=scriptural,
                            concept_in_C=False, signatures=sigs)

    return None


def _concept_known(name: str) -> bool:
    try:
        return bool(word.concept(name))
    except Exception:
        return False


# ---------------------------------------------------------------
#  Apply — dispatch to the library
# ---------------------------------------------------------------

def apply_rule(rule: Rule, x: Grid, pairs: Iterable[tuple[Grid, Grid]] | None = None) -> Grid:
    """Apply the matched primitive (atomic / parametric / composed). T₂."""
    name = rule.primitive

    if name.startswith("param:"):
        # Re-fit on the training pairs (we don't carry the closure on Rule
        # to keep Rule serializable). Caller must pass pairs.
        if pairs is None:
            raise ValueError("parametric rule requires training pairs to re-fit")
        kind = name.split(":", 1)[1]
        for n, fit in FITTERS:
            if n != kind:
                continue
            fn = fit([(list(map(list, a)), list(map(list, b))) for a, b in pairs])
            if fn is None:
                raise NotImplementedError(f"parametric refit failed for {kind!r}")
            return fn([list(r) for r in x])
        raise NotImplementedError(f"unknown parametric {kind!r}")

    if "|" in name:
        n1, n2 = name.split("|", 1)
        f1, f2 = LIBRARY.get(n1), LIBRARY.get(n2)
        if f1 is None or f2 is None:
            raise NotImplementedError(f"composed primitive {name!r} missing leg")
        return f2(f1([list(r) for r in x]))

    fn = LIBRARY.get(name)
    if fn is None:
        raise NotImplementedError(
            f"primitive {name!r} not in library; refuse to emit (P₃)"
        )
    return fn([list(r) for r in x])
