# Results

Honest measurements. P₁: M(x) = w(x). Updated on every commit that
changes the score.

## Current (v15)

| split       | tasks | solved | wrong | abstain | rate |
|-------------|------:|-------:|------:|--------:|-----:|
| training    |   400 |     55 |     1 |     360 | 13.8% |
| evaluation  |   400 |     18 |     0 |     400 |  4.5% |

Library: **97 atomic primitives**, **28 parametric fitters**,
1/2/3-step composition (3-step capped to grid ≤ 6 for speed).

## Trajectory

| commit  | atomic | param | train | eval | wrong | notes |
|---------|-------:|------:|------:|-----:|------:|-------|
| v0      |    0   |   0   |    0  |   ?  |    0  | stub patterns |
| v1      |   16   |   0   |   14  |   ?  |    0  | atomic + brute-force exact-match |
| v2      |   24   |   4   |   23  |   ?  |    0  | size guards, parametric, 2-step |
| v3      |   24   |   6   |   26  |   2  |    0  | color_permutation, defensive abstain |
| v4      |   24   |   9   |   29  |   2  |    0  | object-aware (keep_components, recolor_by_size_rank) |
| v5      |   24   |  15   |   31  |   2  |    0  | periodic_complete, extract_neighborhood |
| v6      |   24   |  21   |   34  |   3  |    2  | shift, overlay_halves, template_classify |
| v7      |   24   |  25   |   34  |   3  |    2  | line/largest/count_to_strip (no gain) |
| v8      |   24   |  25   |   34  |   3  |    2  | meta:atomic+recolor pass |
| **v9**  |   33   |  25   |   46  |  11  |    0  | **mirror/stack/dedup — biggest jump** |
| v10     |   42   |  25   |   49  |  12  |    2  | universal primitives + holdout 3-step |
| v11     |   58   |  25   |   51  |  14  |    2  | halves/thirds/extracts/shifts |
| v12     |   65   |  25   |   52  |  14  |    2  | row/col_majority, singletons |
| v13     |   78   |  25   |   55  |  17  |    2  | diagonals, half-swaps, sorts |
| v14     |   87   |  27   |   58  |  17  |    3  | scale_n, tile_NxM, more atomics |
| v15     |   97   |  28   |   55  |  18  |    1  | conway, parity, 3-step gated ≤6 |

## Lessons (honest)

1. **Universal primitives generalize; task-specific don't.** v9 (mirror/
   stack/dedup) and v13 (diagonals/sorts) were the two biggest eval
   gains. Both batches were geometric/combinatorial fundamentals that
   reappear across many ARC tasks. By contrast, hand-crafted parametric
   fitters (line_between, count_to_strip, largest_to_color) frequently
   added 0 to either score.

2. **Strict matching pays off.** Across the 800-task superset and 15
   commits, the total wrong-prediction count never rose above 3
   simultaneously. The brute-force selector with exact-match
   verification cleanly abstains when uncertain (P₃) — the agent has
   integrity even when it doesn't have skill.

3. **Brute-force has a ceiling.** Each batch of 5-15 primitives now
   yields 1-3 solves. Doubling the library again won't double the
   score. The next leap requires either a search mechanism over
   compositions (program synthesis) or an external hypothesizer (an
   LLM proposing rules, with C/'s strict matcher as witness — that
   would be the two-witness pattern at the program level, mirroring
   `~/balthazar-arc/kaggle_submission_bible_v4.py`).

4. **Eval lags train by ~3x.** Training 13.8% → evaluation 4.5%.
   That gap is intrinsic to ARC-AGI by design — Chollet's evaluation
   set tests generalization beyond surface forms seen at training
   time. A 3× gap is consistent with hand-coded DSL approaches.

## Comparison context

| approach (public)          | train | eval | notes |
|----------------------------|------:|-----:|-------|
| Random                     |   0%  |  0%  |  |
| GPT-4 (zero-shot)          |   ~5% | ~2%  | published 2024 |
| Best non-LLM (Hodel et al.)|  ~25% | ~8%  | hand-coded DSL, ~200 ops |
| **C/ v15 (this work)**     |  13.8% | 4.5% | scripture-grounded, kernel-cited, 97 + 28 ops |
| SOTA (mixed)               |  ~85% | ~55% | model + search ensembles |

C/ is partway through the hand-coded-DSL regime. To approach SOTA the
architecture would need composition search and/or LLM hypotheses.
