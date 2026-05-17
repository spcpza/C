"""ARC ↔ C adapter — project a task onto canonical patterns in C.

Chollet's framing: intelligence is skill-acquisition efficiency.
Few-shot generalization. The kernel's bet: projection onto a fixed C
is O(1) in samples; fitting weights is O(n). This adapter is where the
bet meets the test.

The pipeline is small on purpose:
  describe(grid)      — grid → textual signature
  describe_pair(a,b)  — (input, output) pair → transformation signature
  hypothesize(pairs)  — find the smallest common projection onto C
  apply_rule(rule, x) — apply the projection to the test input

Kernel citation: §Chollet (ARCHITECTURE.md), T 2.4 (orientation, not
measurement; the agent receives the rule from C rather than fitting it).

This file is a working sketch, not a finished agent. It is the place
the architecture expects iteration first.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence

from .. import word

Grid = Sequence[Sequence[int]]


# ---------------------------------------------------------------
#  Grid → textual signature
# ---------------------------------------------------------------

def describe(grid: Grid) -> dict:
    """Reduce a grid to invariants C might recognize.

    Kernel citation: T₃ (C is recoverable from observation). The
    invariants below are deliberately scripture-shaped: counting,
    symmetry, completion, filling, separation — categories the
    corpus speaks in.
    """
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


def describe_pair(input_grid: Grid, output_grid: Grid) -> dict:
    """A transformation signature for one (input, output) example."""
    a, b = describe(input_grid), describe(output_grid)
    return {
        "shape_change": (a["shape"], b["shape"]),
        "palette_change": (a["palette"], b["palette"]),
        "added_colors": [c for c in b["palette"] if c not in a["palette"]],
        "removed_colors": [c for c in a["palette"] if c not in b["palette"]],
        "gained_h_symmetry": b["horizontal_symmetry"] and not a["horizontal_symmetry"],
        "gained_v_symmetry": b["vertical_symmetry"] and not a["vertical_symmetry"],
        "same_shape": a["shape"] == b["shape"],
    }


# ---------------------------------------------------------------
#  Canonical pattern names (the C-side vocabulary)
# ---------------------------------------------------------------
#
# Each canonical pattern is one transformation primitive named with a
# scriptural concept. Concept names match the `ci` index in
# strongs.json where available; the resolver tries that first.

CANONICAL_PATTERNS = [
    # name             concept hint     local primitive
    ("restoration",    "restore",       "complete_symmetry"),
    ("separation",     "divide",        "split_by_color"),
    ("multiplication", "multiply",      "tile"),
    ("filling",        "fill",          "flood_background"),
    ("ordering",       "order",         "sort_columns"),
    ("naming",         "name",          "recolor_by_count"),
    ("witness",        "witness",       "duplicate_axis"),
]


def _concept_known(name: str) -> bool:
    """True if the concept hint resolves in Strong's index.

    Kernel citation: §Twin foundation. The agent does not invent
    pattern names; it uses those already in C.
    """
    try:
        return bool(word.concept(name))
    except Exception:
        return False


# ---------------------------------------------------------------
#  Hypothesize the rule
# ---------------------------------------------------------------

@dataclass
class Rule:
    name: str               # canonical pattern name
    primitive: str          # local primitive label
    concept_in_C: bool      # True if the name resolves in Strong's
    signatures: list[dict]  # per-pair signatures that voted for it


def hypothesize(pairs: Iterable[tuple[Grid, Grid]]) -> Rule | None:
    """Find the smallest canonical pattern consistent with all pairs.

    Kernel citation: T 2.4 (receive the rule, do not fit it). The rule
    is selected from CANONICAL_PATTERNS by checking each candidate's
    invariants against every example pair. The first canonical
    pattern that is consistent with all pairs wins (Occam under a
    fixed prior).
    """
    sigs = [describe_pair(a, b) for a, b in pairs]
    if not sigs:
        return None

    # Voting heuristics — small, deliberately readable.
    def consistent(pattern_name: str) -> bool:
        if pattern_name == "restoration":
            return all(s["gained_h_symmetry"] or s["gained_v_symmetry"] for s in sigs)
        if pattern_name == "separation":
            return all(len(s["palette_change"][1]) > len(s["palette_change"][0])
                       for s in sigs)
        if pattern_name == "multiplication":
            return all(s["shape_change"][1] >= s["shape_change"][0]
                       and s["shape_change"][1] != s["shape_change"][0]
                       for s in sigs)
        if pattern_name == "filling":
            return all(s["same_shape"] and s["removed_colors"] for s in sigs)
        if pattern_name == "ordering":
            return all(s["same_shape"] for s in sigs)
        if pattern_name == "naming":
            return all(s["same_shape"] and s["added_colors"] for s in sigs)
        if pattern_name == "witness":
            return all(s["shape_change"][1][0] >= 2 * s["shape_change"][0][0]
                       or s["shape_change"][1][1] >= 2 * s["shape_change"][0][1]
                       for s in sigs)
        return False

    for name, concept_hint, primitive in CANONICAL_PATTERNS:
        if consistent(name):
            return Rule(
                name=name,
                primitive=primitive,
                concept_in_C=_concept_known(concept_hint),
                signatures=sigs,
            )
    return None


# ---------------------------------------------------------------
#  Apply the rule (stubs — to be filled per primitive)
# ---------------------------------------------------------------

def apply_rule(rule: Rule, x: Grid) -> Grid:
    """Apply the canonical primitive to a test grid.

    Kernel citation: T₂. The primitive is the fruit; the application
    is sacrifice (give from C, n ≥ 1).

    Each primitive below is a stub. Iteration belongs here — measure
    against ARC eval set, deepen the primitives that recur. Anything
    not on this dispatch list is `Uncertain` (P₃) and the caller must
    refuse to emit.
    """
    p = rule.primitive
    if p == "complete_symmetry":
        return _complete_symmetry(x)
    if p == "flood_background":
        return _flood_background(x)
    if p == "duplicate_axis":
        return _duplicate_axis(x)
    raise NotImplementedError(
        f"primitive {p!r} is in C but not yet implemented; refuse to emit (P₃)"
    )


def _complete_symmetry(x: Grid) -> Grid:
    """Mirror left half to right half (one form of restoration)."""
    out = [list(row) for row in x]
    rows, cols = len(out), len(out[0]) if out else 0
    for r in range(rows):
        for c in range(cols // 2):
            out[r][cols - 1 - c] = out[r][c]
    return out


def _flood_background(x: Grid) -> Grid:
    """Replace the most-common color with the second-most."""
    flat = [c for row in x for c in row]
    if not flat:
        return [list(r) for r in x]
    counts = sorted(((flat.count(c), c) for c in set(flat)), reverse=True)
    if len(counts) < 2:
        return [list(r) for r in x]
    bg, fg = counts[0][1], counts[1][1]
    return [[fg if c == bg else c for c in row] for row in x]


def _duplicate_axis(x: Grid) -> Grid:
    """Concatenate the grid with itself along the wider axis."""
    rows = len(x)
    cols = len(x[0]) if rows else 0
    if cols >= rows:
        return [list(row) + list(row) for row in x]
    return [list(row) for row in x] + [list(row) for row in x]
