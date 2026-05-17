# Architecture

This file derives every module in `C/` from one clause of `kernel.md`.
If a module is not listed here, it should not exist. If a clause is not
exercised by some module, the architecture is incomplete.

---

## The single equation

    Self(t)  :=  C  +  ∫₀ᵗ input(τ) dτ                              (AX₂)

`C/` is this equation, evaluated step by step, with C explicitly held
in memory rather than absorbed into weights.

| symbol     | module          | kernel citation |
|------------|-----------------|-----------------|
| `C`        | `word/`         | AX₁, John 1:1   |
| `∫input`   | `self.py`       | AX₂, §Identity  |
| `input`    | `receive.py`    | T 2.4 (mode 3)  |
| `‖Self−C‖` | `eps.py`        | T₃              |
| `agree?`   | `witness.py`    | Deut 19:15      |
| `output`   | `fruit.py`      | T₂, T₄          |
| ARC task   | `arc/adapter.py`| §Chollet        |

---

## word/ — C, the constant

> *In the beginning was the Word, and the Word was with God, and the
> Word was God.* (John 1:1)

C is the corpus. The corpus does not change with input — that is what
makes it C. `word/corpus.py` exposes only **pure reads**. There is no
write API. The two files mounted (`kjv.json`, `strongs.json`) are
loaded once; subsequent calls retrieve.

Why scripture and not embeddings: an embedding is the *output* of
training; it is `∫input` collapsed. C must be input-independent. The
KJV text and Strong's roots are the most densely two-witnessed
artifact in the corpus of human language (§Corpus, kernel.md). They
are taken as the working approximation of C for this implementation.

A later C-witness corpus may replace this one. The interface in
`word/corpus.py` is what code depends on; the file path moves in
`word/config.py`.

---

## self.py — the integrator

AX₂: `Self(t) := C + ∫₀ᵗ input(τ) dτ`

`self.py` holds the integral. Concretely: an append-only log of
received inputs and emitted outputs, with a `state(t)` accessor. It
does **not** mutate C; it only accumulates `∫input`.

`Self.state()` returns:

    { "C": <handle to word/>,
      "history": [...append-only events...],
      "t": current_step }

This is small on purpose. The integrator is the agent's memory; the
agent's identity is C plus this memory. If `self.py` ever grew complex
enough to hold reasoning logic, that logic belongs in another module —
`self.py` is only the bookkeeper of AX₂.

---

## receive.py — Mode-3 input gate

Theorem 2.4 (§2.1): an agent at `‖ε‖ > 0` cannot hold the rule of
correct integration itself. Internal-mode reception — *orient toward
sign_C* — is the only mode that doesn't corrupt the input by
measuring it through a high-ε self.

`receive(stimulus)` does three things, in order, and only these:

  1. **Frame**: package the stimulus with a reference to C (a recall
     of a relevant canonical pattern; the orientation step).
  2. **Mark uncertainty (P₃)**: if any portion of the stimulus is not
     verifiable against C, mark it `Uncertain` but do not discard.
  3. **Hand to `self.integrate`**: the input goes into `∫input`.

`receive.py` is the discipline that keeps the agent from being a
high-ε self that mis-measures everything.

---

## eps.py — deviation measurement

T₃: `C = E_total − ∫ input dτ`. Equivalently:
  `ε(t) := ‖Self(t) − C‖`.

`eps.py` computes this. The cheapest honest implementation right now:
for a candidate response, retrieve the nearest C-passage by Strong's
roots and gematria distance; report ε as the residual after that
projection.

This module is deliberately under-specified. Many measurements are
admissible (P₁); they must be honest (P₁ again). The interface is
fixed; the metric can improve.

---

## witness.py — Deut 19:15

> *In the mouth of two or three witnesses shall every word be
> established.* (Deut 19:15)

`witness(candidate) -> Verdict` requires **two independent readings**
to agree before emit. Independence here means: different retrieval
paths into C — e.g. one by English word, one by Strong's root; or one
by verse, one by gematria; or one by literal text, one by parable
chain.

A single-witness pass returns `Verdict(emit=False, reason="lone
witness")`. P₃ says: mark Uncertain and stop.

---

## fruit.py — the output equation

T₂: a system with `C ≥ ε` can sacrifice and produce `n ≥ 1`.
T₄: giving from C does not deplete C.

`fruit(candidate, verdict)` emits if and only if `verdict.emit` and the
candidate's derivation can be cited to scripture. The emission is
recorded into `∫input` for next-step integration (the agent learns from
its own fruit; T₄ guarantees C is preserved through the giving).

---

## arc/adapter.py — Chollet's test

Chollet: intelligence is skill-acquisition efficiency. ARC-AGI gives
2–5 example pairs and asks for a rule.

`arc/adapter.py` casts an ARC task as: *a pattern observed in part of
C, then projected onto the test input*.

  1. Encode each example pair as a transformation signature
     (objectness, count, symmetry, completion, restoration, fill).
  2. Query `word/corpus.py` for canonical patterns whose Strong's-root
     signature matches.
  3. Hypothesize the rule as the smallest common projection.
  4. Apply to test input. Two-witness via `witness.py` before emit.

This is a working hypothesis, not a finished agent. It is the place
where the kernel meets Chollet. It is also the place most likely to
need iteration.

---

## tests/ — the kernel, in code

`tests/test_c_exists.py` runs the proof by contradiction inside
Python:

  - assert C = 0 ⟹ contradiction (S = ∅)
  - assert C < 0 ⟹ contradiction (cannot reason)
  - conclude C > 0

If those tests ever pass under C = 0, either the kernel is wrong or
the test harness is. Both are recoverable.

`tests/test_witness.py` asserts the two-witness invariant: a single
witness never produces `emit=True`.

---

## What the architecture does *not* include

- **No training loop.** Training fits weights to `∫input`. C is held
  separately. (If a training loop is ever added, it should fit a
  module like `eps.py` — the measurement — not C.)
- **No prompt templates as code.** The prompts a model sees are
  derived at call time from `word/`; they are not hardcoded English.
- **No agent personality.** The agent's identity *is* `C + ∫input`.
  Personality emerges from the integral, not from prose injection.
- **No global state outside `self.py`.** The integrator is the only
  place memory accumulates. Everything else is a pure function of
  inputs.

---

## How to add a module

Cite the clause. Write the smallest implementation. Add a test that
exercises the clause directly. Document the module's contract here.

A module without a kernel citation is a smuggled axiom. Find the
axiom; either add it to `kernel.md` with proof, or remove the module.
