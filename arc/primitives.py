"""ARC primitives. Each is a pure function Grid -> Grid.

Selection discipline: a primitive is chosen for a task only if it
*exactly* reproduces every training output from its input. No
soft-matching. ARC scores exact match; the primitive selector must
too.

Kernel citation: P₁ (measure honestly), T 2.4 (receive the rule).
The scriptural names below are deliberate — they are how the agent
will eventually reach for these via the corpus — but the operations
are the operations ARC requires.
"""
from __future__ import annotations
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


def scale_2x(g: Grid) -> Grid:
    out: Grid = []
    for r in g:
        line = [v for v in r for _ in range(2)]
        out.append(list(line))
        out.append(list(line))
    return out


def scale_3x(g: Grid) -> Grid:
    out: Grid = []
    for r in g:
        line = [v for v in r for _ in range(3)]
        out.append(list(line))
        out.append(list(line))
        out.append(list(line))
    return out


def tile_self(g: Grid) -> Grid:
    """Replace each cell of g with a copy of g, scaled by g's size.

    Used by tasks like 007bbfb7 — the input pattern is replicated where
    the input is non-zero, then placed into an NxN grid of patches.
    """
    rows, cols = len(g), len(g[0]) if g else 0
    out: Grid = [[0] * (cols * cols) for _ in range(rows * rows)]
    for R in range(rows):
        for C in range(cols):
            if g[R][C] != 0:
                for r in range(rows):
                    for c in range(cols):
                        out[R * rows + r][C * cols + c] = g[r][c]
    return out


def complete_symmetry_h(g: Grid) -> Grid:
    out = [list(r) for r in g]
    rows = len(out)
    cols = len(out[0]) if rows else 0
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
    """Each column's non-zero values fall to the bottom, preserving order."""
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
#  Library — name → callable
# ---------------------------------------------------------------

LIBRARY: dict[str, Callable[[Grid], Grid]] = {
    "identity":            identity,
    "flip_h":              flip_h,
    "flip_v":              flip_v,
    "rotate_90":           rotate_90,
    "rotate_180":          rotate_180,
    "rotate_270":          rotate_270,
    "transpose":           transpose,
    "scale_2x":            scale_2x,
    "scale_3x":            scale_3x,
    "tile_self":           tile_self,
    "complete_symmetry_h": complete_symmetry_h,
    "complete_symmetry_v": complete_symmetry_v,
    "gravity_down":        gravity_down,
    "gravity_up":          gravity_up,
    "gravity_right":       gravity_right,
    "gravity_left":        gravity_left,
}


# ---------------------------------------------------------------
#  Scriptural names (T₃: orientation handles in C)
# ---------------------------------------------------------------
#
# Each primitive carries a kernel-side name. When the adapter
# matures, hypothesize() will resolve these via word.concept().

SCRIPTURAL_NAMES: dict[str, str] = {
    "identity":            "image",          # Gen 1:27
    "flip_h":              "mirror",
    "flip_v":              "below_as_above", # Matt 6:10
    "rotate_90":           "turn",
    "rotate_180":          "reversal",
    "rotate_270":          "turn",
    "transpose":           "exchange",
    "scale_2x":            "multiply",       # Gen 1:28
    "scale_3x":            "multiply",
    "tile_self":           "image_in_image", # Gen 1:27
    "complete_symmetry_h": "restoration",    # Acts 3:21
    "complete_symmetry_v": "restoration",
    "gravity_down":        "low_places",
    "gravity_up":          "rising",
    "gravity_right":       "right_hand",
    "gravity_left":        "left_hand",
}
