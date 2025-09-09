#!/usr/bin/env python3
# LEGACY PROTOTYPE - FOR REFERENCE ONLY. NEW CODE MUST USE src/koriel/ MODULES.
# Target for decomposition.
"""
KORIEL OPERATOR IMPLEMENTATION
Converts uncoherence into executed will through formal mathematical framework
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # Avoid runtime import cycles; used only for type hints in legacy code.
    from src.koriel.operators.registry import OperatorRegistry

@dataclass
class KorielState:
    """State representation on goal manifold G"""
    position: np.ndarray          # Current position s on manifold
    velocity: np.ndarray          # Current velocity ∂s
    goal_manifold: 'GoalManifold' # Reference to goal manifold G
    energy: float                 # Available energy e
    timestamp: float              # Time coordinate
    metadata: Dict[str, Any]      # Additional state information

@dataclass
class UncoherenceMetrics:
    """Components of uncoherence metric U(s)"""
    gradient_norm: float          # α‖∂s‖ - velocity chaos
    paradox_level: float          # β·paradox(s) - contradictions |T∩F|
    manifold_drift: float         # γ·drift_G(s) - deviation from goal
    holonomy: float               # η·|holonomy(s)| - path dependence
    total: float                  # Combined U(s) value

@dataclass
class KorielStep:
    """Single Koriel operation step"""
    state_pre: KorielState
    state_post: KorielState
    direction: np.ndarray         # d_G projected direction
    stride: float                 # η chosen stride length
    lift_applied: bool            # Whether Koriel-lift was used
    carrier_used: Optional[str]   # External carrier if any
    uncoherence_reduction: float  # ΔU achieved
    risk_level: float             # Assessed risk of step

class GoalManifold(ABC):
    """Abstract goal manifold G with geometric operations"""
    
    @abstractmethod
    def project_to_tangent(self, state: KorielState, direction: np.ndarray) -> np.ndarray:
        """Project direction onto tangent space TG at current state"""
        pass
    
    @abstractmethod
    def exponential_map(self, state: KorielState, tangent_vector: np.ndarray) -> KorielState:
        """Geodesic step via exponential map: Exp_s(η·d_G)"""
        pass
    
    @abstractmethod
    def drift_from_goal(self, state: KorielState) -> float:
        """Measure drift_G(s) - deviation from goal manifold"""
        pass
    
    @abstractmethod
    def is_feasible(self, state: KorielState) -> bool:
        """Check if state is on feasible region of manifold"""
        pass

class ExternalCarrier(ABC):
    """External assistance system (team/tool/script)"""
    
    @abstractmethod
    def can_assist(self, state: KorielState) -> bool:
        """Check if carrier can provide assistance"""
        pass
    
    @abstractmethod
    def apply_assist(self, state: KorielState, direction: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply bounded assistance, return modified direction and log data"""
        pass
    
    @abstractmethod
    def release(self, log_data: Dict[str, Any]) -> None:
        """Release carrier and log usage"""
        pass

