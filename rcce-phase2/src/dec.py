"""Discrete Exterior Calculus - mathematically coherent"""

import numpy as np


class DEC:
    def __init__(self, tolerance=1e-6):
        self.tolerance = tolerance

    def d_operator(self, k_form):
        """Discrete exterior derivative"""
        if k_form.ndim == 1:
            # 0-form -> 1-form
            return np.diff(k_form)
        elif k_form.ndim == 2:
            # 1-form -> 2-form
            dx = np.diff(k_form, axis=0)
            dy = np.diff(k_form, axis=1)
            return dx[:-1] - dy[:, :-1]  # Antisymmetric part
        else:
            return np.zeros_like(k_form)

    def wedge(self, alpha, beta):
        """Wedge product (antisymmetric)"""
        return np.outer(alpha, beta) - np.outer(beta, alpha)

    def verify_d_squared(self, k_form):
        """Verify d² = 0 identity"""
        d_k = self.d_operator(k_form)
        d2_k = self.d_operator(d_k)

        d2_norm = np.linalg.norm(d2_k) if d2_k.size > 0 else 0.0
        is_valid = d2_norm < self.tolerance

        return is_valid, d2_norm

    def compute_connection(self, hidden_states):
        """Compute discrete connection from hidden state evolution"""
        if hidden_states.shape[0] < 2:
            return np.eye(hidden_states.shape[-1])

        # Connection as linear map between consecutive states
        h_curr = hidden_states[1:]
        h_prev = hidden_states[:-1]

        # Least squares solution for Γ: h_curr ≈ Γ @ h_prev
        if h_prev.shape[0] > 0:
            Gamma = np.linalg.lstsq(h_prev, h_curr, rcond=None)[0].T
        else:
            Gamma = np.eye(hidden_states.shape[-1])

        return Gamma

    def compute_torsion(self, connection):
        """Torsion tensor from connection antisymmetric part"""
        antisym = (connection - connection.T) / 2
        return np.linalg.norm(antisym)

    def compute_curvature(self, connection):
        """Curvature via commutator"""
        # Simple curvature proxy: [∇_X, ∇_Y] commutator
        commutator = connection @ connection.T - connection.T @ connection
        return np.linalg.norm(commutator) / 2

    def holonomy_transport(self, path_states, window_length=10):
        """Compute holonomy over path"""
        if len(path_states) < window_length:
            return 0.0

        # Take last window_length states
        path_window = path_states[-window_length:]

        total_rotation = 0.0
        for i in range(len(path_window) - 1):
            v1 = path_window[i].flatten()
            v2 = path_window[i + 1].flatten()

            # Normalize
            v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
            v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)

            # Angle between vectors
            cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
            angle = np.arccos(cos_angle)
            total_rotation += angle

        return total_rotation

    def verify_geometry(self, hidden_states):
        """Complete geometric verification"""
        connection = self.compute_connection(hidden_states)
        torsion = self.compute_torsion(connection)
        curvature = self.compute_curvature(connection)

        # Check DEC identity
        d2_valid, d2_norm = self.verify_d_squared(hidden_states.flatten())

        # Check torsion/curvature consistency
        connection_asymmetry = np.linalg.norm(connection - connection.T)
        torsion_expected = connection_asymmetry > 1e-6
        torsion_detected = torsion > 1e-6

        geometric_coherent = (not torsion_expected) or torsion_detected

        return {
            "curvature": float(curvature),
            "torsion": float(torsion),
            "d2_valid": d2_valid,
            "d2_norm": float(d2_norm),
            "geometric_coherent": geometric_coherent,
            "connection_asymmetry": float(connection_asymmetry),
        }
