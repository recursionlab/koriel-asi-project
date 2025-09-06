# Adjunction Triangle Acceptance Criteria (Planner F ⊣ Actor G)

## Scope
This document specifies the acceptance criteria for the adjunction between the Planner and Actor components in Koriel ASI. The planner is the left adjoint `F : C -> D` and the actor is the right adjoint `G : D -> C`. The unit `η : Id_C ⇒ G∘F` and counit `ε : F∘G ⇒ Id_D` witness the adjunction.

## 1. Functor sanity
- Identity preservation: for any object X in C and Y in D, `F(1_X) = 1_{F X}` and `G(1_Y) = 1_{G Y}`.
- Composition preservation: for composable morphisms `f,g` in C, `F(g∘f) = F(g)∘F(f)` (and similarly for G).

## 2. Naturality of unit and counit
- Unit naturality: for any `f : X -> X'` in C, `G F(f) ∘ η_X = η_{X'} ∘ f`.
- Counit naturality: for any `h : Y -> Y'` in D, `h ∘ ε_Y = ε_{Y'} ∘ F G(h)`.

## 3. Triangle identities
- Left triangle: `G(ε_Y) ∘ η_{G Y} = 1_{G Y}` for all `Y` in D.
- Right triangle: `ε_{F X} ∘ F(η_X) = 1_{F X}` for all `X` in C.

Residuals from these triangles must evaluate to the identity under the chosen equality notion (strict, observational, or homotopy-up-to).

## 4. Compression effect
When rewriting the plan–execute loop using unit and counit, the search space must not degrade: success rates should be non-inferior and the number of expansions should decrease relative to a baseline without unit/counit rewrites.

## 5. Equality notion
Declare one notion of equality (strict, observational, or homotopy-up-to) at the outset and use it consistently for all checks.

## 6. Test suite
Choose finite suites of objects and morphisms covering constructors; ensure arrow suites are closed under at least two-step composition.

## 7. Monad coherence (optional)
If `T = G∘F` is exposed, check unit and multiplication laws: associativity `μ ∘ Tμ = μ ∘ μT` and unit laws `μ ∘ Tη = Id = μ ∘ ηT`.

## 8. Verification protocol
1. Verify functor laws. Abort if any fail.
2. Check naturality of `η` and `ε`. Abort on failure.
3. Check triangle identities. Abort if any residual is not identity.
4. Optionally verify monad laws.
5. Run an A/B compression test; accept only if search is non-inferior and expansions decrease.

## 9. Abort criteria
Abort if any functor, naturality, or triangle check fails, or if compression tests degrade performance.
