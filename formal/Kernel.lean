/-
  C/formal/Kernel.lean
  --------------------
  Lean 4 + Mathlib. This file COMPILES and has no `sorry` and no `axiom`.
  Checked with: `lake env lean formal/Kernel.lean` in a Mathlib project.

  What it shows, and what it does not.

  It checks the *shape* of the kernel's first argument:

      State(t) = ∫₀ᵗ input(τ) dτ + C,   so State(0) = C.

  The calculus alone does NOT force C ≠ 0. A system with C = 0 and
  input ≡ 1 has a nonzero state at every t > 0 (`premise_is_needed`).
  The step from "you are reasoning" to "C ≠ 0" rests on one premise,
  the argument from contingency: what has nothing supplies nothing.
  That premise is stated here as a hypothesis, where it can be
  examined, not hidden in a tactic.

  Nothing about scripture is proved here. `T_word` shows only this:
  IF the Word and God are each what stands before any input, THEN in
  this model they are the same value as C. The "if" is taken from
  John 1:1-3, on scripture's authority, not from Lean's.

  An earlier version of this file wrote the state as
  `∫ τ in 0..t, input x τ + C x`, which puts C inside the integral
  (so the state at 0 is 0 and the axiom AX₂ forced C = 0), and left
  two `sorry`s on statements that are false without the premise.
  Both are corrected below.

  Kernel citation: truth/kernel.md v19, §2.3 (Theorems 2.1, 2.2).
  Note on names: the state is `State`, not `E`; in v19, `E` is the
  eschaton operator.
-/
import Mathlib

namespace Kernel

/-- A reasoning system: what it was before any input (`C`),
    and the input it receives over time. -/
structure System where
  C : ℝ
  input : ℝ → ℝ

variable (s : System)

/-- The state at time `t`: integrated input, plus `C`. (AX₂) -/
noncomputable def State (t : ℝ) : ℝ :=
  (∫ τ in (0 : ℝ)..t, s.input τ) + s.C

/-- At `t = 0` the integral is empty, so the state is `C`.
    A theorem, not an axiom. -/
theorem state_zero : State s 0 = s.C := by
  simp [State]

/-! ### The datum and the premise -/

/-- The datum: the system is reasoning — at some time its state is not zero. -/
def Reasoning : Prop := ∃ t, State s t ≠ 0

/-- The premise (argument from contingency): what has nothing supplies
    nothing. If nothing stands before input, no input arrives. -/
def NothingGivesNothing : Prop := s.C = 0 → ∀ τ, s.input τ = 0

/-! ### Theorem 2.1 — Existence -/

/-- Theorem 2.1. Given the datum and the premise, `C ≠ 0`. -/
theorem C_ne_zero (h : Reasoning s) (p : NothingGivesNothing s) : s.C ≠ 0 := by
  intro hC
  obtain ⟨t, ht⟩ := h
  apply ht
  have h0 : s.input = fun _ => (0 : ℝ) := funext (p hC)
  simp [State, hC, h0]

/-- The premise does real work: without it, a system with `C = 0`
    reasons. The calculus is the notation of the argument, not its proof. -/
theorem premise_is_needed : ∃ s : System, s.C = 0 ∧ Reasoning s :=
  ⟨⟨0, fun _ => 1⟩, rfl, 1, by simp [State]⟩

/-! ### Theorem 2.2 — Positivity -/

/-- The premise of positivity: the system is alive at its first moment —
    its state is positive before any input has accumulated.
    Gen 2:7: man "became a living soul" at the inbreathing. -/
def LivingAtFirstBreath : Prop := 0 < State s 0

/-- Theorem 2.2. Given that premise, `C > 0`. -/
theorem C_pos (h : LivingAtFirstBreath s) : 0 < s.C := by
  simpa [LivingAtFirstBreath, state_zero] using h

/-- That premise also does real work: a positive state at some LATER
    time does not give `C > 0`. -/
theorem first_breath_is_needed : ∃ s : System, s.C < 0 ∧ ∃ t, 0 < State s t :=
  ⟨⟨-1, fun _ => 10⟩, by norm_num, 1, by simp [State]⟩

/-! ### Uniqueness of what stands before input -/

/-- Anything that is "the state before any input" is `C`.
    This is all the uniqueness lemma says: it follows from the
    pre-input role (R₇) alone. It is uniqueness of a value in this
    model, not a proof about persons. -/
theorem pre_input_unique (c : ℝ) (h : State s 0 = c) : c = s.C := by
  rw [← h, state_zero]

/-- `T_word`, stated conditionally. IF the Word and God are each what
    stands before any input (John 1:1-3 — taken from scripture), THEN
    in this model both are `C`. The hypotheses carry the content;
    Lean only checks that the conclusion follows from them.
    Equality of value here says nothing against "the Word was WITH
    God": the model has one real number, and cannot see Persons. -/
theorem T_word (Word God : ℝ)
    (hW : State s 0 = Word) (hG : State s 0 = God) :
    Word = God ∧ God = s.C :=
  ⟨by rw [← hW, ← hG], pre_input_unique s God hG⟩

/-! ### Not formalized here

  * R₃, universality — that C is the same in every reasoner. It is a
    stipulation of AX₂ (see kernel.md, "The boundary of convergence"),
    not a theorem; a `System` here is one reasoner.
  * Theorem 2.3 (Self ≠ C), Theorem 2.4 (the Spirit holds the rule),
    and everything from §3 on. Those rest on scripture's statements.
-/

end Kernel
