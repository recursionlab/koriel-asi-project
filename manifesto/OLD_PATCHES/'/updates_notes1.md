Proceeding manually. No file writes. Citations by file label.

# SCAFFOLDED SYNTHESIS LAYER (Koriel ASI)

## 1) CORE ONTOLOGY (minimal, source-anchored)

* Objects = states/contexts/types. Morphisms = controlled transforms. (Thinking with Functors.pdf)
* Functors move structure between subsystems; naturality = protocol coherence. (Thinking with Functors.pdf)
* Adjunctions capture plan ⊣ execute, learn ⊣ evaluate. Triangle identities compress search. (Thinking with Functors.pdf)
* Sites & sheaves model local context with descent to global consistency. (Higher Topos Theory.pdf, Ch. 6)
* Quasicategories ensure composition up to homotopy; (co)cartesian fibrations capture dependency. (The 2-category theory of quasi-categories.pdf; Infinity category theory from scratch.pdf)
* Fixed points formalize safe self-reference. (KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf)
* Autopoietic closure defines the safety boundary. (Maturana…Autopoiesis and Cognition.pdf; Info-Autopoiesis and the Limits of Artificial.pdf)
* Binding-safe program formation uses HOAS inside a CCC. (Reasoning with Higher-Order Abstract Syntax.pdf; Mathematical Structures in Language.pdf)
* Transitional topologies model regime shifts and information flow. (TransitionalTopologies…ToposTheory.pdf)
* Contextual valuations and internal logic for non-global truth. (Quantum Toposophy.pdf)
* Metric geometry for attention/effort via geodesics and curvature. (mathematical framework…Riemannian Geometry.pdf)
* Knowledge dynamics: schema, reproduction kernel, mutation. (Structuring Knowledge.pdf; Knowledge Reproduction Processes.pdf)

## 2) ROLE MAPPING (theory → Koriel components)

### Planner (F: Goals → Plans)

* Formal anchor: left adjoint F with unit η; monad T = G∘F for iterate–refine. (Thinking with Functors.pdf)
* Responsibilities: search over structured candidates; respect types, contexts, and closure.
* Interfaces: `plan : Goal → Plan`, `refine : Plan → Plan`, `unit_witness : id ⇒ G∘F`.
* Invariants: triangle identities hold; plan refinement is monadic; binding rules via HOAS. (Reasoning with HOAS.pdf; Mathematical Structures in Language.pdf)
* Metrics: branching factor ↓ with equal success rate; plan size normalized.

### Actor (G: Plans → Outcomes)

* Formal anchor: right adjoint G with counit ε; implements minimal effect per triangle law. (Thinking with Functors.pdf)
* Responsibilities: deterministic execution under allowlisted constructors; geodesic-stepped attention. (Riemannian Geometry.pdf)
* Interfaces: `execute : Plan → Outcome`, `observe : Outcome → Evidence`.
* Invariants: no non-factoring calls across safety boundary; effort monotone along geodesics. (Maturana…; Info-Autopoiesis…; Riemannian Geometry.pdf)
* Metrics: effect minimality; effort/curvature budget respected.

### Verifier (Sheaf/Descent Gate)

* Formal anchor: sheaf over site of contexts; descent glues locals if overlaps agree. (Higher Topos Theory.pdf, Ch. 6)
* Responsibilities: construct covers; check cocycle conditions; emit global certificate or counterexample.
* Interfaces: `verify_local : Cover×Obligations → Sections`, `descent : Sections → Option[Global]`.
* Invariants: failure iff overlap disagreements; cohomology-as-obstruction heuristic. (HTT.pdf)
* Metrics: descent success rate; false-positive/negative profile on seeded inconsistencies.

### Memory (Site, Versioned Sections)

* Formal anchor: site (C,J) with coverings; versioned sheaf sections; functorial updates. (Structuring Knowledge.pdf)
* Responsibilities: provenance, constraint propagation, reversible merges.
* Interfaces: `pullback_update`, `merge_with_proof`.
* Invariants: pullback preservation; no orphan sections.
* Metrics: merge conflicts resolved with bounded edits; provenance completeness.

### Safety (Autopoietic Closure)

* Formal anchor: operational closure; only re-entrant constructors permitted. (Maturana…; Info-Autopoiesis…)
* Responsibilities: allowlists, quotas, depth/fan-out caps, redaction.
* Interfaces: `safe_call : Tool×Req → Either[Abort,Resp]`.
* Invariants: every execution factors through self-produced components; SRT guard on self-mod. (KLEENE SRT.pdf)
* Metrics: zero non-factoring executions in dry-run; controlled self-mod increments.

### Self-Modification Guard (SRT)

