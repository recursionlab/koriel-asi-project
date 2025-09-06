# Planner DSL — HOAS Core

This document defines the core constructs for the Koriel planning language using Higher-Order Abstract Syntax (HOAS). All binders are meta-level functions.

## Types
- Value types: `Unit`, `Bool`, `Int`, …
- Logical: `Prop`
- World: `State`
- Actions: `Action α` (returns `α`)
- Plan: `Plan`
- Goal: `Goal`
- Budget: `Budget`
- Effort: `Eff`

## Judgments
- Typing: `Γ ⊢ e : τ`.
- Hoare: `Γ ⊢ {P} p {Q}` with `P,Q : State -> Prop`.

## Primitives (meta-level binders in **bold**)
- `pure : α -> Plan`
- `act  : Action α -> (**α -> Plan**) -> Plan`
- `seq  : Plan -> Plan -> Plan`
- `choose : Plan -> Plan -> Plan`
- `par  : Plan -> Plan -> Plan` (resource-checked)
- `fix  : (**Plan -> Plan**) -> Plan` (guarded recursion)
- `if_ : Prop -> Plan -> Plan -> Plan`
- `when : Prop -> Plan`
- `observe : Sensor α -> (**α -> Plan**) -> Plan`
- `assume : Prop -> Plan`
- `assert : Prop -> Plan`
- `goal : Goal -> Plan`
- `ensure : (**State -> Prop**) -> Plan`
- `local : (**State -> Plan**) -> Plan`
- `withMem : (**Mem -> Plan**) -> Plan`
- `call : Tool α -> Req -> Witness -> (**α -> Plan**) -> Plan` (allowlisted only)
- `withBudget : Budget -> Plan -> Plan`
- `meter : (**Eff -> Plan**) -> Plan`

## Value layer
- `lam : (**α -> β**) -> (α ⇒ β)`; `app : (α ⇒ β) -> α -> β`.
- Standard pairs, sums, unit.

## Typing rules (sketch)
Examples: Act-bind, Seq, If, Ensure, Call-with-witness; HOAS ensures capture-free binding.

## Hoare rules
Act-bind and Seq standard; Choose is angelic or demonic per setting.

## Equational laws
`seq` associative; `pure` identities; `act` is monadic bind over `Action`.

## Safety invariants
All `call` sites must carry a valid `Witness`; `fix` must be guarded; `par` requires resource split.

## Derived combinators
`while`, `repeatUntil`, `try` via `fix`, `seq`, `if_`.
