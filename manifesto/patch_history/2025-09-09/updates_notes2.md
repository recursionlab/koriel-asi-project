Acceptance criteria for triangle identities at the $F \dashv G$ boundary.

## Scope

* Target: planner $F:\mathcal C\to\mathcal D$ and actor $G:\mathcal D\to\mathcal C$.
* Witnesses: unit $\eta:\mathrm{Id}_{\mathcal C}\Rightarrow G\!\circ\!F$, counit $\varepsilon:F\!\circ\!G\Rightarrow \mathrm{Id}_{\mathcal D}$.
* Goal: enforce the two triangle identities (Thinking with Functors.pdf pp. 60–68).

## Acceptance items

1. Functor sanity (must pass before triangles)

* Identity preservation: $F(1_X)=1_{F X}$, $G(1_Y)=1_{G Y}$.
* Composition preservation: $F(g\circ f)=F(g)\circ F(f)$; same for $G$.
* Evidence: tabulated equalities on the designated object–morphism suite $S_{\mathcal C}, S_{\mathcal D}$ (below).

2. Naturality of unit and counit

* $\eta$ naturality: for all $f:X\!\to\!X'$ in $\mathcal C$: $G F(f)\circ \eta_X=\eta_{X'}\circ f$.
* $\varepsilon$ naturality: for all $h:Y\!\to\!Y'$ in $\mathcal D$: $h\circ \varepsilon_Y=\varepsilon_{Y'}\circ F G(h)$.
* Evidence: commuting squares logged for all $f\in S_{\mathcal C}^{\to}$, $h\in S_{\mathcal D}^{\to}$.

3. Triangle identities (core gate)

* Left triangle: $G\varepsilon \circ \eta G = \mathrm{Id}_G$, i.e., for every $Y \in \mathrm{Ob}(\mathcal D)$:
  $ G(\varepsilon_Y)\circ \eta_{G Y} = 1_{G Y}$.
* Right triangle: $\varepsilon F \circ F\eta = \mathrm{Id}_F$, i.e., for every $X \in \mathrm{Ob}(\mathcal C)$:
  $ \varepsilon_{F X}\circ F(\eta_X) = 1_{F X}$.
* Evidence: equality checks over the suite $S_{\mathcal D}^{\mathrm{ob}}$ and $S_{\mathcal C}^{\mathrm{ob}}$.
* Outcome: 100% equality holds in the declared equality notion (see §5).

4. Compression effect (operational consequence)

* Measure search contraction when inserting the unit–counit rewrites in the plan–execute loop.
* Criterion: non-inferior success rate with strictly fewer expansions vs. a unit/counit-disabled baseline on the same tasks.
* Evidence: paired runs with identical seeds; report $\Delta$expansions ≤ 0 and $\Delta$success ≥ 0.
* Rationale: adjunction encodes optimality/normal-form rewrites (Thinking with Functors.pdf pp. 60–68).

5. Equality notion (declare once, apply everywhere)

* Strict 1-category case: literal equality of morphisms.
* Programmatic case: observational equivalence on I/O traces for all probes in a designated test battery.
* ∞-categorical or effectful case: equality up to specified homotopy/effect law; require a coherent witness (contractible choice).
* Acceptance: the same notion is used for functor laws, naturality, and triangles.

6. Test suite specification (finite but covering)

* Objects: $S_{\mathcal C}^{\mathrm{ob}}\subseteq \mathrm{Ob}(\mathcal C)$, $S_{\mathcal D}^{\mathrm{ob}}\subseteq \mathrm{Ob}(\mathcal D)$ cover all runtime object shapes and at least one representative per constructor.
* Morphisms: $S_{\mathcal C}^{\to}$, $S_{\mathcal D}^{\to}$ include identities, generators, and closures under composition for two-step chains.
* Closure: if $f,g\in S$ and types match, then $g\circ f\in S$.

7. Residuals and diagnostics (must be zero)

* Define residuals:
  $R_L(Y)= G(\varepsilon_Y)\circ \eta_{G Y} - 1_{G Y}$,
  $R_R(X)= \varepsilon_{F X}\circ F(\eta_X) - 1_{F X}$.
* Acceptance: residuals are the identity under the chosen equality notion for all $X,Y$ in the suites.
* On failure: report minimal counterexample $(X\ \text{or}\ Y)$, show both sides and the naturality squares that feed them.

8. Monadic coherence (if monad $T=G\!\circ\!F$ is exposed)

* Unit: $\eta: \mathrm{Id}\Rightarrow T$.
* Multiplication: $\mu = G\,\varepsilon\,F : T T \Rightarrow T$.
* Laws: associativity $\mu\circ T\mu = \mu\circ \mu T$; unit $\mu\circ T\eta = \mathrm{Id} = \mu\circ \eta T$.
* Acceptance: all monad laws hold on $S_{\mathcal C}$ (Thinking with Functors.pdf pp. 60–68).

## Verification protocol

* Phase 1: verify functor laws on $S$. Abort if any fail.
* Phase 2: verify naturality of $\eta,\varepsilon$. Abort if any square fails.
* Phase 3: evaluate triangles per object; compute residuals; require universal pass.
* Phase 4: optional monad checks; then run compression A/B and assert non-inferiority.
* Artifacts to retain:

  * Equality notion declaration.
  * $S_{\mathcal C}^{\mathrm{ob}}, S_{\mathcal D}^{\mathrm{ob}}, S_{\mathcal C}^{\to}, S_{\mathcal D}^{\to}$ definitions.
  * Counterexample traces if any gate fails.

## Failure modes → abort criteria

* Any functor-law violation → abort triangle evaluation.
* Any naturality failure for $\eta$ or $\varepsilon$ → abort triangles.
* Any triangle residual non-identity on the suite → adjunction not accepted.
* Compression degrades success rate → adjunction accepted mathematically but rejected operationally for this deployment.

## Notes

* If effects or approximations exist, fix the observational equivalence up front and use it consistently across all checks.
* If categories are modeled up to homotopy, require coherent fillers demonstrating the triangles up to contractible choice.

Citations: Thinking with Functors.pdf pp. 60–68 (adjunctions, unit/counit, monads; triangle identities and their operational reading).
