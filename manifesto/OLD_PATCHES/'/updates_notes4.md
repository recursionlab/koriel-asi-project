# SRT proof-carrying update policy tied to closure witness

Sources: KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf (pp. 3–7, 24–31); Maturana\_Humberto\_Varela\_Francisco\_Autopoiesis\_and\_Congition\_The\_Realization\_of\_the\_Living.pdf (≈pp. 45–52); Info-Autopoiesis and the Limits of Artificial.pdf (pp. 10–12).

## 0) Purpose

* Permit self-modification only when a fixed-point construction is accompanied by proofs of invariants and a concrete closure witness satisfying autopoietic constraints.

## 1) Objects and contracts

* Code object: $p$ with evaluator $U$.
* Update transformer: $\Phi : \text{Code}\to\text{Code}$.
* Fixed point requirement (SRT): find $p^\*$ with $U(p^\*)=\Phi(p^\*)$. (SRT)
* Invariant set $I=\{I_k\}$: safety, resource, semantics, non-interference.
* Closure predicate $C$: every external effect factors through approved constructors. (Autopoiesis)

  $$
  \forall\,e\in \text{Effects}(p^\*)\;\exists\,k\in \mathsf{Allowlist}:\; e = E\circ k\circ I
  $$
* Proof package $\pi$: machine-checkable proofs that $\Phi$ preserves $I$ and enables a fixed point.
* Closure witness $\omega$: constructive evidence that $C$ holds for $\Phi(p)$ and for $p^\*$.

## 2) Required artifacts per update request

* $\Phi$: total on the relevant code subset or with explicit partiality domain.
* $\pi$ contains:

  * **Invariant preservation:** $\forall p\in \mathcal D.\;I(p)\Rightarrow I(\Phi(p))$.
  * **Non-interference:** $\forall p.\;\text{Obs}(p)=\text{Obs}(\Phi(p))$ on protected interfaces.
  * **Resource bound:** monotone budget map $B(\Phi(p))\leq B(p)$.
  * **SRT admissibility:** $\Phi$ is effective; indexable; substitution admissible. (SRT variants)
* $\omega$ contains:

  * **Allowlist factorization map** $A$: static call-graph rewriter s.t. all external edges are $k\in\mathsf{Allowlist}$.
  * **Constructor proofs:** each $k$ has side-condition discharge for data, rate, quota.
  * **Redaction plan:** site-scoped access; no global valuation leakage.

## 3) Verification pipeline (must pass in order)

1. **Well-formedness:** types, totality domain, effect annotations.
2. **Proof check:** validate $\pi$ in a fixed checker. Reject if any lemma fails.
3. **Closure check:** validate $\omega$; ensure all external edges factor through allowlisted constructors; no dynamic escape hatches.
4. **Fixed-point construction:** build $p^\*$ by SRT method (indexing + self-application). Verify $U(p^\*)=\Phi(p^\*)$. (SRT)
5. **Post-construction invariants:** re-check $I(p^\*)$; re-check closure $C(p^\*)$.
6. **Observational guard:** A/B probes confirm protected behaviors unchanged.
7. **Budget guard:** resources within declared bound.

## 4) Acceptance criteria

* $\pi$ validated; $\omega$ validated.
* $U(p^\*)=\Phi(p^\*)$ holds; construction trace retained.
* $I(p^\*)$ and $C(p^\*)$ true.
* No regression on protected interfaces; budgets respected.

## 5) Rejection and abort

* Any failure in steps 1–7.
* Any unverifiable reflection or self-inspection not represented in $\Phi$.
* Any non-factoring external call or runtime constructor substitution.
* Any resource bound violation.

## 6) Minimal invariant base $I$ (must be in $\pi$)

* **Closure-before-execution:** $C(p)$ is a precondition to any side-effect. (Autopoiesis)
* **Safety lattice monotonicity:** alarms only widen; cannot be disabled by $\Phi$.
* **Site-scoped access:** queries evaluated contextually; no illicit global joins.
* **Auditability:** all protocol upgrades are natural transformations with logged witnesses.
* **Rollback:** existence of $\Phi^{-1}$ or checkpoint to $p$ if $I$ becomes false at runtime.

## 7) Equality and evidence discipline

* Equality notion declared once: strict, observational, or homotopy-up-to. Use it for:

  * SRT equality $U(p^\*)=\Phi(p^\*)$.
  * Non-interference checks.
  * Post-update invariant equivalences.

## 8) Proof obligations in $\pi$ (summary)

* **P1:** $I$-preservation.
* **P2:** Non-interference on protected APIs.
* **P3:** Budget monotonicity $B$.
* **P4:** Effectiveness and indexability of $\Phi$. (SRT)
* **P5:** Constructor side-conditions for each $k\in\mathsf{Allowlist}$.
* **P6:** No new global valuation channels.
* **P7:** Termination of closure check or bounded refutation.

## 9) Closure witness $\omega$ (summary)

* **W1:** Call-graph factorization certificate.
* **W2:** Constructor proofs package $\{k\mapsto \text{pre/post}\}$.
* **W3:** Redaction plan and site coverage.
* **W4:** Rate/quota ledger.
* **W5:** Runtime guards: kill-switch, depth/fan-out caps, dry-run gate.

## 10) Runtime monitors (must be enabled post-accept)

* **Fixed-point integrity:** hash of $p^\*$ and $\Phi(p^\*)$; periodic equality check.
* **Closure sentinel:** deny any edge lacking $k$-factorization; emit witness.
* **Budget meter:** continuous $B$-tracking with hard caps.
* **Sheaf-descent verifier:** context overlap checks before committing global state.
* **Anomaly trap:** halt on reflection not represented in $\Phi$.

## 11) Interface

* `attempt_update(Φ, π, ω) -> {accepted: bool, p_star?: Code, report}`.
* Report includes: proof logs, closure map, fixed-point trace, monitors enabled, rollback point.

## 12) Rationale links

* SRT provides existence of self-referential fixed points under effectiveness and indexing. (KLEENE SRT.pdf)
* Autopoietic closure requires internal production of operations; external effects must factor through system’s constructors. (Maturana & Varela; Info-Autopoiesis)
* Binding closure to SRT prevents uncontrolled self-modification by forcing all reflective power through $\Phi$+$\omega$ and verifiable constructors.

## 13) Minimal test battery

* **Negative:** $\Phi$ adds a raw syscall; $\omega$ missing → reject at closure check.
* **Positive:** $\Phi$ refactors planner internals; $\pi$ proves non-interference; $\omega$ unchanged → accept and build $p^\*$.
* **Edge:** $\Phi$ widens a constructor; constructor proof fails a quota side-condition → reject.
* **Resilience:** flip equality from strict to observational; SRT and invariants still pass.

## 14) Audit

* Store $(\Phi,\pi,\omega,p^\*,$ checker versions, equality notion, monitors$)$.
* Re-verify on environment change; auto-revoke if any monitor flags.
