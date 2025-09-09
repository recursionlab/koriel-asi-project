Acknowledged. Adding a consolidated whitepaper patch.

````diff
diff --git a/docs/whitepaper/koriel-asi-synthesis.md b/docs/whitepaper/koriel-asi-synthesis.md
new file mode 100644
index 0000000..ffeed01
--- /dev/null
+++ b/docs/whitepaper/koriel-asi-synthesis.md
@@ -0,0 +1,260 @@
+# Koriel ASI — Category-Theoretic Architecture and Safety Synthesis
+
+## 1) ABSTRACT
+Koriel ASI organizes planning, execution, verification, memory, safety, and semantics via categorical structure and fixed-point laws. Objects are states/contexts; morphisms are controlled transformations; functors transfer models; adjunctions compress search; sheaves glue local contexts; quasicategories support homotopy-safe composition; Kleene’s SRT governs self-modification; autopoiesis enforces operational closure. We map these to system components and define contracts for: (i) adjunction triangle identities at the Planner–Actor boundary, (ii) a sheaf-descent verifier, (iii) an SRT proof-carrying update policy tied to closure witnesses, (iv) a HOAS planner DSL, and (v) transitional-topology drift alarms. Together they yield testable invariants for reliability under change and self-reference.
+
+## 2) CORPUS MAP (primary sources by file label)
+- **Thinking with Functors.pdf**: functors, naturality, adjunctions, monads (pp. 2, 4, 60–68).
+- **Higher Topos Theory.pdf**: sites, sheaves, descent, hyperdescent (Ch. 6–7).
+- **The 2-category theory of quasi-categories.pdf**; **Infinity category theory from scratch.pdf**: quasicats, homotopy 2-cat, fibrations.
+- **KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf**: SRT fixed points (pp. 3–7, 24–31).
+- **Reasoning with Higher-Order Abstract Syntax.pdf**; **Mathematical Structures in Language.pdf**: HOAS, CCC semantics.
+- **Maturana_Humberto_Varela_Francisco_Autopoiesis_and_Congition_The_Realization_of_the_Living.pdf**; **Info-Autopoiesis and the Limits of Artificial.pdf**: operational closure and info-autopoiesis.
+- **TransitionalTopologiesinAI-MappingHolographicInformationFlowThroughToposTheory.pdf**: phase-indexed sites and gluing across regimes.
+- Others: **Quantum Toposophy.pdf**, **Recursive Distinction Theory.pdf**, **AI-Optimized Learning & Meta-Recursive Intelligence.pdf**, **Structuring Knowledge.pdf**, **Knowledge Reproduction Processes.pdf**, **Riemannian Geometry framework.pdf**.
+
+## 3) SYNTHESIS (minimal shared ontology)
+**Objects** = states/contexts/types. **Morphisms** = policy/program transforms. **Functors** preserve structure; **natural transformations** are protocol upgrades. **Adjunction** \(F \dashv G\) = Plan ⊣ Execute with triangle laws. **Monads** \(T=GF\) encode iterate–refine. **Sheaves** over a site \((\mathcal C,J)\) enforce local-to-global consistency. **Quasicategories** provide homotopy-safe composition. **SRT** gives self-referential fixed points. **Autopoietic closure** restricts effects to allowlisted constructors.
+
+### ASCII concept graph
+```
+[Distinction]→[Objects]--morphisms-->[Objects]
+[Functors] & [NatTrans] → protocol coherence
+[Adjunction F⊣G] ⇒ [Compression] ⇒ [Monad T=GF]
+[Site(C,J)]⇒[Sheaf]⇒[Descent]⇒[Global Plan]
+[Quasicat]⇒[(co)cart. fibrations]  (dependency)
+[SRT]⇒[Self-mod Guard]   [Autopoiesis]⇒[Safety Boundary]
+[Riemann Metric]⇒[Geodesic Attention]  [Quantum Presheaf]⇒[Contextual Logic]
+```
+
+## 4) FORMAL FRAME (anchors)
+- **Adjunction laws** and triangle identities (Thinking with Functors.pdf pp. 60–68).
+- **Sheaf equalizer / Čech nerve** (Higher Topos Theory.pdf Ch. 6).
+- **Fixed points** for effective operators (KLEENE SRT.pdf).
+- **Operational closure** (Maturana & Varela; Info-Autopoiesis).
+- **Quasicategorical composition** up to homotopy; fibrations (2-cat quasicats; Infinity…from scratch).
+- **HOAS adequacy** in a CCC (HOAS; Mathematical Structures in Language).
+
+## 5) SYSTEM MAPPING
+- **Planner (F)**: left adjoint; unit-driven search contraction.
+- **Actor (G)**: right adjoint executor; counit minimality.
+- **Verifier**: sheaf/Čech descent gate on covers.
+- **Memory**: site with versioned sections; pullback-preserving updates.
+- **Safety**: autopoietic closure + allowlists; proof-carrying self-mods (SRT).
+- **Semantics**: quasicategorical/∞-topos layer; homotopy-stable goals.
+- **Monitoring**: transitional topology drift features and phase covers.
+
+## 6) INTERFACES AND CONTRACTS (normative)
+This whitepaper references canonical contracts split into focused docs:
+1. **Adjunction Triangle Acceptance Criteria** → `docs/contracts/adjunction-triangle-criteria.md`
+2. **Sheaf–Descent Verifier** → `docs/contracts/sheaf-descent-verifier.md`
+3. **SRT Proof-Carrying Update Policy (with Closure Witness)** → `docs/policy/srt-proof-carrying-update.md`
+4. **Planner DSL — HOAS Core** → `docs/dsl/planner-hoas-core.md`
+5. **Transitional Topology — Drift Features and Phase Covers** → `docs/monitoring/transitional-topology-alarms.md`
+
+## 7) EVALUATION DESIGN (minimal rigorous checks)
+**Adjoint compression**: enable unit/counit rewrites; assert non-inferior success and reduced expansions.  
+**Descent soundness**: identity cover passes; engineered mismatch produces countercover witness; pairwise-ok but no-global fails.  
+**SRT guard**: reject updates lacking proofs/closure witness; accept with proof and verify \(U(p^\*)=\Phi(p^\*)\).  
+**HOAS adequacy**: adversarial binding cases show zero capture.  
+**Homotopy robustness**: refactor-equivalent plans preserve outcomes.  
+**Phase alarms**: synthetic drift transitions trigger expected phase and diagnostics.
+
+## 8) SAFETY & GOVERNANCE
+Threats: prompt injection, reflection escape, illicit global valuations, runaway composition, phase-shift blind spots.  
+Controls: kill-switch, allowlists, quotas, site-scoped redaction, audit trails (naturality witnesses), SRT fixed-point wrapper, descent gate before global commits.
+
+## 9) RELATED WORK (labels)
+∞-topoi (Lurie), quasicategories (Joyal; Riehl–Verity), HOAS (Pfenning et al.), SRT (Kleene), autopoiesis (Maturana–Varela), quantum topos semantics (Isham–Butterfield line).
+
+## 10) BIBLIOGRAPHY (file labels; pages as anchors)
+- Thinking with Functors.pdf pp. 2, 4, 60–68  
+- Higher Topos Theory.pdf Ch. 6–7  
+- The 2-category theory of quasi-categories.pdf pp. 10–18, 28–36  
+- Infinity category theory from scratch.pdf pp. 3–7, 30–38  
+- KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf pp. 3–7, 24–31  
+- Reasoning with Higher-Order Abstract Syntax.pdf pp. 1–3, 10–12  
+- Mathematical Structures in Language.pdf pp. 210–240  
+- Maturana_Humberto_Varela_Francisco_Autopoiesis_and_Congition_The_Realization_of_the_Living.pdf pp. ~45–52  
+- Info-Autopoiesis and the Limits of Artificial.pdf pp. 10–12  
+- TransitionalTopologiesinAI-MappingHolographicInformationFlowThroughToposTheory.pdf pp. 28–36
+
+---
+
+## APPENDIX A — Glossary (selected)
+**Adjunction** \(F \dashv G\): unit \(\eta\), counit \(\varepsilon\); triangle identities; induces monad \(T=GF\).  
+**Sheaf**: presheaf with gluing/uniqueness on covers; equalizer/Čech conditions.  
+**Čech obstruction**: non-vanishing cocycle preventing descent.  
+**SRT**: existence of fixed points for effective operators; basis for proof-carrying self-mod.  
+**Autopoietic closure**: effects factor through self-produced constructors.  
+**HOAS**: object binding via meta-level binding; capture-free by construction.  
+**Quasicategory**: inner-horn fillers; composition up to homotopy.  
+**Transitional topology**: phase-indexed sites; alarms from drift features.
+
+## APPENDIX B — Cross-reference
+Adjunction↔Compression (Thinking with Functors) · Descent gate (HTT) · SRT+Closure (Kleene; M&V; Info-Autopoiesis) · HOAS adequacy (HOAS; MSiL) · Phase covers (Transitional Topologies).
+
+## APPENDIX C — Open Problems
+Sheaf-level counterexample synthesis; adjoint curriculum existence; bounded-resource SRT; homotopy-stable planning classes; learning phase covers from drift.
````

