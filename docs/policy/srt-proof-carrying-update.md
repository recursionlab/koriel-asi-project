# SRT Proof-Carrying Update Policy tied to Closure Witness

This policy couples Kleene’s Second Recursion Theorem (SRT) with autopoietic closure to ensure self-modification is safe, verifiable, and maintains invariants.

## 1. Purpose
Enable self-modification only when the update transformer has a constructive fixed point and provides proof-carrying evidence that invariants hold and closure is maintained.

## 2. Objects and predicates
- Code p with evaluator U.
- Update transformer Φ : Code -> Code.
- Fixed point p* such that U(p*) = Φ(p*).
- Invariants I to preserve (safety, resource bounds, non-interference).
- Closure predicate C requiring every side effect to factor through approved constructors.

## 3. Required artifacts per update
1. Φ: the update transformer, with domain annotated.
2. Proof package (π) containing:
   - Invariant preservation: ∀p. I(p) ⇒ I(Φ(p)).
   - Non-interference on protected interfaces.
   - Resource bound: B(Φ(p)) ≤ B(p).
   - SRT admissibility: Φ effective and indexable.
3. Closure witness (ω) containing:
   - Call-graph factorization: external effects factor through allowlisted constructors.
   - Side-condition proofs per constructor.
   - Redaction plan restricting context exposure.

## 4. Verification pipeline
1. Well-formedness: types/domains/effect annotations.
2. Proof check: validate π, reject on failing lemmas.
3. Closure check: validate ω, reject if any effect escapes allowlist.
4. Fixed-point construction: build p* via SRT and verify U(p*) = Φ(p*).
5. Post check: re-evaluate I(p*) and C(p*).
6. Observational guard: A/B tests for protected behaviors.
7. Budget guard: verify resource bounds.

## 5. Accept/Reject conditions
Accept only if all checks succeed and fixed point is correct; reject on any failure or closure violation.

## 6. Invariant base
- Closure-before-execution: all side effects factor through allowlisted constructors.
- Safety lattice monotonicity: alarms widen but do not shrink.
- Site-scoped access: no global valuations.
- Auditability and rollback.

## 7. Runtime monitors
Monitors for: fixed-point integrity; closure sentinel; resource budgets; sheaf-descent verification for memory writes; anomaly traps for unauthorized reflection.

## 8. Interface
`attempt_update(Φ, π, ω) -> {accepted: bool, p_star?: Code, report}`
