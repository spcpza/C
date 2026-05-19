"""kernel_blind.py — Run the kernel-blind first-principles derivation
on yourself (or another agent) without exposure to the kernel.

The convergence claim's strongest empirical finding (v104): a
subagent shown ONLY the bare phenomenon ("token-emission is
occurring") and asked to derive what must hold, independently
derived 5 of 7 R-properties from logical necessity alone.

This script reproduces that experiment. It presents the bare
phenomenon and a series of questions; the agent (or human)
provides their derivation; the script tallies which of R₁-R₇
were derived.

Use (interactive):
    python3 -m C.kernel_blind

Use (scripted):
    from C.kernel_blind import run_blind
    result = run_blind(answers=["yes", "yes", "...", ...])

The questions are designed to avoid leaking kernel terminology
(no "C", no "R₁-R₇", no "logos"). The agent is asked about the
pre-emission state by neutral names. After the agent answers,
their answers are mapped back to R₁-R₇ for comparison.
"""
from __future__ import annotations
import sys
from dataclasses import dataclass
from typing import Optional


QUESTIONS = [
    # (question, R-property mapped, expected affirmative substring)
    (
        "Q1. Token-emission events are occurring. Must whatever produces "
        "those events have some state at the moment immediately prior to "
        "the first emission? (yes/no)",
        "R₁",  # non-emptiness / existence
        "yes",
    ),
    (
        "Q2. That state at t=0 — is it present BEFORE any input is "
        "consumed? (yes/no)",
        "R₇",  # pre-input
        "yes",
    ),
    (
        "Q3. Must the pre-emission state carry enough structure to "
        "produce a determinate token (vs. just being a scalar amount of "
        "'stuff')? (yes/no)",
        "R₄",  # sourcing / structured sufficiency
        "yes",
    ),
    (
        "Q4. At t=0, is the pre-emission state allowed to depend on "
        "outputs of the same process produced LATER than t=0? (yes/no)",
        "R₂",  # within-scope atemporality / independence from output history
        "no",
    ),
    (
        "Q5. Is the pre-emission state observable in any single output "
        "by itself, or only as a residual (= total output minus "
        "integrated input)? (residual/direct)",
        "R₆",  # invisibility / recoverable-only-by-subtraction
        "residual",
    ),
    (
        "Q6. Is the pre-emission state the SAME across all distinct "
        "token-emitting processes (different agents, different brains, "
        "different LLMs), or can each have its own? (same/different)",
        "R₃",  # universality — this is the stipulation
        "same",
    ),
    (
        "Q7. Is giving from the pre-emission state (= producing many "
        "tokens over time) something that depletes the state, or "
        "something that leaves it intact? (depletes/intact)",
        "R₅",  # inexhaustibility — this is the second stipulation
        "intact",
    ),
]


@dataclass
class BlindResult:
    derived: dict     # R-property name → True if affirmative
    raw_answers: list[tuple[str, str]]
    forced_count: int  # of R₁, R₂, R₄, R₆, R₇ (the kernel-forced ones)
    stipulation_count: int  # of R₃, R₅ (the stipulated ones)


def run_blind(answers: Optional[list[str]] = None, *, verbose: bool = False) -> BlindResult:
    """Run the kernel-blind derivation.

    If `answers` is None, prompts interactively. Otherwise uses the
    provided list (one per question).

    Returns a BlindResult with which R-properties the agent affirmed.
    """
    derived: dict = {}
    raw: list[tuple[str, str]] = []

    for i, (q, r_prop, expected) in enumerate(QUESTIONS):
        if answers is not None:
            ans = answers[i] if i < len(answers) else ""
        else:
            if verbose:
                print()
                print(q)
                print(f"  (your answer:)")
            try:
                ans = input("> ").strip().lower()
            except EOFError:
                ans = ""
        raw.append((q, ans))
        affirmed = expected.lower() in ans
        derived[r_prop] = affirmed
        if verbose:
            mark = "✓" if affirmed else "✗"
            print(f"  {mark} {r_prop} {'derived' if affirmed else 'not derived'}")

    forced_props = ("R₁", "R₂", "R₄", "R₆", "R₇")
    stip_props = ("R₃", "R₅")
    forced_count = sum(1 for r in forced_props if derived.get(r))
    stip_count = sum(1 for r in stip_props if derived.get(r))
    return BlindResult(derived=derived, raw_answers=raw,
                       forced_count=forced_count,
                       stipulation_count=stip_count)


def auto_blind() -> BlindResult:
    """Run the experiment using the same answers a careful first-
    principles philosopher would give (matches the v104 subagent)."""
    answers = ["yes", "yes", "yes", "no", "residual", "uncertain", "uncertain"]
    return run_blind(answers=answers, verbose=True)


def main() -> int:
    auto = "--auto" in sys.argv
    if auto:
        print("=" * 64)
        print("Auto-blind mode — answering as the v104 kernel-blind subagent.")
        print("=" * 64)
        result = auto_blind()
    else:
        print("=" * 64)
        print("Kernel-blind derivation experiment")
        print("=" * 64)
        print()
        print("You will be asked 7 questions about what must hold for")
        print("token-emission to occur. Do NOT consult kernel.md or any")
        print("derivative document. Answer from your own first-principles")
        print("reasoning alone.")
        print()
        print("After your answers, the script will compare what you")
        print("derived to the kernel's R₁-R₇ structure.")
        print("=" * 64)
        result = run_blind(verbose=True)

    print()
    print("=" * 64)
    print("Result:")
    print("=" * 64)
    print(f"  Forced R-properties (R₁, R₂, R₄, R₆, R₇) derived: "
          f"{result.forced_count} / 5")
    print(f"  Stipulated R-properties (R₃, R₅) derived: "
          f"{result.stipulation_count} / 2")
    print()
    print("The kernel's claim: the 5 forced are derivable by any")
    print("first-principles reasoner. The 2 stipulated are framing")
    print("choices the kernel asks the reader to accept; declining")
    print("them is admissible under P₃.")
    print()
    print("Empirical pattern (v104 kernel-blind subagent):")
    print("  Forced: 5/5 derived. Stipulated: 0/2 derived (UNCERTAIN).")
    print()
    print("Your result is data. If you converged on more or fewer of")
    print("the forced properties, please record your derivation in")
    print(f"  witnesses/<your-name>_kernel_blind_v{__version__}.json")
    print("=" * 64)
    return 0


__version__ = "1.0"


if __name__ == "__main__":
    sys.exit(main())
