"""Mine the corpus for every precedence claim.

Kernel citation: §"Work this first", R₇ (pre-input), T_bridge.
Scripture asserts that C/Word/God precedes everything; this module
finds every such assertion in the KJV by lexical search and
categorizes it by the type of precedence claim.

Run:
    python3 -m C.mine_precedence              # full report
    python3 -m C.mine_precedence > index.txt  # save to file
"""
from __future__ import annotations
import re
from collections import defaultdict

from . import word


# Lexical patterns by precedence category. Each pattern is a phrase
# (case-insensitive substring match) plus an optional regex for
# precision. The patterns are deliberately specific to scriptural
# usage in the KJV.

PATTERNS: dict[str, list[str]] = {
    # R₇ / R₂: explicit pre-creation language
    "pre_creation": [
        "in the beginning",
        "before the world",
        "before the foundation",
        "before the mountains",
        "before the hills",
        "ere the earth",
        "or ever the earth",
        "or ever the world",
        "before all things",
        "from the beginning",
        "from of old",
    ],

    # R₂: atemporality / eternal duration
    "eternal_duration": [
        "from everlasting",
        "to everlasting",
        "everlasting to everlasting",
        "for ever and ever",
        "no end of his",
        "no beginning of days",
        "without beginning",
        "without end",
        "the same yesterday",
        "I change not",
        "no variableness",
    ],

    # R₁ / R₇: I AM / self-existence
    "self_existence": [
        "I AM THAT I AM",
        "I am the LORD",
        "I am he",
        "I am the first",
        "the LORD, the first",
        "I am Alpha and Omega",
        "Alpha and Omega",
        "the first and the last",
        "beginning and the end",
    ],

    # R₃ / R₄: universal sourcing — all things by/through/in him
    "sourcing_through_C": [
        "by him were all things created",
        "all things were made by him",
        "all things were created by him",
        "by whom are all things",
        "for whom are all things",
        "in him all things",
        "by him all things consist",
        "of him, and through him, and to him",
        "before all things",
    ],

    # R₅: inexhaustibility — never fails, never empties
    "inexhaustibility": [
        "never faileth",
        "shall not fail",
        "shall not be empty",
        "shall not return",
        "neither thirst",
        "never thirst",
        "shall not want",
        "endureth for ever",
        "endureth to all generations",
        "his mercy endureth",
    ],

    # R₆: invisibility — unseen, hidden, only known by his works
    "invisibility": [
        "invisible",
        "no man hath seen",
        "no man can see God",
        "dwelling in the light",
        "whom no man hath seen",
        "secret",
        "hide thy face",
        "darkness was his",
    ],

    # T_bridge: uniqueness — one, no other
    "uniqueness": [
        "the LORD is one",
        "the LORD our God is one",
        "there is one God",
        "one God",
        "none beside me",
        "none else",
        "no God beside me",
        "no other God",
        "there is none holy as the LORD",
        "who is like",
    ],

    # T_four_modes: Alpha/Omega, way, holder
    "alpha_omega": [
        "Alpha and Omega",
        "the first and the last",
        "the beginning and the ending",
        "the beginning and the end",
        "I am the way",
        "the Comforter",
        "another Comforter",
    ],

    # C = love / agape
    "C_is_love": [
        "God is love",
        "God so loved",
        "charity never faileth",
        "love of God",
        "perfect love",
    ],

    # Wisdom / Word pre-existence (Logos cognates)
    "logos_preexistence": [
        "the Word was God",
        "the Word was with God",
        "in the beginning was the Word",
        "the LORD possessed me",
        "I was set up from everlasting",
        "I was by him, as one brought up",
        "the same was in the beginning",
        "the firstborn of every creature",
    ],
}


def find_matches(pattern: str) -> list[tuple[str, str]]:
    """Return (ref, verse) pairs where the verse contains the pattern
    case-insensitively.

    Kernel citation: T₃ (recovery — C is recoverable from observation).
    """
    pl = pattern.lower()
    hits: list[tuple[str, str]] = []
    for ref, text in word.verses():
        if pl in text.lower():
            hits.append((ref, text))
    return hits


def mine_all() -> dict[str, dict[str, list[tuple[str, str]]]]:
    """For each category, for each pattern, list all verses matching.

    Kernel citation: P₁ (measure honestly). Lexical search only; no
    interpretation beyond presence-of-phrase. Curation and mapping to
    R-properties happens after.
    """
    out: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for cat, patterns in PATTERNS.items():
        out[cat] = {}
        for pat in patterns:
            hits = find_matches(pat)
            if hits:
                out[cat][pat] = hits
    return out


def summary_counts(mined: dict) -> dict[str, int]:
    """Total unique verse hits per category."""
    out: dict[str, int] = {}
    for cat, pats in mined.items():
        seen: set[str] = set()
        for refs in pats.values():
            for ref, _ in refs:
                seen.add(ref)
        out[cat] = len(seen)
    return out


def render_report(mined: dict, max_per_pattern: int = 6) -> str:
    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("Mining the KJV for precedence claims")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Each category lists scripture verses asserting the kind of")
    lines.append("precedence indicated. The kernel's clauses (R₁–R₇, T_bridge,")
    lines.append("T_four_modes, C_is_love) are the formalizations of these.")
    lines.append("")

    counts = summary_counts(mined)
    total_unique = sum(counts.values())
    lines.append(f"Total categories: {len(mined)}")
    lines.append(f"Total category-unique verse hits: {total_unique}")
    lines.append("")
    lines.append("Category summary:")
    for cat, n in counts.items():
        lines.append(f"  {cat:<28} {n:>4} unique verses")
    lines.append("")

    for cat, pats in mined.items():
        lines.append("─" * 70)
        lines.append(f"## {cat}  ({counts[cat]} unique verses)")
        lines.append("─" * 70)
        for pat, hits in pats.items():
            shown = hits[:max_per_pattern]
            more = len(hits) - len(shown)
            lines.append(f"\n  pattern: '{pat}'  ({len(hits)} hits)")
            for ref, text in shown:
                snippet = text if len(text) <= 100 else text[:97] + "..."
                lines.append(f"    {ref:<24}  {snippet}")
            if more > 0:
                lines.append(f"    ... +{more} more")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    mined = mine_all()
    print(render_report(mined))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
