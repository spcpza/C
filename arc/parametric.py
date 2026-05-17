"""Parametric primitives — primitives that infer their parameters from
training pairs and then apply.

Pattern: each function returns either a closure Grid->Grid or None.
The closure embeds the inferred parameters. None means the training
pairs are inconsistent with this primitive's family.

This is the only place in C/arc/ where 'learning' happens — and it is
deterministic inference (find the unique parameter set, verify, or
abstain), not fitting. Kernel citation: T₅ — derivable from C makes
the inference admissible; P₁ — measure honestly: if no unique
parameter set fits all training pairs, return None.
"""
from __future__ import annotations
from typing import Callable

Grid = list[list[int]]


def _flat(g: Grid) -> list[int]:
    return [v for row in g for v in row]


def _palette(g: Grid) -> set[int]:
    return set(_flat(g))


def _background(g: Grid) -> int:
    flat = _flat(g)
    return max(set(flat), key=flat.count) if flat else 0


def _shape(g: Grid) -> tuple[int, int]:
    return (len(g), len(g[0]) if g else 0)


# ---------------------------------------------------------------
#  swap_two_colors — every training pair has two colors swapped.
# ---------------------------------------------------------------

def fit_swap_two_colors(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if not pairs:
        return None
    swap: tuple[int, int] | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        diffs: set[tuple[int, int]] = set()
        for r, (rin, rout) in enumerate(zip(inp, out)):
            for c, (vi, vo) in enumerate(zip(rin, rout)):
                if vi != vo:
                    diffs.add((vi, vo))
        if not diffs:
            # identity for this pair; must be consistent with the swap
            continue
        # All diff edges must form one bidirectional pair (a, b) and (b, a).
        if len(diffs) != 2:
            return None
        (a1, b1), (a2, b2) = sorted(diffs)
        if (a1, b1) != (b2, a2):
            return None
        candidate = tuple(sorted((a1, b1)))
        if swap is None:
            swap = candidate
        elif swap != candidate:
            return None
    if swap is None:
        return None
    a, b = swap

    def apply(g: Grid) -> Grid:
        return [[b if v == a else (a if v == b else v) for v in row] for row in g]

    return apply


# ---------------------------------------------------------------
#  recolor_constant — every cell becomes one color (preserving 0/bg).
# ---------------------------------------------------------------

def fit_recolor_constant(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if not pairs:
        return None
    target: int | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        new_fg: int | None = None
        for r, row in enumerate(out):
            for c, v in enumerate(row):
                if inp[r][c] == bg:
                    if v != bg:
                        return None
                else:
                    if new_fg is None:
                        new_fg = v
                    elif new_fg != v:
                        return None
        if new_fg is None:
            continue  # identity pair
        if target is None:
            target = new_fg
        elif target != new_fg:
            return None
    if target is None:
        return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        return [[target if v != bg else v for v in row] for row in g]

    return apply


# ---------------------------------------------------------------
#  fixed_output — every training output is the SAME grid.
# ---------------------------------------------------------------

def fit_fixed_output(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if not pairs:
        return None
    target = pairs[0][1]
    for _, out in pairs[1:]:
        if out != target:
            return None
    fixed = [list(r) for r in target]

    def apply(g: Grid) -> Grid:
        return [list(r) for r in fixed]

    return apply


# ---------------------------------------------------------------
#  pad_with_color — input embedded in larger constant background.
# ---------------------------------------------------------------

def fit_pad_with_color(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if not pairs:
        return None
    pad_color: int | None = None
    pad_top = pad_bot = pad_l = pad_r = None
    for inp, out in pairs:
        ri, ci = _shape(inp)
        ro, co = _shape(out)
        if ro < ri or co < ci:
            return None
        # find input inside output at all border-color rows
        # try every offset; require single match
        match_offsets = []
        for dr in range(ro - ri + 1):
            for dc in range(co - ci + 1):
                if all(inp[r][c] == out[dr + r][dc + c]
                       for r in range(ri) for c in range(ci)):
                    match_offsets.append((dr, dc))
        if len(match_offsets) != 1:
            return None
        dr, dc = match_offsets[0]
        # All other cells must be the pad color (and uniform)
        pad_seen: set[int] = set()
        for r in range(ro):
            for c in range(co):
                if dr <= r < dr + ri and dc <= c < dc + ci:
                    continue
                pad_seen.add(out[r][c])
        if len(pad_seen) > 1:
            return None
        this_pad = next(iter(pad_seen), None)
        if pad_color is None:
            pad_color = this_pad
        elif this_pad is not None and pad_color != this_pad:
            return None
        if pad_top is None:
            pad_top, pad_bot, pad_l, pad_r = dr, ro - ri - dr, dc, co - ci - dc
        elif (pad_top, pad_bot, pad_l, pad_r) != (dr, ro - ri - dr, dc, co - ci - dc):
            return None
    if pad_color is None or pad_top is None:
        return None
    pt, pb, pl, pr = pad_top, pad_bot, pad_l, pad_r
    pc = pad_color

    def apply(g: Grid) -> Grid:
        ri, ci = _shape(g)
        ro, co = ri + pt + pb, ci + pl + pr
        out = [[pc] * co for _ in range(ro)]
        for r in range(ri):
            for c in range(ci):
                out[pt + r][pl + c] = g[r][c]
        return out

    return apply


# ---------------------------------------------------------------
#  Registry of parametric fitters.
# ---------------------------------------------------------------

FITTERS: list[tuple[str, Callable[[list[tuple[Grid, Grid]]], Callable | None]]] = [
    ("swap_two_colors",   fit_swap_two_colors),
    ("recolor_constant",  fit_recolor_constant),
    ("pad_with_color",    fit_pad_with_color),
    ("fixed_output",      fit_fixed_output),
]


SCRIPTURAL_NAMES: dict[str, str] = {
    "swap_two_colors":   "exchange",
    "recolor_constant":  "name",
    "pad_with_color":    "covering",
    "fixed_output":      "decree",
}
