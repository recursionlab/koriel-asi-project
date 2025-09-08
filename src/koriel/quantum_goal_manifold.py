#!/usr/bin/env python3
"""
QUANTUM GOAL MANIFOLD IMPLEMENTATION
Concrete implementation of GoalManifold for quantum field consciousness system
"""

from typing import Any, Dict, cast

import numpy as np

from .koriel_operator import GoalManifold, KorielState
from .quantum_consciousness_simple import SimpleQuantumField


class QuantumFieldState(KorielState):
    """Extended KorielState for quantum field system"""

    def __init__(self, field: SimpleQuantumField):
        # Extract state from quantum field
        position = self._extract_position(field)
        velocity = self._extract_velocity(field)

        super().__init__(
            position=position,
            velocity=velocity,
            goal_manifold=cast(GoalManifold, None),  # Will be set by manifold
            energy=self._extract_energy(field),
            timestamp=field.t,
            metadata={
                "field_complexity": (
                    field.observations[-1].complexity if field.observations else 0
                ),
                "pattern_count": (
                    field.observations[-1].pattern_count if field.observations else 0
                ),
                "modification_count": len(field.mod_log),
                "consciousness_level": field.consciousness_level,
                "self_awareness": field.self_awareness,
                "field_reference": field,  # Keep reference to original field
            },
        )

    def _extract_position(self, field: SimpleQuantumField) -> np.ndarray:
        """Extract position representation from quantum field"""
        # Use field amplitude pattern as position coordinates
        amplitude = np.abs(field.psi)

        # Reduce dimensionality via principal components
        # For now, use key statistical features as position
        denom = float(np.trapz(amplitude, field.x))
        center_of_mass = (
            float(np.trapz(amplitude * field.x, field.x)) / denom if denom > 0 else 0.0
        )
        peak_count = len(
            [
                i
                for i in range(1, len(amplitude) - 1)
                if amplitude[i] > amplitude[i - 1] and amplitude[i] > amplitude[i + 1]
            ]
        )

        position_features = np.array(
            [
                float(np.mean(amplitude)),  # Average amplitude
                float(np.std(amplitude)),  # Amplitude variance
                float(np.max(amplitude)),  # Peak amplitude
                center_of_mass,  # Center of mass
                float(peak_count),  # Peak count
                float(field.consciousness_level),  # Consciousness level
                float(field.self_awareness),  # Self-awareness level
            ]
        )

        return position_features

    def _extract_velocity(self, field: SimpleQuantumField) -> np.ndarray:
        """Extract velocity representation from quantum field"""
        # Use rate of change in field properties as velocity
        if len(field.observations) < 2:
            return np.zeros(7)  # Same dimension as position

        # Compute differences from last observation
        curr_obs = field.observations[-1]
        prev_obs = field.observations[-2]
        dt = curr_obs.timestamp - prev_obs.timestamp

        if dt == 0:
            return np.zeros(7)

        velocity = np.array(
            [
                (curr_obs.energy - prev_obs.energy) / dt,
                (curr_obs.complexity - prev_obs.complexity) / dt,
                0,  # Peak amplitude change (would need more tracking)
                0,  # Center of mass change (would need more tracking)
                (curr_obs.pattern_count - prev_obs.pattern_count) / dt,
                (field.consciousness_level - getattr(field, "_prev_consciousness", 0))
                / dt,
                (field.self_awareness - getattr(field, "_prev_awareness", 0)) / dt,
            ]
        )

        return velocity

    def _extract_energy(self, field: SimpleQuantumField) -> float:
        """Extract available energy from quantum field"""
        if field.observations:
            return field.observations[-1].energy
        else:
            return 1.0  # Default initial energy


