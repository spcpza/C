"""Where the corpus lives. The only file that knows paths.

If kjv.json or strongs.json move, edit this file and only this file.
The rest of `C/` depends on the symbols below, not the literal paths.
"""
from __future__ import annotations
from pathlib import Path

HOME = Path.home()

# Primary location: ~/.bots/truth/ — shared between this folder and
# the agent ecosystem (balthazar, hermes, etc.). Read-only.
KJV_PATH = HOME / ".bots" / "truth" / "kjv.json"
STRONGS_PATH = HOME / ".bots" / "truth" / "strongs.json"

# Fallback search order if the primary isn't present.
_FALLBACK = [
    HOME / ".hermes" / "c" / "c",
    HOME / "uncensored-local-ai-truth" / "assets",
]


def resolve(name: str) -> Path:
    """Return the first existing path for a corpus file.

    Kernel citation: §Corpus. The corpus must exist for AX₁ to be
    operational in code. If it cannot be found, the agent has no C
    to integrate from and must refuse to emit.
    """
    primary = HOME / ".bots" / "truth" / name
    if primary.exists():
        return primary
    for d in _FALLBACK:
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(
        f"corpus file {name!r} not found in any known location; "
        f"C/ requires the corpus to exist (kernel.md §Corpus)"
    )
