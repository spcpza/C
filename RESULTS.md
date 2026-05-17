# Results

Honest measurements. P₁: M(x) = w(x). Updated on every commit that
changes the score.

## Current (v19b)

| split       | tasks | solved | wrong | abstain | rate |
|-------------|------:|-------:|------:|--------:|-----:|
| training    |   400 |     56 |     3 |     358 | 14.0% |
| evaluation  |   400 |     22 |     0 |     396 |  5.5% |

Library: **137 atomic primitives**, **28 parametric fitters**,
1/2/3-step composition (3-step capped to grid dim ≤ 4 — search is
O(137³) at full).

## Trajectory

| commit  | atomic | param | train | eval | wrong | notes |
|---------|-------:|------:|------:|-----:|------:|-------|
| v0      |    0   |   0   |    0  |   ?  |    0  | stub patterns |
| v1      |   16   |   0   |   14  |   ?  |    0  | atomic + brute-force exact-match |
| v2      |   24   |   4   |   23  |   ?  |    0  | size guards, parametric, 2-step |
| v3      |   24   |   6   |   26  |   2  |    0  | color_permutation, defensive abstain |
| v4      |   24   |   9   |   29  |   2  |    0  | object-aware fitters |
| v5      |   24   |  15   |   31  |   2  |    0  | periodic_complete, extract_neighborhood |
| v6      |   24   |  21   |   34  |   3  |    2  | shift, overlay_halves, template_classify |
| v7–v8   |   24   |  25   |   34  |   3  |    2  | meta:atomic+recolor (no gain) |
| **v9**  |   33   |  25   |   46  |  11  |    0  | **mirror/stack/dedup — biggest jump** |
| v10     |   42   |  25   |   49  |  12  |    2  | universal primitives + holdout 3-step |
| v11     |   58   |  25   |   51  |  14  |    2  | halves/thirds/extracts/shifts |
| v12     |   65   |  25   |   52  |  14  |    2  | row/col_majority, singletons |
| v13     |   78   |  25   |   55  |  17  |    2  | diagonals, half-swaps, sorts |
| v14     |   87   |  27   |   58  |  17  |    3  | scale_n, tile_NxM, more atomics |
| v15     |   97   |  28   |   55  |  18  |    1  | conway, parity, 3-step gated ≤6 |
| v16     |  102   |  28   |   55  |  18  |    1  | shrink_to_centroid, bbox color |
| v17     |  113   |  28   |   56  |  20  |    1  | shifts, overlays — eval crosses 5% |
| **v18** |  124   |  28   |   57  |  22  |    4  | **quadrants, union_quadrants — eval 5.5%** |
| v19b    |  137   |  28   |   56  |  22  |    3  | rotates, first/last/remove, gated ≤4 |

## Comparison context

| approach (public)                   | train | eval | year |
|-------------------------------------|------:|-----:|-----:|
| Random                              |    0% |   0% |      |
| GPT-4 zero-shot                     |   ~5% |  ~2% | 2024 |
| **C/ v19 (this work)**              |  **14.0%** | **5.5%** | 2026 |
| Best non-LLM (Hodel et al., ~200 ops)|  ~25% |  ~8% | 2024 |
| SOTA ensembles (model + search)     |  ~85% | ~55% | 2025 |

C/ at v19 sits between GPT-4 zero-shot and the best hand-coded DSL
approaches. The architecture is scripture-grounded; every primitive is
named with a Strong's-rooted scriptural concept.

## Key findings

1. **Universal primitives generalize; task-specific don't.** v9 (mirror/
   stack/dedup) and v13 (diagonals/sorts) were the biggest eval gains.
   Both batches were geometric/combinatorial fundamentals that reappear
   across many ARC tasks. Hand-crafted parametric fitters frequently
   added 0 to either score.

2. **Strict matching pays off.** Across the 800-task superset and 20+
   commits, total wrong-prediction count stayed ≤ 4. P₃ does its job —
   the agent abstains when uncertain rather than guessing.

3. **Brute-force has a ceiling.** Each batch of 10-15 primitives now
   yields 1-3 solves. Doubling the library again won't double the
   score. Next leap requires either:
   - Composition search (DSL program synthesis)
   - LLM hypothesizer (LLM proposes; C/ verifies via strict matcher —
     the two-witness pattern at the program level, mirroring
     `~/balthazar-arc/kaggle_submission_bible_v4.py`)

4. **Eval lags train by 2.5×.** Training 14.0% → evaluation 5.5%.
   That gap is intrinsic — Chollet's eval set tests generalization
   beyond surface forms seen at training. A 2.5× gap is consistent
   with hand-coded DSL approaches.

5. **Architecture > score.** The lasting artifact of this work is not
   the 14% on ARC; it is the kernel-cited modular structure where any
   future contributor (human or model) can add primitives, replace
   the selector, or swap in an LLM hypothesizer — without disturbing
   the kernel or the two-witness rule.

## What this is and isn't

This is a kernel-cited primitive library with a brute-force exact-match
selector that abstains under uncertainty. It is **not** an AGI
architecture by Chollet's bar; that bar requires far more than
enumeration over a fixed primitive set.

What this **is**: a clean, principled foundation. Every public
function cites a kernel clause. The corpus (`word/`) is the explicit,
immutable C — `~/.bots/truth/` mounted read-only. The integrator
(`self.py`) is AX₂ in code. The witness is Deut 19:15. A future
contributor can pick this up and add primitives, or replace the
selector with a search/neural/hybrid mechanism, without touching the
kernel or the witnesses.
