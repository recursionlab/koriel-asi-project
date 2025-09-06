# Transitional Topology — Drift Features and Phase Covers

This document defines drift features and phase covers for monitoring regime shifts in a transitional-topology framework.

## Drift feature set
1. Overlap mismatch `δ_pair` — average indicator of pairwise disagreements on overlaps.
2. Čech 1-cocycle presence — non-trivial cocycle on the cover nerve.
3. Descent success `χ_descent` ∈ {0,1}.
4. Nerve homology delta `Δβ` — change in Betti numbers across windows.
5. Cover churn `r` — refinements per window.
6. Protocol naturality residual `R_nat` — mean squared commuting-square gaps.
7. Adjunction residual `R_triangle` — mean residual of triangle identities.
8. Distributional drift (Wasserstein-1 or TV).
9. Phase reindex demand — fraction needing site change.
10. Time-to-failure proxy — hazard estimate.

## Phase cover family
- `U_Sheaf-Stable`: `δ_pair ≤ ε1` and `χ_descent = 1`.
- `U_Sheaf-Fragile`: small disagreements but still glues.
- `U_Descent-Fail`: `χ_descent = 0` or nontrivial 1-cocycle.
- `U_Proto-Shift`: `R_nat > τ_nat`.
- `U_Adjoint-Drift`: `R_triangle > τ_triangle`.
- `U_Data-Shift`: distributional drift > `τ_W`.
- `U_Cover-Turbulent`: `r > τ_r` or `|Δβ| > τ_β`.
- `U_Reindex`: fraction requiring reindexing > `τ_idx`.

## Alarm policy
- Soft alarm: any single feature crosses threshold.
- Hard alarm: descent failure, nontrivial 1-cocycle, two+ features cross, or simultaneous churn and homology change.
- Severity order: Descent-Fail > Reindex > Cover-Turbulent > Proto-Shift > Adjoint-Drift > Data-Shift > Sheaf-Fragile > Sheaf-Stable.

## Defaults
- `ε1 = 0`, `ε2 = 0.02`.
- `τ_nat = τ_triangle = 1e-3`.
- `τ_W = 0.1 × median intra-week W1`.
- `τ_r = 3`, `τ_β = 1`, `τ_idx = 0.1`.

## Diagnostics
Log minimal countercover, Čech obstruction certificate, offending morphisms, nerve homology before/after, asserted phase and predicates.

## Safety caps
Nerve depth ≤ 3; redact payloads; deterministic pair ordering.

## Minimal tests
Identity cover passes; synthetic mismatch yields Descent-Fail with witness; protocol non-naturality raises Proto-Shift.
