# Sheaf–Descent Verifier: Contract and Overlap Diagnostics (Higher Topos Theory.pdf, Ch. 6)

## Scope

* Target: verification over a site $(\mathcal C,J)$ with covers $ \{U_i \to U\}$.
* Object: presheaf $F:\mathcal C^{op}\to \mathsf{Set}$ (or $\infty$-valued), with restriction maps $F(f):F(U)\to F(V)$.
* Goal: decide the sheaf condition on a given cover and compute descent or a minimal counterexample.

## Contract

### Inputs

* `U`: object in $\mathcal C$.
* `Cover`: finite family $\{u_i:U_i \to U\}\in J(U)$.
* `Locals`: tuple $\mathbf s = (s_i)$ with $s_i \in F(U_i)$.
* `Eq`: equality predicate on section values (strict, observational, or homotopy-up-to).
* `Mode`: {`sheaf` (equalizer), `hyper` (hyperdescent)}; default `sheaf`.

### Outputs

* `status`: {`pass`, `fail`}.
* `global`: section $s\in F(U)$ if `pass`, else `null`.
* `witness`: diagnostics record (see “Overlap diagnostics”).
* `uniqueness`: boolean and, if `false`, two distinct globals with same restrictions.
* `depth_checked`: 2 for equalizer check; ≥3 if `hyper` used.

### Pre-conditions

* Restriction functoriality holds: $F(\mathrm{id}_U)=\mathrm{id}$, $F(g\!\circ\! f)=F(f)\!\circ\! F(g)$ on all morphisms used.
* Cover arrows compose and fiber products $U_{ij}:=U_i\times_U U_j$ (and $U_{ijk}$, … if `hyper`) exist in $\mathcal C$.

### Post-conditions (sheaf equalizer form)

* Pairwise agreement: for all $(i,j)$,

  $$
  F(\pi_{ij}^i)(s_i) \;=\_{Eq}\; F(\pi_{ij}^j)(s_j)\quad\text{in }F(U_{ij}).
  $$
* Existence: if pairwise agreement holds, `status=pass` iff there exists $s\in F(U)$ with $F(u_i)(s)=s_i$ for all $i$.
* Uniqueness: if `status=pass`, uniqueness must hold under `Eq`.

(HTT equalizer form: $F(U) \xrightarrow{\;\delta\;} \prod_i F(U_i) \rightrightarrows \prod_{i,j} F(U_{ij})$ with $F(U)$ the equalizer.)

## Overlap diagnostics

### Data recorded

* `pair_matrix`: table of all $(i,j)$ with

  * `lhs` = $F(\pi_{ij}^i)(s_i)$, `rhs` = $F(\pi_{ij}^j)(s_j)$, `ok` = `Eq(lhs,rhs)`.
* `triple_coherence` (optional unless `hyper`): for all $(i,j,k)$,

  * check $F$ on $U_{ijk}$ that pairwise agreements are compatible.
* `nerve_depth`: deepest overlap level inspected (2 by default; ≥3 if `hyper`).
* `minimal_countercover`: smallest subcover that fails pairwise agreement or fails existence.
* `cause`: enum

  * `PAIR_MISMATCH` (some $(i,j)$ fail),
  * `NO_GLOBAL` (pairwise ok, but no $s$ glues),
  * `NON_UNIQUE` (two distinct globals restrict equally),
  * `FUNCTORIALITY_FAIL` (restriction laws broken).

### Witness construction

* For `PAIR_MISMATCH`:

  * emit $(i,j)$, the computed `lhs`,`rhs`, and the two restriction morphisms.
* For `NO_GLOBAL`:

  * emit solver trace: attempted $s$ reconstruction from $\mathbf s$ and the obstruction (e.g., inconsistent pullbacks along a commuting triangle).
  * in $\infty$-setting, return a nontrivial 1-cocycle representative if available (Čech obstruction).
* For `NON_UNIQUE`:

  * emit two distinct candidates $s,s'\in F(U)$ with $F(u_i)(s)=F(u_i)(s')$ all $i$.
* For `FUNCTORIALITY_FAIL`:

  * emit violating morphism pair $(f,g)$ with $F(g\!\circ\! f)\neq F(f)\!\circ\! F(g)$.

## Algorithms (mode = `sheaf`)

* **Pair stage:** compute all $U_{ij}$ and test agreements; if any fail → `fail/P AR_MISMATCH`.
* **Glue stage:** solve for $s$ such that $F(u_i)(s)=s_i$ (equalizer preimage). If none → `fail/NO_GLOBAL`.
* **Unique stage:** if two solutions arise under `Eq`, mark `NON_UNIQUE`; else `pass`.

## Algorithms (mode = `hyper`)

* Replace pair/triple checks by Čech nerve $C^\bullet(\mathcal U)$ up to configured degree $n$.
* Require vanishing of obstructions up to $n$ (hyperdescent surrogate). Record highest non-vanishing level if `fail`.

## Equality discipline

* **Strict:** literal equality in $F$.
* **Observational:** equal under a designated suite of probes.
* **Homotopy:** equal up to specified homotopy; require coherent fillers (contractible choice).

Use the same `Eq` across pair, glue, and uniqueness.

## Acceptance criteria

* Functoriality of restrictions holds on all arrows used.
* All pairs agree on $U_{ij}$ (and triples coherent if `hyper`).
* A global $s$ exists and is unique under `Eq`.
* Diagnostics empty; `minimal_countercover` undefined.

## Rejection criteria

* Any functoriality violation.
* Any pairwise disagreement.
* Pairwise agreement but no global section exists.
* Non-uniqueness under declared `Eq`.

## Complexity notes

* Pairwise stage is $O(m^2)$ evaluations for $m=|\mathcal U|$.
* Hyper stage adds $O(m^3)$ triple checks and higher if configured.

## Safety/robustness hooks

* Bounded `nerve_depth` to cap cost.
* Deterministic order of pairs for reproducible witnesses.
* Redaction of section payloads; expose only hashed or probed summaries if sensitive.

## Minimal test suite (soundness)

* Identity cover $\{U\to U\}$: must `pass` and return the given section.
* Two-open cover with engineered mismatch: must `fail/PAIR_MISMATCH` with correct witness.
* Pairwise-consistent cover with forced non-existence (category-specific): must `fail/NO_GLOBAL`.
* Constructed non-unique example (if category allows): must `fail/NON_UNIQUE`.

Reference: Higher Topos Theory.pdf, Ch. 6 (sheaves on a site, descent via equalizer and Čech nerve).