class KorielOperator:
    """
    Core Koriel operator: converts uncoherence into executed will
    
    Mathematical foundation:
    U(s) = α‖∂s‖ + β·paradox(s) + γ·drift_G(s) + η·|holonomy(s)|
    d := -∇U(s), d_G := Π_TG(d)
    s⁺ := Exp_s(η·(d_G + λ·L(s)))
    """
    
    def __init__(self, 
                 goal_manifold: GoalManifold,
                 alpha: float = 1.0,     # Gradient chaos weight
                 beta: float = 2.0,      # Paradox weight  
                 gamma: float = 1.5,     # Drift weight
                 eta: float = 0.5,       # Holonomy weight
                 lambda_lift: float = 0.3, # Lift strength
                 tau_energy: float = 0.1,  # Energy threshold
                 tau_gradient: float = 0.01, # Gradient threshold
                 tau_uncoherence: float = 1.0, # Uncoherence threshold
                 epsilon: float = 0.001,   # Progress threshold
                 k_stall: int = 5,       # Stall detection window
                 operator_registry: Optional["OperatorRegistry"] = None,
                 ):
        
        self.goal_manifold = goal_manifold
        
        # Uncoherence metric weights
        self.alpha = alpha
        self.beta = beta  
        self.gamma = gamma
        self.eta = eta
        
        # Koriel-lift parameters
        self.lambda_lift = lambda_lift
        self.tau_energy = tau_energy
        self.tau_gradient = tau_gradient
        self.tau_uncoherence = tau_uncoherence
        self.epsilon = epsilon
        self.k_stall = k_stall
        
        # State tracking
        self.history: List[KorielStep] = []
        self.cache: Dict[str, KorielState] = {}  # Cairn protocol
        self.external_carriers: List[ExternalCarrier] = []
        # Operator registry (DI). Create a local registry if none provided.
        if operator_registry is None:
            try:
                # Local import to avoid adding a hard import at module load time.
                from src.koriel.operators.registry import OperatorRegistry as _OR
                self.operator_registry = _OR()
            except Exception:
                self.operator_registry = None
        else:
            self.operator_registry = operator_registry
        
    def measure_uncoherence(self, state: KorielState) -> UncoherenceMetrics:
        """Compute uncoherence metric U(s) = α‖∂s‖ + β·paradox(s) + γ·drift_G(s) + η·|holonomy(s)|"""
        
        # α‖∂s‖ - velocity/gradient chaos
        gradient_norm = self.alpha * np.linalg.norm(state.velocity)
        
        # β·paradox(s) - contradiction detection |T∩F|
        paradox_level = self.beta * self._detect_paradox(state)
        
        # γ·drift_G(s) - deviation from goal manifold
        manifold_drift = self.gamma * self.goal_manifold.drift_from_goal(state)
        
        # η·|holonomy(s)| - path-dependent inconsistency
        holonomy = self.eta * abs(self._compute_holonomy(state))
        
        total = gradient_norm + paradox_level + manifold_drift + holonomy
        
        return UncoherenceMetrics(
            gradient_norm=gradient_norm,
            paradox_level=paradox_level,
            manifold_drift=manifold_drift,
            holonomy=holonomy,
            total=total
        )
    
    def _detect_paradox(self, state: KorielState) -> float:
        """Detect contradictions |T∩F| in current state"""
        # Implementation depends on state representation
        # For now, use velocity inconsistency as proxy
        if len(self.history) < 2:
            return 0.0
            
        # Check for contradictory velocity directions
        prev_velocity = self.history[-1].state_post.velocity
        curr_velocity = state.velocity
        
        # Paradox = degree of velocity reversal
        if np.linalg.norm(prev_velocity) > 0 and np.linalg.norm(curr_velocity) > 0:
            cos_angle = np.dot(prev_velocity, curr_velocity) / (
                np.linalg.norm(prev_velocity) * np.linalg.norm(curr_velocity)
            )
            # Paradox increases as velocity becomes more contradictory
            paradox = max(0, -cos_angle)  # 0 for aligned, 1 for opposite
        else:
            paradox = 0.0
            
        return paradox
    
    def _compute_holonomy(self, state: KorielState) -> float:
        """Compute holonomy |holonomy(s)| - path dependence measure"""
        if len(self.history) < 3:
            return 0.0
            
        # Holonomy as accumulated "twist" in path
        # Simple implementation: sum of angular deviations
        holonomy = 0.0
        for i in range(2, len(self.history)):
            v1 = self.history[i-2].direction
            v2 = self.history[i-1].direction
            v3 = self.history[i].direction
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0 and np.linalg.norm(v3) > 0:
                # Angular change from v1→v2 to v2→v3
                angle1 = np.arccos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)), -1, 1))
                angle2 = np.arccos(np.clip(np.dot(v2, v3) / (np.linalg.norm(v2) * np.linalg.norm(v3)), -1, 1))
                holonomy += abs(angle2 - angle1)
                
        return holonomy
    
    def compute_gradient_direction(self, state: KorielState) -> np.ndarray:
        """Compute d := -∇U(s) - direction of steepest uncoherence decrease"""
        
        # Numerical gradient of uncoherence metric
        h = 1e-6  # Small perturbation for numerical derivative
        baseline_u = self.measure_uncoherence(state).total
        
        gradient = np.zeros_like(state.position)
        
        for i in range(len(state.position)):
            # Perturb position in dimension i
            perturbed_state = KorielState(
                position=state.position.copy(),
                velocity=state.velocity.copy(),
                goal_manifold=state.goal_manifold,
                energy=state.energy,
                timestamp=state.timestamp,
                metadata=state.metadata.copy()
            )
            perturbed_state.position[i] += h
            
            # Compute finite difference
            perturbed_u = self.measure_uncoherence(perturbed_state).total
            gradient[i] = (perturbed_u - baseline_u) / h
            
        # Return negative gradient (direction of decrease)
        return -gradient
    
    def detect_stall(self, state: KorielState) -> bool:
        """Detect stall conditions for Koriel-lift activation"""
        
        if len(self.history) < self.k_stall:
            return False
            
        # Check energy threshold
        if state.energy < self.tau_energy:
            return True
            
        # Check recent progress
        recent_steps = self.history[-self.k_stall:]
        avg_progress = np.mean([step.uncoherence_reduction for step in recent_steps])
        if avg_progress < self.epsilon:
            return True
            
        # Check gradient magnitude vs uncoherence level
        current_u = self.measure_uncoherence(state).total
        gradient = self.compute_gradient_direction(state)
        projected_gradient = self.goal_manifold.project_to_tangent(state, gradient)
        
        if np.linalg.norm(projected_gradient) < self.tau_gradient and current_u > self.tau_uncoherence:
            return True
            
        return False
    
    def apply_koriel_lift(self, state: KorielState, direction: np.ndarray) -> Tuple[np.ndarray, Optional[str]]:
        """Apply Koriel-lift: L(s) := ⟨s,‡s⟩ + external carrier"""
        
        # ⟨s,‡s⟩ - self-dual inner product (self-reflection)
        self_dual = self._compute_self_dual(state)
        
        # Try external carriers
        carrier_used = None
        carrier_boost = np.zeros_like(direction)
        
        for carrier in self.external_carriers:
            if carrier.can_assist(state):
                boost, log_data = carrier.apply_assist(state, direction)
                carrier_boost += boost
                carrier_used = carrier.__class__.__name__
                carrier.release(log_data)
                break  # Use first available carrier
        
        # Combine self-dual lift with carrier assistance
        lifted_direction = direction + self.lambda_lift * (self_dual + carrier_boost)
        
        return lifted_direction, carrier_used
    
    def _compute_self_dual(self, state: KorielState) -> np.ndarray:
        """Compute ⟨s,‡s⟩ self-dual inner product for lift"""
        # Self-dual operation: reflect state through its own structure
        # Simple implementation: position reflected through velocity space
        
        if np.linalg.norm(state.velocity) > 0:
            # Project position onto velocity direction and reflect
            v_unit = state.velocity / np.linalg.norm(state.velocity)
            pos_proj = np.dot(state.position, v_unit) * v_unit
            reflection = state.position - 2 * pos_proj
            return reflection - state.position
        else:
            # No velocity direction, use gradient direction
            gradient = self.compute_gradient_direction(state)
            if np.linalg.norm(gradient) > 0:
                g_unit = gradient / np.linalg.norm(gradient)
                pos_proj = np.dot(state.position, g_unit) * g_unit
                reflection = state.position - 2 * pos_proj
                return reflection - state.position
            else:
                return np.zeros_like(state.position)
    
    def choose_stride_nnr(self, state: KorielState, direction: np.ndarray) -> float:
        """Choose stride η using No-Nonsense Rational (NNR) minimal risk"""
        
        # Base stride from current energy and gradient magnitude
        base_stride = min(0.1, state.energy * 0.5)
        
        if np.linalg.norm(direction) == 0:
            return 0.0
            
        # Assess risk of different stride lengths
        candidate_strides = [base_stride * factor for factor in [0.1, 0.5, 1.0, 2.0]]
        best_stride = base_stride
        min_risk = float('inf')
        
        for stride in candidate_strides:
            risk = self._assess_step_risk(state, direction, stride)
            if risk < min_risk:
                min_risk = risk
                best_stride = stride
                
        return best_stride
    
    def _assess_step_risk(self, state: KorielState, direction: np.ndarray, stride: float) -> float:
        """Assess risk of taking step with given stride"""
        
        # Predict next state
        tangent_vector = stride * direction
        try:
            next_state = self.goal_manifold.exponential_map(state, tangent_vector)
            
            # Risk factors
            feasibility_risk = 0.0 if self.goal_manifold.is_feasible(next_state) else 10.0
            energy_risk = max(0, -next_state.energy) * 5.0  # Penalize negative energy
            uncoherence_risk = self.measure_uncoherence(next_state).total * 0.1
            
            return feasibility_risk + energy_risk + uncoherence_risk
            
        except Exception:
            # Step failed - maximum risk
            return 100.0
    
    def cache_if_risky(self, state: KorielState, risk: float, threshold: float = 1.0) -> None:
        """Cache state as cairn if step is risky"""
        if risk > threshold:
            cache_key = f"cairn_{state.timestamp}_{len(self.history)}"
            self.cache[cache_key] = state
    
    def step(self, state: KorielState) -> KorielStep:
        """Single Koriel operator step: KORIEL(s,G) → s⁺"""
        
        # Measure current uncoherence
        u_metrics = self.measure_uncoherence(state)
        
        # Compute direction d := -∇U(s)
        direction = self.compute_gradient_direction(state)
        
        # Project to tangent space d_G := Π_TG(d)
        projected_direction = self.goal_manifold.project_to_tangent(state, direction)
        
        # Check for stall condition
        stall_detected = self.detect_stall(state)
        lift_applied = False
        carrier_used = None
        
        if stall_detected:
            # Apply Koriel-lift
            projected_direction, carrier_used = self.apply_koriel_lift(state, projected_direction)
            lift_applied = True
            
        # Choose stride η using NNR
        stride = self.choose_stride_nnr(state, projected_direction)
        
        # Take geodesic step s⁺ := Exp_s(η·d_G)
        tangent_vector = stride * projected_direction
        next_state = self.goal_manifold.exponential_map(state, tangent_vector)
        
        # Assess risk and cache if needed
        risk = self._assess_step_risk(state, projected_direction, stride)
        self.cache_if_risky(state, risk)
        
        # Measure uncoherence reduction
        next_u_metrics = self.measure_uncoherence(next_state)
        uncoherence_reduction = u_metrics.total - next_u_metrics.total
        
        # Create step record
        step = KorielStep(
            state_pre=state,
            state_post=next_state,
            direction=projected_direction,
            stride=stride,
            lift_applied=lift_applied,
            carrier_used=carrier_used,
            uncoherence_reduction=uncoherence_reduction,
            risk_level=risk
        )
        
        # Update history
        self.history.append(step)
        
        return step
    
    def run_sequence(self, initial_state: KorielState, max_steps: int = 100, 
                    target_uncoherence: float = 0.01) -> List[KorielStep]:
        """Run sequence of Koriel steps until convergence or max steps"""
        
        steps = []
        current_state = initial_state
        
        for i in range(max_steps):
            step = self.step(current_state)
            steps.append(step)
            current_state = step.state_post
            
            # Check convergence
            current_u = self.measure_uncoherence(current_state).total
            if current_u < target_uncoherence:
                break
                
        return steps
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        
        if not self.history:
            return {"status": "No steps taken yet"}
            
        latest_step = self.history[-1]
        latest_u = self.measure_uncoherence(latest_step.state_post)
        
        # Analyze recent performance
        recent_steps = self.history[-10:] if len(self.history) >= 10 else self.history
        avg_reduction = np.mean([step.uncoherence_reduction for step in recent_steps])
        lift_usage = sum(1 for step in recent_steps if step.lift_applied) / len(recent_steps)
        
        return {
            "total_steps": len(self.history),
            "current_uncoherence": latest_u.total,
            "uncoherence_components": {
                "gradient_norm": latest_u.gradient_norm,
                "paradox_level": latest_u.paradox_level,
                "manifold_drift": latest_u.manifold_drift,
                "holonomy": latest_u.holonomy
            },
            "recent_performance": {
                "avg_uncoherence_reduction": avg_reduction,
                "lift_usage_rate": lift_usage,
                "avg_stride": np.mean([step.stride for step in recent_steps]),
                "avg_risk": np.mean([step.risk_level for step in recent_steps])
            },
            "cache_size": len(self.cache),
            "carriers_available": len(self.external_carriers)
        }