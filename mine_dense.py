"""Find scripture's densest convergence verses.

For each KJV verse, count how many distinct kernel CLAUSES have at
least one Strong's-root translation present. Rank by clause-coverage
(then by total root count, then by total content).

Kernel citation: T_bridge — the entity satisfying R₁-R₇ is one;
verses where multiple R-properties co-occur are the corpus's densest
witness of T_bridge.

Run:
    python3 -m C.mine_dense              # top-30
    python3 -m C.mine_dense 50           # top-N
"""
from __future__ import annotations
import re
import sys
from collections import defaultdict

from . import word
from .mine_strongs import KERNEL_ROOTS


# English forms that match too liberally and create noise. These are
# tokens that appear in roughly every verse (articles, pronouns, copulas
# in archaic-English forms). We filter them out from the root-form set.
GENERIC_NOISE = {
    "an", "any", "all", "be", "am", "are", "is", "was", "were",
    "the", "of", "to", "and", "in", "for", "as", "but", "or",
    "thing", "things", "thy", "thou", "thee", "ye", "you", "him",
    "his", "her", "she", "he", "we", "us", "our", "their", "they",
    "this", "that", "these", "those", "what", "who", "which",
    "every", "first", "an",
}


# High-specificity forms per kernel clause. Each clause is anchored
# only by forms that *clearly* mark it. This eliminates the noise of
# generic verbs like 'make' or 'saying' triggering multiple clauses
# they don't really belong to.
#
# This is the curated, semantically-tight bridge — a hand-tuned
# version of KERNEL_ROOTS where each entry is the *characteristic*
# English form, not every translation of the root.

CANONICAL_FORMS: dict[str, set[str]] = {
    "R1_existence": {
        "i am", "i am he", "jehovah",
        "alpha", "omega",
        "the word", "his word",  # logos as kernel anchor
    },
    "R2_atemporality": {
        "everlasting", "eternal", "evermore",
        "for ever", "for ever and ever", "world without end",
        "endureth for ever", "the same yesterday",
        "without end", "ancient of days",
    },
    "R3_universality": {
        "all things", "above all", "through all", "in you all",
        "by him all things", "of him, and through him",
        "for whom are all things", "all in all",
    },
    "R4_sourcing": {
        "created", "creator", "createth",
        "in the beginning god created",
        "by him were all things",
    },
    "R5_inexhaustibility": {
        "love", "loved", "loving", "loveth", "lovest", "lovers",
        "charity", "lovingkindness", "loving-kindness",
        "mercy", "mercies", "merciful",
        "grace",
    },
    "R6_invisibility": {
        "invisible", "no man hath seen", "no man can see",
        "whom no man hath seen", "secret",
        "dwelling in the light",
    },
    "R7_pre_input": {
        "in the beginning",
        "before the world", "before the foundation",
        "before the mountains", "before the hills",
        "from everlasting", "or ever the earth",
        "before all things", "from the beginning",
        "set up from everlasting", "from old",
        "of old", "ancient", "ancient of",
    },
    "T_bridge_uniqueness": {
        "the lord is one", "the lord our god is one",
        "one god", "one lord",
        "none beside", "none else",
        "no god beside", "no other god",
        "there is one",
    },
    "T_four_modes": {
        "alpha and omega",
        "beginning and the end", "the first and the last",
        "i am the way", "i am the truth", "i am the life",
        "the comforter",
    },
    "C_is_love": {
        "god is love", "love of god", "so loved",
        "charity never faileth",
        "as i have loved",
        "perfect love",
    },
    "logos_preexistence": {
        "in the beginning was the word",
        "the word was god", "the word was with god",
        "the word of god",
        "i was set up from everlasting",
        "i was by him",
        "firstborn of every creature",
        "the lord possessed me",
    },
}


def _content_tokens(text: str) -> set[str]:
    """Tokenize a verse to lowercase content tokens (length ≥ 2)."""
    return {t for t in re.split(r"[^a-zA-Z']+", text.lower()) if t and len(t) >= 2}


