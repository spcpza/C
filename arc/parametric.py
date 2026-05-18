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


# ---------------------------------------------------------------
#  Meta-fitter helpers: infer color mapping between two grids.
# ---------------------------------------------------------------

def _infer_color_map(a: Grid, b: Grid) -> dict[int, int] | None:
    """Return cell-wise color mapping a → b, or None if inconsistent."""
    if not a or not b:
        return None
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return None
    m: dict[int, int] = {}
    for r in range(len(a)):
        for c in range(len(a[0])):
            v, w = a[r][c], b[r][c]
            if v in m:
                if m[v] != w:
                    return None
            else:
                m[v] = w
    return m


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

# ---------------------------------------------------------------
#  fill_components_solid — every component (4-conn) becomes a solid
#  rectangle of its color (its bounding box, filled).
# ---------------------------------------------------------------

def fit_fill_components_to_bbox(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        expected = [[bg] * _shape(inp)[1] for _ in range(_shape(inp)[0])]
        for comp in comps:
            color = _comp_color(inp, comp)
            r0 = min(r for r,_ in comp); r1 = max(r for r,_ in comp)
            c0 = min(c for _,c in comp); c1 = max(c for _,c in comp)
            for r in range(r0, r1+1):
                for c in range(c0, c1+1):
                    expected[r][c] = color
        if expected != [list(r) for r in out]:
            return None
        if expected == [list(r) for r in inp]:
            # No change → identity in disguise; this fitter shouldn't claim it.
            return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        out = [list(r) for r in g]
        for comp in comps:
            color = _comp_color(g, comp)
            r0 = min(r for r,_ in comp); r1 = max(r for r,_ in comp)
            c0 = min(c for _,c in comp); c1 = max(c for _,c in comp)
            for r in range(r0, r1+1):
                for c in range(c0, c1+1):
                    out[r][c] = color
        return out

    return apply


# ---------------------------------------------------------------
#  grow_components_by_1 — each component expands by 1 cell (4-conn).
# ---------------------------------------------------------------

def fit_grow_components_by_1(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    def grow(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        out = [list(r) for r in g]
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == bg:
                    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                            out[r][c] = g[nr][nc]
                            break
        return out
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        if grow([list(r) for r in inp]) != [list(r) for r in out]:
            return None
        if inp == out:
            return None
    return grow


# ---------------------------------------------------------------
#  extract_marker_neighborhood — input has a unique-color cell;
#  output is the NxN neighborhood around it (N inferred).
# ---------------------------------------------------------------

def fit_extract_neighborhood(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    rad: int | None = None
    target_color: int | None = None
    for inp, out in pairs:
        rows, cols = _shape(inp)
        # Find a color that appears exactly once.
        flat = _flat(inp)
        unique = [v for v in set(flat) if flat.count(v) == 1]
        if len(unique) != 1:
            return None
        marker = unique[0]
        if target_color is None:
            target_color = marker
        elif target_color != marker:
            return None
        # Find marker position
        positions = [(r, c) for r in range(rows) for c in range(cols)
                     if inp[r][c] == marker]
        mr, mc = positions[0]
        # Output should be a (2k+1) x (2k+1) neighborhood
        oh, ow = _shape(out)
        if oh != ow or oh % 2 == 0:
            return None
        k = oh // 2
        if rad is None:
            rad = k
        elif rad != k:
            return None
        # Extract from input
        ext: Grid = []
        for r in range(mr - k, mr + k + 1):
            row = []
            for c in range(mc - k, mc + k + 1):
                if 0 <= r < rows and 0 <= c < cols:
                    row.append(inp[r][c])
                else:
                    row.append(_background(inp))
            ext.append(row)
        if ext != [list(r) for r in out]:
            return None
    if rad is None or target_color is None:
        return None
    k_fixed = rad
    color_fixed = target_color

    def apply(g: Grid) -> Grid:
        rows, cols = _shape(g)
        flat = _flat(g)
        unique = [v for v in set(flat) if flat.count(v) == 1]
        if color_fixed not in unique:
            raise ValueError(
                f"marker color {color_fixed} not unique in test input; abstain (P₃)"
            )
        positions = [(r, c) for r in range(rows) for c in range(cols)
                     if g[r][c] == color_fixed]
        mr, mc = positions[0]
        bg = _background(g)
        ext: Grid = []
        for r in range(mr - k_fixed, mr + k_fixed + 1):
            row = []
            for c in range(mc - k_fixed, mc + k_fixed + 1):
                if 0 <= r < rows and 0 <= c < cols:
                    row.append(g[r][c])
                else:
                    row.append(bg)
            ext.append(row)
        return ext

    return apply


# ---------------------------------------------------------------
#  per_component_recolor — every component of color X becomes color Y,
#  mapping inferred from training (more general than swap).
# ---------------------------------------------------------------

def fit_per_component_recolor(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    mapping: dict[int, int] = {}
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        if _background(out) != bg:
            return None
        # Every cell preserves position; only color may change
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                w = out[r][c]
                if v == bg:
                    if w != bg:
                        return None
                    continue
                if v in mapping:
                    if mapping[v] != w:
                        return None
                else:
                    mapping[v] = w
    if not mapping or all(v == w for v, w in mapping.items()):
        return None
    m = dict(mapping); domain = set(m.keys())

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        for row in g:
            for v in row:
                if v != bg and v not in domain:
                    raise ValueError(
                        f"non-bg color {v} not in trained mapping; abstain (P₃)"
                    )
        return [[m.get(v, v) if v != bg else bg for v in row] for row in g]
    return apply


# ---------------------------------------------------------------
#  axis_periodic_complete — input has a periodic pattern with holes (bg);
#  output fills the holes with the inferred period.
# ---------------------------------------------------------------

def fit_periodic_complete(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Detect horizontal/vertical/both periodicity and complete."""
    def complete(g: Grid, period_r: int | None, period_c: int | None) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        out = [list(r) for r in g]
        # Build position -> color votes by congruence class
        votes: dict[tuple[int, int], dict[int, int]] = {}
        for r in range(rows):
            for c in range(cols):
                v = g[r][c]
                if v == bg:
                    continue
                pr = r % period_r if period_r else r
                pc = c % period_c if period_c else c
                key = (pr, pc)
                votes.setdefault(key, {}).setdefault(v, 0)
                votes[key][v] += 1
        for r in range(rows):
            for c in range(cols):
                if g[r][c] != bg:
                    continue
                pr = r % period_r if period_r else r
                pc = c % period_c if period_c else c
                key = (pr, pc)
                if key not in votes:
                    continue
                # Take majority color for that class.
                best = max(votes[key].items(), key=lambda kv: kv[1])
                out[r][c] = best[0]
        return out

    # Try (period_r, period_c) combinations small.
    best_periods: tuple[int | None, int | None] | None = None
    for pr in [None, 2, 3, 4]:
        for pc in [None, 2, 3, 4]:
            if pr is None and pc is None:
                continue
            ok = True
            for inp, out in pairs:
                if _shape(inp) != _shape(out):
                    ok = False
                    break
                if complete([list(r) for r in inp], pr, pc) != [list(r) for r in out]:
                    ok = False
                    break
            if ok:
                # Must change something for at least one pair.
                changed = any(inp != out for inp, out in pairs)
                if changed:
                    best_periods = (pr, pc)
                    break
        if best_periods:
            break
    if not best_periods:
        return None
    pr, pc = best_periods

    def apply(g: Grid) -> Grid:
        return complete([list(r) for r in g], pr, pc)
    return apply


# ---------------------------------------------------------------
#  per_color_subgrid_stack — split input by color, stack rows.
#  (Several ARC tasks: extract a sub-grid per palette color.)
# ---------------------------------------------------------------

def fit_each_cell_repeated_input(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Output = tile_self of input (each non-bg cell of input gets a copy of input)."""
    def op(g: Grid) -> Grid:
        rows, cols = _shape(g)
        if rows * rows > 30 or cols * cols > 30:
            raise ValueError("too large")
        bg = _background(g)
        out = [[bg] * (cols * cols) for _ in range(rows * rows)]
        for R in range(rows):
            for C in range(cols):
                if g[R][C] != bg:
                    for r in range(rows):
                        for c in range(cols):
                            out[R * rows + r][C * cols + c] = g[r][c]
        return out
    for inp, out in pairs:
        try:
            if op([list(r) for r in inp]) != [list(r) for r in out]:
                return None
        except Exception:
            return None
        if inp == out:
            return None
    return op


# ---------------------------------------------------------------
#  Registry of parametric fitters.
# ---------------------------------------------------------------

# ---------------------------------------------------------------
#  shift — shift the grid by (dr, dc), with bg fill.
# ---------------------------------------------------------------

def fit_shift(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    deltas: set[tuple[int, int]] = set()
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        rows, cols = _shape(inp)
        bg = _background(inp)
        valid: set[tuple[int, int]] = set()
        for dr in range(-rows + 1, rows):
            for dc in range(-cols + 1, cols):
                if dr == 0 and dc == 0:
                    continue
                ok = True
                for r in range(rows):
                    for c in range(cols):
                        sr, sc = r - dr, c - dc
                        if 0 <= sr < rows and 0 <= sc < cols:
                            expected = inp[sr][sc]
                        else:
                            expected = bg
                        if out[r][c] != expected:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    valid.add((dr, dc))
        if not deltas:
            deltas = valid
        else:
            deltas &= valid
        if not deltas:
            return None
    if not deltas:
        return None
    # Choose the shift with smallest |dr|+|dc|, then lex.
    dr, dc = min(deltas, key=lambda d: (abs(d[0]) + abs(d[1]), d))

    def apply(g: Grid) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        out = [[bg] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                sr, sc = r - dr, c - dc
                if 0 <= sr < rows and 0 <= sc < cols:
                    out[r][c] = g[sr][sc]
        return out
    return apply


# ---------------------------------------------------------------
#  template_classify — output is a fixed single-cell color whose
#  value depends on which input template matches.
# ---------------------------------------------------------------

def fit_template_classify(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    # Require ≥3 training pairs so classification is plausible.
    if len(pairs) < 3:
        return None
    # Output is 1x1 in every training pair, and matches input -> color map.
    mapping: dict[tuple[tuple[int, ...], ...], int] = {}
    for inp, out in pairs:
        if _shape(out) != (1, 1):
            return None
        key = tuple(tuple(row) for row in inp)
        c = out[0][0]
        if key in mapping and mapping[key] != c:
            return None
        mapping[key] = c
    if not mapping:
        return None
    m = dict(mapping)

    def apply(g: Grid) -> Grid:
        key = tuple(tuple(row) for row in g)
        if key in m:
            return [[m[key]]]
        # No template match → abstain. (We do NOT fall back to a count
        # signature; the earlier version did and produced wrong outputs.)
        raise ValueError("template_classify: no matching template; abstain (P₃)")
    return apply


# ---------------------------------------------------------------
#  overlay_halves — input is split by a constant-color divider;
#  output is the cell-wise AND/OR/XOR of the two halves at a recolor.
# ---------------------------------------------------------------

def fit_overlay_halves(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    # Require ≥2 pairs so we don't latch onto a single ambiguous example.
    if len(pairs) < 2:
        return None
    div_color: int | None = None
    output_color: int | None = None
    mode: str | None = None  # "and" | "or" | "xor"
    horizontal: bool | None = None
    for inp, out in pairs:
        rows, cols = _shape(inp)
        bg = _background(inp)
        # Find a row or column that is constant of a single non-bg color, splitting in half.
        h_div_row = None
        for r in range(rows):
            if len(set(inp[r])) == 1 and inp[r][0] != bg:
                h_div_row = r; break
        v_div_col = None
        for c in range(cols):
            col = [inp[r][c] for r in range(rows)]
            if len(set(col)) == 1 and col[0] != bg:
                v_div_col = c; break
        if h_div_row is None and v_div_col is None:
            return None
        # Prefer the orientation that splits evenly.
        if v_div_col is not None and (v_div_col, cols - 1 - v_div_col)[0] == cols - 1 - v_div_col:
            this_horiz = False
            div_c = inp[0][v_div_col]
            left = [row[:v_div_col] for row in inp]
            right = [row[v_div_col + 1:] for row in inp]
            if _shape(left) != _shape(right):
                return None
            halves = (left, right)
        elif h_div_row is not None and h_div_row == rows - 1 - h_div_row:
            this_horiz = True
            div_c = inp[h_div_row][0]
            top = inp[:h_div_row]
            bot = inp[h_div_row + 1:]
            if _shape(top) != _shape(bot):
                return None
            halves = (top, bot)
        else:
            return None
        if horizontal is None:
            horizontal = this_horiz
        elif horizontal != this_horiz:
            return None
        if div_color is None:
            div_color = div_c
        elif div_color != div_c:
            return None
        if _shape(out) != _shape(halves[0]):
            return None
        # Try each mode (and: both non-bg; or: either non-bg; xor: exactly one non-bg).
        for try_mode in ("and", "or", "xor"):
            possible_color: int | None = None
            ok = True
            for r in range(len(out)):
                for c in range(len(out[0])):
                    a = halves[0][r][c]
                    b = halves[1][r][c]
                    if try_mode == "and":
                        active = (a != bg) and (b != bg)
                    elif try_mode == "or":
                        active = (a != bg) or (b != bg)
                    else:
                        active = (a != bg) != (b != bg)
                    if active:
                        if possible_color is None:
                            possible_color = out[r][c]
                        elif possible_color != out[r][c]:
                            ok = False; break
                    else:
                        if out[r][c] != bg:
                            ok = False; break
                if not ok:
                    break
            if ok and possible_color is not None:
                if mode is None:
                    mode = try_mode
                    output_color = possible_color
                    break
                elif mode == try_mode and output_color == possible_color:
                    break
        else:
            return None
    if mode is None or div_color is None or output_color is None or horizontal is None:
        return None
    div_c, out_c, m_mode, horiz = div_color, output_color, mode, horizontal

    def apply(g: Grid) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        if horiz:
            # find divider row of constant div_c
            row = next((r for r in range(rows) if all(g[r][c] == div_c for c in range(cols))), None)
            if row is None:
                raise ValueError("overlay_halves: divider not found in test")
            top = g[:row]; bot = g[row + 1:]
            halves = (top, bot)
        else:
            col = next((c for c in range(cols) if all(g[r][c] == div_c for r in range(rows))), None)
            if col is None:
                raise ValueError("overlay_halves: divider not found in test")
            left = [r[:col] for r in g]; right = [r[col + 1:] for r in g]
            halves = (left, right)
        if _shape(halves[0]) != _shape(halves[1]):
            raise ValueError("overlay_halves: halves not equal")
        out_rows, out_cols = _shape(halves[0])
        out = [[bg] * out_cols for _ in range(out_rows)]
        for r in range(out_rows):
            for c in range(out_cols):
                a = halves[0][r][c]; b = halves[1][r][c]
                if m_mode == "and":
                    active = (a != bg) and (b != bg)
                elif m_mode == "or":
                    active = (a != bg) or (b != bg)
                else:
                    active = (a != bg) != (b != bg)
                if active:
                    out[r][c] = out_c
        return out
    return apply


# ---------------------------------------------------------------
#  grid_tile — output = input tiled in an NxM arrangement; N,M inferred.
# ---------------------------------------------------------------

def fit_grid_tile(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    tile_n: int | None = None
    tile_m: int | None = None
    for inp, out in pairs:
        ri, ci = _shape(inp)
        ro, co = _shape(out)
        if ro % ri or co % ci:
            return None
        n = ro // ri; m = co // ci
        if (n, m) == (1, 1):
            return None
        # Verify out is input tiled n x m
        ok = True
        for R in range(n):
            for C in range(m):
                for r in range(ri):
                    for c in range(ci):
                        if out[R * ri + r][C * ci + c] != inp[r][c]:
                            ok = False; break
                    if not ok: break
                if not ok: break
            if not ok: break
        if not ok:
            return None
        if tile_n is None:
            tile_n, tile_m = n, m
        elif (tile_n, tile_m) != (n, m):
            return None
    if tile_n is None or tile_m is None:
        return None
    n_fixed, m_fixed = tile_n, tile_m

    def apply(g: Grid) -> Grid:
        ri, ci = _shape(g)
        if ri * n_fixed > 30 or ci * m_fixed > 30:
            raise ValueError("grid_tile: exceeds ARC max grid")
        out = [[0] * (ci * m_fixed) for _ in range(ri * n_fixed)]
        for R in range(n_fixed):
            for C in range(m_fixed):
                for r in range(ri):
                    for c in range(ci):
                        out[R * ri + r][C * ci + c] = g[r][c]
        return out
    return apply


# ---------------------------------------------------------------
#  remove_isolated_or_keep_isolated — keep only cells whose 4-neighbours are bg (isolated).
# ---------------------------------------------------------------

def fit_keep_isolated(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    def op(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        out = [[bg] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == bg:
                    continue
                isolated = True
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                        isolated = False; break
                if isolated:
                    out[r][c] = g[r][c]
        return out
    any_change = False
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        if op([list(r) for r in inp]) != [list(r) for r in out]:
            return None
        if inp != out:
            any_change = True
    if not any_change:
        return None
    return op


def fit_remove_isolated(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    def op(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        out = [list(r) for r in g]
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == bg:
                    continue
                isolated = True
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                        isolated = False; break
                if isolated:
                    out[r][c] = bg
        return out
    any_change = False
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        if op([list(r) for r in inp]) != [list(r) for r in out]:
            return None
        if inp != out:
            any_change = True
    if not any_change:
        return None
    return op


# ---------------------------------------------------------------
#  draw_line_between_two_points — when input has exactly two non-bg
#  cells, output draws a line (h/v/diag) connecting them.
# ---------------------------------------------------------------

def fit_line_between_two_points(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if len(pairs) < 2:
        return None
    line_color_rule: str | None = None  # "preserve" only
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        rows, cols = _shape(inp)
        non_bg = [(r, c) for r in range(rows) for c in range(cols) if inp[r][c] != bg]
        if len(non_bg) != 2:
            return None
        (r1, c1), (r2, c2) = non_bg
        # Determine direction & line cells
        if r1 == r2:
            cells = [(r1, c) for c in range(min(c1, c2), max(c1, c2) + 1)]
        elif c1 == c2:
            cells = [(r, c1) for r in range(min(r1, r2), max(r1, r2) + 1)]
        elif abs(r1 - r2) == abs(c1 - c2):
            n = abs(r1 - r2)
            dr = 1 if r2 > r1 else -1
            dc = 1 if c2 > c1 else -1
            cells = [(r1 + dr * k, c1 + dc * k) for k in range(n + 1)]
        else:
            return None
        expected = [[bg] * cols for _ in range(rows)]
        # color = whichever non-bg is on the line; if both, use input's color at endpoints
        line_c1 = inp[r1][c1]; line_c2 = inp[r2][c2]
        for (r, c) in cells:
            expected[r][c] = inp[r][c] if inp[r][c] != bg else line_c1
        # Check
        if expected != [list(r) for r in out]:
            return None
        line_color_rule = "preserve"
    if line_color_rule is None:
        return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        non_bg = [(r, c) for r in range(rows) for c in range(cols) if g[r][c] != bg]
        if len(non_bg) != 2:
            raise ValueError("line_between: need exactly 2 non-bg cells")
        (r1, c1), (r2, c2) = non_bg
        if r1 == r2:
            cells = [(r1, c) for c in range(min(c1, c2), max(c1, c2) + 1)]
        elif c1 == c2:
            cells = [(r, c1) for r in range(min(r1, r2), max(r1, r2) + 1)]
        elif abs(r1 - r2) == abs(c1 - c2):
            n = abs(r1 - r2)
            dr = 1 if r2 > r1 else -1
            dc = 1 if c2 > c1 else -1
            cells = [(r1 + dr * k, c1 + dc * k) for k in range(n + 1)]
        else:
            raise ValueError("line_between: points not aligned")
        out = [[bg] * cols for _ in range(rows)]
        line_c1 = g[r1][c1]
        for (r, c) in cells:
            out[r][c] = g[r][c] if g[r][c] != bg else line_c1
        return out
    return apply


# ---------------------------------------------------------------
#  largest_component_to_color — largest non-bg component → fixed
#  color, others stay/erased.
# ---------------------------------------------------------------

def fit_largest_to_color(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    target: int | None = None
    erase_rest: bool | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        if not comps:
            return None
        biggest = max(comps, key=len)
        big_set = set(biggest)
        # Find color of biggest in out
        out_big_colors = {out[r][c] for r, c in biggest}
        if len(out_big_colors) != 1:
            return None
        out_big_color = next(iter(out_big_colors))
        if out_big_color == _comp_color(inp, biggest):
            return None  # no recolor of biggest → not this rule
        if target is None:
            target = out_big_color
        elif target != out_big_color:
            return None
        # Examine non-biggest cells
        rest_erased = True
        rest_preserved = True
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if (r, c) in big_set:
                    continue
                if v == bg:
                    if out[r][c] != bg:
                        rest_erased = rest_preserved = False
                else:
                    if out[r][c] != bg:
                        rest_erased = False
                    if out[r][c] != v:
                        rest_preserved = False
        if rest_erased and not rest_preserved:
            this_erase = True
        elif rest_preserved and not rest_erased:
            this_erase = False
        elif rest_erased and rest_preserved:
            this_erase = False  # nothing to disambiguate; prefer preserve
        else:
            return None
        if erase_rest is None:
            erase_rest = this_erase
        elif erase_rest != this_erase:
            return None
    if target is None or erase_rest is None:
        return None
    c_target, do_erase = target, erase_rest

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        if not comps:
            return [list(r) for r in g]
        biggest = max(comps, key=len)
        big = set(biggest)
        out = []
        for r, row in enumerate(g):
            new_row = []
            for c, v in enumerate(row):
                if (r, c) in big:
                    new_row.append(c_target)
                elif do_erase and v != bg:
                    new_row.append(bg)
                else:
                    new_row.append(v)
            out.append(new_row)
        return out
    return apply


# ---------------------------------------------------------------
#  output_shape_from_count — output is a 1xN or NxN grid where N is
#  the count of components. Color is the dominant fg color.
# ---------------------------------------------------------------

def fit_count_to_strip(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    # Output is 1xN of a single color, N = count of components.
    color: int | None = None
    orient: str | None = None
    if len(pairs) < 2:
        return None
    for inp, out in pairs:
        ri, ci = _shape(inp)
        ro, co = _shape(out)
        bg = _background(inp)
        comps = _components_4(inp, bg)
        n = len(comps)
        if n == 0:
            return None
        if (ro, co) == (1, n):
            this_orient = "h"
        elif (ro, co) == (n, 1):
            this_orient = "v"
        else:
            return None
        if orient is None:
            orient = this_orient
        elif orient != this_orient:
            return None
        out_colors = {out[r][c] for r in range(ro) for c in range(co) if out[r][c] != bg}
        if len(out_colors) != 1:
            return None
        c = next(iter(out_colors))
        if color is None:
            color = c
        elif color != c:
            return None
    if color is None or orient is None:
        return None
    c_fixed, o_fixed = color, orient

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        n = len(comps)
        if n == 0:
            raise ValueError("count_to_strip: no components")
        if o_fixed == "h":
            return [[c_fixed] * n]
        return [[c_fixed] for _ in range(n)]
    return apply


# ---------------------------------------------------------------
#  fill_inside_outline — closed loops in input → interior filled.
#  Subsumed by complete-bbox in some cases; this targets hollow shapes.
# ---------------------------------------------------------------

def fit_fill_hollow(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    def op(g: Grid) -> Grid:
        bg = _background(g)
        rows, cols = _shape(g)
        out = [list(r) for r in g]
        # Flood the OUTSIDE bg starting from border
        outside = [[False] * cols for _ in range(rows)]
        q = deque()
        for r in range(rows):
            for c in (0, cols - 1):
                if g[r][c] == bg:
                    outside[r][c] = True; q.append((r, c))
        for c in range(cols):
            for r in (0, rows - 1):
                if g[r][c] == bg and not outside[r][c]:
                    outside[r][c] = True; q.append((r, c))
        while q:
            r, c = q.popleft()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and not outside[nr][nc] and g[nr][nc] == bg:
                    outside[nr][nc] = True; q.append((nr, nc))
        # Interior bg cells: find the surrounding non-bg color
        for r in range(rows):
            for c in range(cols):
                if g[r][c] == bg and not outside[r][c]:
                    # Find a surrounding color (BFS to a non-bg cell)
                    neighbors = []
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                                neighbors.append(g[nr][nc])
                    if neighbors:
                        # Use most common neighbor color
                        out[r][c] = max(set(neighbors), key=neighbors.count)
        return out
    any_change = False
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        if op([list(r) for r in inp]) != [list(r) for r in out]:
            return None
        if inp != out:
            any_change = True
    if not any_change:
        return None
    return op


# ---------------------------------------------------------------
#  smallest_component_recolor — smallest non-bg component → inferred color.
# ---------------------------------------------------------------

def fit_smallest_recolor(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    target: int | None = None
    erase_rest: bool | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        if len(comps) < 2:
            return None
        smallest = min(comps, key=len)
        small_set = set(smallest)
        out_colors = {out[r][c] for r, c in smallest}
        if len(out_colors) != 1:
            return None
        out_color = next(iter(out_colors))
        if out_color == _comp_color(inp, smallest):
            return None
        if target is None:
            target = out_color
        elif target != out_color:
            return None
        # Rest behavior
        rest_erased = True; rest_preserved = True
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if (r, c) in small_set:
                    continue
                if v == bg:
                    if out[r][c] != bg:
                        rest_erased = rest_preserved = False
                else:
                    if out[r][c] != bg:
                        rest_erased = False
                    if out[r][c] != v:
                        rest_preserved = False
        if rest_erased and not rest_preserved:
            this_erase = True
        elif rest_preserved and not rest_erased:
            this_erase = False
        elif rest_erased and rest_preserved:
            this_erase = False
        else:
            return None
        if erase_rest is None:
            erase_rest = this_erase
        elif erase_rest != this_erase:
            return None
    if target is None or erase_rest is None:
        return None
    c_target, do_erase = target, erase_rest

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        if not comps:
            return [list(r) for r in g]
        smallest = min(comps, key=len)
        small = set(smallest)
        out = []
        for r, row in enumerate(g):
            new_row = []
            for c, v in enumerate(row):
                if (r, c) in small:
                    new_row.append(c_target)
                elif do_erase and v != bg:
                    new_row.append(bg)
                else:
                    new_row.append(v)
            out.append(new_row)
        return out
    return apply


# ---------------------------------------------------------------
#  Output shape is a count of components × something.
# ---------------------------------------------------------------

def fit_output_NxN_count(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Output is NxN where N = count of fg components; cells all one color."""
    if len(pairs) < 2:
        return None
    color: int | None = None
    for inp, out in pairs:
        bg = _background(inp)
        comps = _components_4(inp, bg)
        n = len(comps)
        ro, co = _shape(out)
        if (ro, co) != (n, n):
            return None
        out_colors = {out[r][c] for r in range(ro) for c in range(co) if out[r][c] != bg}
        if len(out_colors) > 1:
            return None
        # Could be all bg.
        c = next(iter(out_colors)) if out_colors else None
        if color is None:
            color = c
        elif color != c:
            return None
    if color is None:
        return None
    c_fixed = color

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        n = len(comps)
        if n == 0:
            raise ValueError("output_NxN_count: no components")
        return [[c_fixed] * n for _ in range(n)]
    return apply


# ---------------------------------------------------------------
#  keep_unique_color_component — keep the component whose color
#  appears exactly once across all components.
# ---------------------------------------------------------------

def fit_keep_unique_color_component(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Many ARC tasks: one component has a unique color; that's the answer."""
    if len(pairs) < 2:
        return None
    erase_rest = True  # require this variant
    keep_color_or_unique: str | None = None  # tracking only
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        if len(comps) < 2:
            return None
        # Count color occurrences across components
        comp_colors = [_comp_color(inp, c) for c in comps]
        counts: dict[int, int] = {}
        for cc in comp_colors:
            counts[cc] = counts.get(cc, 0) + 1
        unique_colors = [c for c, n in counts.items() if n == 1]
        if len(unique_colors) != 1:
            return None
        uc = unique_colors[0]
        # The unique-colored component(s) must be preserved
        kept_idx = [i for i, c in enumerate(comp_colors) if c == uc]
        kept_set = set()
        for i in kept_idx:
            kept_set.update(comps[i])
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if (r, c) in kept_set:
                    if out[r][c] != v:
                        return None
                else:
                    if out[r][c] != bg:
                        return None
        keep_color_or_unique = "unique"
    if keep_color_or_unique is None:
        return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        if not comps:
            return [list(r) for r in g]
        comp_colors = [_comp_color(g, c) for c in comps]
        counts: dict[int, int] = {}
        for cc in comp_colors:
            counts[cc] = counts.get(cc, 0) + 1
        unique_colors = [c for c, n in counts.items() if n == 1]
        if len(unique_colors) != 1:
            raise ValueError("keep_unique_color: no/multi unique colors in test")
        uc = unique_colors[0]
        kept_idx = [i for i, c in enumerate(comp_colors) if c == uc]
        kept = set()
        for i in kept_idx:
            kept.update(comps[i])
        return [[g[r][c] if (r, c) in kept else bg for c in range(_shape(g)[1])]
                for r in range(_shape(g)[0])]
    return apply


# ---------------------------------------------------------------
#  recolor_smallest_to_uniquecolor — smallest gets recolored to the
#  one color not currently in palette. Subsumes some classification tasks.
# ---------------------------------------------------------------

# ---------------------------------------------------------------
#  scale_n — every pixel becomes an N×N block. N inferred.
# ---------------------------------------------------------------

def fit_scale_n(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    n: int | None = None
    for inp, out in pairs:
        ri, ci = _shape(inp)
        ro, co = _shape(out)
        if ri == 0 or ci == 0 or ro % ri or co % ci:
            return None
        scale_r = ro // ri; scale_c = co // ci
        if scale_r != scale_c or scale_r < 2:
            return None
        for r in range(ri):
            for c in range(ci):
                v = inp[r][c]
                for dr in range(scale_r):
                    for dc in range(scale_r):
                        if out[r * scale_r + dr][c * scale_r + dc] != v:
                            return None
        if n is None:
            n = scale_r
        elif n != scale_r:
            return None
    if n is None:
        return None
    n_fixed = n

    def apply(g: Grid) -> Grid:
        ri, ci = _shape(g)
        if ri * n_fixed > 30 or ci * n_fixed > 30:
            raise ValueError("scale_n: exceeds ARC max")
        out = [[0] * (ci * n_fixed) for _ in range(ri * n_fixed)]
        for r in range(ri):
            for c in range(ci):
                v = g[r][c]
                for dr in range(n_fixed):
                    for dc in range(n_fixed):
                        out[r * n_fixed + dr][c * n_fixed + dc] = v
        return out
    return apply


def fit_tile_NxM(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    n: int | None = None
    m: int | None = None
    for inp, out in pairs:
        ri, ci = _shape(inp)
        ro, co = _shape(out)
        if ri == 0 or ci == 0 or ro % ri or co % ci:
            return None
        N = ro // ri; M = co // ci
        if (N, M) == (1, 1):
            return None
        for R in range(N):
            for C in range(M):
                for r in range(ri):
                    for c in range(ci):
                        if out[R * ri + r][C * ci + c] != inp[r][c]:
                            return None
        if n is None:
            n, m = N, M
        elif (n, m) != (N, M):
            return None
    if n is None or m is None:
        return None
    n_fixed, m_fixed = n, m

    def apply(g: Grid) -> Grid:
        ri, ci = _shape(g)
        if ri * n_fixed > 30 or ci * m_fixed > 30:
            raise ValueError("tile_NxM: exceeds ARC max")
        out = [[0] * (ci * m_fixed) for _ in range(ri * n_fixed)]
        for R in range(n_fixed):
            for C in range(m_fixed):
                for r in range(ri):
                    for c in range(ci):
                        out[R * ri + r][C * ci + c] = g[r][c]
        return out
    return apply


def fit_recolor_largest_keep_rest(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Like largest_to_color but preserves other components instead of erasing."""
    target: int | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        if not comps:
            return None
        biggest = max(comps, key=len)
        out_colors = {out[r][c] for r, c in biggest}
        if len(out_colors) != 1:
            return None
        out_color = next(iter(out_colors))
        if out_color == _comp_color(inp, biggest):
            return None
        if target is None:
            target = out_color
        elif target != out_color:
            return None
        big = set(biggest)
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if (r, c) in big:
                    continue
                if out[r][c] != v:
                    return None
    if target is None:
        return None
    c_target = target

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        if not comps:
            return [list(r) for r in g]
        biggest = max(comps, key=len)
        big = set(biggest)
        return [[c_target if (r, c) in big else g[r][c]
                 for c in range(_shape(g)[1])] for r in range(_shape(g)[0])]
    return apply


# ---------------------------------------------------------------
#  classify_by_count_components — output is 1×1; color depends on
#  the number of 4-connected non-bg components in input.
# ---------------------------------------------------------------

def fit_classify_by_count_components(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if len(pairs) < 3:
        return None
    mapping: dict[int, int] = {}
    for inp, out in pairs:
        if _shape(out) != (1, 1):
            return None
        bg = _background(inp)
        n = len(_components_4(inp, bg))
        c = out[0][0]
        if n in mapping and mapping[n] != c:
            return None
        mapping[n] = c
    if len(mapping) < 2:
        return None
    m = dict(mapping)

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        n = len(_components_4(g, bg))
        if n not in m:
            raise ValueError(
                f"classify_by_count_components: count {n} not in trained mapping; abstain"
            )
        return [[m[n]]]
    return apply


# ---------------------------------------------------------------
#  classify_by_palette_size — output is 1×1 by distinct-color count.
# ---------------------------------------------------------------

def fit_classify_by_palette_size(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if len(pairs) < 3:
        return None
    mapping: dict[int, int] = {}
    for inp, out in pairs:
        if _shape(out) != (1, 1):
            return None
        n = len(set(_flat(inp)))
        c = out[0][0]
        if n in mapping and mapping[n] != c:
            return None
        mapping[n] = c
    if len(mapping) < 2:
        return None
    m = dict(mapping)

    def apply(g: Grid) -> Grid:
        n = len(set(_flat(g)))
        if n not in m:
            raise ValueError(
                f"classify_by_palette_size: count {n} not in trained mapping; abstain"
            )
        return [[m[n]]]
    return apply


# ---------------------------------------------------------------
#  classify_by_symmetry — output 1×1; color depends on which symmetries hold.
# ---------------------------------------------------------------

def fit_classify_by_symmetry(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    if len(pairs) < 3:
        return None
    mapping: dict[tuple[bool, bool], int] = {}
    for inp, out in pairs:
        if _shape(out) != (1, 1):
            return None
        rows = len(inp); cols = len(inp[0]) if rows else 0
        h = all(inp[r] == list(reversed(inp[r])) for r in range(rows))
        v = inp[: rows // 2] == [list(r) for r in reversed(inp)][: rows // 2]
        key = (h, v)
        c = out[0][0]
        if key in mapping and mapping[key] != c:
            return None
        mapping[key] = c
    if len(mapping) < 2:
        return None
    m = dict(mapping)

    def apply(g: Grid) -> Grid:
        rows = len(g); cols = len(g[0]) if rows else 0
        h = all(g[r] == list(reversed(g[r])) for r in range(rows))
        v = g[: rows // 2] == [list(r) for r in reversed(g)][: rows // 2]
        key = (h, v)
        if key not in m:
            raise ValueError(
                f"classify_by_symmetry: ({h},{v}) not in trained mapping; abstain"
            )
        return [[m[key]]]
    return apply


# ---------------------------------------------------------------
#  each_component_recolor_by_size — small/medium/large → different colors.
# ---------------------------------------------------------------

def fit_each_component_by_size_class(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Each component is recolored based on its size class (small/medium/large).

    Class buckets: small (1-2 cells), medium (3-5), large (6+).
    The size→color mapping is inferred from training.
    """
    if len(pairs) < 2:
        return None
    mapping: dict[str, int] = {}

    def size_class(n: int) -> str:
        if n <= 2:
            return "small"
        if n <= 5:
            return "medium"
        return "large"

    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        comps = _components_4(inp, bg)
        if not comps:
            return None
        for comp in comps:
            cls = size_class(len(comp))
            out_colors = {out[r][c] for r, c in comp}
            if len(out_colors) != 1:
                return None
            c = next(iter(out_colors))
            if cls in mapping:
                if mapping[cls] != c:
                    return None
            else:
                mapping[cls] = c
        # Background cells must stay bg
        big_set: set[tuple[int, int]] = set()
        for comp in comps:
            big_set.update(comp)
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if (r, c) not in big_set and out[r][c] != bg:
                    return None
    if len(mapping) < 2:
        return None  # not enough size classes to claim
    m = dict(mapping)

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        comps = _components_4(g, bg)
        out = [[bg] * len(g[0]) for _ in g]
        for comp in comps:
            cls = size_class(len(comp))
            if cls not in m:
                raise ValueError(
                    f"each_component_by_size_class: class {cls!r} not in mapping"
                )
            color = m[cls]
            for r, c in comp:
                out[r][c] = color
        return out
    return apply


# ---------------------------------------------------------------
#  draw_diagonal_from_marker — extend each marker's color along its diagonal.
# ---------------------------------------------------------------

def fit_extend_diagonals(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Each non-bg cell extends a diagonal of its color across the grid."""
    if len(pairs) < 2:
        return None
    direction: str | None = None  # 'both', 'down_right', etc.

    def extend(g: Grid, mode: str) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        out = [list(r) for r in g]
        for r in range(rows):
            for c in range(cols):
                v = g[r][c]
                if v == bg:
                    continue
                paths = []
                if mode in ("both", "down_right"):
                    paths.append((1, 1))
                if mode in ("both", "down_left"):
                    paths.append((1, -1))
                if mode in ("both", "up_right"):
                    paths.append((-1, 1))
                if mode in ("both", "up_left"):
                    paths.append((-1, -1))
                for dr, dc in paths:
                    nr, nc = r + dr, c + dc
                    while 0 <= nr < rows and 0 <= nc < cols:
                        if out[nr][nc] == bg:
                            out[nr][nc] = v
                        nr += dr; nc += dc
        return out

    for mode in ("both", "down_right", "down_left", "up_right", "up_left"):
        ok = True
        for inp, out in pairs:
            if _shape(inp) != _shape(out):
                ok = False; break
            if extend([list(r) for r in inp], mode) != [list(r) for r in out]:
                ok = False; break
        if ok:
            direction = mode
            break
    if direction is None:
        return None
    mode_fixed = direction

    def apply(g: Grid) -> Grid:
        return extend([list(r) for r in g], mode_fixed)
    return apply


# ---------------------------------------------------------------
#  replace_with_marker_color — output is input where every non-bg
#  cell takes the color of a designated marker cell.
# ---------------------------------------------------------------

def fit_unify_to_marker_color(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """If a single cell has a unique color in input, all other fg cells
    are recolored to that unique color in output.
    """
    if len(pairs) < 2:
        return None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        flat_in = _flat(inp)
        counts: dict[int, int] = {}
        for v in flat_in:
            counts[v] = counts.get(v, 0) + 1
        unique_colors = [c for c, n in counts.items() if n == 1 and c != bg]
        if len(unique_colors) != 1:
            return None
        marker = unique_colors[0]
        for r, row in enumerate(inp):
            for c, v in enumerate(row):
                if v == bg:
                    if out[r][c] != bg:
                        return None
                elif out[r][c] != marker:
                    return None

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        flat = _flat(g)
        counts: dict[int, int] = {}
        for v in flat:
            counts[v] = counts.get(v, 0) + 1
        unique_colors = [c for c, n in counts.items() if n == 1 and c != bg]
        if len(unique_colors) != 1:
            raise ValueError("unify_to_marker_color: no unique marker")
        marker = unique_colors[0]
        return [[marker if v != bg else bg for v in row] for row in g]
    return apply


# ---------------------------------------------------------------
#  move_objects_by_offset — translate all non-bg cells by a fixed (dr, dc).
# ---------------------------------------------------------------

def fit_move_objects(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """All non-bg cells translate by the same (dr, dc); bg fills the rest."""
    if not pairs:
        return None
    offset: tuple[int, int] | None = None
    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        bg = _background(inp)
        in_cells = [(r, c, v) for r, row in enumerate(inp)
                    for c, v in enumerate(row) if v != bg]
        out_cells = [(r, c, v) for r, row in enumerate(out)
                     for c, v in enumerate(row) if v != bg]
        if len(in_cells) != len(out_cells):
            return None
        if not in_cells:
            continue
        # Group by color and sort, then check uniform offset.
        in_sorted = sorted(in_cells, key=lambda x: (x[2], x[0], x[1]))
        out_sorted = sorted(out_cells, key=lambda x: (x[2], x[0], x[1]))
        if [v for *_, v in in_sorted] != [v for *_, v in out_sorted]:
            return None
        diffs = [(o[0] - i[0], o[1] - i[1]) for i, o in zip(in_sorted, out_sorted)]
        if len(set(diffs)) != 1:
            return None
        d = diffs[0]
        if offset is None:
            offset = d
        elif offset != d:
            return None
    if offset is None or offset == (0, 0):
        return None
    dr, dc = offset

    def apply(g: Grid) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        out = [[bg] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                v = g[r][c]
                if v == bg:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    out[nr][nc] = v
        return out
    return apply


# ---------------------------------------------------------------
#  reflect_about_marker_axis — input has a marker line; output reflects
#  the rest of the input across that line.
# ---------------------------------------------------------------

def fit_reflect_about_axis(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Detect a constant-color row or column, reflect about it."""
    axis_color: int | None = None
    axis_kind: str | None = None  # 'row' or 'col'

    def reflect(g: Grid, axis_c: int, kind: str) -> Grid:
        rows, cols = _shape(g)
        bg = _background(g)
        out = [list(r) for r in g]
        if kind == "row":
            row_idx = next((r for r in range(rows)
                            if all(g[r][c] == axis_c for c in range(cols))), None)
            if row_idx is None:
                return out
            for r in range(rows):
                if r == row_idx:
                    continue
                mirror_r = 2 * row_idx - r
                if 0 <= mirror_r < rows and out[mirror_r] == [bg] * cols:
                    out[mirror_r] = list(g[r])
        else:  # col
            col_idx = next((c for c in range(cols)
                            if all(g[r][c] == axis_c for r in range(rows))), None)
            if col_idx is None:
                return out
            for c in range(cols):
                if c == col_idx:
                    continue
                mirror_c = 2 * col_idx - c
                for r in range(rows):
                    if 0 <= mirror_c < cols and out[r][mirror_c] == bg:
                        out[r][mirror_c] = g[r][c]
        return out

    for inp, out in pairs:
        if _shape(inp) != _shape(out):
            return None
        rows, cols = _shape(inp)
        # Find a row that's constant non-bg
        bg = _background(inp)
        row_axis = next(((r, inp[r][0]) for r in range(rows)
                         if len(set(inp[r])) == 1 and inp[r][0] != bg), None)
        col_axis = next(((c, inp[0][c]) for c in range(cols)
                         if len(set(inp[r][c] for r in range(rows))) == 1
                         and inp[0][c] != bg), None)
        if row_axis is None and col_axis is None:
            return None
        for kind, axis in (("row", row_axis), ("col", col_axis)):
            if axis is None:
                continue
            _, color = axis
            if reflect([list(r) for r in inp], color, kind) == [list(r) for r in out]:
                if axis_color is None:
                    axis_color, axis_kind = color, kind
                    break
                elif (axis_color, axis_kind) == (color, kind):
                    break
                else:
                    return None
        else:
            return None
    if axis_color is None or axis_kind is None:
        return None
    c_fixed, k_fixed = axis_color, axis_kind

    def apply(g: Grid) -> Grid:
        return reflect([list(r) for r in g], c_fixed, k_fixed)
    return apply


# ---------------------------------------------------------------
#  one_object_per_row_palette — output is a row palette where each
#  cell color reflects whether that row had ≥1 non-bg cell.
# ---------------------------------------------------------------

def fit_row_presence_strip(pairs: list[tuple[Grid, Grid]]) -> Callable | None:
    """Output is 1xN where N = #rows; cell c = inferred presence color."""
    if len(pairs) < 2:
        return None
    on_color: int | None = None; off_color: int | None = None
    for inp, out in pairs:
        rows = len(inp)
        if _shape(out) != (1, rows):
            return None
        bg = _background(inp)
        for r in range(rows):
            present = any(v != bg for v in inp[r])
            target = out[0][r]
            if present:
                if on_color is None:
                    on_color = target
                elif on_color != target:
                    return None
            else:
                if off_color is None:
                    off_color = target
                elif off_color != target:
                    return None
    if on_color is None:
        return None
    on = on_color; off = off_color if off_color is not None else 0

    def apply(g: Grid) -> Grid:
        bg = _background(g)
        return [[on if any(v != bg for v in g[r]) else off for r in range(len(g))]]
    return apply


FITTERS: list[tuple[str, Callable[[list[tuple[Grid, Grid]]], Callable | None]]] = [
    ("move_objects",              fit_move_objects),
    ("reflect_about_axis",        fit_reflect_about_axis),
    ("row_presence_strip",        fit_row_presence_strip),
    ("each_component_by_size_class", fit_each_component_by_size_class),
    ("extend_diagonals",          fit_extend_diagonals),
    ("unify_to_marker_color",     fit_unify_to_marker_color),
    ("classify_by_count_components", fit_classify_by_count_components),
    ("classify_by_palette_size",  fit_classify_by_palette_size),
    ("classify_by_symmetry",      fit_classify_by_symmetry),
    ("color_permutation",         fit_color_permutation),
    ("swap_two_colors",           fit_swap_two_colors),
    ("recolor_constant",          fit_recolor_constant),
    ("per_component_recolor",     fit_per_component_recolor),
    ("keep_components_of_color",  fit_keep_components_of_color),
    ("recolor_by_size_rank",      fit_recolor_by_size_rank),
    ("largest_to_color",          fit_largest_to_color),
    ("recolor_largest_keep_rest", fit_recolor_largest_keep_rest),
    ("smallest_recolor",          fit_smallest_recolor),
    ("keep_unique_color_component", fit_keep_unique_color_component),
    ("output_NxN_count",          fit_output_NxN_count),
    ("outline_objects",           fit_outline_objects),
    ("fill_components_to_bbox",   fit_fill_components_to_bbox),
    ("fill_hollow",               fit_fill_hollow),
    ("grow_components_by_1",      fit_grow_components_by_1),
    ("keep_isolated",             fit_keep_isolated),
    ("remove_isolated",           fit_remove_isolated),
    ("shift",                     fit_shift),
    ("bbox_of_nonbg",             fit_bbox_of_nonbg),
    ("pad_with_color",            fit_pad_with_color),
    ("extract_neighborhood",      fit_extract_neighborhood),
    ("periodic_complete",         fit_periodic_complete),
    ("each_cell_repeated_input",  fit_each_cell_repeated_input),
    ("scale_n",                   fit_scale_n),
    ("tile_NxM",                  fit_tile_NxM),
    ("grid_tile",                 fit_grid_tile),
    ("line_between_two_points",   fit_line_between_two_points),
    ("count_to_strip",            fit_count_to_strip),
    ("overlay_halves",            fit_overlay_halves),
    ("template_classify",         fit_template_classify),
    ("fixed_output",              fit_fixed_output),
]


SCRIPTURAL_NAMES: dict[str, str] = {
    "move_objects":              "passage",
    "reflect_about_axis":        "mirror",
    "row_presence_strip":        "witness",
    "each_component_by_size_class": "ordering",
    "extend_diagonals":          "way",
    "unify_to_marker_color":     "naming",
    "classify_by_count_components": "counting",
    "classify_by_palette_size":  "counting",
    "classify_by_symmetry":      "judge",
    "color_permutation":         "renaming",
    "swap_two_colors":           "exchange",
    "recolor_constant":          "name",
    "per_component_recolor":     "renaming",
    "keep_components_of_color":  "winnow",
    "recolor_by_size_rank":      "ordering",
    "outline_objects":           "boundary",
    "fill_components_to_bbox":   "filling",
    "grow_components_by_1":      "increase",
    "keep_isolated":             "remnant",
    "remove_isolated":           "winnow",
    "shift":                     "passage",
    "bbox_of_nonbg":             "remnant",
    "pad_with_color":            "covering",
    "extract_neighborhood":      "set_apart",
    "periodic_complete":         "restoration",
    "each_cell_repeated_input":  "image_in_image",
    "scale_n":                   "multiply",
    "tile_NxM":                  "multiply",
    "grid_tile":                 "multiply",
    "overlay_halves":            "witness",
    "template_classify":         "judge",
    "largest_to_color":          "naming",
    "recolor_largest_keep_rest": "anointing",
    "smallest_recolor":          "least",
    "keep_unique_color_component": "elect",
    "output_NxN_count":          "counting",
    "fill_hollow":               "filling",
    "line_between_two_points":   "joining",
    "count_to_strip":            "counting",
    "fixed_output":              "decree",
}
