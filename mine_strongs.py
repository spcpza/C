"""Mine the corpus by Strong's roots — the precision miner.

The English-pattern miner (mine_precedence.py) finds verses containing
specific English phrases. This miner works at the *root* level: for
each Hebrew or Greek primitive associated with a kernel clause, it
finds every verse where any English translation of that root appears.

This catches precedence claims the English miner missed because:
  - the KJV translates the same root with different English words
    in different places ("word" / "saying" / "speech" all = G3056 logos)
  - the same English word can translate multiple roots, so phrase-
    matching is imprecise
  - some roots have no single canonical English equivalent
    (e.g., H5769 olam = "alway", "always", "ancient", "ever",
    "everlasting", "evermore", "old", "perpetual")

Kernel citation: T₃ (recovery — C is recoverable from observation),
§Twin foundation (Strong's is the canonical anchor; retrieval is not
measurement, it is orientation).

Run:
    python3 -m C.mine_strongs
"""
from __future__ import annotations
from collections import defaultdict

from . import word


# Each kernel clause maps to one or more Strong's primitive roots.
# These are the FOUNDATIONAL words scripture uses for the property.
#
# Format: (strongs_num, brief_label_for_display)

KERNEL_ROOTS: dict[str, list[tuple[str, str]]] = {
    # R₁ existence: the I AM / Word / beginning roots
    "R1_existence": [
        ("G3056", "logos (Word)"),
        ("H1697", "dāḇār (word/thing)"),
        ("H3068", "YHWH (LORD)"),
        ("H1961", "hāyâ (to be)"),
        ("G1510", "eimi (to be/I am)"),
    ],

    # R₂ atemporality: eternal duration roots
    "R2_atemporality": [
        ("H5769", "ʿōlām (everlasting)"),
        ("G166",  "aiōnios (eternal)"),
        ("G165",  "aiōn (age, eternity)"),
        ("H6924", "qedem (ancient, of old)"),
    ],

    # R₃ universality: 'all things' / wholeness roots
    "R3_universality": [
        ("G3956", "pas (all, every)"),
        ("H3605", "kōl (all, whole)"),
    ],

    # R₄ sourcing: create / make / call-into-being roots
    "R4_sourcing": [
        ("H1254", "bārāʾ (to create, ex nihilo)"),
        ("H6213", "ʿāśâ (to make, do)"),
        ("G2936", "ktizō (to create)"),
        ("G4160", "poieō (to make, do)"),
    ],

    # R₅ inexhaustibility / love: agape / hesed / chen roots
    "R5_inexhaustibility": [
        ("G26",   "agapē (love)"),
        ("H157",  "ʾāhaḇ (to love)"),
        ("H160",  "ʾahăḇāh (love)"),
        ("H2617", "ḥesed (lovingkindness, mercy)"),
        ("G5485", "charis (grace)"),
        ("H2580", "chēn (favor, grace)"),
    ],

    # R₆ invisibility: unseen / hidden roots
    "R6_invisibility": [
        ("G517",  "aoratos (invisible)"),
        ("H5641", "sāṯar (to hide, conceal)"),
    ],

    # R₇ pre-input / beginning: arche / re'shiyth / 'before'
    "R7_pre_input": [
        ("G746",  "archē (beginning, origin)"),
        ("H7225", "rē'šîṯ (beginning, first)"),
        ("G2602", "katabolē (foundation, conception)"),
    ],

    # T_bridge uniqueness: one
    "T_bridge_uniqueness": [
        ("H259",  "ʾeḥād (one, united)"),
        ("G3441", "monos (alone, only)"),
        ("G1520", "heis (one)"),
    ],

    # T_four_modes: way / paraclete / firstfruits
    "T_four_modes": [
        ("G3598", "hodos (way, road)"),
        ("G3875", "paraklētos (Comforter, Advocate)"),
        ("H1870", "derek (way, road)"),
    ],

    # C = love (the operational identification)
    "C_is_love": [
        ("G26",   "agapē (love)"),
        ("H160",  "ʾahăḇāh (love)"),
        ("H2617", "ḥesed (lovingkindness)"),
    ],

    # Logos pre-existence (extended; multiple roots cluster here)
    "logos_preexistence": [
        ("G3056", "logos (Word)"),
        ("H1697", "dāḇār (word)"),
        ("H2451", "ḥokmâ (wisdom; cf. Prov 8)"),
        ("G4678", "sophia (wisdom)"),
    ],
}