If you want me to bundle the multi-doc and whitepaper diffs into a single patchset, say “bundle both,” and I’ll emit one combined diff.


Here’s a single unified patch that adds all five contracts and the consolidated whitepaper to your repository. Apply this diff against the root of your repo to create the new documentation files:

````diff
diff --git a/docs/contracts/adjunction-triangle-criteria.md b/docs/contracts/adjunction-triangle-criteria.md
new file mode 100644
index 0000000..e372d3a
--- /dev/null
+++ b/docs/contracts/adjunction-triangle-criteria.md
@@ -0,0 +1,65 @@
+# Adjunction Triangle Acceptance Criteria (Planner F ⊣ Actor G)
+
+## Scope
+This document specifies the acceptance criteria for the adjunction between the Planner and Actor components in Koriel ASI. The planner is the left adjoint \(F : \mathcal{C} \to \mathcal{D}\) and the actor is the right adjoint \(G : \mathcal{D} \to \mathcal{C}\). The unit \(\eta : \mathrm{Id}_{\mathcal C} \Rightarrow G\!\circ\!F\) and counit \(\varepsilon : F\!\circ\!G \Rightarrow \mathrm{Id}_{\mathcal D}\) witness the adjunction.
+
+## 1. Functor sanity
+- **Identity preservation**: For any object \(X\) in \(\mathcal{C}\) and any object \(Y\) in \(\mathcal{D}\), the functors satisfy \(F(1_X) = 1_{F X}\) and \(G(1_Y) = 1_{G Y}\).
+- **Composition preservation**: For composable morphisms \(f,g\) in \(\mathcal{C}\), \(F(g\circ f) = F(g)\circ F(f)\). The same holds for \(G\) on morphisms in \(\mathcal{D}\).
+
+## 2. Naturality of unit and counit
+- **Unit naturality**: For any \(f : X \to X'\) in \(\mathcal{C}\), \(G F(f) \circ \eta_X = \eta_{X'} \circ f\).
+- **Counit naturality**: For any \(h : Y \to Y'\) in \(\mathcal{D}\), \(h \circ \varepsilon_Y = \varepsilon_{Y'} \circ F G(h)\).
+
+## 3. Triangle identities
+- **Left triangle**: \(G(\varepsilon_Y) \circ \eta_{G Y} = 1_{G Y}\) for all \(Y \in \mathrm{Ob}(\mathcal{D})\).
+- **Right triangle**: \(\varepsilon_{F X} \circ F(\eta_X) = 1_{F X}\) for all \(X \in \mathrm{Ob}(\mathcal{C})\).
+
+Residuals from these triangles must evaluate to the identity under the chosen equality notion (strict equality, observational equivalence, or homotopy equivalence).
+
+## 4. Compression effect
+When rewriting the plan–execute loop using the unit and counit, the search space should not degrade. Success rates must be non-inferior, and the number of expansions should decrease relative to a baseline without unit/counit rewrites.
+
+## 5. Equality notion
+Declare one notion of equality at the outset (strict, observational, or homotopy-up-to) and use it consistently in all checks.
+
+## 6. Test suite
+Choose finite suites of objects and morphisms that cover all constructors. Ensure arrow suites are closed under at least two-step composition.
+
+## 7. Monad coherence (optional)
+If the monad \(T = G\circ F\) is exposed, check unit and multiplication laws: associativity \( \mu \circ T\mu = \mu \circ \mu T \) and unit laws \(\mu \circ T\eta = \mathrm{Id} = \mu \circ \eta T\).
+
+## 8. Verification protocol
+1. Verify functor laws. Abort if any fail.  
+2. Check naturality of \(\eta\) and \(\varepsilon\). Abort on failure.  
+3. Check triangle identities. Abort if any residual is not identity.  
+4. Optionally verify monad laws.  
+5. Run an A/B test with unit/counit rewrites. Accept only if search is non-inferior and expansions decrease.
+
+## 9. Abort criteria
+Abort if any functor, naturality, or triangle check fails, or if the compression test degrades performance.
diff --git a/docs/contracts/sheaf-descent-verifier.md b/docs/contracts/sheaf-descent-verifier.md
new file mode 100644
index 0000000..f89ef2b
--- /dev/null
+++ b/docs/contracts/sheaf-descent-verifier.md
@@ -0,0 +1,101 @@
+# Sheaf–Descent Verifier Contract and Overlap Diagnostics
+
+This document defines the contract for a sheaf-descent verifier that checks the sheaf condition on covers of a site and reports detailed diagnostics when descent fails.
+
+## Inputs
+- **U**: Object in the site \(\mathcal C\).
+- **Cover**: Finite family \(\{u_i : U_i \to U\} \in J(U)\) in the Grothendieck topology.
+- **Locals**: Tuple \(\mathbf{s} = (s_i)\) with each \(s_i \in F(U_i)\), where \(F\) is the presheaf or sheaf.
+- **Eq**: Equality predicate (strict, observational, or homotopy-up-to).
+- **Mode**: Either `sheaf` (equalizer check) or `hyper` (hyperdescent check).
+
+## Outputs
+- `status`: `pass` or `fail`.  
+- `global`: Glued section \(s \in F(U)\) if passing; `null` if none exists.  
+- `witness`: Diagnostics record for failures.  
+- `uniqueness`: `true` if the global section is unique under `Eq`; otherwise `false`.  
+- `depth_checked`: 2 for equalizer checks; ≥3 for hyperdescent checks.
+
+## Preconditions
+- Restriction maps of \(F\) are functorial: \(F(\mathrm{id}_U) = \mathrm{id}_{F(U)}\) and \(F(g\circ f) = F(f)\circ F(g)\).  
+- Fiber products \(U_{ij} = U_i\times_U U_j\) (and higher overlaps) exist as needed.
+
+## Sheaf equalizer condition
+1. **Pairwise agreement**: For each \((i,j)\), the restrictions of \(s_i\) and \(s_j\) to \(U_{ij}\) agree under `Eq`.  
+2. **Existence/uniqueness**: A unique global section \(s\) exists with \(F(u_i)(s) = s_i\) for all \(i\).
+
+## Overlap diagnostics
+- **pair_matrix**: Records each \((i,j)\) with left-hand and right-hand restrictions and their agreement result.  
+- **triple_coherence**: When `mode` is `hyper`, checks triple overlaps.  
+- **nerve_depth**: Depth of overlaps inspected (2 in sheaf mode).  
+- **minimal_countercover**: Minimal subcover responsible for failure.  
+- **cause**: One of {`PAIR_MISMATCH`, `NO_GLOBAL`, `NON_UNIQUE`, `FUNCTORIALITY_FAIL`}.
+
+## Witness rules
+- `PAIR_MISMATCH`: Include offending \((i,j)\) and the mismatched restrictions.  
+- `NO_GLOBAL`: Provide reconstruction trace or Čech obstruction.  
+- `NON_UNIQUE`: Provide two distinct global sections with identical restrictions.  
+- `FUNCTORIALITY_FAIL`: Specify the morphism pair violating functoriality.
+
+## Verification algorithm
+**Sheaf mode**:  
+1. Compute all \(U_{ij}\) and test agreements. If any fail → `fail` with `PAIR_MISMATCH`.  
+2. Solve the equalizer for a global \(s\). If none exists → `fail` with `NO_GLOBAL`.  
+3. If multiple \(s\) exist under `Eq` → `fail` with `NON_UNIQUE`.  
+4. Otherwise → `pass`.
+
+**Hyper mode**:  
+Extend checks to triples and higher overlaps via Čech cochains; require vanishing obstructions up to configured depth.
+
+## Acceptance and rejection
+Acceptance requires functoriality, pairwise agreement, a global section, uniqueness, and no diagnostics.  
+Reject if any verification step fails.
+
+## Complexity and safety
+Pairwise checks are \(O(m^2)\) for \(m\) cover elements; hyper checks can grow to \(O(m^3)\). Limit nerve depth to 3, redact payloads (hash or probe), and use deterministic ordering.
diff --git a/docs/policy/srt-proof-carrying-update.md b/docs/policy/srt-proof-carrying-update.md
new file mode 100644
index 0000000..272a95a
--- /dev/null
+++ b/docs/policy/srt-proof-carrying-update.md
@@ -0,0 +1,109 @@
+# SRT Proof-Carrying Update Policy tied to Closure Witness
+
+This policy couples Kleene’s Second Recursion Theorem (SRT) with autopoietic closure to ensure that self-modification in Koriel ASI is safe, verifiable, and maintains invariants.
+
+## 1. Purpose
+Enable self-modification only when the update transformer has a constructive fixed point and provides proof-carrying evidence that invariants hold and closure is maintained.
+
+## 2. Objects and predicates
+- **Code** \(p\) with evaluator \(U\).  
+- **Update transformer** \(\Phi : \mathrm{Code} \to \mathrm{Code}\).  
+- **Fixed point** \(p^*\) such that \(U(p^*) = \Phi(p^*)\).  
+- **Invariants** \(I\) to preserve (safety, resource bounds, non-interference).  
+- **Closure predicate** \(C\) requiring every side effect to factor through approved constructors.
+
+## 3. Required artifacts per update
+1. **\(\Phi\)**: The update transformer, with domain annotated.  
+2. **Proof package (\(\pi\))** containing:  
+   * Invariant preservation: \( \forall p \in \mathrm{dom}(\Phi).\, I(p) \Rightarrow I(\Phi(p)) \).  
+   * Non-interference: Observations on protected interfaces remain unchanged.  
+   * Resource bound: \(B(\Phi(p)) \leq B(p)\).  
+   * SRT admissibility: \(\Phi\) is effective and indexable.  
+3. **Closure witness (\(\omega\))** containing:  
+   * Call-graph factorization: all external effects factor through allowlisted constructors.  
+   * Side-condition proofs for each constructor (data, rate, quota).  
+   * Redaction plan restricting context exposure to allowed scopes.
+
+## 4. Verification pipeline
+1. **Well-formedness**: Check types, domains, and effect annotations.  
+2. **Proof check**: Validate \(\pi\). Reject on any failing lemma.  
+3. **Closure check**: Validate \(\omega\). Reject if any effect escapes the allowlist.  
+4. **Fixed-point construction**: Construct \(p^*\) via SRT and verify \(U(p^*) = \Phi(p^*)\).  
+5. **Post-invariant and closure checks**: Re-evaluate \(I(p^*)\) and \(C(p^*)\).  
+6. **Observational guard**: A/B test to ensure protected behaviors are unchanged.  
+7. **Budget guard**: Verify resource bounds.
+
+## 5. Accept/Reject conditions
+Accept only if all checks succeed and the fixed point is correct. Reject on any failure, inadmissible \(\Phi\), closure violation, or resource overrun.
+
+## 6. Invariant base
+- **Closure-before-execution**: All side effects factor through allowlisted constructors.  
+- **Safety lattice monotonicity**: Alarms may widen but never shrink.  
+- **Site-scoped access**: No global valuations; queries must be context-restricted.  
+- **Auditability**: All upgrades must have naturality witnesses.  
+- **Rollback**: Provide a way to revert if invariants are violated.
+
+## 7. Runtime monitors
+Implement monitors for:  
+- Fixed-point integrity (hash equality of \(p^*\) and \(\Phi(p^*)\)).  
+- Closure sentinel (block non-factorized calls).  
+- Resource budgets.  
+- Sheaf-descent verification for memory writes.  
+- Anomaly traps for unauthorized reflection.
+
+## 8. Interface
+`attempt_update(Φ, π, ω) -> {accepted: bool, p_star?: Code, report}`
diff --git a/docs/dsl/planner-hoas-core.md b/docs/dsl/planner-hoas-core.md
new file mode 100644
index 0000000..a5eae79
--- /dev/null
+++ b/docs/dsl/planner-hoas-core.md
@@ -0,0 +1,139 @@
+# Planner DSL — HOAS Core
+
+This document defines the core constructs for the Koriel ASI planning language using Higher-Order Abstract Syntax (HOAS). It provides a minimal sound foundation where all binders are meta-level functions.
+
+## Types
+- **Value types**: `Unit`, `Bool`, `Int`, …  
+- **Logical type**: `Prop`  
+- **World type**: `State`  
+- **Action type**: `Action α` (returns an `α`)  
+- **Plan type**: `Plan`  
+- **Goal type**: `Goal`  
+- **Resource type**: `Budget`  
+- **Effort type**: `Eff`
+
+## Judgments
+- **Typing**: `Γ ⊢ e : τ`.  
+- **Hoare**: `Γ ⊢ {P} p {Q}` with predicates \(P,Q : \text{State} \to \text{Prop}\).
+
+## Primitive operations (meta-level binders in bold)
+- `pure : α → Plan` — return a value without side effects.  
+- `act : Action α → (**α → Plan**) → Plan` — execute an action and bind its result.  
+- `seq : Plan → Plan → Plan` — sequential composition.  
+- `choose : Plan → Plan → Plan` — nondeterministic choice.  
+- `par : Plan → Plan → Plan` — parallel composition with resource checks.  
+- `fix : (**Plan → Plan**) → Plan` — guarded recursion.  
+- `if_ : Prop → Plan → Plan → Plan` — conditional.  
+- `when : Prop → Plan` — guard.  
+- `observe : Sensor α → (**α → Plan**) → Plan` — measurement binder.  
+- `assume : Prop → Plan` — add an assumption.  
+- `assert : Prop → Plan` — assertion.  
+- `goal : Goal → Plan` — start a goal.  
+- `ensure : (**State → Prop**) → Plan` — enforce a postcondition.  
+- `local : (**State → Plan**) → Plan` — scoped state thread.  
+- `withMem : (**Mem → Plan**) → Plan` — scoped memory region.  
+- `call : Tool α → Req → Witness → (**α → Plan**) → Plan` — external call with allowlist witness.  
+- `withBudget : Budget → Plan → Plan` — resource budgeting.  
+- `meter : (**Eff → Plan**) → Plan` — expose effort or curvature samples.
+
+## Value layer
+- `lam : (**α → β**) → (α ⇒ β)` — function abstraction.  
+- `app : (α ⇒ β) → α → β` — function application.  
+- Standard pairs, sums, and unit types.
+
+## Typing rules (examples)
+- **Act-bind**: If `Γ ⊢ a : Action α` and `Γ, x:α ⊢ k x : Plan`, then `Γ ⊢ act a k : Plan`.  
+- **Seq**: If `Γ ⊢ p : Plan` and `Γ ⊢ q : Plan`, then `Γ ⊢ seq p q : Plan`.  
+- **If**: If `Γ ⊢ P : Prop`, `Γ ⊢ p : Plan`, and `Γ ⊢ q : Plan`, then `Γ ⊢ if_ P p q : Plan`.
+
+## Hoare logic (examples)
+- **Act-bind**: If `Γ ⊢ {P} a {R}` and \(\forall v.\, Γ ⊢ {R v} k v {Q}\), then `Γ ⊢ {P} act a k {Q}`.  
+- **Seq**: If `Γ ⊢ {P} p {R}` and `Γ ⊢ {R} q {Q}`, then `Γ ⊢ {P} seq p q {Q}`.
+
+## Equational laws
+- Associativity: `seq (seq p q) r ≡ seq p (seq q r)`.  
+- Identity: `seq (pure v) p ≡ p`.  
+- `act` behaves like monadic bind over `Action`.
+
+## Safety invariants
+- All `call` invocations must supply a valid witness for allowlisted external calls.  
+- `fix` must be productivity-guarded.  
+- `par` requires a resource split that balances the budget.
+
+## Derived combinators
+Using the primitives, one can define higher-level operations like `while`, `repeatUntil`, and `try` via `fix`, `seq`, `if_`, etc.
diff --git a/docs/monitoring/transitional-topology-alarms.md b/docs/monitoring/transitional-topology-alarms.md
new file mode 100644
index 0000000..df60cbd
--- /dev/null
+++ b/docs/monitoring/transitional-topology-alarms.md
@@ -0,0 +1,113 @@
+# Transitional Topology — Drift Features and Phase Covers
+
+This document defines drift features and phase covers for monitoring regime shifts in a transitional-topology framework. It allows systems to detect and respond to changes in information-flow topology.
+
+## Drift feature set
+1. **Overlap mismatch** \(\delta_{\text{pair}}\): Average indicator of pairwise disagreements when restricting local sections to overlaps.  
+2. **Čech 1-cocycle presence**: Flag if a non-trivial 1-cocycle exists on the Čech nerve.  
+3. **Descent success** \(\chi_{\text{descent}} \in \{0,1\}\): 1 if the sheaf equalizer finds a unique global section.  
+4. **Nerve homology delta** \(\Delta\boldsymbol{\beta}\): Change in Betti numbers of the cover nerve across windows.  
+5. **Cover churn** \(r\): Number of cover changes per window.  
+6. **Protocol naturality residual** \(\bar{R}_{\text{nat}}\): Mean squared residual of naturality checks on protocol upgrades.  
+7. **Adjunction residual** \(\bar{R}_{\triangle}\): Mean residual of the adjunction triangle identities.  
+8. **Distributional drift**: Wasserstein-1 or total variation on local section distributions.  
+9. **Phase reindex demand**: Fraction of objects needing a site or phase change.  
+10. **Time-to-failure proxy**: Hazard estimate from recent alarms.
+
+## Phase cover family
+* **\(U_{\text{Sheaf-Stable}}\)**: \(\delta_{\text{pair}}\le \epsilon_1\) and \(\chi_{\text{descent}}=1\).  
+* **\(U_{\text{Sheaf-Fragile}}\)**: Small pairwise disagreements but still glues.  
+* **\(U_{\text{Descent-Fail}}\)**: \(\chi_{\text{descent}}=0\) or non-trivial 1-cocycle.  
+* **\(U_{\text{Proto-Shift}}\)**: \(\bar{R}_{\text{nat}} > \tau_{\text{nat}}\).  
+* **\(U_{\text{Adjoint-Drift}}\)**: \(\bar{R}_{\triangle} > \tau_{\triangle}\).  
+* **\(U_{\text{Data-Shift}}\)**: Distributional drift exceeds \(\tau_W\).  
+* **\(U_{\text{Cover-Turbulent}}\)**: Cover churn \(r>\tau_r\) or \(|\Delta\boldsymbol{\beta}|>\tau_\beta\).  
+* **\(U_{\text{Reindex}}\)**: Fraction requiring reindexing exceeds \(\tau_{\text{idx}}\).
+
+## Alarm policy
+* **Soft alarm**: Any single feature crossing its threshold triggers a soft alarm.  
+* **Hard alarm**: Descent failure, non-trivial 1-cocycle, two or more features crossing thresholds, or simultaneous cover churn and homology change.  
+Severity order: Descent-Fail > Reindex > Cover-Turbulent > Proto-Shift > Adjoint-Drift > Data-Shift > Sheaf-Fragile > Sheaf-Stable.
+
+## Default thresholds
+* \(\epsilon_1=0\), \(\epsilon_2=0.02\).  
+* \(\tau_{\text{nat}}=\tau_{\triangle}=10^{-3}\).  
+* \(\tau_W=0.1\times\) median intra-week Wasserstein-1.  
+* \(\tau_r=3\) cover changes per window.  
+* \(\tau_\beta=1\).  
+* \(\tau_{\text{idx}}=0.1\).
+
+## Diagnostics
+Record the minimal countercover witnessing pair mismatch, Čech obstruction certificate (index and cochain), offending morphisms for naturality residuals, nerve homology before/after, asserted phase, and activated predicates.
+
+## Safety caps
+* Limit nerve depth to 3.  
+* Redact section payloads via hashing/probing.  
+* Use deterministic ordering for reproducible diagnostics.
+
+## Minimal test suite
+* **Identity cover**: No drift features fire; descent passes.  
+* **Synthetic mismatch**: Pair mismatches trigger Descent-Fail.  
+* **Protocol upgrade**: Non-naturality residual triggers Proto-Shift.  
+* **Refactor**: Cover/homology shifts trigger Cover-Turbulent.
diff --git a/docs/whitepaper/koriel-asi-synthesis.md b/docs/whitepaper/koriel-asi-synthesis.md
new file mode 100644
index 0000000..7e440fc
--- /dev/null
+++ b/docs/whitepaper/koriel-asi-synthesis.md
@@ -0,0 +1,178 @@
+# Koriel ASI — Category-Theoretic Architecture and Safety Synthesis
+
+## 1) ABSTRACT
+Koriel ASI organizes planning, execution, verification, memory, safety, and semantics via categorical structure and fixed-point laws. Objects are states/contexts; morphisms are controlled transformations; functors transfer models; adjunctions compress search; sheaves glue local contexts; quasicategories support homotopy-safe composition; Kleene’s SRT governs self-modification; autopoiesis enforces operational closure. We map these to system components and define contracts for adjunction triangle identities, a sheaf-descent verifier, an SRT proof-carrying update policy, a HOAS planner DSL, and transitional-topology drift alarms. Together they yield testable invariants for reliability under change and self-reference.
+
+## 2) CORPUS MAP
+The corpus spans categorical algebra, ∞-topos theory, quasicategories, recursion theory, autopoiesis, HOAS, and phase-topology. Key files include: Thinking with Functors (adjunctions/monads), Higher Topos Theory (sites/sheaves/descent), The 2-category theory of quasi-categories and Infinity category theory from scratch (quasicategories), Kleene’s SRT (self-reference), Reasoning with HOAS and Mathematical Structures in Language (binding), Maturana & Varela and Info-Autopoiesis (closure), and Transitional Topologies in AI (phase-indexed sites).
+
+## 3) SYNTHESIS
+**Objects** = states, contexts, types; **Morphisms** = transformations/programs.  
+**Functors** preserve structure; **natural transformations** are protocol upgrades.  
+**Adjunction** \(F \dashv G\) defines Plan ⊣ Execute; triangle identities compress search.  
+**Monads** encode iterate–refine cycles.  
+**Sheaves** and **descent** glue local data into global plans.  
+**Quasicategories** support composition up to homotopy; fibrations encode dependencies.  
+**Kleene’s SRT** gives fixed points for self-referential programs.  
+**Autopoietic closure** restricts effects to self-produced components.
+
+### ASCII concept graph
+```
+[Distinction]→[Objects]--morphisms-->[Objects]
+[Functors] & [NatTrans] → protocol coherence
+[Adjunction F⊣G] ⇒ [Compression] ⇒ [Monad T=GF]
+[Site(C,J)]⇒[Sheaf]⇒[Descent]⇒[Global Plan]
+[Quasicat]⇒[(co)cart. fibrations]  (dependency)
+[SRT]⇒[Self-mod Guard]   [Autopoiesis]⇒[Safety Boundary]
+[Riemann Metric]⇒[Geodesic Attention]  [Quantum Presheaf]⇒[Contextual Logic]
+```
+
+## 4) FORMAL FRAME
+The architecture rests on: (i) adjunction laws and triangle identities (see Adjunction criteria doc); (ii) sheaf equalizers and Čech nerve for descent (see Sheaf–Descent verifier); (iii) SRT fixed-point construction and proof-carrying updates with closure witnesses; (iv) autopoietic closure constraints; (v) quasicategorical composition and fibrations; and (vi) HOAS for capture-free binding.
+
+## 5) SYSTEM MAPPING
+- **Planner (F)**: Left adjoint constructing plans; unit \(\eta\) contracts search.  
+- **Actor (G)**: Right adjoint executing plans; counit \(\varepsilon\) ensures minimal effects.  
+- **Verifier**: Sheaf descent gate; fails on local overlap disagreements.  
+- **Memory**: Site with versioned covers; functorial updates.  
+- **Safety**: Autopoietic closure plus allowlists; SRT proof-carrying update policy.  
+- **Semantics**: Quasicategorical/∞-topos layer; homotopy-stable goals.  
+- **Monitoring**: Transitional-topology drift features and phase alarms.
+
+## 6) INTERFACES AND CONTRACTS
+The following documentation provides normative interfaces and checks:  
+1. **Adjunction criteria** → `docs/contracts/adjunction-triangle-criteria.md`.  
+2. **Sheaf-descent verifier** → `docs/contracts/sheaf-descent-verifier.md`.  
+3. **SRT update policy** → `docs/policy/srt-proof-carrying-update.md`.  
+4. **HOAS planner DSL** → `docs/dsl/planner-hoas-core.md`.  
+5. **Drift monitoring** → `docs/monitoring/transitional-topology-alarms.md`.
+
+## 7) EVALUATION DESIGN
+Tests to run now include:  
+* **Adjoint compression**: A/B tests with and without unit/counit rewrites; success rates must not decrease, and search expansions must shrink.  
+* **Descent soundness**: Identity covers pass; mismatched covers produce counterexamples; no-global or non-unique cases are caught.  
+* **SRT guard**: Reject updates lacking proof/closure; accept when fixed points and invariants are validated.  
+* **HOAS adequacy**: Adversarial binding cases yield no capture failures.  
+* **Homotopy robustness**: Refactor-equivalent plans yield identical outcomes.  
+* **Phase alarms**: Synthetic drifts trigger the expected phase and diagnostic output.
+
+## 8) SAFETY AND GOVERNANCE
+Threats include prompt injection, reflection escapes, illicit global valuations, runaway composition, and mis-detected regime shifts. Controls: kill-switch, allowlists, quotas, context redaction, naturality witnesses, SRT proof wrappers, sheaf descent checks, and drift alarms.
+
+## 9) RELATED WORK
+∞-topoi (Lurie); quasicategories (Joyal; Riehl–Verity); HOAS (Pfenning et al.); SRT (Kleene); autopoiesis (Maturana & Varela); quantum topos semantics (Isham–Butterfield); phase-topology frameworks.
+
+## 10) BIBLIOGRAPHY
+Primary references include:  
+* Thinking with Functors.pdf pp. 2, 4, 60–68.  
+* Higher Topos Theory.pdf Ch. 6–7.  
+* The 2-category theory of quasi-categories.pdf pp. 10–18, 28–36.  
+* Infinity category theory from scratch.pdf pp. 3–7, 30–38.  
+* KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf pp. 3–7, 24–31.  
+* Reasoning with Higher-Order Abstract Syntax.pdf pp. 1–3, 10–12.  
+* Mathematical Structures in Language.pdf pp. 210–240.  
+* Maturana & Varela — Autopoiesis and Cognition pp. ~45–52.  
+* Info-Autopoiesis and the Limits of Artificial.pdf pp. 10–12.  
+* TransitionalTopologiesinAI-MappingHolographicInformationFlowThroughToposTheory.pdf pp. 28–36.
+
+---
+
+### Glossary (selected terms)
+**Adjunction**: Functors \(F\) and \(G\) with unit and counit satisfying triangle identities; yields compression and monads.  
+**Sheaf**: Presheaf with gluing and uniqueness on covers; equalizer or Čech nerve conditions.  
+**Čech obstruction**: Non-vanishing cocycle preventing descent.  
+**SRT**: Existence of fixed points for effective operators; used for self-modification.  
+**Autopoietic closure**: All effects factor through self-produced constructors.  
+**HOAS**: Encoding of object-level binding by meta-level functions; ensures capture-free substitution.  
+**Quasicategory**: Simplicial set with inner horn fillers; composition up to homotopy.  
+**Transitional topology**: Phase-indexed sites; drift features and phase covers detect regime shifts.
````

This patch creates all the necessary markdown files in your `docs/` directory and populates them with the contracts and whitepaper synthesis. You can apply the patch using `git apply` or similar.
