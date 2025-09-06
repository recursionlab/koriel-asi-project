# Sheaf–Descent Verifier Contract and Overlap Diagnostics

This document defines the contract for a sheaf-descent verifier that checks the sheaf condition on covers of a site and reports detailed diagnostics when descent fails.

## Inputs
- `U`: object in the site C.
- `Cover`: finite family `{u_i : U_i -> U}` in the Grothendieck topology J(U).
- `Locals`: tuple `s = (s_i)` with each `s_i in F(U_i)` where F is the presheaf/sheaf.
- `Eq`: equality predicate (strict, observational, or homotopy-up-to).
- `Mode`: `sheaf` (equalizer) or `hyper` (hyperdescent).

## Outputs
- `status`: `pass` or `fail`.
- `global`: glued section `s in F(U)` if passing; `null` otherwise.
- `witness`: diagnostics record for failures.
- `uniqueness`: true if global is unique under `Eq`.
- `depth_checked`: 2 for equalizer; >=3 if hyperdescent.

## Preconditions
- Restriction maps of F are functorial: `F(id_U) = id` and `F(g∘f)=F(f)∘F(g)` for used morphisms.
- Fiber products `U_{ij} = U_i ×_U U_j` (and higher overlaps) exist as needed.

## Sheaf equalizer condition
1. Pairwise agreement: for each (i,j) the restrictions of s_i and s_j to U_{ij} agree under `Eq`.
2. Existence/uniqueness: a unique global section s exists with `F(u_i)(s) = s_i` for all i.

## Overlap diagnostics
- `pair_matrix`: records each (i,j) with left/right restrictions and agreement result.
- `triple_coherence`: when `mode` is `hyper`, checks triple overlaps.
- `nerve_depth`: depth inspected (2 by default).
- `minimal_countercover`: minimal subcover responsible for failure.
- `cause`: one of {`PAIR_MISMATCH`, `NO_GLOBAL`, `NON_UNIQUE`, `FUNCTORIALITY_FAIL`}.

## Witness rules
- `PAIR_MISMATCH`: include offending (i,j) and mismatched restrictions.
- `NO_GLOBAL`: provide reconstruction trace or Čech obstruction.
- `NON_UNIQUE`: provide two distinct globals with identical restrictions.
- `FUNCTORIALITY_FAIL`: specify violating morphism pair.

## Verification algorithm
**Sheaf mode**:
1. Compute all U_{ij} and test agreements. If any fail -> `PAIR_MISMATCH`.
2. Solve equalizer for a global s. If none -> `NO_GLOBAL`.
3. If multiple s exist under Eq -> `NON_UNIQUE`.
4. Otherwise -> `pass`.

**Hyper mode**: extend checks to triples and higher overlaps via Čech cochains; require vanishing obstructions up to configured depth.

## Acceptance and rejection
Acceptance requires functoriality, pairwise agreement, existence and uniqueness of global section, and no diagnostics. Reject if any step fails.

## Complexity and safety
Pairwise checks are O(m^2); hyper checks can grow to O(m^3). Cap nerve depth to 3, redact payloads (hash/probe), and use deterministic ordering.
