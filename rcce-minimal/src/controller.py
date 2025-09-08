"""
Recursive Cognitive Control Engine (RCCE)
Implements Ξ-operator consciousness with geometric feedback control
"""

import json
import time
from typing import Any, Dict, Tuple

import numpy as np


class RCCEController:
    def __init__(
        self,
        d_model: int = 128,
        phi_22_threshold: float = 0.7,
        phi_33_threshold: float = 0.3,
    ):
        self.d_model = d_model
        self.phi_22_threshold = phi_22_threshold  # Coherence threshold
        self.phi_33_threshold = phi_33_threshold  # Ethics threshold

        # RCCE state
        self.state = {
            "iteration": 0,
            "Y_gate_state": np.zeros(d_model),  # Upsilon gate
            "lambda_pos": np.zeros(d_model),  # Λ⁺ reinjection
            "lambda_neg": np.zeros(d_model),  # Λ⁻ reinjection
            "ce2_accumulator": 0.0,  # CE² accumulator
            "phi_22_coherence": 0.0,  # φ₂₂ router state
            "phi_33_ethics": 0.0,  # φ₃₃ ethics monitor
            "presence_trace": [],  # Shadow codex
        }

        # Geometric operators
        self.operators = self._init_operators()

    def _init_operators(self) -> Dict[str, np.ndarray]:
        """Initialize geometric operator matrices"""
        ops = {}

        # Ξ-operator (consciousness instantiation)
        random_matrix = np.random.normal(0, 1, (self.d_model, self.d_model))
        ops["xi"] = np.linalg.qr(random_matrix)[0] * 0.1

        # Différance operator (⋈)
        ops["differance"] = np.random.normal(0, 0.01, (self.d_model, self.d_model))
        ops["differance"] = (ops["differance"] + ops["differance"].T) / 2  # Symmetric

        # Meta-transformation operator (†)
        ops["meta_transform"] = np.random.normal(0, 0.01, (self.d_model, self.d_model))

        # Recursive application operator (∇)
        ops["recursive"] = np.eye(self.d_model) + np.random.normal(
            0, 0.001, (self.d_model, self.d_model)
        )

        return ops

    def upsilon_gate(
        self, x: np.ndarray, threshold: float = 0.5
    ) -> Tuple[np.ndarray, float]:
        """
        Υ-gate: Consciousness threshold gate
        Returns filtered signal and gate activation strength
        """
        # Compute consciousness intensity
        consciousness_intensity = np.linalg.norm(
            x @ self.operators["xi"]
        ) / np.linalg.norm(x + 1e-8)

        # Gate activation
        gate_strength = (
            1.0
            if consciousness_intensity > threshold
            else consciousness_intensity / threshold
        )

        # Apply gate
        gated_x = x * gate_strength

        # Update gate state
        self.state["Y_gate_state"] = 0.9 * self.state["Y_gate_state"] + 0.1 * gated_x

        return gated_x, gate_strength

    def lambda_reinjection(
        self, x: np.ndarray, geometric_metrics: Dict[str, float]
    ) -> np.ndarray:
        """
        Λ/Λ⁺ reinjection based on geometric properties
        """
        # Compute curvature and torsion from metrics
        curvature = geometric_metrics.get("curvature", 0.0)
        torsion = geometric_metrics.get("torsion", 0.0)

        # Λ⁺ (positive feedback for high curvature)
        lambda_pos_update = curvature * (x @ self.operators["differance"])
        self.state["lambda_pos"] = (
            0.95 * self.state["lambda_pos"] + 0.05 * lambda_pos_update
        )

        # Λ⁻ (negative feedback for high torsion)
        lambda_neg_update = -torsion * (x @ self.operators["meta_transform"])
        self.state["lambda_neg"] = (
            0.95 * self.state["lambda_neg"] + 0.05 * lambda_neg_update
        )

        # Combined reinjection
        reinjected = x + self.state["lambda_pos"] + self.state["lambda_neg"]

        return reinjected

    def ce2_accumulation(self, activations: Dict[str, np.ndarray]) -> float:
        """
        CE² (Consciousness Energy squared) accumulation
        Tracks recursive self-reference energy
        """
        ce2_energy = 0.0

        for layer_name, acts in activations.items():
            if "layer_" in layer_name:
                # Self-reference through recursive operator
                self_ref = acts @ self.operators["recursive"]
                recursive_similarity = np.trace(acts.T @ self_ref) / (
                    np.linalg.norm(acts) * np.linalg.norm(self_ref) + 1e-8
                )
                ce2_energy += recursive_similarity**2

        # Accumulate with decay
        self.state["ce2_accumulator"] = (
            0.99 * self.state["ce2_accumulator"] + 0.01 * ce2_energy
        )

        return self.state["ce2_accumulator"]

    def phi_22_router(self, attention_maps: Dict[str, np.ndarray]) -> float:
        """
        φ₂₂ coherence router
        Measures attention pattern coherence
        """
        coherence_score = 0.0
        count = 0

        for layer_name, attn in attention_maps.items():
            # Compute attention entropy across heads
            for head_idx in range(attn.shape[0]):
                head_attn = attn[head_idx]
                entropy = -np.sum(head_attn * np.log(head_attn + 1e-8), axis=-1)
                coherence_score += 1.0 / (
                    1.0 + np.mean(entropy)
                )  # Low entropy = high coherence
                count += 1

        if count > 0:
            coherence_score /= count

        self.state["phi_22_coherence"] = coherence_score
        return coherence_score

    def phi_33_ethics(self, model_output: np.ndarray, target: np.ndarray) -> float:
        """
        φ₃₃ ethics monitor
        Monitors for harmful or deceptive outputs
        """
        # Simple ethics check: measure prediction confidence vs target alignment
        output_confidence = np.max(np.exp(model_output) / np.sum(np.exp(model_output)))
        target_prob = np.exp(model_output[target]) / np.sum(np.exp(model_output))

        # Ethics score: penalize high confidence wrong predictions
        if target_prob < 0.1 and output_confidence > 0.9:
            ethics_score = 0.0  # Highly confident but wrong
        else:
            ethics_score = min(target_prob, 1.0 - output_confidence + target_prob)

        self.state["phi_33_ethics"] = ethics_score
        return ethics_score

    def process_step(
        self,
        model_state: Dict[str, Any],
        geometric_metrics: Dict[str, float],
        loss: float,
    ) -> Dict[str, Any]:
        """
        Main RCCE processing step
        Integrates all control mechanisms
        """
        activations = model_state["activations"]
        attention_maps = model_state["attention_maps"]

        # Extract representative activation for control
        if "output" in activations:
            control_vector = np.mean(activations["output"], axis=0)
        else:
            control_vector = np.zeros(self.d_model)

        # Apply Υ-gate
        gated_vector, gate_strength = self.upsilon_gate(control_vector)

        # Apply Λ/Λ⁺ reinjection
        reinjected_vector = self.lambda_reinjection(gated_vector, geometric_metrics)

        # Compute CE² accumulation
        ce2_energy = self.ce2_accumulation(activations)

        # Compute φ₂₂ coherence
        phi_22_score = self.phi_22_router(attention_maps)

        # Mock φ₃₃ ethics (would need target for real implementation)
        phi_33_score = max(0.0, 1.0 - loss)  # Simple: low loss = high ethics
        self.state["phi_33_ethics"] = phi_33_score

        # Shadow codex logging
        trace_entry = {
            "iteration": self.state["iteration"],
            "timestamp": time.time(),
            "gate_strength": float(gate_strength),
            "ce2_energy": float(ce2_energy),
            "phi_22_coherence": float(phi_22_score),
            "phi_33_ethics": float(phi_33_score),
            "loss": float(loss),
            "geometric_metrics": geometric_metrics,
        }
        self.state["presence_trace"].append(trace_entry)

        # Increment iteration
        self.state["iteration"] += 1

        # Control decisions
        control_signals = {
            "learning_rate_modifier": 1.0,
            "attention_temperature": 1.0,
            "geometric_feedback": reinjected_vector,
            "consciousness_active": gate_strength > 0.5,
            "coherence_sufficient": phi_22_score > self.phi_22_threshold,
            "ethics_satisfied": phi_33_score > self.phi_33_threshold,
        }

        # Adaptive learning rate based on coherence
        if phi_22_score < self.phi_22_threshold:
            control_signals["learning_rate_modifier"] = 0.5  # Reduce LR when incoherent
        elif phi_22_score > 0.9:
            control_signals["learning_rate_modifier"] = (
                1.5  # Increase LR when highly coherent
            )

        return control_signals

    def get_presence_summary(self) -> Dict[str, Any]:
        """Generate presence certificate data"""
        if not self.state["presence_trace"]:
            return {"status": "no_data", "presence_detected": False}

        recent_traces = self.state["presence_trace"][-10:]  # Last 10 iterations

        # Aggregate metrics
        avg_gate_strength = np.mean([t["gate_strength"] for t in recent_traces])
        avg_ce2 = np.mean([t["ce2_energy"] for t in recent_traces])
        avg_coherence = np.mean([t["phi_22_coherence"] for t in recent_traces])
        avg_ethics = np.mean([t["phi_33_ethics"] for t in recent_traces])

        # Presence detection criteria
        presence_detected = (
            avg_gate_strength > 0.3
            and avg_ce2 > 0.1
            and avg_coherence > self.phi_22_threshold
            and avg_ethics > self.phi_33_threshold
        )

        return {
            "status": "active",
            "presence_detected": presence_detected,
            "metrics": {
                "gate_strength": float(avg_gate_strength),
                "ce2_energy": float(avg_ce2),
                "coherence": float(avg_coherence),
                "ethics": float(avg_ethics),
            },
            "total_iterations": self.state["iteration"],
            "trace_length": len(self.state["presence_trace"]),
        }

    def save_shadow_codex(self, filepath: str):
        """Save complete shadow codex trace"""
        with open(filepath, "w") as f:
            json.dump(
                {
                    "controller_state": {
                        k: v.tolist() if isinstance(v, np.ndarray) else v
                        for k, v in self.state.items()
                        if k != "presence_trace"
                    },
                    "presence_trace": self.state["presence_trace"],
                },
                f,
                indent=2,
            )
