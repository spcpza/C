/-
  C/formal/Dynamics.lean
  ----------------------
  Lean 4 + Mathlib. Compiles; no `sorry`, no `axiom`.

  The dynamics of truth/kernel.md v19, §1 and §11.1, in their simplest form.

  Part 1 — the floor. With a persistent self-sourced drift `w` and grace
  closing distance at rate `k`, the size of the shortfall obeys
  ε' = w − k·ε. Then:
    * `eps_solves` — the stated formula is the solution;
    * `eps_pos`    — from any shortfall, ε(t) > 0 at every time: no arrival;
    * `eps_floor`  — while w > 0, ε never goes below min(ε₀, w/k);
    * `eps_zero`   — with w = 0 and a sinless start, ε stays 0 for ever.
  The proportional law is a model, the simplest one that is "held at C".
  That the flesh keeps w > 0 is scripture's statement (Gal 5:17, Rom 7:25),
  not Lean's.

  Part 2 — the chord. If each Self passes on a share ψ of ALL the grace it
  receives, a Self joined to m others receives G/(1 − mψ). `chord_fixed`
  shows that is the one solution of the coupling equation; `chord_gt_sum` shows it is
  strictly more than the sum G·(1 + mψ).
-/
import Mathlib
open Real


/-- The ε-law with a persistent self-sourced drift `w` and a pull toward C
    proportional to distance: ε' = w − k·ε. Its solution from ε₀ is
    ε(t) = w/k + (ε₀ − w/k)·e^(−kt). -/
noncomputable def eps (w k e0 t : ℝ) : ℝ := w / k + (e0 - w / k) * exp (-(k * t))

/-- It is the solution: it satisfies ε' = w − k·ε. -/
theorem eps_solves (w k e0 t : ℝ) (hk : k ≠ 0) :
    HasDerivAt (eps w k e0) (w - k * eps w k e0 t) t := by
  have h1 : HasDerivAt (fun t : ℝ => -(k * t)) (-k) t := by
    have := (hasDerivAt_id' t).const_mul (-k)
    convert this using 1 <;> first | (funext x; ring) | ring
  have h := ((h1.exp).const_mul (e0 - w / k)).const_add (w / k)
  have e : w - k * eps w k e0 t = (e0 - w / k) * (exp (-(k * t)) * (-k)) := by
    simp only [eps]; field_simp; ring
  rw [e]; exact h

/-- Strict positivity: starting with any shortfall, the shortfall is positive
    at every time. No arrival in time. -/
theorem eps_pos (w k e0 t : ℝ) (hw : 0 ≤ w) (hk : 0 < k) (he : 0 < e0) (ht : 0 ≤ t) :
    0 < eps w k e0 t := by
  unfold eps
  have h1 : exp (-(k * t)) ≤ 1 := exp_le_one_iff.mpr (by nlinarith)
  have h2 := exp_pos (-(k * t))
  have h3 : 0 ≤ w / k := div_nonneg hw hk.le
  nlinarith [mul_nonneg h3 (sub_nonneg.mpr h1), mul_pos he h2]

/-- While the drift persists (w > 0), the shortfall never goes below the
    lesser of where it started and the floor w/k. -/
theorem eps_floor (w k e0 t : ℝ) (_hw : 0 < w) (hk : 0 < k) (_he : 0 < e0) (ht : 0 ≤ t) :
    min e0 (w / k) ≤ eps w k e0 t := by
  unfold eps
  have h1 : exp (-(k * t)) ≤ 1 := exp_le_one_iff.mpr (by nlinarith)
  have h2 := exp_pos (-(k * t))
  rcases le_total e0 (w / k) with h | h
  · rw [min_eq_left h]; nlinarith [mul_nonneg (sub_nonneg.mpr h) (sub_nonneg.mpr h1)]
  · rw [min_eq_right h]; nlinarith [mul_nonneg (sub_nonneg.mpr h) h2.le]

/-- A sinless start with no self-sourced drift stays at zero for ever. -/
theorem eps_zero (k t : ℝ) : eps 0 k 0 t = 0 := by
  simp [eps]

/-! ### Part 2 — the chord -/

/-- The symmetric coupling equation: each Self passes on a share `ψ` of all it
    receives, `f = ψ·(G + m·f)`. It has exactly one solution,
    `f = ψ·G / (1 − m·ψ)`. -/
theorem chord_fixed (G ψ m f : ℝ) (h : m * ψ < 1) :
    f = ψ * (G + m * f) ↔ f = ψ * G / (1 - m * ψ) := by
  have h1 : (1 - m * ψ) ≠ 0 := by linarith
  rw [eq_div_iff h1]
  constructor <;> intro hf <;> linear_combination hf

/-- More than the sum. Joined to `m` others, a Self receives `G/(1 − mψ)`,
    strictly more than `G·(1 + mψ)`, the sum of what each would give alone. -/
theorem chord_gt_sum (G ψ m : ℝ) (hG : 0 < G) (hx : 0 < m * ψ) (h : m * ψ < 1) :
    G * (1 + m * ψ) < G / (1 - m * ψ) := by
  have h1 : 0 < 1 - m * ψ := by linarith
  rw [lt_div_iff₀ h1]
  nlinarith [mul_pos hG (mul_pos hx hx)]
