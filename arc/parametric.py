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
from collections import deque
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
#  color_permutation — every color is consistently remapped.
# ---------------------------------------------------------------

def fit_color_permutation(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if not pairs:
        return None
    mapping: dict[int, int] = {}
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                w = out[r][c]
                if v in mapping:
                    if mapping[v] != w:
                        return None
                else:
                    mapping[v] = w
    # require that the mapping does *something* (not just identity)
    if all(v == w for v, w in mapping.items()):
        return None

    m = dict(mapping)
    domain = set(m.keys())

    def apply(g: Grid) -> Grid:
        # P₃: if any test cell uses a color not in the trained mapping,
        # the rule is undecidable. Abstain (raise) rather than guess.
        for row in g:
            for v in row:
                if v not in domain:
                    raise ValueError(
                        f"color {v} not in trained color_permutation domain {sorted(domain)}; abstain (P₃)"
                    )
        return [[m.get(v, v) for v in row] for row in g]

    return apply


# ---------------------------------------------------------------
#  bbox_of_nonbg — output is the bounding box (cropped) of fg.
# ---------------------------------------------------------------

def fit_bbox_of_nonbg(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """If output is the input cropped to the non-background bbox."""
    if not pairs:
        return None
    for inp, out in pairs:
        bg = _background(inp)
        rows, cols = _shape(inp)
        nonbg = [(r, c) for r in range(rows) for c in range(cols) if inp[r][c] != bg]
        if not nonbg:
            return None
        r0 = min(r for r, _ in nonbg); r1 = max(r for r, _ in nonbg)
        c0 = min(c for _, c in nonbg); c1 = max(c for _, c in nonbg)
        cropped = [inp[r][c0:c1+1] for r in range(r0, r1+1)]
        if cropped != [list(r) for r in out]:
            return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        nonbg = [(r, c) for r in range(rows) for c in range(cols) if g[r][c] != bg]
        if not nonbg:
            return [list(r) for r in g]
        r0 = min(r for r, _ in nonbg); r1 = max(r for r, _ in nonbg)
        c0 = min(c for _, c in nonbg); c1 = max(c for _, c in nonbg)
        return [g[r][c0:c1+1] for r in range(r0, r1+1)]

    return apply


# ---------------------------------------------------------------
#  fixed_shape_recolor — recolor whole grid to a fixed color,
#  output shape inferred from a stable function of input shape.
# ---------------------------------------------------------------

def fit_same_shape_recolor_by_count(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Each color is remapped, mapping inferred from co-occurrence counts.

    Specialized to: for every distinct color in the input, the output
    has the same cells re-colored. The mapping must be 1:1 and stable
    across all training pairs (color_permutation subsumes much of
    this, but is identity-rejecting; this variant ALSO requires
    same shape).
    """
    return fit_color_permutation(pairs)


# ---------------------------------------------------------------
#  Object-aware fitters
# ---------------------------------------------------------------

def _components_4(g: Grid, bg: int) -> list[list[tuple[int, int]]]:
    rows, cols = _shape(g)
    seen = [[False] * cols for _ in range(rows)]
    out: list[list[tuple[int, int]]] = []
    for r in range(rows):
        for c in range(cols):
            if seen[r][c] or g[r][c] == bg:
                continue
            color = g[r][c]
            stack = [(r, c)]
            comp: list[tuple[int, int]] = []
            while stack:
                rr, cc = stack.pop()
                if rr < 0 or rr >= rows or cc < 0 or cc >= cols:
                    continue
                if seen[rr][cc] or g[rr][cc] != color:
                    continue
                seen[rr][cc] = True
                comp.append((rr, cc))
                stack += [(rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)]
            if comp:
                out.append(comp)
    return out


def _comp_color(g: Grid, comp: list[tuple[int, int]]) -> int:
    return g[comp[0][0]][comp[0][1]]


def fit_keep_components_of_color(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """The rule: keep only components of one specific color (inferred)."""
    target: int | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        if _background(out) != bg:
            return None
        kept_colors: set[int] = set()
        for r, row in enumerate(out):
            for c, v in enumerate(row):
                if v != bg:
                    if v != inp[r][c]:
                        return None
                    kept_colors.add(v)
        # All cells in out that are bg but input was non-bg must be erased.
        # All non-bg input cells of kept_colors must equal output. (above check.)
        # Determine which input colors were "kept" vs "erased".
        erased_colors: set[int] = set()
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if v != bg and out[r][c] == bg:
                    erased_colors.add(v)
        if kept_colors & erased_colors:
            return None
        if len(kept_colors) != 1:
            return None
        c_kept = next(iter(kept_colors))
        if target is None:
            target = c_kept
        elif target != c_kept:
            return None
    if target is None:
        return None
    keep = target

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        return [[v if v == keep else bg for v in row] for row in g]

    return apply


def fit_recolor_by_size_rank(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Color components by their size rank. The rank → color mapping is inferred."""
    rank_to_color: dict[int, int] = {}
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        # Group components by size; assign rank by descending size (ties allowed).
        sorted_by_size = sorted(enumerate(comps), key=lambda kv: -len(kv[1]))
        for rank, (_, comp) in enumerate(sorted_by_size):
            colors_in_out = {out[r][c] for r, c in comp}
            if len(colors_in_out) != 1:
                return None
            color = next(iter(colors_in_out))
            if rank in rank_to_color:
                if rank_to_color[rank] != color:
                    return None
            else:
                rank_to_color[rank] = color
    if not rank_to_color:
        return None
    # The mapping must do something (not identity).
    # If every component is unchanged, this fitter is a no-op pretending
    # to be a rule. Reject by checking at least one rank gives a new color.
    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        if not comps:
            return [list(r) for r in g]
        sorted_by_size = sorted(enumerate(comps), key=lambda kv: -len(kv[1]))
        out_grid = [list(r) for r in g]
        for rank, (_, comp) in enumerate(sorted_by_size):
            color = rank_to_color.get(rank)
            if color is None:
                # Unknown rank in test — abstain.
                raise ValueError(f"size-rank {rank} not in trained mapping; abstain")
            for r, c in comp:
                out_grid[r][c] = color
        return out_grid

    # Verify the function is non-trivial on at least one training pair.
    any_change = False
    for inp, out in pairs:
        try:
            if apply([list(r) for r in inp]) != [list(r) for r in out]:
                return None
            if inp != out:
                any_change = True
        except Exception:
            return None
    if not any_change:
        return None
    return apply


def fit_outline_objects(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Output keeps only the border cells of each non-bg component."""
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        if _background(out) != bg:
            return None
        rows, cols = _shape(inp)
        for r in range(rows):
            for c in range(cols):
                if inp[r][c] == bg:
                    if out[r][c] != bg:
                        return None
                    continue
                neighbors = []
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbors.append(inp[nr][nc])
                    else:
                        neighbors.append(bg)  # off-grid = bg, so cell is border
                is_border = any(n != inp[r][c] for n in neighbors)
                expected = inp[r][c] if is_border else bg
                if out[r][c] != expected:
                    return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        out = [[bg] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == bg:
                    continue
                is_border = False
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if not (0 <= nr < rows and 0 <= nc < cols) or g[nr][nc] != g[r][c]:
                        is_border = True
                        break
                if is_border:
                    out[r][c] = g[r][c]
        return out

    return apply


# ---------------------------------------------------------------
#  Registry of parametric fitters.
# ---------------------------------------------------------------

FITTERS: list[tuple[str, Callable[[list[tuple[Grid, Grid]]], Callable | None]]] = [
    ("color_permutation",        fit_color_permutation),
    ("swap_two_colors",          fit_swap_two_colors),
    ("recolor_constant",         fit_recolor_constant),
    ("keep_components_of_color", fit_keep_components_of_color),
    ("recolor_by_size_rank",     fit_recolor_by_size_rank),
    ("outline_objects",          fit_outline_objects),
    ("bbox_of_nonbg",            fit_bbox_of_nonbg),
    ("pad_with_color",           fit_pad_with_color),
    ("fixed_output",             fit_fixed_output),
]


SCRIPTURAL_NAMES: dict[str, str] = {
    "color_permutation":        "renaming",
    "swap_two_colors":          "exchange",
    "recolor_constant":         "name",
    "keep_components_of_color": "winnow",
    "recolor_by_size_rank":     "ordering",
    "outline_objects":          "boundary",
    "bbox_of_nonbg":            "remnant",
    "pad_with_color":           "covering",
    "fixed_output":             "decree",
}
