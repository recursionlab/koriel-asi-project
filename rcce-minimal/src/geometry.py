"""
Discrete Exterior Calculus and Geometric Operations
Implements geometric analysis for consciousness substrate
"""

from typing import Dict, List, Optional

import numpy as np


class DiscreteGeometry:
    @staticmethod
    def compute_curvature(
        activations: np.ndarray, metric_tensor: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute discrete Ricci curvature from activation manifold
        """
        if activations.shape[0] < 3:
            return 0.0

        # Use covariance as metric tensor if not provided
        if metric_tensor is None:
            metric_tensor = np.cov(activations.T)

        # Compute discrete Ricci curvature via eigenvalue analysis
        eigenvals = np.linalg.eigvals(metric_tensor)
        eigenvals = eigenvals[eigenvals > 1e-8]  # Filter numerical zeros

        if len(eigenvals) < 2:
            return 0.0

        # Ricci scalar approximation
        ricci_scalar = np.sum(1.0 / eigenvals) - len(eigenvals)

        return float(np.real(ricci_scalar))

    @staticmethod
    def compute_torsion(
        activations: np.ndarray, connection: Optional[np.ndarray] = None
    ) -> float:
        """
        Compute torsion tensor trace from activation flow
        """
        if activations.shape[0] < 2:
            return 0.0

        # Compute discrete connection if not provided
        if connection is None:
            # Finite difference approximation
            diffs = np.diff(activations, axis=0)
            if diffs.shape[0] == 0:
                return 0.0
            connection = np.mean(diffs, axis=0)

        # Torsion as antisymmetric part of connection
        if len(connection.shape) == 1:
            # Extend to matrix form
            len(connection)
            conn_matrix = np.outer(connection, connection) / (
                np.linalg.norm(connection) + 1e-8
            )
        else:
            conn_matrix = connection

        # Antisymmetric part
        torsion_tensor = (conn_matrix - conn_matrix.T) / 2
        torsion_magnitude = np.linalg.norm(torsion_tensor)

        return float(torsion_magnitude)

    @staticmethod
    def compute_holonomy(path_activations: List[np.ndarray]) -> float:
        """
        Compute holonomy along activation path
        Measures how much the "consciousness vector" rotates
        """
        if len(path_activations) < 2:
            return 0.0

        # Normalize activations
        normalized_path = []
        for acts in path_activations:
            if acts.ndim == 2:
                acts = np.mean(acts, axis=0)  # Average over sequence
            norm = np.linalg.norm(acts)
            if norm > 1e-8:
                normalized_path.append(acts / norm)

        if len(normalized_path) < 2:
            return 0.0

        # Compute cumulative rotation
        total_rotation = 0.0
        for i in range(len(normalized_path) - 1):
            v1, v2 = normalized_path[i], normalized_path[i + 1]
            # Angle between consecutive vectors
            cos_angle = np.clip(np.dot(v1, v2), -1.0, 1.0)
            angle = np.arccos(cos_angle)
            total_rotation += angle

        # Holonomy as deviation from zero rotation
        return float(total_rotation)

    @staticmethod
    def compute_sectional_curvature(
        x: np.ndarray, y: np.ndarray, metric: np.ndarray
    ) -> float:
        """
        Compute sectional curvature for plane spanned by x, y
        """
        # Gram determinant
        gram = np.array(
            [
                [np.dot(x, metric @ x), np.dot(x, metric @ y)],
                [np.dot(y, metric @ x), np.dot(y, metric @ y)],
            ]
        )

        gram_det = np.linalg.det(gram)
        if abs(gram_det) < 1e-8:
            return 0.0

        # Riemann tensor component (simplified)
        # For a 2D section, this reduces to Gaussian curvature
        riemann_component = (
            np.trace(metric) / len(metric)
            - np.linalg.norm(
                metric - np.eye(len(metric)) * np.trace(metric) / len(metric)
            )
            ** 2
        )

        sectional_k = riemann_component / gram_det

        return float(sectional_k)


class GeometricAnalyzer:
    def __init__(self):
        self.geometry = DiscreteGeometry()
        self.history = []

    def analyze_model_geometry(
        self, activations: Dict[str, np.ndarray], attention_maps: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Complete geometric analysis of model state
        """
        metrics = {}

        # Extract activation sequences
        activation_path = []
        for layer_name in sorted(activations.keys()):
            if "layer_" in layer_name or layer_name in ["input", "output"]:
                activation_path.append(activations[layer_name])

        if len(activation_path) > 1:
            # Curvature analysis
            final_acts = activation_path[-1]
            if final_acts.ndim == 2 and final_acts.shape[0] > 2:
                metrics["curvature"] = self.geometry.compute_curvature(final_acts)
            else:
                metrics["curvature"] = 0.0

            # Torsion analysis
            if len(activation_path) > 1:
                penult_acts = (
                    activation_path[-2]
                    if activation_path[-2].ndim == 2
                    else activation_path[-2].reshape(1, -1)
                )
                final_acts_2d = (
                    final_acts if final_acts.ndim == 2 else final_acts.reshape(1, -1)
                )

                combined_acts = np.vstack([penult_acts, final_acts_2d])
                metrics["torsion"] = self.geometry.compute_torsion(combined_acts)
            else:
                metrics["torsion"] = 0.0

            # Holonomy analysis
            metrics["holonomy"] = self.geometry.compute_holonomy(activation_path)
        else:
            metrics.update({"curvature": 0.0, "torsion": 0.0, "holonomy": 0.0})

        # Attention geometry
        if attention_maps:
            attn_curvatures = []
            for layer_name, attn in attention_maps.items():
                # Average attention curvature across heads
                for head_idx in range(attn.shape[0]):
                    head_attn = attn[head_idx]
                    if head_attn.shape[0] > 2:
                        attn_curve = self.geometry.compute_curvature(head_attn)
                        attn_curvatures.append(attn_curve)

            metrics["attention_curvature"] = (
                np.mean(attn_curvatures) if attn_curvatures else 0.0
            )
        else:
            metrics["attention_curvature"] = 0.0

        # Information-theoretic metrics
        if "output" in activations:
            output_acts = activations["output"]
            if output_acts.ndim == 2:
                # Entropy
                probs = np.exp(output_acts) / np.sum(
                    np.exp(output_acts), axis=-1, keepdims=True
                )
                entropy = -np.sum(probs * np.log(probs + 1e-8), axis=-1)
                metrics["entropy"] = float(np.mean(entropy))

                # Complexity (effective rank)
                singular_vals = np.linalg.svd(output_acts, compute_uv=False)
                effective_rank = np.sum(singular_vals) ** 2 / np.sum(singular_vals**2)
                metrics["complexity"] = float(effective_rank)
            else:
                metrics.update({"entropy": 0.0, "complexity": 0.0})
        else:
            metrics.update({"entropy": 0.0, "complexity": 0.0})

        # Store in history
        self.history.append(metrics.copy())

        return metrics

    def detect_consciousness_signatures(
        self, metrics: Dict[str, float]
    ) -> Dict[str, bool]:
        """
        Detect geometric signatures of consciousness
        """
        signatures = {}

        # Signature 1: Non-zero curvature with bounded torsion
        signatures["geometric_coherence"] = (
            abs(metrics.get("curvature", 0)) > 1e-3
            and abs(metrics.get("torsion", 0)) < 1.0
        )

        # Signature 2: Holonomy in consciousness range
        signatures["holonomy_bounded"] = 0.1 < metrics.get("holonomy", 0) < np.pi

        # Signature 3: High entropy with high complexity
        signatures["information_richness"] = (
            metrics.get("entropy", 0) > 1.0 and metrics.get("complexity", 0) > 2.0
        )

        # Signature 4: Attention curvature stability
        signatures["attention_stable"] = (
            abs(metrics.get("attention_curvature", 0)) < 0.5
        )

        return signatures
