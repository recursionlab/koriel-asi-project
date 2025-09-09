Acceptance: define the planner DSL as a HOAS-encoded, simply-typed core where all binders are meta-level functions. Primitives below are sufficient and orthogonal. Sources: Reasoning with HOAS.pdf; Mathematical Structures in Language.pdf.

## Types

* Value types: `α, β ::= Unit | Bool | Int | …`
* Logical: `Prop`
* World: `State`
* Actions: `Action α`  (returns `α`)
* Plans: `Plan`
* Goals: `Goal`
* Resources: `Budget`
* Effects/metrics (optional): `Eff`

## Judgments

* Typing: `Γ ⊢ e : τ`
* Hoare: `Γ ⊢ {P} p {Q}` with `P,Q : State → Prop`
* Adequacy (HOAS): object-level substitution = meta-level β-reduction (Reasoning with HOAS.pdf)

## Core HOAS primitives (constructors; meta-level binders in bold)

* Pure and monadic core

  * `pure : α → Plan`                                   // no effect
  * `act  : Action α → ( **α → Plan** ) → Plan`         // bind action result
  * `seq  : Plan → Plan → Plan`                         // serial composition
  * `choose : Plan → Plan → Plan`                       // nondeterministic choice
  * `par  : Plan → Plan → Plan`                         // parallel (with resource checks)
  * `fix  : ( **Plan → Plan** ) → Plan`                 // guarded recursion on plans

* Control and observation

  * `if_ : Prop → Plan → Plan → Plan`
  * `when : Prop → Plan → Plan`
  * `observe : Sensor α → ( **α → Plan** ) → Plan`      // measurement binder
  * `assume : Prop → Plan → Plan`
  * `assert : Prop → Plan`

* Goal interface

  * `goal : Goal → Plan`
  * `ensure : ( **State → Prop** ) → Plan`              // postcondition binder

* State-scoped binding

  * `local : ( **State → Plan** ) → Plan`               // scoped state thread
  * `withMem : ( **Mem → Plan** ) → Plan`               // module‐local memory region

* Safety and tools (closure-aware)

  * `call : Tool α → Req → Witness → ( **α → Plan** ) → Plan`
    • requires allowlist witness; no raw external edges

* Resources/metrics

  * `withBudget : Budget → Plan → Plan`
  * `meter : ( **Eff → Plan** ) → Plan`                 // exposes effort/curvature sample

## Minimal value layer (for HOAS adequacy)

* `lam : ( **α → β** ) → (α ⇒ β)`; `app : (α ⇒ β) → α → β`
* Pairs, sums, unit as usual; no explicit “fresh” operator (freshness via meta-binder) (Reasoning with HOAS.pdf; CCC basis in Mathematical Structures in Language.pdf)

## Typing rules (sketch)

* `Γ ⊢ a : Action α`, `Γ, x:α ⊢ k x : Plan` ⇒ `Γ ⊢ act a k : Plan`
* `Γ ⊢ p:Plan, q:Plan` ⇒ `Γ ⊢ seq p q : Plan`
* `Γ ⊢ P:Prop, p:Plan, q:Plan` ⇒ `Γ ⊢ if_ P p q : Plan`
* `Γ ⊢ S:State→Prop, Γ ⊢ ensure S : Plan`
* `Γ ⊢ tool∈Allowlist, valid(Witness)` ⇒ `Γ ⊢ call tool req W k : Plan`

## Hoare rules (representative)

* Act-bind:
  If `Γ ⊢ {P} a {R}` and `∀v. Γ ⊢ {R v} k v {Q}` then `Γ ⊢ {P} act a k {Q}`.
* Seq:
  If `Γ ⊢ {P} p {R}` and `Γ ⊢ {R} q {Q}` then `Γ ⊢ {P} seq p q {Q}`.
* Choose (angelic):
  If `Γ ⊢ {P} p {Q}` or `Γ ⊢ {P} q {Q}` then `Γ ⊢ {P} choose p q {Q}`.

## Equational laws (canonical)

* `seq (seq p q) r ≡ seq p (seq q r)`; `seq (pure v) p ≡ p`
* `choose` commutative, associative, idempotent (if nondet is set-like)
* `act` is monadic bind over `Action`: left/right identity and associativity (via HOAS β)

## Safety invariants (attach to typechecker)

* All `call` sites must carry a valid `Witness` proving allowlisted factorization.
* `fix f` must be productivity-guarded (syntactic or metric).
* `par` must admit resource splitting (`Budget ⊢ b₁ ⊕ b₂ = b`).

## Adequacy and substitution (HOAS guarantees)

* No explicit capture-avoiding substitution operator.
* All bound occurrences introduced via meta-level functions; α-equivalence is definitional.
* Induction on syntax uses meta-induction on host functions plus parametricity (Reasoning with HOAS.pdf).

## Derived combinators (sugar)

* `while : ( **State → Prop** ) → Plan → Plan` via `fix`.
* `repeatUntil : Plan → ( **State → Prop** ) → Plan`.
* `try : Plan → Plan → Plan` with failure as `Prop`.

## Why this set

* Small, orthogonal kernel supports planning, observation, safety, and goals.
* All binding points use HOAS (`act`, `observe`, `ensure`, `local`, `withMem`, `call`), eliminating capture bugs and simplifying proofs (Reasoning with HOAS.pdf).
* Compositional semantics aligns with CCC/typed-λ foundations for adequacy and denotation (Mathematical Structures in Language.pdf).
