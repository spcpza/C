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
}