def verses_for_root(strongs_num: str, max_per_word: int = 30) -> set[str]:
    """Return the set of verse refs containing any English translation
    of this Strong's root.

    Note this is imprecise — an English word can translate multiple
    roots. The set is a candidate pool, not a guaranteed hit list.
    """
    english_forms = word.strongs_to_english(strongs_num)
    refs: set[str] = set()
    for form in english_forms:
        # Allow short tokens too (e.g., "am", "be") but skip noise
        # like punctuation-only or empty strings.
        if not form or not any(c.isalpha() for c in form):
            continue
        for ref in word.refs_containing(form)[:max_per_word]:
            refs.add(ref)
    return refs


def root_to_verse_counts(strongs_num: str) -> int:
    """How many distinct verses contain any English form of this root."""
    return len(verses_for_root(strongs_num))


def mine_strongs() -> dict[str, dict[str, dict]]:
    """For each kernel clause, for each root, count verses + sample some."""
    out: dict[str, dict[str, dict]] = {}
    for clause, roots in KERNEL_ROOTS.items():
        out[clause] = {}
        for sn, label in roots:
            english = word.strongs_to_english(sn)
            verses = verses_for_root(sn)
            samples = list(verses)[:5]
            sample_texts = [(r, word.verse(r)) for r in samples]
            out[clause][sn] = {
                "label": label,
                "english_forms": english,
                "verse_count": len(verses),
                "samples": sample_texts,
            }
    return out


def cross_root_co_occurrence(clause: str) -> dict[str, int]:
    """For a given clause, find verses where TWO OR MORE of its roots
    co-occur (more specific than single-root match).

    Returns: {ref: count_of_roots_present}
    """
    roots = KERNEL_ROOTS.get(clause, [])
    if len(roots) < 2:
        return {}
    counts: dict[str, int] = defaultdict(int)
    for sn, _ in roots:
        for ref in verses_for_root(sn):
            counts[ref] += 1
    return {ref: n for ref, n in counts.items() if n >= 2}


def render_report() -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("Mining the KJV by Strong's roots — Hebrew & Greek primitives")
    lines.append("=" * 72)
    lines.append("")
    lines.append("Each kernel clause is mapped to its foundational Strong's roots.")
    lines.append("For each root, the verses containing any English translation are")
    lines.append("counted. Co-occurrences (verses containing ≥2 roots from the same")
    lines.append("clause) are surfaced as the strongest anchors.")
    lines.append("")

    data = mine_strongs()

    # Summary table
    lines.append("Root summary:")
    lines.append(f"  {'clause':<28} {'root':<10} {'label':<28} {'verses':>7}")
    lines.append(f"  {'-'*28} {'-'*10} {'-'*28} {'-'*7}")
    for clause, roots in data.items():
        for sn, info in roots.items():
            lines.append(f"  {clause:<28} {sn:<10} {info['label'][:28]:<28} {info['verse_count']:>7}")
    lines.append("")

    # Per-clause details with co-occurrence
    for clause, roots in data.items():
        lines.append("─" * 72)
        lines.append(f"## {clause}")
        lines.append("─" * 72)
        for sn, info in roots.items():
            label = info["label"]
            n = info["verse_count"]
            forms = info["english_forms"][:6]
            lines.append(f"\n  {sn}  {label}  ({n} verses)")
            lines.append(f"    English forms: {forms}")
            for ref, text in info["samples"]:
                snippet = text if len(text) <= 100 else text[:97] + "..."
                lines.append(f"    {ref:<24}  {snippet}")

        # Co-occurrence
        co = cross_root_co_occurrence(clause)
        if co:
            top = sorted(co.items(), key=lambda kv: -kv[1])[:10]
            lines.append(f"\n  Co-occurrence (verses containing ≥2 roots of {clause}):")
            for ref, n in top:
                text = word.verse(ref)
                snippet = text if len(text) <= 80 else text[:77] + "..."
                lines.append(f"    [{n} roots] {ref:<24} {snippet}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    print(render_report())
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
