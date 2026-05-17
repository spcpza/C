# Results

Honest measurements. P₁: M(x) = w(x). Updated on every commit that
changes a primitive.

## 2026-05-17 — initial baseline

ARC-AGI training split (400 tasks):

| metric           |   value | notes |
|------------------|--------:|-------|
| tasks            |     400 | all 400 attempted |
| task-attempted   |     320 | hypothesizer fired |
| task-solved      |       0 | exact-match on all test pairs |
| test-pairs solved|       0 | |
| test-pairs wrong |      96 | rule fired, applied, didn't match |
| test-pairs abstain|    320 | rule fired but primitive missing or wrong |

Primitive fire counts:

    sort_columns       111
    split_by_color      95
    flood_background    51
    complete_symmetry   42
    tile                21

### What this tells us

- The 7 canonical primitives in `arc/adapter.py` are stubs. The
  hypothesizer's heuristics fire on 80% of tasks but the primitives
  underneath are wrong for nearly all of them.
- The kernel architecture itself is intact: receive → eps → witness →
  fruit works end-to-end; tests pass; the corpus loads. ARC requires
  inductive bias the stubs do not yet carry.
- 0/400 is the floor. Future commits must move this or explain why.

### Path forward

The honest sequence:

1. Pick the highest-fire primitive (`sort_columns`, 111 hits).
2. Study the 111 tasks it fires on; identify the actual rule family.
3. Implement; re-run; record here.
4. Stop iterating a primitive only when its solved count plateaus.

This file is the project's scorecard. No commit may move a primitive
without updating this table.
