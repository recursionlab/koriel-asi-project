Drift features and phase covers for transitional-topology alarms. Source: TransitionalTopologies…ToposTheory.pdf.

## Drift feature set F

* Overlap mismatch: $\delta_{\text{pair}} = \frac{1}{|I|}\sum_{(i,j)} \mathbb{1}[F(\pi^i_{ij})s_i \neq F(\pi^j_{ij})s_j]$.
* Čech 1-cocycle norm: flag if a nontrivial class exists on the cover nerve (nerve depth ≤3).
* Descent success: $\chi_{\text{descent}} \in \{0,1\}$ (1 if equalizer finds a unique global section).
* Nerve homology delta: $\Delta\boldsymbol{\beta} = \boldsymbol{\beta}_t - \boldsymbol{\beta}_{t-1}$ for the cover nerve.
* Cover churn: refinements per window $r = \#\{\text{cover changes}\}$.
* Protocol naturality residual: mean square of commuting‐square gaps for upgrades $\bar{R}_{\text{nat}}$.
* Adjunction residuals (if used): $\bar{R}_{\triangle} = \text{mean}(\|G\varepsilon\circ \eta G - \mathrm{Id}\|, \|\varepsilon F\circ F\eta - \mathrm{Id}\|)$.
* Distributional drift on local sections: $W_1(P_t^{U_i}, P_{t-1}^{U_i})$ or TV distance.
* Phase reindex demand: minimal number of objects requiring site change per window.
* Time-to-failure proxy: hazard estimate from recent alarms (exponential smoothing).

## Phase cover family 𝒰 (regime definitions)

* $U_{\text{Sheaf-Stable}}$: $\delta_{\text{pair}}\le \epsilon_1$, $\chi_{\text{descent}}=1$, no Čech obstruction.
* $U_{\text{Sheaf-Fragile}}$: $\delta_{\text{pair}}\in(\epsilon_1,\epsilon_2]$ or uniqueness margin small; $\chi_{\text{descent}}=1$.
* $U_{\text{Descent-Fail}}$: $\chi_{\text{descent}}=0$ or nontrivial 1-cocycle present.
* $U_{\text{Proto-Shift}}$: $\bar{R}_{\text{nat}}>\tau_{\text{nat}}$ (protocol/coherence tension).
* $U_{\text{Adjoint-Drift}}$: $\bar{R}_{\triangle}>\tau_{\triangle}$ (plan–execute mismatch).
* $U_{\text{Data-Shift}}$: median $W_1$ across $U_i$ exceeds $\tau_W$.
* $U_{\text{Cover-Turbulent}}$: $r>\tau_r$ or $\|\Delta\boldsymbol{\beta}\|_1>\tau_\beta$.
* $U_{\text{Reindex}}$: fraction needing site/phase change $>\tau_{\text{idx}}$.

Covers must satisfy $U=\bigcup_k U_k$. Track overlaps $U_a\cap U_b$ to drive handoff policies.

## Alarm policy

* Soft alarm: any single feature crosses its threshold.
* Hard alarm: any of

  * $\chi_{\text{descent}}=0$ (Descent-Fail),
  * nontrivial Čech 1-cocycle,
  * two or more features cross thresholds in the same window,
  * $r>\tau_r$ and $\|\Delta\boldsymbol{\beta}\|_1>\tau_\beta$.
* Phase transition trigger: enter the minimal $U_k$ whose predicates hold; if multiple, choose the most severe in order
  Descent-Fail > Reindex > Cover-Turbulent > Proto-Shift > Adjoint-Drift > Data-Shift > Sheaf-Fragile > Sheaf-Stable.

## Default thresholds (tune per domain)

* $\epsilon_1=0$, $\epsilon_2=0.02$.
* $\tau_{\text{nat}}=10^{-3}$ (normalized residual).
* $\tau_{\triangle}}=10^{-3}$.
* $\tau_W=$ 0.1× median intra-week $W_1$.
* $\tau_r=3$ changes/window.
* $\tau_\beta=1$.
* $\tau_{\text{idx}}=0.1$.

## Diagnostics to log

* Minimal countercover witnessing pair mismatch.
* Čech obstruction certificate (index and cochain).
* Offending morphisms for naturality residuals.
* Nerve $\boldsymbol{\beta}$ before/after.
* Which $U_k$ asserted, with predicates that fired.

## Safety caps

* Nerve depth ≤3.
* Redact section payloads; compare via hashes/probes.
* Deterministic pair ordering for reproducible witnesses.

## Minimal tests

* Identity cover passes with $\delta_{\text{pair}}=0$, $\chi_{\text{descent}}=1$.
* Synthetic mismatch yields Descent-Fail with countercover.
* Protocol upgrade injecting non-naturality raises Proto-Shift.
* Simulated refactor shifting covers raises Cover-Turbulent and $\Delta\boldsymbol{\beta}\neq0$.