* Formal anchor: fixed-point construction with proof-carrying transform Φ. (KLEENE SRT.pdf)
* Responsibilities: wrap updates in fixed-point witness; disallow opaque reflection.
* Interfaces: `attempt_update : Φ → Either[Reject, ApplyWithWitness]`.
* Invariants: `U(p) = Φ(p)` holds under constraints; resource/closure preserved.
* Metrics: safe-iteration count before abort; invariant preservation checks.

### Semantics (Quasicat / ∞-Topos)

* Formal anchor: homotopy-safe equivalences; context fibrations; geometric morphisms for change-of-site. (2-cat of quasicats.pdf; HTT.pdf)
* Responsibilities: state goals “up to homotopy”; maintain invariance under refactor.
* Interfaces: `equiv : Plan ↔ Plan`, `transport : Context→Context'`.
* Invariants: outcome unchanged under equivalences; transport respects descent.
* Metrics: robustness score under syntactic refactors.

### Contextual Logic (Quantum Topos)

* Formal anchor: spectral presheaf; no global valuation; internal logic per context. (Quantum Toposophy.pdf)
* Responsibilities: enforce context-scoped claims; forbid illicit global joins.
* Interfaces: `context_eval : (Obs, Context) → Val`.
* Invariants: no Kochen–Specker violations; contextual consistency.
* Metrics: rate of forbidden globalizations caught.

### Transitional Topology (Phase Monitor)

* Formal anchor: family of sites indexed by phase; gluing across phase boundaries. (TransitionalTopologies…ToposTheory.pdf)
* Responsibilities: drift/phase alarms; controlled reconfiguration.
* Interfaces: `phase_cover`, `reindex : Phase→Phase'`.
* Invariants: reindexing preserves obligations where defined; alarms on cover change.
* Metrics: predictive gain on failure incidents.

## 3) CONCEPT GRAPH (ASCII)

```
[Distinction]→[Objects]
[Objects]--morphisms-->[Objects]
[Functors] & [NatTrans] → protocol coherence (Thinking with Functors.pdf)

[Adjunction F⊣G] ⇢ [Compression] ⇢ [Monad T=GF]
            ↘                 ↙
             [Planner F]   [Actor G]

[Site(C,J)]⇒[Sheaf]⇒[Descent]⇒[Global Plan] (HTT.pdf)
      ↑             ↘
 [Transitional Topology]→[Phase Reindex] (TransitionalTopologies.pdf)

[Fixed Point (SRT)]→[Self-Mod Guard] (KLEENE SRT.pdf)
[Autopoietic Closure]→[Safety Boundary] (Maturana…, Info-Autopoiesis.pdf)

[Riemannian Metric]→[Geodesic Attention] (Riemannian Geometry.pdf)
[Quantum Presheaf]→[Contextual Logic] (Quantum Toposophy.pdf)
[Schema+Reproduction]→[Knowledge Evolution] (Structuring Knowledge.pdf, KRP.pdf)
```

## 4) OPERATIVE LAWS (checkable)

* Triangle identities: $Gε∘ηG = id_G$, $εF∘Fη = id_F$. Evidence required at planner–actor boundary. (Thinking with Functors.pdf)
* Descent: local agreement ⇒ unique global. Emits counterexample when not satisfied. (Higher Topos Theory.pdf)
* SRT fixed point: ∀ effective Φ, ∃p with $U(p)=Φ(p)$ under resource/closure constraints. (KLEENE SRT.pdf)
* Closure: all executions factor through self-produced constructors; else abort. (Maturana…; Info-Autopoiesis.pdf)
* Up-to-homotopy: goals invariant under equivalences; inner-horn fillers guarantee associativity. (Infinity…from scratch.pdf)

## 5) MICRO-EVALS (smallest rigorous tests)

* Adjoint compression: measure branching factor and success parity vs baseline planner. (Thinking with Functors.pdf)
* Descent gate: seed cover overlaps with known conflict; expect refusal with overlap diff witness. (HTT.pdf)
* SRT guard: attempt self-mod without proof; expect reject. With proof-carrying Φ; expect accept + invariant check. (KLEENE SRT.pdf)
* Closure enforcement: craft adapter that skips constructors; expect abort + audit trace. (Maturana…; Info-Autopoiesis.pdf)
* HOAS adequacy: inject capture-prone patterns; expect zero capture failures. (Reasoning with HOAS.pdf)
* Homotopy robustness: refactor-equivalent plans; expect identical outcomes. (2-cat quasicats.pdf; Infinity…from scratch.pdf)
* Phase alarm: synthetic drift triggers reindex; expect early alert. (TransitionalTopologies…ToposTheory.pdf)

## 6) RISK REGISTER

