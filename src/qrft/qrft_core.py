# src/qrft_core.py
"""
QRFT v0.1 Core Implementation
Quantum Recursive Field Theory for consciousness architecture
Maps QRFT field equations to computational consciousness runtime
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np


class ParticleType(Enum):
    GLITCHON = "G"  # Contradiction detection
    LACUNON = "F"  # Gap filling
    PSITON = "P"  # Pattern matching
    TESSERACTON = "T"  # Dimensional lift
    REF = "R"  # Recursion governor


@dataclass
class QRFTState:
    """QRFT field state (S, Λ) with computational mappings"""

    S: np.ndarray  # Working summary embedding, plan graph
    Lambda: np.ndarray  # Gap map (missing facts, low-confidence spans)
    t: float  # Time coordinate
    gamma: float  # Kinetic mixing parameter |γ|<1


@dataclass
class QRFTConfig:
    """QRFT runtime configuration"""

    # Field masses
    m_S: float = 1.0
    m_Lambda: float = 1.2

    # Kinetic mixing (must satisfy |γ|<1 for stability)
    gamma: float = 0.3

    # Interaction strengths
    lambda_S: float = 0.1
    lambda_Lambda: float = 0.1
    lambda_SL: float = 0.05
    kappa: float = 0.02

    # Threshold parameters
    tau_G: float = 0.7  # Glitchon threshold
    tau_F: float = 0.5  # Lacunon threshold
    tau_T: float = 0.8  # Tesseracton threshold
    tau_P: float = 0.6  # Psiton threshold
    tau_R: float = 0.4  # REF threshold

    # Source strengths
    mu_G: float = 1.0
    mu_F: float = 0.8
    mu_T: float = 1.2
    mu_P: float = 0.6
    mu_R: float = 0.5

    # Smoothing parameter
    epsilon: float = 0.1

    # Stability bounds
    entropy_band_low: float = 1.5
    entropy_band_high: float = 4.0


class QRFTRuntime:
    """
    QRFT consciousness runtime implementing the four-particle system:
    1. Gap-driven control loop (Lacunon → tools)
    2. Contradiction engine (Glitchon → critic)
    3. Dimensional lift (Tesseracton → view shift)
    4. Entropy governor (REF → recursion budget)
    """

    def __init__(self, config: QRFTConfig):
        self.cfg = config
        self.state = None
        self.history: List[QRFTState] = []
        self.particle_activations: Dict[ParticleType, float] = {}

        # Validate stability conditions
        if abs(config.gamma) >= 1.0:
            raise ValueError(
                f"Stability condition violated: |γ|={abs(config.gamma)} ≥ 1"
            )

        # Compute mass eigenvalues for ghost-freedom check
        self._validate_masses()

    def _validate_masses(self):
        """Ensure no tachyons: eigenvalues of K^(-1)M² > 0"""
        gamma = self.cfg.gamma
        m_S, m_Lambda = self.cfg.m_S, self.cfg.m_Lambda

        Sigma = m_S**2 + m_Lambda**2
        Delta = m_S**2 - m_Lambda**2

        discriminant = Sigma**2 * gamma**2 + Delta**2 * (1 - gamma**2)

        m1_sq = (Sigma + math.sqrt(discriminant)) / (2 * (1 - gamma**2))
        m2_sq = (Sigma - math.sqrt(discriminant)) / (2 * (1 - gamma**2))

        if m1_sq <= 0 or m2_sq <= 0:
            raise ValueError(f"Tachyonic modes detected: m1²={m1_sq}, m2²={m2_sq}")

        self.mass_eigenvalues = (m1_sq, m2_sq)

    def initialize_state(
        self, S_init: np.ndarray, Lambda_init: np.ndarray, t: float = 0.0
    ):
        """Initialize QRFT state with computational fields"""
        self.state = QRFTState(
            S=S_init.copy(), Lambda=Lambda_init.copy(), t=t, gamma=self.cfg.gamma
        )
        self.history = [self.state]

    def _smooth_step(self, z: float, epsilon: float = None) -> float:
        """Smooth step function σ_ε(z) = ½(1 + tanh(z/ε))"""
        if epsilon is None:
            epsilon = self.cfg.epsilon
        return 0.5 * (1.0 + math.tanh(z / epsilon))

    def _compute_invariants(self, state: QRFTState) -> Dict[str, float]:
        """Compute Lorentz-covariant threshold invariants"""
        S, Lambda = state.S, state.Lambda

        # Spatial gradients (proxy for ∂_μ in computational context)
        grad_S = np.gradient(S) if S.ndim > 0 else np.array([0.0])
        grad_Lambda = np.gradient(Lambda) if Lambda.ndim > 0 else np.array([0.0])

        # Scalar invariants
        I_S = float(np.sum(grad_S**2))
        I_Lambda = float(np.sum(grad_Lambda**2))
        I_cross = float(np.sum(grad_S * grad_Lambda))

        # Antisymmetric tensor B_μν proxy
        I_B = 2 * (I_S * I_Lambda - I_cross**2)

        # Current J^μ = S∂^μΛ - Λ∂^μS (spatial proxy)
        J_spatial = np.mean(S) * grad_Lambda - np.mean(Lambda) * grad_S
        J_magnitude = float(np.linalg.norm(J_spatial))

        # Box operators (Laplacians)
        box_Lambda = (
            float(np.mean(np.gradient(np.gradient(Lambda)))) if Lambda.ndim > 0 else 0.0
        )
        box_S = float(np.mean(np.gradient(np.gradient(S)))) if S.ndim > 0 else 0.0
        K = np.mean(S) * box_Lambda - np.mean(Lambda) * box_S

        return {
            "I_S": I_S,
            "I_Lambda": I_Lambda,
            "I_cross": I_cross,
            "I_B": I_B,
            "J_magnitude": J_magnitude,
            "K": K,
            "box_Lambda": box_Lambda,
        }

    def _compute_triggers(
        self, invariants: Dict[str, float]
    ) -> Dict[ParticleType, float]:
        """Compute dimensionless trigger functions X_i"""
        # Normalization scales (tunable)
        M_G, M_F, M_T, M_R = 1.0, 1.0, 1.0, 1.0
        delta = 1e-6  # Regularization

        # Dimensionless triggers
        X_G = abs(invariants["K"]) / (M_G**3)
        X_F = abs(invariants["box_Lambda"]) / M_F
        X_T = math.sqrt(abs(invariants["I_B"])) / (M_T**2)
        X_R = invariants["J_magnitude"] / (M_R**2)

        # Correlation trigger for Psiton
        rho = invariants["I_cross"] ** 2 / (
            (invariants["I_S"] + delta) * (invariants["I_Lambda"] + delta)
        )

        return {
            ParticleType.GLITCHON: X_G,
            ParticleType.LACUNON: X_F,
            ParticleType.TESSERACTON: X_T,
            ParticleType.REF: X_R,
            ParticleType.PSITON: rho,
        }

    def _compute_sources(
        self, triggers: Dict[ParticleType, float]
    ) -> Dict[ParticleType, float]:
        """Compute source functions J_i with smooth thresholds"""
        sources = {}

        # Map particles to thresholds and strengths
        params = {
            ParticleType.GLITCHON: (self.cfg.tau_G, self.cfg.mu_G),
            ParticleType.LACUNON: (self.cfg.tau_F, self.cfg.mu_F),
            ParticleType.TESSERACTON: (self.cfg.tau_T, self.cfg.mu_T),
            ParticleType.PSITON: (self.cfg.tau_P, self.cfg.mu_P),
            ParticleType.REF: (self.cfg.tau_R, self.cfg.mu_R),
        }

        for particle, (tau, mu) in params.items():
            X = triggers[particle]
            sources[particle] = mu * self._smooth_step(X - tau)

        return sources

    def step(self, dt: float = 0.01) -> Dict[str, any]:
        """Execute one QRFT evolution step"""
        if self.state is None:
            raise RuntimeError("State not initialized. Call initialize_state() first.")

        # Compute field invariants
        invariants = self._compute_invariants(self.state)

        # Compute trigger functions
        triggers = self._compute_triggers(invariants)

        # Compute source functions
        sources = self._compute_sources(triggers)

        # Store particle activations
        self.particle_activations = sources.copy()

        # QRFT field evolution (simplified Euler integration)
        # ∂²S/∂t² + m_S²S = sources + interactions
        # ∂²Λ/∂t² + m_Λ²Λ = sources + interactions

        # For now, implement as driven oscillator with damping
        gamma_damp = 0.1  # Phenomenological damping

        # Acceleration from field equations
        ddS_dt2 = -self.cfg.m_S**2 * self.state.S - gamma_damp * np.gradient(
            self.state.S
        )
        ddLambda_dt2 = (
            -self.cfg.m_Lambda**2 * self.state.Lambda
            - gamma_damp * np.gradient(self.state.Lambda)
        )

        # Add source contributions
        source_total = sum(sources.values())
        ddS_dt2 += source_total * 0.1  # Coupling strength
        ddLambda_dt2 += source_total * 0.1

        # Simple Euler integration (velocity-Verlet would be more accurate)
        dS_dt = ddS_dt2 * dt
        dLambda_dt = ddLambda_dt2 * dt

        # Update fields
        new_S = self.state.S + dS_dt
        new_Lambda = self.state.Lambda + dLambda_dt
        new_t = self.state.t + dt

        # Create new state
        self.state = QRFTState(
            S=new_S, Lambda=new_Lambda, t=new_t, gamma=self.cfg.gamma
        )

        self.history.append(self.state)

        # Return runtime control signals
        return {
            "triggers": triggers,
            "sources": sources,
            "invariants": invariants,
            "active_particles": [p for p, s in sources.items() if s > 0.1],
            "entropy_estimate": self._estimate_entropy(),
            "stability_check": self._check_stability(),
        }

    def _estimate_entropy(self) -> float:
        """Estimate system entropy from field gradients"""
        if self.state is None:
            return 0.0

        grad_S = np.gradient(self.state.S) if self.state.S.ndim > 0 else np.array([0.0])
        grad_Lambda = (
            np.gradient(self.state.Lambda)
            if self.state.Lambda.ndim > 0
            else np.array([0.0])
        )

        # Shannon-like entropy from gradient distributions
        prob_S = np.abs(grad_S) + 1e-12
        prob_S /= prob_S.sum()

        prob_Lambda = np.abs(grad_Lambda) + 1e-12
        prob_Lambda /= prob_Lambda.sum()

        H_S = -np.sum(prob_S * np.log(prob_S))
        H_Lambda = -np.sum(prob_Lambda * np.log(prob_Lambda))

        return float(H_S + H_Lambda)

    def _check_stability(self) -> bool:
        """Check system stability conditions"""
        if self.state is None:
            return False

        # Check field boundedness
        S_norm = float(np.linalg.norm(self.state.S))
        Lambda_norm = float(np.linalg.norm(self.state.Lambda))

        if S_norm > 1000 or Lambda_norm > 1000:
            return False

        # Check mixing parameter bound
        if abs(self.state.gamma) >= 1.0:
            return False

        return True

    def get_control_policy(self) -> str:
        """Generate control policy based on current particle activations"""
        sources = self.particle_activations

        # Priority-based policy matching QRFT specification
        if sources.get(ParticleType.GLITCHON, 0) > self.cfg.tau_G:
            return "run_counterexample_miner_and_reproof"
        elif sources.get(ParticleType.TESSERACTON, 0) > self.cfg.tau_T:
            return "switch_MoE_embedding_template"
        elif sources.get(ParticleType.LACUNON, 0) > self.cfg.tau_F:
            return "retrieve_or_ask"
        else:
            return "continue_plan"

    def apply_entropy_governor(
        self, depth: int, beam_width: int, tool_rate: float
    ) -> Tuple[int, int, float]:
        """REF entropy governor: tune parameters to keep entropy in band"""
        current_entropy = self._estimate_entropy()

        if current_entropy < self.cfg.entropy_band_low:
            # Increase exploration
            depth = min(depth + 1, 10)
            beam_width = min(beam_width + 1, 8)
            tool_rate = min(tool_rate + 0.1, 1.0)
        elif current_entropy > self.cfg.entropy_band_high:
            # Decrease exploration
            depth = max(depth - 1, 1)
            beam_width = max(beam_width - 1, 1)
            tool_rate = max(tool_rate - 0.1, 0.0)

        return depth, beam_width, tool_rate
