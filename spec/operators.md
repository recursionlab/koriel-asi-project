# Operators

Koriel-ASI defines a family of operators that transform state on a goal manifold
while respecting ethical and energetic constraints.

### KorielOperator
* **measure_uncoherence(s)** – computes the uncoherence metric
  `U(s) = α||∂s|| + β·paradox(s) + γ·drift_G(s) + η·|holonomy(s)|`.
* **compute_gradient_direction(s)** – returns the steepest descent direction to
  reduce `U(s)`.
* **project_to_tangent(d)** – projects a direction onto the manifold's tangent
  space before applying the exponential map.
* **koriel_lift(d)** – optional assistance step that injects bounded external
  help when progress stalls.
* **step(state)** – applies the above primitives to produce a new state with
  lower uncoherence and updated metrics.

### GoalManifold
Abstract interface providing `project_to_tangent`, `exponential_map`,
`drift_from_goal` and `is_feasible` methods used by the operator.

### ExternalCarrier
Pluggable helper that can modify a step direction when additional external
support is allowed. Each carrier implements `can_assist`, `apply_assist` and
`release`.