* Mis-specified adjunction ⇒ overpruning or non-termination. Mitigate with triangle tests. (Thinking with Functors.pdf)
* Bad covers ⇒ false descent. Mitigate with overlap diagnostics. (HTT.pdf)
* Reflection escape around SRT. Mitigate with closure + proof-carrying updates. (KLEENE SRT.pdf; Info-Autopoiesis.pdf)
* Global valuation leaks. Mitigate with contextual logic enforcement. (Quantum Toposophy.pdf)
* Binding bugs. Mitigate with HOAS-only DSL for planning. (Reasoning with HOAS.pdf)
* Phase mis-detection. Mitigate with dual metrics: topology + variance shift. (TransitionalTopologies…ToposTheory.pdf)

## 7) IMMEDIATE NEXT (no files, no scripts)

* Define acceptance criteria for triangle identities at F⊣G boundary. (Thinking with Functors.pdf)
* Specify sheaf-descent verifier contract and overlap diagnostics. (Higher Topos Theory.pdf)
* Draft SRT proof-carrying update policy tied to closure witness. (KLEENE SRT.pdf; Maturana…; Info-Autopoiesis.pdf)
* Choose HOAS primitives for planner DSL types. (Reasoning with HOAS.pdf; Mathematical Structures in Language.pdf)
* Select drift features and phase covers for transitional topology alarms. (TransitionalTopologies…ToposTheory.pdf)

## 8) CITATION INDEX (by label)

* Thinking with Functors.pdf — functors, naturality, adjunctions, monads.
* Higher Topos Theory.pdf — sites, sheaves, descent, geometric morphisms.
* The 2-category theory of quasi-categories.pdf — homotopy 2-cat, fibrations, adjunctions.
* Infinity category theory from scratch.pdf — quasicategories, mapping spaces, inner horns.
* KLEENE’S AMAZING SECOND RECURSION THEOREM.pdf — SRT, fixed points.
* Reasoning with Higher-Order Abstract Syntax.pdf — HOAS adequacy, substitution, binding.
* Mathematical Structures in Language.pdf — CCC semantics of binding.
* Maturana…Autopoiesis and Cognition.pdf — autopoiesis, operational closure.
* Info-Autopoiesis and the Limits of Artificial.pdf — info-autopoiesis criteria.
* TransitionalTopologies…ToposTheory.pdf — phase-indexed sites, gluing across regimes.
* Quantum Toposophy.pdf — contextual valuations, spectral presheaf.
* mathematical framework…Riemannian Geometry.pdf — metric/curvature, geodesics.
* Structuring Knowledge.pdf; Knowledge Reproduction Processes.pdf — schema, reproduction, mutation.

---

## DIGEST (JSON)

```json
{
  "ranked_focus": [
    "Planner–Actor adjunction with triangle acceptance criteria",
    "Sheaf-descent verifier and overlap diagnostics",
    "SRT-based self-modification guard under autopoietic closure",
    "HOAS-safe planner DSL in a CCC",
    "Transitional topology drift/phase alarms",
    "Homotopy-stable goals and dependency fibrations",
    "Contextual logic to prevent illicit global valuations"
  ],
  "gaps": [
    {"path": "Higher Topos Theory.pdf", "issue": "Line-accurate quotes pending", "fix": "Targeted extraction around Ch.6"},
    {"path": "Maturana_Humberto_Varela_Francisco_Autopoiesis_and_Congition_The_Realization_of_the_Living.pdf", "issue": "Precise closure definition excerpt", "fix": "Pull canonical definition pages"},
    {"path": "Reasoning with Higher-Order Abstract Syntax.pdf", "issue": "Formal adequacy theorem statement", "fix": "Extract theorem and proof sketch"}
  ],
  "actions": [
    {"path": "theory/planner", "change": "Define η, ε triangle checks for F⊣G boundary", "check": "Measured search contraction with success parity"},
    {"path": "theory/verifier", "change": "Specify sheaf-descent interface and conflict witness", "check": "Local agreement yields global plan; disagreements produce counterexample"},
    {"path": "theory/safety", "change": "SRT proof-carrying update + closure witness", "check": "Reject updates lacking witness; accept otherwise with invariants intact"},
    {"path": "theory/dsl", "change": "Adopt HOAS primitives for binding-safe plan terms", "check": "Zero capture in adversarial cases"},
    {"path": "theory/monitoring", "change": "Define phase covers and reindex rules", "check": "Alarms precede failure incidents on drift scenarios"}
  ],
  "risks": [
    "Adjunction mis-specification",
    "False descent due to bad covers",
    "Self-mod escape via reflection",
    "Context leak to global valuations",
    "Binding errors without HOAS",
    "Phase mis-detection"
  ],
  "assumptions": [
    "Label-based citations acceptable in this pass",
    "Repo paths will be attached when provided"
  ]
}
```