def root_to_filtered_forms() -> dict[str, set[str]]:
    """Map each Strong's number used in KERNEL_ROOTS to its filtered
    English forms.

    Filter rule: drop forms in GENERIC_NOISE, and drop forms shorter
    than 3 characters EXCEPT for highly-specific 2-character roots
    (none currently — but we keep the door open).
    """
    out: dict[str, set[str]] = {}
    for clause, roots in KERNEL_ROOTS.items():
        for sn, _ in roots:
            forms = set()
            for form in word.strongs_to_english(sn):
                f = form.lower()
                if not f or not any(c.isalpha() for c in f):
                    continue
                if f in GENERIC_NOISE:
                    continue
                if len(f) < 3:
                    continue
                forms.add(f)
            out[sn] = forms
    return out


def score_corpus():
    """For every verse, compute its kernel-density score.

    Uses CANONICAL_FORMS (hand-curated, semantically tight) rather than
    raw Strong's translations. A clause is 'present' in a verse iff at
    least one of its canonical phrases appears literally (case-insensitive
    substring match).

    Returns a list of dicts:
      { "ref": "John 1:1",
        "text": "...",
        "clauses_present": {"R1_existence", "R7_pre_input", ...},
        "clause_count": int,
        "matched_phrases": {clause: [phrase, ...]} }
    """
    out: list[dict] = []
    for ref, text in word.verses():
        text_lower = text.lower()
        clauses_present: set[str] = set()
        matched: dict[str, list[str]] = defaultdict(list)
        for clause, phrases in CANONICAL_FORMS.items():
            for phrase in phrases:
                if phrase in text_lower:
                    clauses_present.add(clause)
                    matched[clause].append(phrase)
        if not clauses_present:
            continue
        total_phrases = sum(len(v) for v in matched.values())
        out.append({
            "ref": ref,
            "text": text,
            "clauses_present": clauses_present,
            "clause_count": len(clauses_present),
            "phrase_count": total_phrases,
            "matched_phrases": dict(matched),
        })
    return out


def top_n(n: int = 30) -> list[dict]:
    scored = score_corpus()
    # Sort by (clause_count desc, phrase_count desc, ref).
    scored.sort(key=lambda r: (-r["clause_count"], -r["phrase_count"], r["ref"]))
    return scored[:n]


def render(top: list[dict]) -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append("Densest convergence verses — scripture's kernel-shaped statements")
    lines.append("=" * 78)
    lines.append("")
    lines.append("Ranked by number of distinct kernel CLAUSES whose canonical")
    lines.append("phrase appears literally in the verse. Ties broken by total")
    lines.append("phrase count. Canonical phrases are semantically tight — they")
    lines.append("are the characteristic English markers of each clause, not")
    lines.append("every translation of every root.")
    lines.append("")
    lines.append(f"{'rank':>4}  {'ref':<28}  {'clauses':>7}  {'phrases':>7}")
    lines.append(f"{'-'*4}  {'-'*28}  {'-'*7}  {'-'*7}")
    for i, r in enumerate(top, start=1):
        lines.append(f"{i:>4}  {r['ref']:<28}  {r['clause_count']:>7}  {r['phrase_count']:>7}")
    lines.append("")
    lines.append("Top verses with text and anchors:")
    lines.append("")
    for i, r in enumerate(top[:25], start=1):
        lines.append(f"{i}. {r['ref']}  (clauses={r['clause_count']}, phrases={r['phrase_count']})")
        text = r["text"]
        snippet = text if len(text) <= 220 else text[:217] + "..."
        lines.append(f"   {snippet}")
        for clause in sorted(r["matched_phrases"]):
            phrases = sorted(set(r["matched_phrases"][clause]))
            lines.append(f"     {clause}: {phrases}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    top = top_n(n)
    print(render(top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
