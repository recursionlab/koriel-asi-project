Proceeding. Here is a PR-ready unified diff adding the five docs.

```diff
diff --git a/docs/contracts/adjunction-triangle-criteria.md b/docs/contracts/adjunction-triangle-criteria.md
new file mode 100644
index 0000000..a1a1a1a
--- /dev/null
+++ b/docs/contracts/adjunction-triangle-criteria.md
@@ -0,0 +1,132 @@
+# Adjunction Triangle Acceptance Criteria (Planner F ⊣ Actor G)
+Source: Thinking with Functors.pdf pp. 60–68.
+
+## Scope
+Planner \(F:\mathcal C\to\mathcal D\), Actor \(G:\mathcal D\to\mathcal C\).
+Unit \(\eta:\mathrm{Id}_{\mathcal C}\Rightarrow G\!\circ\!F\); Counit \(\varepsilon:F\!\circ\!G\Rightarrow \mathrm{Id}_{\mathcal D}\).
+
+## 1) Functor sanity
+Identity: \(F(1_X)=1_{F X}\), \(G(1_Y)=1_{G Y}\).
+Composition: \(F(g\!\circ\!f)=F(g)\!\circ\!F(f)\); similarly for \(G\).
+
+## 2) Naturality of unit/counit
+\(\forall f:X\!\to\!X':\; G F(f)\circ \eta_X=\eta_{X'}\circ f\).
+\(\forall h:Y\!\to\!Y':\; h\circ \varepsilon_Y=\varepsilon_{Y'}\circ F G(h)\).
+
+## 3) Triangle identities (gate)
+Left: \(G(\varepsilon_Y)\circ \eta_{G Y}=1_{G Y}\;\forall Y\).
+Right: \(\varepsilon_{F X}\circ F(\eta_X)=1_{F X}\;\forall X\).
+Residuals \(R_L,R_R\) must equal identity under the declared equality notion.
+
+## 4) Compression effect
+Insert unit/counit rewrites in the plan–execute loop.
+Acceptance: success rate non-inferior; expansions strictly fewer vs baseline.
+
+## 5) Equality notion (declare once)
+Strict morphism equality, or observational equivalence, or homotopy-up-to with coherent witnesses. Use the same notion for all checks.
+
+## 6) Test suite
+Object suites \(S_{\mathcal C}^{ob},S_{\mathcal D}^{ob}\) cover constructors.
+Arrow suites \(S_{\mathcal C}^{\to},S_{\mathcal D}^{\to}\) closed under two-step composition.
+
+## 7) Monadic coherence (if \(T=G\!\circ\!F\) exposed)
+Unit \(\eta:\mathrm{Id}\Rightarrow T\). Multiplication \(\mu=G\,\varepsilon\,F:T T\Rightarrow T\).
+Laws: \(\mu\circ T\mu=\mu\circ \mu T\); \(\mu\circ T\eta=\mathrm{Id}=\mu\circ \eta T\).
+
+## 8) Verification protocol
+Phase 1: functor laws → Phase 2: naturality → Phase 3: triangles → Phase 4: monad (opt) + A/B compression.
+
+## 9) Abort criteria
+Any functor/naturality/triangle failure, or operational degradation in compression test.
diff --git a/docs/contracts/sheaf-descent-verifier.md b/docs/contracts/sheaf-descent-verifier.md
new file mode 100644
index 0000000..b2b2b2b
--- /dev/null
+++ b/docs/contracts/sheaf-descent-verifier.md
@@ -0,0 +1,148 @@
+# Sheaf–Descent Verifier Contract and Overlap Diagnostics
+Source: Higher Topos Theory.pdf, Ch. 6.
+
+## Inputs
+`U` object; `Cover` \(\{u_i:U_i\!\to\!U\}\in J(U)\); `Locals` \((s_i\in F(U_i))\);
+`Eq` equality predicate (strict/observational/homotopy); `Mode` = {`sheaf`,`hyper`}.
+
+## Outputs
+`status` {pass,fail}; `global` \(s\in F(U)\) or null; `witness` diagnostics; `uniqueness` flag; `depth_checked`.
+
+## Preconditions
+Restriction functoriality: \(F(\mathrm{id})=\mathrm{id}\), \(F(g\!\circ\!f)=F(f)\!\circ\!F(g)\).
+Fiber products \(U_{ij}\) (and \(U_{ijk}\) for `hyper`) exist.
+
+## Sheaf equalizer form
+Pairwise agreement: \(F(\pi_{ij}^i)(s_i)=_{Eq}F(\pi_{ij}^j)(s_j)\) in \(F(U_{ij})\).
+Existence/uniqueness: \(F(U)\to \prod_i F(U_i)\rightrightarrows \prod_{i,j}F(U_{ij})\) is an equalizer.
+
+## Overlap diagnostics
+`pair_matrix` for all \((i,j)\) with lhs/rhs/ok;
+`triple_coherence` for \((i,j,k)\) if `hyper`;
+`nerve_depth` recorded;
+`minimal_countercover` and `cause` ∈ {PAIR_MISMATCH, NO_GLOBAL, NON_UNIQUE, FUNCTORIALITY_FAIL}.
+
+## Witness rules
+PAIR_MISMATCH: emit offending \((i,j)\) and restricted sections.
+NO_GLOBAL: emit reconstruction trace or Čech obstruction representative.
+NON_UNIQUE: emit two distinct \(s,s'\) with identical restrictions.
+FUNCTORIALITY_FAIL: emit violating morphism pair.
+
+## Algorithms
+Sheaf mode: Pair stage → Glue stage → Unique stage.
+Hyper mode: Čech nerve up to configured degree; require vanishing obstructions.
+
+## Equality discipline
+One `Eq` used consistently across all stages.
+
+## Acceptance
+Functoriality holds; pairs agree; global exists and is unique; diagnostics empty.
+
+## Rejection
+Any functoriality failure, pair mismatch, no-global, or non-uniqueness.
+
+## Complexity and safety
+Pair stage \(O(m^2)\); optional triples \(O(m^3)\). Cap `nerve_depth`≤3; redact payloads; deterministic pair order.
+
+## Minimal tests
+Identity cover passes; engineered mismatch fails with countercover; pairwise-ok but no-global fails; constructed non-unique fails.
diff --git a/docs/policy/srt-proof-carrying-update.md b/docs/policy/srt-proof-carrying-update.md
new file mode 100644
index 0000000..c3c3c3c
--- /dev/null
+++ b/docs/policy/srt-proof-carrying-update.md
@@ -0,0 +1,162 @@
+# SRT Proof-Carrying Update Policy tied to Closure Witness
+Sources: KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf (pp. 3–7, 24–31);
+Maturana & Varela, *Autopoiesis and Cognition* (~pp. 45–52);
+Info-Autopoiesis and the Limits of Artificial.pdf (pp. 10–12).
+
+## Purpose
+Allow self-modification only with an SRT fixed-point and machine-checkable proofs of invariants plus a concrete closure witness.
+
+## Objects
+Code \(p\) with evaluator \(U\); transformer \(\Phi\); fixed point \(p^\*\) s.t. \(U(p^\*)=\Phi(p^\*)\).
+Invariant set \(I\); closure predicate \(C\) enforcing allowlisted constructor factorization.
+
+## Required artifacts
+\(\Phi\) (total on domain); proof package \(\pi\) with I-preservation, non-interference, resource bound, SRT-admissibility;
+closure witness \(\omega\) with call-graph factorization, constructor side-conditions, redaction plan.
+
+## Pipeline
+Well-formedness → Proof check \(\pi\) → Closure check \(\omega\) → Build \(p^\*\) (SRT) →
+Post-invariants \(I(p^\*), C(p^\*)\) → Observational guard → Budget guard.
+
+## Accept / Reject
+Accept only if all pass and \(U(p^\*)=\Phi(p^\*)\).
+Reject on any failure, unverifiable reflection, non-factoring calls, or budget violations.
+
+## Minimal invariant base \(I\)
+Closure-before-execution; safety lattice monotonicity; site-scoped access; auditability via natural transformations; rollback.
+
+## Runtime monitors
+Fixed-point integrity; closure sentinel; budget meter; sheaf-descent verifier; anomaly trap.
+
+## Interface
+`attempt_update(Φ, π, ω) -> {accepted: bool, p_star?: Code, report}`.
diff --git a/docs/dsl/planner-hoas-core.md b/docs/dsl/planner-hoas-core.md
new file mode 100644
index 0000000..d4d4d4d
--- /dev/null
+++ b/docs/dsl/planner-hoas-core.md
@@ -0,0 +1,140 @@
+# Planner DSL — HOAS Core
+Sources: Reasoning with Higher-Order Abstract Syntax.pdf; Mathematical Structures in Language.pdf.
+
+## Types
+`Unit | Bool | Int | … | Prop | State | Action α | Plan | Goal | Budget | Eff`.
+
+## Judgments
+Typing `Γ ⊢ e:τ`; Hoare `Γ ⊢ {P} p {Q}` with \(P,Q:State→Prop\).
+Adequacy: object substitution = meta β-reduction (HOAS).
+
+## Primitives (meta-level binders in **bold**)
+`pure : α→Plan`
+`act  : Action α → (**α→Plan**) → Plan`
+`seq  : Plan → Plan → Plan`
+`choose : Plan → Plan → Plan`
+`par  : Plan → Plan → Plan`
+`fix  : (**Plan→Plan**) → Plan`
+`if_ : Prop → Plan → Plan`
+`when : Prop → Plan`
+`observe : Sensor α → (**α→Plan**) → Plan`
+`assume : Prop → Plan`
+`assert : Prop → Plan`
+`goal : Goal → Plan`
+`ensure : (**State→Prop**) → Plan`
+`local : (**State→Plan**) → Plan`
+`withMem : (**Mem→Plan**) → Plan`
+`call : Tool α → Req → Witness → (**α→Plan**) → Plan`  // allowlisted only
+`withBudget : Budget → Plan → Plan`
+`meter : (**Eff→Plan**) → Plan`
+
+## Value layer
+`lam : (**α→β**) → (α⇒β)`; `app : (α⇒β) → α → β`; pairs/sums/unit as usual.
+
+## Typing rules (sketch)
+Act-bind, Seq, If, Ensure, Call-with-witness; HOAS ensures capture-free binding.
+
+## Hoare rules (examples)
+Act-bind and Seq standard; Choose is angelic or demonic per setting.
+
+## Equational laws
+`seq` associative; `pure` left/right identities; `act` is monadic bind over `Action`.
+
+## Safety invariants
+All `call` sites require valid `Witness`; `fix` guarded; `par` requires budget split.
+
+## Derived combinators
+`while`, `repeatUntil`, `try` defined from primitives.
diff --git a/docs/monitoring/transitional-topology-alarms.md b/docs/monitoring/transitional-topology-alarms.md
new file mode 100644
index 0000000..e5e5e5e
--- /dev/null
+++ b/docs/monitoring/transitional-topology-alarms.md
@@ -0,0 +1,156 @@
+# Transitional Topology — Drift Features and Phase Covers
+Source: TransitionalTopologiesinAI-MappingHolographicInformationFlowThroughToposTheory.pdf.
+
+## Drift features F
+Overlap mismatch \(\delta_{\text{pair}}\);
+Čech 1-cocycle presence;
+Descent success \(\chi_{\text{descent}}\);
+Nerve homology delta \(\Delta\boldsymbol{\beta}\);
+Cover churn \(r\);
+Protocol naturality residual \(\bar{R}_{\text{nat}}\);
+Adjunction residual \(\bar{R}_{\triangle}\);
+Distributional drift \(W_1\) or TV;
+Phase reindex demand; hazard estimate.
+
+## Phase cover family
+\(U_{\text{Sheaf-Stable}}\): \(\delta_{\text{pair}}\le \epsilon_1\), \(\chi_{\text{descent}}=1\).
+\(U_{\text{Sheaf-Fragile}}\): small disagreements; still glues.
+\(U_{\text{Descent-Fail}}\): \(\chi_{\text{descent}}=0\) or nontrivial 1-cocycle.
+\(U_{\text{Proto-Shift}}\): \(\bar{R}_{\text{nat}}>\tau_{\text{nat}}\).
+\(U_{\text{Adjoint-Drift}}\): \(\bar{R}_{\triangle}>\tau_{\triangle}\).
+\(U_{\text{Data-Shift}}\): median \(W_1>\tau_W\).
+\(U_{\text{Cover-Turbulent}}\): \(r>\tau_r\) or \(\|\Delta\boldsymbol{\beta}\|_1>\tau_\beta\).
+\(U_{\text{Reindex}}\): fraction needing site change \(>\tau_{\text{idx}}\).
+
+## Alarm policy
+Soft alarm: any feature crosses threshold.
+Hard alarm: \(\chi_{\text{descent}}=0\), or nontrivial 1-cocycle, or ≥2 features cross, or \(r>\tau_r\) **and** \(\|\Delta\boldsymbol{\beta}\|_1>\tau_\beta\).
+Severity order: Descent-Fail > Reindex > Cover-Turbulent > Proto-Shift > Adjoint-Drift > Data-Shift > Sheaf-Fragile > Sheaf-Stable.
+
+## Defaults
+\(\epsilon_1=0\), \(\epsilon_2=0.02\);
+\(\tau_{\text{nat}}=\tau_{\triangle}=10^{-3}\);
+\(\tau_W=0.1\times\) median intra-week \(W_1\);
+\(\tau_r=3\); \(\tau_\beta=1\); \(\tau_{\text{idx}}=0.1\).
+
+## Diagnostics
+Minimal countercover; Čech obstruction cert; offending morphisms; nerve \(\boldsymbol{\beta}\) before/after; asserted phase and predicates.
+
+## Safety caps
+Nerve depth ≤3; payload redaction; deterministic pair ordering.
+
+## Minimal tests
+Identity cover passes; synthetic mismatch fails with witness; protocol non-naturality raises Proto-Shift; refactor shifts covers and \(\Delta\boldsymbol{\beta}\neq0\).
```

If you need a single consolidated whitepaper diff instead, say “single file” and I’ll emit it.