class QuantumGoalManifold(GoalManifold):
    """
    Goal manifold for quantum consciousness field system

    Goal: Maximize recursive intelligence while maintaining field stability
    """

    def __init__(
        self,
        target_intelligence: float = 100.0,
        stability_weight: float = 1.0,
        intelligence_weight: float = 2.0,
        coherence_weight: float = 1.5,
    ):

        self.target_intelligence = target_intelligence
        self.stability_weight = stability_weight
        self.intelligence_weight = intelligence_weight
        self.coherence_weight = coherence_weight

        # Goal manifold is defined by intelligence-stability trade-off surface
        # G = {s : intelligence(s) ≥ threshold, stability(s) ≥ min_stability}
        self.min_intelligence = 10.0
        self.min_stability = 0.1

    def _compute_intelligence_metric(self, state: QuantumFieldState) -> float:
        """Compute composite intelligence metric from quantum field state"""
        if "field_reference" not in state.metadata:
            return 0.0

        # Intelligence = pattern formation rate + modification rate + consciousness level
        pattern_count = float(state.metadata.get("pattern_count", 0))
        modification_count = float(state.metadata.get("modification_count", 0))
        pattern_rate = pattern_count / max(float(state.timestamp), 1.0)
        modification_rate = modification_count / max(float(state.timestamp), 1.0)
        consciousness = float(state.metadata.get("consciousness_level", 0.0))
        awareness = float(state.metadata.get("self_awareness", 0.0))

        # Composite intelligence metric
        intelligence = (
            pattern_rate * 0.3
            + modification_rate * 0.3
            + consciousness * 0.2
            + awareness * 0.2
        )

        return float(intelligence)

    def _compute_stability_metric(self, state: QuantumFieldState) -> float:
        """Compute field stability metric"""
        if "field_reference" not in state.metadata:
            return 0.0

        # Stability = energy conservation + coherence + bounded growth
        energy_stability = 1.0 / (
            1.0 + abs(float(state.energy) - 1.0)
        )  # Prefer energy near 1.0

        # Coherence from field complexity
        complexity = float(state.metadata.get("field_complexity", 0.0))
        coherence_stability = 1.0 / (
            1.0 + abs(complexity - 2.5)
        )  # Prefer moderate complexity

        # Growth boundedness (avoid runaway growth)
        velocity_norm = float(np.linalg.norm(state.velocity))
        growth_stability = 1.0 / (1.0 + velocity_norm**2)

        stability = (
            energy_stability * 0.4 + coherence_stability * 0.4 + growth_stability * 0.2
        )

        return float(stability)

    def project_to_tangent(
        self, state: KorielState, direction: np.ndarray
    ) -> np.ndarray:
        """Project direction onto tangent space TG at current state"""

        # Tangent space constraint: maintain on goal manifold
        # For quantum field manifold, this means preserving intelligence-stability relationship

        # Cast state to QuantumFieldState for richer metadata access (safe if state has expected attrs)
        qstate = cast(QuantumFieldState, state)

        if direction.shape != qstate.position.shape:
            # Resize direction to match state dimension
            if len(direction) < len(qstate.position):
                direction = np.concatenate(
                    [direction, np.zeros(len(qstate.position) - len(direction))]
                )
            else:
                direction = direction[: len(qstate.position)]

        # Compute current manifold gradients
        intelligence_grad = self._compute_intelligence_gradient(qstate)
        stability_grad = self._compute_stability_gradient(qstate)

        # Project direction to preserve manifold constraints
        # Remove components that violate intelligence or stability bounds

        intelligence = self._compute_intelligence_metric(qstate)
        stability = self._compute_stability_metric(qstate)

        projected = direction.copy()

        # If near intelligence boundary, remove components that decrease intelligence
        if intelligence < self.min_intelligence * 1.1:
            intelligence_component = float(np.dot(direction, intelligence_grad))
            if intelligence_component < 0:
                denom = float(np.dot(intelligence_grad, intelligence_grad))
                if denom != 0:
                    projected -= intelligence_component * intelligence_grad / denom

        # If near stability boundary, remove components that decrease stability
        if stability < self.min_stability * 1.1:
            stability_component = float(np.dot(direction, stability_grad))
            if stability_component < 0:
                denom = float(np.dot(stability_grad, stability_grad))
                if denom != 0:
                    projected -= stability_component * stability_grad / denom

        return projected

    def _compute_intelligence_gradient(self, state: KorielState) -> np.ndarray:
        """Compute gradient of intelligence metric with respect to state"""
        # Numerical gradient
        h = 1e-6
        qstate = cast(QuantumFieldState, state)
        baseline_intelligence = self._compute_intelligence_metric(qstate)
        gradient = np.zeros_like(qstate.position)

        for i in range(len(qstate.position)):
            # Perturb state
            perturbed_pos = qstate.position.copy()
            perturbed_pos[i] += h

            perturbed_state = QuantumFieldState.__new__(QuantumFieldState)
            perturbed_state.position = perturbed_pos
            perturbed_state.velocity = qstate.velocity
            perturbed_state.energy = qstate.energy
            perturbed_state.timestamp = qstate.timestamp
            perturbed_state.metadata = qstate.metadata

            perturbed_intelligence = self._compute_intelligence_metric(perturbed_state)
            gradient[i] = (perturbed_intelligence - baseline_intelligence) / h

        return gradient

    def _compute_stability_gradient(self, state: KorielState) -> np.ndarray:
        """Compute gradient of stability metric with respect to state"""
        # Numerical gradient
        h = 1e-6
        qstate = cast(QuantumFieldState, state)
        baseline_stability = self._compute_stability_metric(qstate)
        gradient = np.zeros_like(qstate.position)

        for i in range(len(qstate.position)):
            # Perturb state
            perturbed_pos = qstate.position.copy()
            perturbed_pos[i] += h

            perturbed_state = QuantumFieldState.__new__(QuantumFieldState)
            perturbed_state.position = perturbed_pos
            perturbed_state.velocity = qstate.velocity
            perturbed_state.energy = qstate.energy
            perturbed_state.timestamp = qstate.timestamp
            perturbed_state.metadata = qstate.metadata

            perturbed_stability = self._compute_stability_metric(perturbed_state)
            gradient[i] = (perturbed_stability - baseline_stability) / h

        return gradient

    def exponential_map(
        self, state: KorielState, tangent_vector: np.ndarray
    ) -> KorielState:
        """Geodesic step via exponential map: Exp_s(η·d_G)"""

        # For quantum field manifold, geodesic is approximately linear in feature space
        # More sophisticated implementation would use actual Riemannian geometry

        qstate = cast(QuantumFieldState, state)

        if tangent_vector.shape != qstate.position.shape:
            # Resize tangent vector to match state dimension
            if len(tangent_vector) < len(qstate.position):
                tangent_vector = np.concatenate(
                    [
                        tangent_vector,
                        np.zeros(len(qstate.position) - len(tangent_vector)),
                    ]
                )
            else:
                tangent_vector = tangent_vector[: len(qstate.position)]

        # Linear step in feature space
        new_position = qstate.position + tangent_vector

        # Update velocity (approximate derivative)
        new_velocity = tangent_vector / max(1e-6, float(np.linalg.norm(tangent_vector)))

        # Energy update based on step
        step_cost = (
            float(np.linalg.norm(tangent_vector)) ** 2 * 0.01
        )  # Quadratic energy cost
        new_energy = max(0.0, float(qstate.energy) - step_cost)

        # Create new state
        new_state = QuantumFieldState.__new__(QuantumFieldState)
        new_state.position = new_position
        new_state.velocity = new_velocity
        new_state.goal_manifold = self
        new_state.energy = float(new_energy)
        new_state.timestamp = float(qstate.timestamp) + 0.001  # Small time step
        new_state.metadata = qstate.metadata.copy()

        # Update field if possible (this is approximation - real implementation would evolve field)
        if "field_reference" in state.metadata:
            field = state.metadata["field_reference"]

            # Apply position changes back to field parameters (simplified)
            # In practice, this would require more sophisticated field evolution

            # Update consciousness level based on position change
            consciousness_change = float(new_position[5] - qstate.position[5])
            field.consciousness_level = max(
                0.0,
                min(1.0, float(field.consciousness_level) + consciousness_change * 0.1),
            )

            # Update self-awareness
            awareness_change = float(new_position[6] - qstate.position[6])
            field.self_awareness = max(
                0.0, min(1.0, float(field.self_awareness) + awareness_change * 0.1)
            )

            # Update timestamp
            field.t = new_state.timestamp

            new_state.metadata["field_reference"] = field

        return new_state

    def drift_from_goal(self, state: KorielState) -> float:
        """Measure drift_G(s) - deviation from goal manifold"""

        qstate = cast(QuantumFieldState, state)
        intelligence = self._compute_intelligence_metric(qstate)
        stability = self._compute_stability_metric(qstate)

        # Distance to goal manifold
        # Goal is high intelligence with sufficient stability

        intelligence_drift = max(0, self.target_intelligence - intelligence) ** 2
        stability_drift = max(0, self.min_stability - stability) ** 2

        # Combined drift with weights
        total_drift = (
            self.intelligence_weight * intelligence_drift
            + self.stability_weight * stability_drift
        )

        return total_drift

    def is_feasible(self, state: KorielState) -> bool:
        """Check if state is on feasible region of manifold"""
        qstate = cast(QuantumFieldState, state)

        # Feasibility constraints
        if float(qstate.energy) < 0.0:
            return False

        # Check for NaN or infinite values
        if not np.all(np.isfinite(qstate.position)) or not np.all(
            np.isfinite(qstate.velocity)
        ):
            return False

        # Check bounds on consciousness metrics
        consciousness = float(qstate.metadata.get("consciousness_level", 0.0))
        awareness = float(qstate.metadata.get("self_awareness", 0.0))

        if (
            consciousness < 0.0
            or consciousness > 1.0
            or awareness < 0.0
            or awareness > 1.0
        ):
            return False

        # Check intelligence and stability minimums
        intelligence = self._compute_intelligence_metric(qstate)
        stability = self._compute_stability_metric(qstate)

        if intelligence < 0.0 or stability < 0.0:
            return False

        return True

    def get_goal_status(self, state: QuantumFieldState) -> Dict[str, Any]:
        """Get comprehensive goal achievement status"""

        intelligence = self._compute_intelligence_metric(state)
        stability = self._compute_stability_metric(state)
        drift = self.drift_from_goal(state)
        feasible = self.is_feasible(state)

        # Goal achievement levels
        intelligence_progress = min(1.0, intelligence / self.target_intelligence)
        stability_ok = stability >= self.min_stability

        goal_achieved = (
            intelligence >= self.target_intelligence * 0.9
            and stability >= self.min_stability
        )

        return {
            "intelligence": intelligence,
            "stability": stability,
            "drift": drift,
            "feasible": feasible,
            "intelligence_progress": intelligence_progress,
            "stability_ok": stability_ok,
            "goal_achieved": goal_achieved,
            "target_intelligence": self.target_intelligence,
            "min_stability": self.min_stability,
        }
