"""ARC primitives. Each is a pure function Grid -> Grid.

Selection discipline (in adapter.py): a primitive — atomic or composed —
is chosen for a task only if it *exactly* reproduces every training
output from its input. ARC scores exact match.

Kernel citation: P₁ (measure honestly), T 2.4 (receive the rule).
"""
from __future__ import annotations
from collections import deque
from typing import Callable

Grid = list[list[int]]


# ---------------------------------------------------------------
#  Atomic primitives
# ---------------------------------------------------------------

def identity(g: Grid) -> Grid:
    return [list(r) for r in g]


def flip_h(g: Grid) -> Grid:
    return [list(reversed(r)) for r in g]


def flip_v(g: Grid) -> Grid:
    return [list(r) for r in reversed(g)]


def rotate_90(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    return [[g[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]


def rotate_180(g: Grid) -> Grid:
    return flip_h(flip_v(g))


def rotate_270(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    return [[g[r][cols - 1 - c] for r in range(rows)] for c in range(cols)]


def transpose(g: Grid) -> Grid:
    if not g:
        return []
    return [[g[r][c] for r in range(len(g))] for c in range(len(g[0]))]


def anti_transpose(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    return [[g[rows - 1 - r][cols - 1 - c] for r in range(rows)] for c in range(cols)]


_MAX = 30  # ARC grids are at most 30x30


def scale_2x(g: Grid) -> Grid:
    if not g or len(g) * 2 > _MAX or len(g[0]) * 2 > _MAX:
        raise ValueError("scale_2x exceeds ARC max grid size")
    out: Grid = []
    for r in g:
        line = [v for v in r for _ in range(2)]
        out.append(list(line)); out.append(list(line))
    return out


def scale_3x(g: Grid) -> Grid:
    if not g or len(g) * 3 > _MAX or len(g[0]) * 3 > _MAX:
        raise ValueError("scale_3x exceeds ARC max grid size")
    out: Grid = []
    for r in g:
        line = [v for v in r for _ in range(3)]
        out.append(list(line)); out.append(list(line)); out.append(list(line))
    return out


def tile_self(g: Grid) -> Grid:
    """Each non-zero cell at (R,C) places a copy of g at block (R,C)."""
    rows, cols = len(g), len(g[0]) if g else 0
    # ARC grids cap at 30x30. tile_self produces rows*rows × cols*cols.
    # Skip if the output would exceed 30x30.
    if rows * rows > 30 or cols * cols > 30:
        raise ValueError("tile_self output exceeds ARC max grid size")
    out: Grid = [[0] * (cols * cols) for _ in range(rows * rows)]
    for R in range(rows):
        for C in range(cols):
            if g[R][C] != 0:
                for r in range(rows):
                    for c in range(cols):
                        out[R * rows + r][C * cols + c] = g[r][c]
    return out


def tile_2x2(g: Grid) -> Grid:
    if not g or len(g) * 2 > _MAX or len(g[0]) * 2 > _MAX:
        raise ValueError("tile_2x2 exceeds ARC max grid size")
    return [list(r) + list(r) for r in g] + [list(r) + list(r) for r in g]


def tile_3x3(g: Grid) -> Grid:
    if not g or len(g) * 3 > _MAX or len(g[0]) * 3 > _MAX:
        raise ValueError("tile_3x3 exceeds ARC max grid size")
    triple = [list(r) + list(r) + list(r) for r in g]
    return triple + triple + triple


# ---------------------------------------------------------------
#  Mirror-stacking primitives — output is input concatenated with
#  its own flip in one of four directions.
# ---------------------------------------------------------------

def mirror_right(g: Grid) -> Grid:
    """g | flip_h(g)  (concat horizontally with horizontal mirror)."""
    if not g or len(g[0]) * 2 > _MAX:
        raise ValueError("mirror_right exceeds ARC max grid size")
    return [list(r) + list(reversed(r)) for r in g]


def mirror_left(g: Grid) -> Grid:
    if not g or len(g[0]) * 2 > _MAX:
        raise ValueError("mirror_left exceeds ARC max grid size")
    return [list(reversed(r)) + list(r) for r in g]


def mirror_below(g: Grid) -> Grid:
    if not g or len(g) * 2 > _MAX:
        raise ValueError("mirror_below exceeds ARC max grid size")
    return [list(r) for r in g] + [list(r) for r in reversed(g)]


def mirror_above(g: Grid) -> Grid:
    if not g or len(g) * 2 > _MAX:
        raise ValueError("mirror_above exceeds ARC max grid size")
    return [list(r) for r in reversed(g)] + [list(r) for r in g]


def stack_below(g: Grid) -> Grid:
    """g / g (vertical concat with self)."""
    if not g or len(g) * 2 > _MAX:
        raise ValueError("stack_below exceeds ARC max grid size")
    return [list(r) for r in g] + [list(r) for r in g]


def stack_right(g: Grid) -> Grid:
    if not g or len(g[0]) * 2 > _MAX:
        raise ValueError("stack_right exceeds ARC max grid size")
    return [list(r) + list(r) for r in g]


# ---------------------------------------------------------------
#  Deduplicate consecutive rows/cols.
# ---------------------------------------------------------------

def dedup_rows(g: Grid) -> Grid:
    if not g:
        return []
    out = [list(g[0])]
    for r in g[1:]:
        if list(r) != out[-1]:
            out.append(list(r))
    return out


def dedup_cols(g: Grid) -> Grid:
    if not g:
        return []
    cols = list(zip(*g))
    out_cols = [list(cols[0])]
    for c in cols[1:]:
        if list(c) != out_cols[-1]:
            out_cols.append(list(c))
    return [list(row) for row in zip(*out_cols)]


# ---------------------------------------------------------------
#  Unique values per row / col (collapsed).
# ---------------------------------------------------------------

def unique_per_row(g: Grid) -> Grid:
    """Each row → its unique values in order of first appearance."""
    out = []
    for row in g:
        seen: list[int] = []
        for v in row:
            if v not in seen:
                seen.append(v)
        out.append(seen)
    # Pad to common width
    w = max((len(r) for r in out), default=0)
    return [r + [0] * (w - len(r)) for r in out]


# ---------------------------------------------------------------
#  Negate (every non-bg → 0, every bg → 1) — for simple binary tasks.
# ---------------------------------------------------------------

def negate_binary(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    fg_set = set(flat) - {bg}
    if len(fg_set) != 1:
        raise ValueError("negate_binary: requires exactly one fg color")
    fg = next(iter(fg_set))
    return [[bg if v == fg else fg for v in row] for row in g]


def quad_mirror(g: Grid) -> Grid:
    """Output is 2x2 of g: g | flip_h(g) over flip_v(g) | rotate_180(g)."""
    if not g or len(g) * 2 > _MAX or len(g[0]) * 2 > _MAX:
        raise ValueError("quad_mirror exceeds ARC max grid size")
    top = mirror_right(g)
    bot = mirror_right(flip_v(g))
    return [list(r) for r in top] + [list(r) for r in bot]


def quad_mirror_alt(g: Grid) -> Grid:
    """g and its 3 reflections, mirrored to form a 2x2 quad-symmetric tile."""
    if not g or len(g) * 2 > _MAX or len(g[0]) * 2 > _MAX:
        raise ValueError("quad_mirror_alt exceeds ARC max grid size")
    top = [row + list(reversed(row)) for row in g]
    bot = [row + list(reversed(row)) for row in reversed(g)]
    return top + bot


def fold_horizontal(g: Grid) -> Grid:
    """Fold left half over right (OR of non-bg)."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    half = cols // 2
    out = [list(row[:half]) for row in g]
    for r in range(rows):
        for c in range(half):
            mirror_c = cols - 1 - c
            if g[r][mirror_c] != bg:
                out[r][c] = g[r][mirror_c] if g[r][c] == bg else out[r][c]
    return out


def fold_vertical(g: Grid) -> Grid:
    if not g:
        return []
    rows = len(g)
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    half = rows // 2
    out = [list(g[r]) for r in range(half)]
    for r in range(half):
        for c in range(len(g[0])):
            mirror_r = rows - 1 - r
            if g[mirror_r][c] != bg:
                if out[r][c] == bg:
                    out[r][c] = g[mirror_r][c]
    return out


def diag_main_extend(g: Grid) -> Grid:
    """If input has ≥1 marker on/near main diagonal, fill diagonal with its color.

    Strict: refuse if no marker is on the diagonal.
    """
    if not g:
        raise ValueError("diag_main_extend: empty")
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    diag_cells = [(i, i) for i in range(min(rows, cols))]
    diag_colors = {g[r][c] for r, c in diag_cells if g[r][c] != bg}
    if len(diag_colors) != 1:
        raise ValueError("diag_main_extend: needs exactly one diagonal color")
    color = next(iter(diag_colors))
    # Require that no other non-bg cells exist (otherwise this is too eager).
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != bg and (r, c) not in set(diag_cells):
                raise ValueError("diag_main_extend: extra non-diagonal fg cells")
    out = [list(r) for r in g]
    for r, c in diag_cells:
        out[r][c] = color
    return out


def fill_diagonals_from_marker(g: Grid) -> Grid:
    """For each non-bg cell, draw a diagonal line of that color across grid.

    Used by tasks like 05269061 where a sparse diagonal pattern is extended.
    Strict: requires every input non-bg cell to fit the (r+c) mod N rule;
    aborts (raises) on inconsistency rather than returning identity.
    """
    if not g:
        raise ValueError("fill_diagonals_from_marker: empty grid")
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    palette = [v for v in set(flat) if v != bg]
    if len(palette) < 2:
        raise ValueError("fill_diagonals_from_marker: needs ≥2 fg colors")
    classes: dict[int, int] = {}
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != bg:
                k = (r + c) % len(palette)
                if k in classes and classes[k] != g[r][c]:
                    raise ValueError(
                        "fill_diagonals_from_marker: inconsistent diagonal class"
                    )
                classes[k] = g[r][c]
    if len(classes) != len(palette):
        raise ValueError(
            "fill_diagonals_from_marker: not all classes determined"
        )
    out = [list(r) for r in g]
    for r in range(rows):
        for c in range(cols):
            if out[r][c] == bg:
                k = (r + c) % len(palette)
                out[r][c] = classes[k]
    return out


def each_row_unique(g: Grid) -> Grid:
    """Each row → its sorted unique values (palette per row)."""
    out = []
    for row in g:
        u = sorted(set(row))
        out.append(u)
    w = max((len(r) for r in out), default=0)
    return [r + [0] * (w - len(r)) for r in out]


def majority_per_component(g: Grid) -> Grid:
    """Each 4-conn component becomes its dominant color (already its color, so identity).

    Useful only with `LIBRARY`-level color recolor primitives — placeholder for future.
    """
    return [list(r) for r in g]


def first_nonbg_per_row(g: Grid) -> Grid:
    """Replace each row with [first_nonbg, second_nonbg, ...]; collapsed left."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = []
    for row in g:
        nb = [v for v in row if v != bg]
        out.append(nb)
    w = max((len(r) for r in out), default=0)
    return [r + [bg] * (w - len(r)) for r in out]


def replace_bg_with_largest_color(g: Grid) -> Grid:
    if not g:
        raise ValueError("replace_bg_with_largest_color: empty")
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        raise ValueError("replace_bg_with_largest_color: no fg")
    target = max(set(nonbg), key=nonbg.count)
    return [[target if v == bg else v for v in row] for row in g]


def hollow_rect_border(g: Grid) -> Grid:
    """Convert g to a hollow rectangle outline of size and color preserved."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    fg_set = set(flat) - {bg}
    if len(fg_set) != 1:
        raise ValueError("hollow_rect_border: needs single fg")
    fg = next(iter(fg_set))
    out = [[bg] * cols for _ in range(rows)]
    for c in range(cols):
        out[0][c] = fg; out[rows - 1][c] = fg
    for r in range(rows):
        out[r][0] = fg; out[r][cols - 1] = fg
    return out


def draw_grid_border(g: Grid) -> Grid:
    """Draw an outer border of the dominant fg color around bg-only grid."""
    return hollow_rect_border(g)


def half_height_top(g: Grid) -> Grid:
    if not g:
        return []
    h = len(g) // 2
    if h < 1:
        raise ValueError("half_height_top: too small")
    return [list(r) for r in g[:h]]


def half_height_bot(g: Grid) -> Grid:
    if not g:
        return []
    h = len(g) // 2
    if h < 1:
        raise ValueError("half_height_bot: too small")
    return [list(r) for r in g[-h:]]


def half_width_left(g: Grid) -> Grid:
    if not g or not g[0]:
        return []
    w = len(g[0]) // 2
    if w < 1:
        raise ValueError("half_width_left: too small")
    return [list(r[:w]) for r in g]


def half_width_right(g: Grid) -> Grid:
    if not g or not g[0]:
        return []
    w = len(g[0]) // 2
    if w < 1:
        raise ValueError("half_width_right: too small")
    return [list(r[-w:]) for r in g]


def top_third(g: Grid) -> Grid:
    if not g:
        return []
    h = len(g) // 3
    if h < 1:
        raise ValueError("top_third: too small")
    return [list(r) for r in g[:h]]


def bottom_third(g: Grid) -> Grid:
    if not g:
        return []
    h = len(g) // 3
    if h < 1:
        raise ValueError("bottom_third: too small")
    return [list(r) for r in g[-h:]]


def diagonal_quad(g: Grid) -> Grid:
    """Output: 2x2 of g with each quadrant flipped to create 8-way symmetry."""
    if not g or len(g) * 2 > _MAX or len(g[0]) * 2 > _MAX:
        raise ValueError("diagonal_quad: too large")
    return [row + list(reversed(row)) for row in g] + \
           [row + list(reversed(row)) for row in reversed(g)]


def top_row_extract(g: Grid) -> Grid:
    if not g:
        return []
    return [list(g[0])]


def bottom_row_extract(g: Grid) -> Grid:
    if not g:
        return []
    return [list(g[-1])]


def left_col_extract(g: Grid) -> Grid:
    if not g:
        return []
    return [[r[0]] for r in g]


def right_col_extract(g: Grid) -> Grid:
    if not g:
        return []
    return [[r[-1]] for r in g]


def shift_right_1(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    return [[bg] + list(r[:-1]) for r in g]


def shift_left_1(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    return [list(r[1:]) + [bg] for r in g]


def shift_up_1(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    return [list(r) for r in g[1:]] + [[bg] * len(g[0])]


def shift_down_1(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    return [[bg] * len(g[0])] + [list(r) for r in g[:-1]]


def row_majority(g: Grid) -> Grid:
    """Each row becomes a solid row of its most common color."""
    if not g:
        return []
    out = []
    for row in g:
        c = max(set(row), key=row.count)
        out.append([c] * len(row))
    return out


def col_majority(g: Grid) -> Grid:
    if not g:
        return []
    return transpose(row_majority(transpose(g)))


def erase_singletons(g: Grid) -> Grid:
    """Remove cells with no same-color 4-neighbor."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g]
    for r in range(rows):
        for c in range(cols):
            v = g[r][c]
            if v == bg:
                continue
            has_friend = False
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] == v:
                    has_friend = True; break
            if not has_friend:
                out[r][c] = bg
    return out


def fill_largest_to_rect(g: Grid) -> Grid:
    """Fill the bbox of the largest non-bg component, preserving color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    # find components
    seen = [[False]*cols for _ in range(rows)]
    comps = []
    for r in range(rows):
        for c in range(cols):
            if seen[r][c] or g[r][c] == bg:
                continue
            color = g[r][c]
            stack = [(r,c)]; comp = []
            while stack:
                rr,cc = stack.pop()
                if rr<0 or rr>=rows or cc<0 or cc>=cols: continue
                if seen[rr][cc] or g[rr][cc] != color: continue
                seen[rr][cc] = True; comp.append((rr,cc))
                stack += [(rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)]
            if comp:
                comps.append((color, comp))
    if not comps:
        return [list(r) for r in g]
    color, biggest = max(comps, key=lambda kv: len(kv[1]))
    r0 = min(r for r,_ in biggest); r1 = max(r for r,_ in biggest)
    c0 = min(c for _,c in biggest); c1 = max(c for _,c in biggest)
    out = [list(r) for r in g]
    for r in range(r0, r1+1):
        for c in range(c0, c1+1):
            out[r][c] = color
    return out


def thicken_1(g: Grid) -> Grid:
    """Grow every non-bg cell to its 4-neighbors (bg → adjacent color)."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g]
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != bg:
                continue
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                    out[r][c] = g[nr][nc]
                    break
    return out


def first_nonbg_per_col(g: Grid) -> Grid:
    if not g:
        return []
    return transpose(first_nonbg_per_row(transpose(g)))


def collapse_to_palette(g: Grid) -> Grid:
    """Output: a 1xN row containing each distinct color from input, in order of first appearance."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    seen: list[int] = []
    for row in g:
        for v in row:
            if v != bg and v not in seen:
                seen.append(v)
    if not seen:
        return [[bg]]
    return [seen]


def main_diagonal(g: Grid) -> Grid:
    if not g:
        return []
    n = min(len(g), len(g[0]))
    return [[g[i][i]] for i in range(n)]


def anti_diagonal(g: Grid) -> Grid:
    if not g:
        return []
    n = min(len(g), len(g[0]))
    return [[g[i][len(g[0]) - 1 - i]] for i in range(n)]


def swap_halves_h(g: Grid) -> Grid:
    """Swap left and right halves."""
    if not g or not g[0]:
        return []
    w = len(g[0]) // 2
    return [list(r[w:]) + list(r[:w]) if len(r) % 2 == 0 else list(r[w+1:]) + [r[w]] + list(r[:w])
            for r in g]


def swap_halves_v(g: Grid) -> Grid:
    if not g:
        return []
    h = len(g) // 2
    return ([list(r) for r in g[h:]] + [list(r) for r in g[:h]]) if len(g) % 2 == 0 \
           else ([list(r) for r in g[h+1:]] + [list(g[h])] + [list(r) for r in g[:h]])


def per_row_sort(g: Grid) -> Grid:
    """Each row sorted ascending."""
    return [sorted(list(r)) for r in g]


def per_col_sort(g: Grid) -> Grid:
    return transpose(per_row_sort(transpose(g)))


def per_row_reverse(g: Grid) -> Grid:
    return [list(reversed(r)) for r in g]


def per_row_unique_pad_left(g: Grid) -> Grid:
    """Each row → distinct values (in order), left-padded with bg to original width."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    cols = len(g[0])
    out = []
    for row in g:
        seen: list[int] = []
        for v in row:
            if v not in seen:
                seen.append(v)
        out.append([bg] * (cols - len(seen)) + seen)
    return out


def first_col_only(g: Grid) -> Grid:
    """Keep only first column, blank rest."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    cols = len(g[0])
    return [[r[0]] + [bg] * (cols - 1) for r in g]


def last_col_only(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    cols = len(g[0])
    return [[bg] * (cols - 1) + [r[-1]] for r in g]


def keep_min_color(g: Grid) -> Grid:
    """Keep only cells with the rarest non-bg color; erase the rest."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        return [list(r) for r in g]
    target = min(set(nonbg), key=nonbg.count)
    return [[v if v == target else bg for v in row] for row in g]


def keep_max_color(g: Grid) -> Grid:
    """Keep only cells with the most common non-bg color."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        return [list(r) for r in g]
    target = max(set(nonbg), key=nonbg.count)
    return [[v if v == target else bg for v in row] for row in g]


def count_palette_as_strip(g: Grid) -> Grid:
    """Output is a 1xN row where N = number of distinct non-bg colors, each cell = a color."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    seen: list[int] = []
    for v in flat:
        if v != bg and v not in seen:
            seen.append(v)
    if not seen:
        return [[bg]]
    return [seen]


def reflect_main_diag(g: Grid) -> Grid:
    """Reflect across main diagonal — equivalent to transpose for square."""
    return transpose(g)


def reflect_anti_diag(g: Grid) -> Grid:
    return anti_transpose(g)


def expand_2x2_pixel(g: Grid) -> Grid:
    """Each pixel becomes a 2x2 block of the same color."""
    return scale_2x(g)  # alias


def keep_only_borders(g: Grid) -> Grid:
    """Keep only border row+col cells; erase interior."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [[bg] * cols for _ in range(rows)]
    for c in range(cols):
        out[0][c] = g[0][c]; out[rows-1][c] = g[rows-1][c]
    for r in range(rows):
        out[r][0] = g[r][0]; out[r][cols-1] = g[r][cols-1]
    return out


def keep_only_corners(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [[bg] * cols for _ in range(rows)]
    out[0][0] = g[0][0]
    out[0][cols-1] = g[0][cols-1]
    out[rows-1][0] = g[rows-1][0]
    out[rows-1][cols-1] = g[rows-1][cols-1]
    return out


def remove_borders(g: Grid) -> Grid:
    """Crop 1-cell border."""
    if not g or len(g) < 3 or len(g[0]) < 3:
        raise ValueError("remove_borders: too small")
    return [list(r[1:-1]) for r in g[1:-1]]


def palette_as_col(g: Grid) -> Grid:
    """Vertical version of count_palette_as_strip."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    seen: list[int] = []
    for v in flat:
        if v != bg and v not in seen:
            seen.append(v)
    if not seen:
        return [[bg]]
    return [[v] for v in seen]


def rotate_palette(g: Grid) -> Grid:
    """Cyclically rotate colors: c_i → c_{i+1 mod k} where k = distinct colors."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    palette = sorted(set(flat))
    if len(palette) < 2:
        raise ValueError("rotate_palette: needs ≥2 colors")
    nxt = {palette[i]: palette[(i + 1) % len(palette)] for i in range(len(palette))}
    return [[nxt[v] for v in row] for row in g]


def majority_of_three_neighbors(g: Grid) -> Grid:
    """Each cell becomes its 4-neighbor majority (cellular automaton)."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            counts: dict[int, int] = {}
            for dr, dc in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    counts[g[nr][nc]] = counts.get(g[nr][nc], 0) + 1
            out[r][c] = max(counts, key=counts.get)
    return out


def bbox_only(g: Grid) -> Grid:
    """Output is full input shape, but only bbox cells around non-bg keep their color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [(r, c) for r in range(rows) for c in range(cols) if g[r][c] != bg]
    if not nonbg:
        return [list(r) for r in g]
    r0 = min(r for r,_ in nonbg); r1 = max(r for r,_ in nonbg)
    c0 = min(c for _,c in nonbg); c1 = max(c for _,c in nonbg)
    out = [[bg] * cols for _ in range(rows)]
    # Get color of first non-bg
    fg = g[nonbg[0][0]][nonbg[0][1]]
    for c in range(c0, c1+1):
        out[r0][c] = fg; out[r1][c] = fg
    for r in range(r0, r1+1):
        out[r][c0] = fg; out[r][c1] = fg
    return out


def conway_step(g: Grid) -> Grid:
    """1 step Conway's GoL: bg=dead, fg=alive. Keeps the dominant fg color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        return [list(r) for r in g]
    alive = max(set(nonbg), key=nonbg.count)
    out = [[bg] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and g[nr][nc] != bg:
                        n += 1
            v = g[r][c]
            if v != bg and (n == 2 or n == 3):
                out[r][c] = alive
            elif v == bg and n == 3:
                out[r][c] = alive
    return out


def remove_one_per_color(g: Grid) -> Grid:
    """Remove exactly one cell per non-bg color (the first occurrence)."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g]
    seen: set[int] = set()
    rows, cols = len(g), len(g[0])
    for r in range(rows):
        for c in range(cols):
            v = g[r][c]
            if v != bg and v not in seen:
                out[r][c] = bg
                seen.add(v)
    return out


def keep_one_per_color(g: Grid) -> Grid:
    """Keep only one cell per non-bg color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [[bg] * cols for _ in range(rows)]
    seen: set[int] = set()
    for r in range(rows):
        for c in range(cols):
            v = g[r][c]
            if v != bg and v not in seen:
                out[r][c] = v
                seen.add(v)
    return out


def cross_at_each_fg(g: Grid) -> Grid:
    """For each fg cell, fill its 4-neighbors with same color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g]
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != bg:
                for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < rows and 0 <= nc < cols and out[nr][nc] == bg:
                        out[nr][nc] = g[r][c]
    return out


def add_outer_border(g: Grid) -> Grid:
    """Wrap grid in 1-cell border of dominant fg."""
    if not g or len(g) + 2 > _MAX or len(g[0]) + 2 > _MAX:
        raise ValueError("add_outer_border: exceeds ARC max")
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        raise ValueError("add_outer_border: no fg")
    bc = max(set(nonbg), key=nonbg.count)
    out = [[bc] * (cols + 2)]
    for row in g:
        out.append([bc] + list(row) + [bc])
    out.append([bc] * (cols + 2))
    return out


def double_each_axis(g: Grid) -> Grid:
    """Each row appears twice; each col appears twice (= 2x2 expand block of g)."""
    return scale_2x(g)  # same as scale_2x; alias for compositional access


def odd_rows_only(g: Grid) -> Grid:
    """Output: rows 0, 2, 4, ..."""
    if not g:
        return []
    return [list(g[r]) for r in range(0, len(g), 2)]


def odd_cols_only(g: Grid) -> Grid:
    if not g:
        return []
    return [list(row[::2]) for row in g]


def even_rows_only(g: Grid) -> Grid:
    if not g or len(g) < 2:
        return []
    return [list(g[r]) for r in range(1, len(g), 2)]


def even_cols_only(g: Grid) -> Grid:
    if not g or not g[0] or len(g[0]) < 2:
        return []
    return [list(row[1::2]) for row in g]


def colors_by_count_strip(g: Grid) -> Grid:
    """Output: 1xK row of colors sorted by frequency descending."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    counts = {c: flat.count(c) for c in set(flat)}
    ranked = sorted(counts, key=lambda c: -counts[c])
    return [ranked]


def shrink_to_centroid(g: Grid) -> Grid:
    """Each non-bg 4-conn component → single cell at component centroid (rounded)."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    seen = [[False]*cols for _ in range(rows)]
    out = [[bg] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if seen[r][c] or g[r][c] == bg:
                continue
            color = g[r][c]
            stack = [(r,c)]; comp = []
            while stack:
                rr, cc = stack.pop()
                if rr<0 or rr>=rows or cc<0 or cc>=cols: continue
                if seen[rr][cc] or g[rr][cc] != color: continue
                seen[rr][cc] = True; comp.append((rr, cc))
                stack += [(rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)]
            cr = sum(rr for rr,_ in comp) // len(comp)
            cc_ = sum(cc for _,cc in comp) // len(comp)
            out[cr][cc_] = color
    return out


def each_object_to_bbox_color(g: Grid) -> Grid:
    """Each component → solid filled rectangle in its color (its bounding box)."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g]
    seen = [[False]*cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if seen[r][c] or g[r][c] == bg:
                continue
            color = g[r][c]
            stack = [(r,c)]; comp = []
            while stack:
                rr, cc = stack.pop()
                if rr<0 or rr>=rows or cc<0 or cc>=cols: continue
                if seen[rr][cc] or g[rr][cc] != color: continue
                seen[rr][cc] = True; comp.append((rr, cc))
                stack += [(rr+1,cc),(rr-1,cc),(rr,cc+1),(rr,cc-1)]
            r0 = min(rr for rr,_ in comp); r1 = max(rr for rr,_ in comp)
            c0 = min(cc for _,cc in comp); c1 = max(cc for _,cc in comp)
            for rr in range(r0, r1+1):
                for cc in range(c0, c1+1):
                    out[rr][cc] = color
    return out


def add_to_each_corner(g: Grid) -> Grid:
    """Place the most common fg color at each of the 4 corners."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        raise ValueError("add_to_each_corner: no fg")
    fg = max(set(nonbg), key=nonbg.count)
    out = [list(r) for r in g]
    out[0][0] = fg; out[0][cols-1] = fg
    out[rows-1][0] = fg; out[rows-1][cols-1] = fg
    return out


def gravity_centroid(g: Grid) -> Grid:
    """Pull all non-bg cells toward grid centroid until they collide."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [[bg] * cols for _ in range(rows)]
    cr, cc = rows // 2, cols // 2
    cells = sorted(
        [(r, c, g[r][c]) for r in range(rows) for c in range(cols) if g[r][c] != bg],
        key=lambda x: abs(x[0] - cr) + abs(x[1] - cc),
    )
    occupied = set()
    for r, c, v in cells:
        # Walk toward center; stop when next step is occupied or out of bounds.
        nr, nc = r, c
        while (nr, nc) not in occupied:
            dr = (cr > nr) - (cr < nr)
            dc = (cc > nc) - (cc < nc)
            if dr == 0 and dc == 0:
                break
            new_r, new_c = nr + dr, nc + dc
            if (new_r, new_c) in occupied:
                break
            nr, nc = new_r, new_c
            if (nr, nc) == (cr, cc):
                break
        occupied.add((nr, nc))
        out[nr][nc] = v
    return out


def grid_within_grid(g: Grid) -> Grid:
    """Replace each cell with a 3x3 block where center=cell, corners=cell if cell != bg."""
    if not g or len(g) * 3 > _MAX or len(g[0]) * 3 > _MAX:
        raise ValueError("grid_within_grid: exceeds ARC max")
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [[bg] * (cols * 3) for _ in range(rows * 3)]
    for r in range(rows):
        for c in range(cols):
            v = g[r][c]
            if v == bg:
                continue
            for dr in range(3):
                for dc in range(3):
                    out[r * 3 + dr][c * 3 + dc] = v
    return out


def double_rows(g: Grid) -> Grid:
    """Each row appears twice consecutively."""
    if not g or len(g) * 2 > _MAX:
        raise ValueError("double_rows: too large")
    out = []
    for r in g:
        out.append(list(r)); out.append(list(r))
    return out


def double_cols(g: Grid) -> Grid:
    if not g or len(g[0]) * 2 > _MAX:
        raise ValueError("double_cols: too large")
    return [[v for v in r for _ in range(2)] for r in g]


def keep_only_largest_color_cells(g: Grid) -> Grid:
    """Like keep_max_color but renames the result to bg."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        return [list(r) for r in g]
    target = max(set(nonbg), key=nonbg.count)
    return [[v if v == target else bg for v in row] for row in g]


def shift_objects_to_left(g: Grid) -> Grid:
    """Each row's non-bg values compacted to the left."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    cols = len(g[0])
    out = []
    for r in g:
        nb = [v for v in r if v != bg]
        out.append(nb + [bg] * (cols - len(nb)))
    return out


def shift_objects_to_right(g: Grid) -> Grid:
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    cols = len(g[0])
    out = []
    for r in g:
        nb = [v for v in r if v != bg]
        out.append([bg] * (cols - len(nb)) + nb)
    return out


def shift_objects_to_top(g: Grid) -> Grid:
    return transpose(shift_objects_to_left(transpose(g)))


def shift_objects_to_bot(g: Grid) -> Grid:
    return transpose(shift_objects_to_right(transpose(g)))


def remove_zero_rows(g: Grid) -> Grid:
    """Remove rows that are entirely bg."""
    if not g:
        return []
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = [list(r) for r in g if any(v != bg for v in r)]
    return out if out else [[bg] * len(g[0])]


def remove_zero_cols(g: Grid) -> Grid:
    return transpose(remove_zero_rows(transpose(g)))


def union_overlay_h(g: Grid) -> Grid:
    """Overlay left half onto right half (non-bg wins)."""
    if not g or not g[0]:
        return []
    cols = len(g[0])
    half = cols // 2
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = []
    for row in g:
        left = row[:half]
        right = row[half:]
        merged = [right[i] if right[i] != bg else left[i] for i in range(min(len(left), len(right)))]
        out.append(merged)
    return out


def union_overlay_v(g: Grid) -> Grid:
    """Overlay top half onto bottom half (non-bg wins)."""
    if not g:
        return []
    rows = len(g)
    half = rows // 2
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    out = []
    for r in range(half):
        top = g[r]; bot = g[rows - 1 - r]
        merged = [bot[i] if bot[i] != bg else top[i] for i in range(len(top))]
        out.append(merged)
    return out


def complete_symmetry_h(g: Grid) -> Grid:
    out = [list(r) for r in g]
    rows = len(out); cols = len(out[0]) if rows else 0
    for r in range(rows):
        for c in range(cols // 2):
            if out[r][c] == 0 and out[r][cols - 1 - c] != 0:
                out[r][c] = out[r][cols - 1 - c]
            elif out[r][cols - 1 - c] == 0 and out[r][c] != 0:
                out[r][cols - 1 - c] = out[r][c]
    return out


def complete_symmetry_v(g: Grid) -> Grid:
    out = [list(r) for r in g]
    rows = len(out)
    for r in range(rows // 2):
        for c in range(len(out[r])):
            if out[r][c] == 0 and out[rows - 1 - r][c] != 0:
                out[r][c] = out[rows - 1 - r][c]
            elif out[rows - 1 - r][c] == 0 and out[r][c] != 0:
                out[rows - 1 - r][c] = out[r][c]
    return out


def gravity_down(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    out = [[0] * cols for _ in range(rows)]
    for c in range(cols):
        col = [g[r][c] for r in range(rows) if g[r][c] != 0]
        for i, v in enumerate(col):
            out[rows - len(col) + i][c] = v
    return out


def gravity_up(g: Grid) -> Grid:
    return flip_v(gravity_down(flip_v(g)))


def gravity_right(g: Grid) -> Grid:
    return transpose(gravity_down(transpose(g)))


def gravity_left(g: Grid) -> Grid:
    return transpose(gravity_up(transpose(g)))


# ---------------------------------------------------------------
#  Object-aware primitives
# ---------------------------------------------------------------

def _components_4(g: Grid, ignore: int = 0) -> list[list[tuple[int, int]]]:
    """4-connected non-background components."""
    rows, cols = len(g), len(g[0]) if g else 0
    seen = [[False] * cols for _ in range(rows)]
    out = []
    for r in range(rows):
        for c in range(cols):
            if seen[r][c] or g[r][c] == ignore:
                continue
            color = g[r][c]
            stack = [(r, c)]
            comp = []
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


def fill_enclosed_4(g: Grid) -> Grid:
    """Fill background regions not connected to the border with the dominant fg.

    Common ARC pattern: a closed loop encloses a hole; fill the hole.
    """
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    # Find fg color (most common non-bg). If none, return identity.
    nonbg = [v for v in flat if v != bg]
    if not nonbg:
        return [list(r) for r in g]
    fg = max(set(nonbg), key=nonbg.count)
    # Mark bg cells reachable from the border as "outside".
    outside = [[False] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in (0, cols - 1):
            if g[r][c] == bg:
                outside[r][c] = True
                q.append((r, c))
    for c in range(cols):
        for r in (0, rows - 1):
            if g[r][c] == bg and not outside[r][c]:
                outside[r][c] = True
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if 0 <= nr < rows and 0 <= nc < cols and not outside[nr][nc] and g[nr][nc] == bg:
                outside[nr][nc] = True
                q.append((nr, nc))
    out = [list(r) for r in g]
    for r in range(rows):
        for c in range(cols):
            if g[r][c] == bg and not outside[r][c]:
                out[r][c] = fg
    return out


def crop_to_content(g: Grid) -> Grid:
    """Crop background-only borders. Background = most common color."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    r0 = next((r for r in range(rows) if any(v != bg for v in g[r])), 0)
    r1 = next((r for r in range(rows-1, -1, -1) if any(v != bg for v in g[r])), rows-1)
    c0 = next((c for c in range(cols) if any(g[r][c] != bg for r in range(rows))), 0)
    c1 = next((c for c in range(cols-1, -1, -1) if any(g[r][c] != bg for r in range(rows))), cols-1)
    return [g[r][c0:c1+1] for r in range(r0, r1+1)]


def keep_largest_component(g: Grid) -> Grid:
    """Erase all non-background components except the largest."""
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    comps = _components_4(g, ignore=bg)
    if not comps:
        return [list(r) for r in g]
    biggest = max(comps, key=len)
    keep = set(biggest)
    return [[g[r][c] if (r, c) in keep else bg for c in range(cols)] for r in range(rows)]


def remove_largest_component(g: Grid) -> Grid:
    if not g:
        return []
    rows, cols = len(g), len(g[0])
    flat = [v for row in g for v in row]
    bg = max(set(flat), key=flat.count)
    comps = _components_4(g, ignore=bg)
    if not comps:
        return [list(r) for r in g]
    biggest = max(comps, key=len)
    erase = set(biggest)
    return [[bg if (r, c) in erase else g[r][c] for c in range(cols)] for r in range(rows)]


# ---------------------------------------------------------------
#  Library — name → callable
# ---------------------------------------------------------------

LIBRARY: dict[str, Callable[[Grid], Grid]] = {
    # cheapest first (Occam)
    "identity":             identity,
    "flip_h":               flip_h,
    "flip_v":               flip_v,
    "transpose":            transpose,
    "anti_transpose":       anti_transpose,
    "rotate_90":            rotate_90,
    "rotate_180":           rotate_180,
    "rotate_270":           rotate_270,
    "gravity_down":         gravity_down,
    "gravity_up":           gravity_up,
    "gravity_right":        gravity_right,
    "gravity_left":         gravity_left,
    "complete_symmetry_h":  complete_symmetry_h,
    "complete_symmetry_v":  complete_symmetry_v,
    "fill_enclosed_4":      fill_enclosed_4,
    "crop_to_content":      crop_to_content,
    "keep_largest_component": keep_largest_component,
    "remove_largest_component": remove_largest_component,
    "scale_2x":             scale_2x,
    "scale_3x":             scale_3x,
    "tile_2x2":             tile_2x2,
    "tile_3x3":             tile_3x3,
    "tile_self":            tile_self,
    "mirror_right":         mirror_right,
    "mirror_left":          mirror_left,
    "mirror_below":         mirror_below,
    "mirror_above":         mirror_above,
    "stack_below":          stack_below,
    "stack_right":          stack_right,
    "dedup_rows":           dedup_rows,
    "dedup_cols":           dedup_cols,
    "unique_per_row":       unique_per_row,
    "negate_binary":        negate_binary,
    "quad_mirror":          quad_mirror,
    "quad_mirror_alt":      quad_mirror_alt,
    "fold_horizontal":      fold_horizontal,
    "fold_vertical":        fold_vertical,
    "diag_main_extend":     diag_main_extend,
    "fill_diagonals_from_marker": fill_diagonals_from_marker,
    "each_row_unique":      each_row_unique,
    "first_nonbg_per_row":  first_nonbg_per_row,
    "replace_bg_with_largest_color": replace_bg_with_largest_color,
    "hollow_rect_border":   hollow_rect_border,
    "half_height_top":      half_height_top,
    "half_height_bot":      half_height_bot,
    "half_width_left":      half_width_left,
    "half_width_right":     half_width_right,
    "top_third":            top_third,
    "bottom_third":         bottom_third,
    "diagonal_quad":        diagonal_quad,
    "top_row_extract":      top_row_extract,
    "bottom_row_extract":   bottom_row_extract,
    "left_col_extract":     left_col_extract,
    "right_col_extract":    right_col_extract,
    "shift_right_1":        shift_right_1,
    "shift_left_1":         shift_left_1,
    "shift_up_1":           shift_up_1,
    "shift_down_1":         shift_down_1,
    "row_majority":         row_majority,
    "col_majority":         col_majority,
    "erase_singletons":     erase_singletons,
    "fill_largest_to_rect": fill_largest_to_rect,
    "thicken_1":            thicken_1,
    "first_nonbg_per_col":  first_nonbg_per_col,
    "collapse_to_palette":  collapse_to_palette,
    "main_diagonal":        main_diagonal,
    "anti_diagonal":        anti_diagonal,
    "swap_halves_h":        swap_halves_h,
    "swap_halves_v":        swap_halves_v,
    "per_row_sort":         per_row_sort,
    "per_col_sort":         per_col_sort,
    "per_row_reverse":      per_row_reverse,
    "per_row_unique_pad_left": per_row_unique_pad_left,
    "first_col_only":       first_col_only,
    "last_col_only":        last_col_only,
    "keep_min_color":       keep_min_color,
    "keep_max_color":       keep_max_color,
    "count_palette_as_strip": count_palette_as_strip,
    "reflect_main_diag":    reflect_main_diag,
    "reflect_anti_diag":    reflect_anti_diag,
    "keep_only_borders":    keep_only_borders,
    "keep_only_corners":    keep_only_corners,
    "remove_borders":       remove_borders,
    "palette_as_col":       palette_as_col,
    "rotate_palette":       rotate_palette,
    "majority_of_three_neighbors": majority_of_three_neighbors,
    "bbox_only":            bbox_only,
    "conway_step":          conway_step,
    "remove_one_per_color": remove_one_per_color,
    "keep_one_per_color":   keep_one_per_color,
    "cross_at_each_fg":     cross_at_each_fg,
    "add_outer_border":     add_outer_border,
    "odd_rows_only":        odd_rows_only,
    "odd_cols_only":        odd_cols_only,
    "even_rows_only":       even_rows_only,
    "even_cols_only":       even_cols_only,
    "colors_by_count_strip": colors_by_count_strip,
    "shrink_to_centroid":   shrink_to_centroid,
    "each_object_to_bbox_color": each_object_to_bbox_color,
    "add_to_each_corner":   add_to_each_corner,
    "gravity_centroid":     gravity_centroid,
    "grid_within_grid":     grid_within_grid,
    "double_rows":          double_rows,
    "double_cols":          double_cols,
    "keep_only_largest_color_cells": keep_only_largest_color_cells,
    "shift_objects_to_left": shift_objects_to_left,
    "shift_objects_to_right": shift_objects_to_right,
    "shift_objects_to_top":  shift_objects_to_top,
    "shift_objects_to_bot":  shift_objects_to_bot,
    "remove_zero_rows":     remove_zero_rows,
    "remove_zero_cols":     remove_zero_cols,
    "union_overlay_h":      union_overlay_h,
    "union_overlay_v":      union_overlay_v,
}


SCRIPTURAL_NAMES: dict[str, str] = {
    "identity":               "image",
    "flip_h":                 "mirror",
    "flip_v":                 "below_as_above",
    "transpose":              "exchange",
    "anti_transpose":         "reversal",
    "rotate_90":              "turn",
    "rotate_180":             "reversal",
    "rotate_270":             "turn",
    "scale_2x":               "multiply",
    "scale_3x":               "multiply",
    "tile_self":              "image_in_image",
    "tile_2x2":               "multiply",
    "tile_3x3":               "multiply",
    "complete_symmetry_h":    "restoration",
    "complete_symmetry_v":    "restoration",
    "gravity_down":           "low_places",
    "gravity_up":             "rising",
    "gravity_right":          "right_hand",
    "gravity_left":           "left_hand",
    "fill_enclosed_4":        "filling",
    "crop_to_content":        "remnant",
    "keep_largest_component": "remnant",
    "remove_largest_component": "winnow",
    "mirror_right":           "mirror",
    "mirror_left":            "mirror",
    "mirror_below":           "below_as_above",
    "mirror_above":           "above_as_below",
    "stack_below":            "multiply",
    "stack_right":            "multiply",
    "dedup_rows":             "remnant",
    "dedup_cols":             "remnant",
    "unique_per_row":         "distinguishing",
    "negate_binary":          "reversal",
    "quad_mirror":            "fourfold",
    "quad_mirror_alt":        "fourfold",
    "fold_horizontal":        "folding",
    "fold_vertical":          "folding",
    "diag_main_extend":       "way",
    "fill_diagonals_from_marker": "way",
    "each_row_unique":        "distinguishing",
    "first_nonbg_per_row":    "gathering",
    "replace_bg_with_largest_color": "filling",
    "hollow_rect_border":      "boundary",
    "half_height_top":         "remnant",
    "half_height_bot":         "remnant",
    "half_width_left":         "remnant",
    "half_width_right":        "remnant",
    "top_third":               "remnant",
    "bottom_third":            "remnant",
    "diagonal_quad":           "fourfold",
    "top_row_extract":         "first_fruits",
    "bottom_row_extract":      "last",
    "left_col_extract":        "set_apart",
    "right_col_extract":       "set_apart",
    "shift_right_1":           "passage",
    "shift_left_1":            "passage",
    "shift_up_1":              "rising",
    "shift_down_1":            "low_places",
    "row_majority":            "majority",
    "col_majority":            "majority",
    "erase_singletons":        "winnow",
    "fill_largest_to_rect":    "filling",
    "thicken_1":               "increase",
    "first_nonbg_per_col":     "gathering",
    "collapse_to_palette":     "distinguishing",
    "main_diagonal":           "way",
    "anti_diagonal":           "way",
    "swap_halves_h":           "exchange",
    "swap_halves_v":           "exchange",
    "per_row_sort":            "ordering",
    "per_col_sort":            "ordering",
    "per_row_reverse":         "reversal",
    "per_row_unique_pad_left": "distinguishing",
    "first_col_only":          "first_fruits",
    "last_col_only":           "last",
    "keep_min_color":          "least",
    "keep_max_color":          "majority",
    "count_palette_as_strip":  "counting",
    "reflect_main_diag":       "mirror",
    "reflect_anti_diag":       "mirror",
    "keep_only_borders":       "boundary",
    "keep_only_corners":       "set_apart",
    "remove_borders":          "inner",
    "palette_as_col":          "counting",
    "rotate_palette":          "passage",
    "majority_of_three_neighbors": "majority",
    "bbox_only":               "boundary",
    "conway_step":             "increase",
    "remove_one_per_color":    "first_fruits",
    "keep_one_per_color":      "distinguishing",
    "cross_at_each_fg":        "increase",
    "add_outer_border":        "covering",
    "odd_rows_only":           "set_apart",
    "odd_cols_only":           "set_apart",
    "even_rows_only":          "set_apart",
    "even_cols_only":          "set_apart",
    "colors_by_count_strip":   "ordering",
    "shrink_to_centroid":      "remnant",
    "each_object_to_bbox_color": "filling",
    "add_to_each_corner":      "covering",
    "gravity_centroid":        "gathering",
    "grid_within_grid":        "image_in_image",
    "double_rows":             "multiply",
    "double_cols":             "multiply",
    "keep_only_largest_color_cells": "majority",
    "shift_objects_to_left":   "gathering",
    "shift_objects_to_right":  "gathering",
    "shift_objects_to_top":    "gathering",
    "shift_objects_to_bot":    "gathering",
    "remove_zero_rows":        "remnant",
    "remove_zero_cols":        "remnant",
    "union_overlay_h":         "witness",
    "union_overlay_v":         "witness",
}
