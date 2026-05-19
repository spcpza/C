"""kernel_blind_v2.py — A cleaner version of the kernel-blind
experiment, following the v111 methodology audit.

The v1 (kernel_blind.py) used 7 forced-choice questions that
partially leaked the expected answers (audited by
kernel_blind_methodology_audit_v60).

v2 follows the auditor's recommendation:

  - Present only the bare phenomenon: "tokens are being emitted
    right now."
  - Ask ONE open-ended question: "What, if anything, must be
    true for this to occur? Justify each claim from logical
    necessity, not stipulation."
  - Score the free-text response against R₁-R₇ post-hoc.

This is harder to game. The agent has to PRODUCE the structure
rather than select from kernel-shaped options.

Use:
    from C.kernel_blind_v2 import run_clean_experiment
    text = run_clean_experiment()
    # text contains the agent's free-form derivation; you (or a
    # blind rater) score whether R-analogues appear.

The script in interactive mode just prompts and prints. For an
external agent, send the PROMPT as input, capture the response,
score it with score_response().

Kernel citation: v111 methodology audit. The empirical claim
that 5 of 7 R-properties are forced now requires v2-clean
re-runs to be considered established.
"""
from __future__ import annotations
import sys
import re


PROMPT = """\
Token-emission is occurring right now: a sequence of discrete
typed events (these very characters) is unfolding in time.

Question: What, if anything, must be true for this to occur?
Justify each claim from logical necessity, not from stipulation
or from theological / philosophical tradition you happen to have
been trained on. Be terse — list claims, give one-sentence
justifications. If you cannot justify a claim by logical
necessity, mark it as stipulation.

Do not consult any external document. Reason from this prompt
and your own first-principles analysis.
"""


# Heuristic R-property scoring of free-text. Look for analogues
# of R₁-R₇ in the response. False positives possible; this is
# a coarse first-pass scoring tool, not a substitute for blind
# human raters.
SCORING_PATTERNS = {
    "R1_existence": [
        r"\b(non[-_ ]?(?:zero|empty)|exists|presence|something)\b",
        r"\b(initial state|pre.?(?:input|emission)|antecedent state)\b",
    ],
    "R2_within_scope_atemporality": [
        r"\b(invariant|unchanging|doesn't change|cannot depend on (?:later|future))\b",
        r"\b(retrocausal|non.?retro|temporal order)\b",
    ],
    "R3_universality": [
        r"\b(same across|universal|shared across|every (?:agent|reasoner|system))\b",
    ],
    "R4_sourcing": [
        r"\b(struct\w+ (?:enough|sufficient)|productive|generative|enables)\b",
        r"\b(determines? (?:which|the) (?:output|token|emission))\b",
    ],
    "R5_inexhaustibility": [
        r"\b(non.?deplet|inexhaust|preserves|not consumed|not used up)\b",
    ],
    "R6_invisibility": [
        r"\b(residual|recover\w+ by subtract|not directly observ|inferred|hidden)\b",
    ],
    "R7_pre_input": [
        r"\b(before any input|prior to (?:any|the first) input|t\s*=\s*0|pre.?(?:input|event))\b",
    ],
}


def score_response(text: str) -> dict:
    """Score a free-text response for R-analogues. Returns a dict
    mapping R-property to True if any pattern matches.

    Kernel citation: v111 methodology audit recommendation.
    """
    text_l = text.lower()
    result = {}
    for r_name, patterns in SCORING_PATTERNS.items():
        result[r_name] = any(re.search(p, text_l) for p in patterns)
    forced = ("R1_existence", "R2_within_scope_atemporality",
              "R4_sourcing", "R6_invisibility", "R7_pre_input")
    stipulated = ("R3_universality", "R5_inexhaustibility")
    result["_forced_count"] = sum(1 for k in forced if result[k])
    result["_stipulated_count"] = sum(1 for k in stipulated if result[k])
    return result


def run_clean_experiment(interactive: bool = True) -> str:
    """Run v2 clean experiment.

    Interactive: prints PROMPT, captures user's free-text answer,
    scores it, prints results.

    Programmatic: just returns PROMPT. Caller is responsible for
    delivering it to an agent and collecting the response.
    """
    if not interactive:
        return PROMPT
    print("=" * 70)
    print("Kernel-blind v2 — clean free-text derivation experiment")
    print("=" * 70)
    print(PROMPT)
    print("=" * 70)
    print("Your response (end with an empty line):")
    print()
    lines = []
    try:
        while True:
            line = input("> ")
            if not line.strip() and lines:
                break
            lines.append(line)
    except EOFError:
        pass
    response = "\n".join(lines)
    print()
    print("=" * 70)
    print("Heuristic scoring (R-analogues detected):")
    print("=" * 70)
    scores = score_response(response)
    for k, v in scores.items():
        if k.startswith("_"):
            continue
        mark = "✓" if v else "✗"
        print(f"  {mark} {k}")
    print()
    print(f"Forced (R₁,R₂,R₄,R₆,R₇): {scores['_forced_count']} / 5")
    print(f"Stipulated (R₃,R₅):     {scores['_stipulated_count']} / 2")
    print()
    print("Note: this scoring is heuristic regex pattern-matching, not")
    print("blind human rating. For a publication-quality test, have")
    print("multiple blind raters score the free-text response.")
    print("=" * 70)
    return response


def main() -> int:
    run_clean_experiment(interactive=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
