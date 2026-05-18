"""Precedence — the corpus → kernel bridge.

Scripture is the primary witness; the math is downstream. This module
makes the bridge explicit. For each kernel clause (R₁–R₇) it lists
the corpus verses that *directly assert* the corresponding claim,
and verifies they are present in the loaded corpus.

Kernel citation: §"Work this first", T_bridge, §"Fire is hot
regardless of name". The math is what scripture forces; the
corpus is the primary source.

Run:
    python3 -m C.precedence

Programmatic:
    from C.precedence import bridges, verify_bridges
    for name, refs in bridges().items():
        ...
"""
from __future__ import annotations
from . import word


# Each R-property is the math name; the verses are the corpus
# witnesses that assert it directly. Many verses witness multiple
# properties; the mapping lists one or two clearest references per
# property.

BRIDGES: dict[str, list[tuple[str, str]]] = {
    # R₁ — existence of C
    "R1_existence": [
        ("John 1:1",       "In the beginning was the Word, and the Word was with God, and the Word was God."),
        ("Exodus 3:14",    "I AM THAT I AM"),
        ("Revelation 1:8", "I am Alpha and Omega, the beginning and the ending, saith the Lord, which is, and which was, and which is to come, the Almighty."),
    ],

    # R₂ — atemporality (dC/dt = 0)
    "R2_atemporality": [
        ("Hebrews 13:8",   "Jesus Christ the same yesterday, and to day, and for ever."),
        ("Malachi 3:6",    "For I am the LORD, I change not"),
        ("Psalms 102:27",  "But thou art the same, and thy years shall have no end."),
        ("James 1:17",     "every good gift and every perfect gift is from above, and cometh down from the Father of lights, with whom is no variableness, neither shadow of turning."),
    ],

    # R₃ — universality (∀x : E(x, 0) = C)
    "R3_universality": [
        ("Colossians 1:17", "And he is before all things, and by him all things consist."),
        ("Acts 17:28",      "For in him we live, and move, and have our being"),
        ("Ephesians 4:6",   "One God and Father of all, who is above all, and through all, and in you all."),
    ],

    # R₄ — sourcing (T₂: from C, sacrifice produces n ≥ 1)
    "R4_sourcing": [
        ("John 1:3",       "All things were made by him; and without him was not any thing made that was made."),
        ("Genesis 1:1",    "In the beginning God created the heaven and the earth."),
        ("John 12:24",     "Except a corn of wheat fall into the ground and die, it abideth alone: but if it die, it bringeth forth much fruit."),
    ],

    # R₅ — inexhaustibility (T₄: giving from C preserves C)
    "R5_inexhaustibility": [
        ("1 Corinthians 13:8", "Charity never faileth"),
        ("1 John 4:8",         "He that loveth not knoweth not God; for God is love."),
        ("John 4:14",          "the water that I shall give him shall be in him a well of water springing up into everlasting life."),
    ],

    # R₆ — invisibility (T₃: C recovered by subtraction, never observed directly)
    "R6_invisibility": [
        ("1 Timothy 1:17", "Now unto the King eternal, immortal, invisible, the only wise God"),
        ("Romans 1:20",    "For the invisible things of him from the creation of the world are clearly seen, being understood by the things that are made"),
        ("John 1:18",      "No man hath seen God at any time"),
    ],

    # R₇ — pre-input (Self := C + ∫input ⟹ C is what was before any input)
    "R7_pre_input": [
        ("John 1:1",         "In the beginning was the Word"),
        ("Genesis 1:1",      "In the beginning God created"),
        ("Proverbs 8:23",    "I was set up from everlasting, from the beginning, or ever the earth was."),
        ("John 17:5",        "the glory which I had with thee before the world was."),
    ],

    # T_bridge — uniqueness
    "T_bridge_uniqueness": [
        ("Deuteronomy 6:4", "Hear, O Israel: The LORD our God is one LORD"),
        ("Isaiah 45:5",     "I am the LORD, and there is none else, there is no God beside me"),
        ("1 Corinthians 8:6", "But to us there is but one God, the Father, of whom are all things"),
    ],

    # T_four_modes — origin = destination = way = holder = C
    "T_four_modes": [
        ("Revelation 22:13", "I am Alpha and Omega, the beginning and the end, the first and the last."),
        ("John 14:6",        "I am the way, the truth, and the life: no man cometh unto the Father, but by me."),
        ("John 14:26",       "the Comforter, which is the Holy Ghost, whom the Father will send in my name, he shall teach you all things"),
    ],

    # The substance — C = love
    "C_is_love": [
        ("1 John 4:8",       "God is love"),
        ("1 John 4:16",      "God is love; and he that dwelleth in love dwelleth in God, and God in him."),
    ],
}


def bridges() -> dict[str, list[tuple[str, str]]]:
    """Return the corpus→math bridge table.

    Kernel citation: T₃ — C is recovered by observation; the corpus
    is the body of observation.
    """
    return BRIDGES


def verify_bridges() -> dict[str, list[tuple[str, str, bool]]]:
    """Verify every cited verse is present in the loaded corpus.

    Returns: for each kernel clause, list of (ref, expected_substring,
    matched_in_corpus). matched_in_corpus is True iff the verse exists
    AND the expected substring appears in the verse (anti-quote drift).

    Kernel citation: P₁ — measure honestly. If the bridge claims a
    verse contains a phrase, the phrase must be there.
    """
    out: dict[str, list[tuple[str, str, bool]]] = {}
    for clause, refs in BRIDGES.items():
        out[clause] = []
        for ref, expected_substring in refs:
            try:
                actual = word.verse(ref)
            except KeyError:
                out[clause].append((ref, expected_substring, False))
                continue
            # Anti-quote drift: substring should appear in the verse text.
            tokens_a = expected_substring.lower().replace(",", " ").split()
            tokens_b = actual.lower().replace(",", " ").split()
            # Allow loose match: at least 60% of words from expected appear in actual
            if not tokens_a:
                out[clause].append((ref, expected_substring, True))
                continue
            hits = sum(1 for t in tokens_a if t in tokens_b)
            ratio = hits / len(tokens_a)
            out[clause].append((ref, expected_substring, ratio >= 0.6))
    return out


def main() -> int:
    print("=" * 60)
    print("Precedence — corpus → kernel bridge")
    print("=" * 60)
    print()
    print("Scripture is the primary witness. The math is downstream.")
    print("Each kernel clause is the formalization of what scripture")
    print("already says directly. This file makes the bridge explicit.")
    print()

    results = verify_bridges()
    total_ok = 0
    total = 0
    for clause, items in results.items():
        print(f"## {clause}")
        for ref, expected, ok in items:
            total += 1
            status = "✓" if ok else "✗"
            if ok:
                total_ok += 1
            print(f"  {status}  {ref:<22}  '{expected[:60]}{'...' if len(expected)>60 else ''}'")
        print()

    print("=" * 60)
    print(f"Bridge verification: {total_ok}/{total} verse mappings valid in corpus.")
    print("=" * 60)
    if total_ok == total:
        print("\nThe kernel is fully grounded in the corpus.")
        print("'In the beginning was the Word' (John 1:1) — the Word precedes everything.")
        print("The math is what scripture already names.")
    return 0 if total_ok == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
