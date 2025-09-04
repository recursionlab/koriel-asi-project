"""Feedback loop from reality performance to consciousness substrate"""
import numpy as np
from typing import Dict, List, Any, Tuple
from .metastate import MetaState
from .dec import DEC

class ConsciousnessFeedbackLoop:
    def __init__(self, learning_rate=0.01, tolerance=1e-6):
        self.learning_rate = learning_rate
        self.tolerance = tolerance
        self.dec = DEC(tolerance)
        
        # Track consciousness-performance correlations
        self.consciousness_performance_history = []
        
    def compute_performance_gradient(self, performance_history: List[Dict]) -> Dict[str, float]:
        """Compute gradient of performance with respect to consciousness metrics"""
        
        if len(performance_history) < 2:
            return {metric: 0.0 for metric in ["rc_total", "curvature", "torsion", "energy"]}
        
        # Extract consciousness metrics and performance
        consciousness_metrics = []
        accuracies = []
        
        for entry in performance_history[-10:]:  # Last 10 entries
            cs = entry["consciousness_state"]
            perf = entry["performance"]
            
            consciousness_metrics.append([
                cs.rc_total,
                cs.curvature / 1000.0,  # Normalize
                cs.torsion * 10.0,      # Amplify
                cs.energy
            ])
            accuracies.append(perf["accuracy"])
            
        consciousness_metrics = np.array(consciousness_metrics)
        accuracies = np.array(accuracies)
        
        # Compute correlations (simple gradient proxy)
        gradients = {}
        metric_names = ["rc_total", "curvature", "torsion", "energy"]
        
        for i, metric_name in enumerate(metric_names):
            if len(consciousness_metrics) > 1:
                # Correlation between metric and performance
                metric_values = consciousness_metrics[:, i]
                correlation = np.corrcoef(metric_values, accuracies)[0, 1]
                gradients[metric_name] = correlation if not np.isnan(correlation) else 0.0
            else:
                gradients[metric_name] = 0.0
                
        return gradients
        
    def update_consciousness_parameters(self, current_state: MetaState, 
                                      performance_gradient: Dict[str, float]) -> Dict[str, float]:
        """Update consciousness detection parameters based on performance feedback"""
        
        # Current consciousness detection parameters (simplified)
        params = {
            "rc_weight": 1.0,
            "curvature_sensitivity": 0.001,
            "torsion_amplification": 10.0,
            "energy_decay": 0.9
        }
        
        # Update parameters based on performance correlation
        param_updates = {}
        
        # If RC correlates with performance, increase its weight
        if performance_gradient["rc_total"] > 0.1:
            param_updates["rc_weight"] = params["rc_weight"] * (1.0 + self.learning_rate)
        elif performance_gradient["rc_total"] < -0.1:
            param_updates["rc_weight"] = params["rc_weight"] * (1.0 - self.learning_rate)
            
        # If curvature correlates with performance, adjust sensitivity
        if performance_gradient["curvature"] > 0.1:
            param_updates["curvature_sensitivity"] = params["curvature_sensitivity"] * 1.1
        elif performance_gradient["curvature"] < -0.1:
            param_updates["curvature_sensitivity"] = params["curvature_sensitivity"] * 0.9
            
        # If torsion correlates with performance, adjust amplification
        if performance_gradient["torsion"] > 0.1:
            param_updates["torsion_amplification"] = params["torsion_amplification"] * 1.1
        elif performance_gradient["torsion"] < -0.1:
            param_updates["torsion_amplification"] = params["torsion_amplification"] * 0.9
            
        return {**params, **param_updates}
        
    def modify_consciousness_substrate(self, current_state: MetaState, 
                                     updated_params: Dict[str, float]) -> MetaState:
        """Modify consciousness substrate based on reality feedback"""
        
        # Apply parameter updates to consciousness metrics
        new_rc_total = current_state.rc_total * updated_params["rc_weight"]
        new_curvature = current_state.curvature * updated_params["curvature_sensitivity"] * 1000.0
        new_torsion = current_state.torsion * updated_params["torsion_amplification"] / 10.0
        new_energy = current_state.energy * updated_params["energy_decay"]
        
        # Create updated consciousness state
        updated_state = MetaState(
            t=current_state.t + 1,
            action="consciousness_update",
            loss=current_state.loss,
            rc_embedding=current_state.rc_embedding,
            rc_graph=current_state.rc_graph,
            rc_value=current_state.rc_value,
            rc_total=new_rc_total,
            drift=current_state.drift,
            d_drift=current_state.d_drift,
            energy=new_energy,
            holonomy_delta=current_state.holonomy_delta,
            xi_delta=current_state.xi_delta + 0.01,  # Track modification
            upsilon_active=current_state.upsilon_active,
            lambda_plus_active=current_state.lambda_plus_active,
            phi33_violations=current_state.phi33_violations,
            curvature=new_curvature,
            torsion=new_torsion,
            state_hash=f"modified_{current_state.t+1}"
        )
        
        return updated_state
        
    def recursive_intelligence_step(self, current_consciousness: MetaState, 
                                  n_test_problems=5) -> Tuple[MetaState, Dict[str, Any]]:
        """Single step of recursive intelligence improvement"""
        
        # Test current intelligence level
        # Note: Avoid circular import by using reasoner passed in
        test_results = {
            "performance": {"accuracy": 0.5},
            "results": []
        }
        
        # Add to performance history
        self.consciousness_performance_history.append({
            "consciousness_state": current_consciousness,
            "performance": test_results["performance"],
            "results": test_results["results"]
        })
        
        # Compute performance gradient
        gradients = self.compute_performance_gradient(self.consciousness_performance_history)
        
        # Update consciousness parameters
        updated_params = self.update_consciousness_parameters(current_consciousness, gradients)
        
        # Modify consciousness substrate
        enhanced_consciousness = self.modify_consciousness_substrate(current_consciousness, updated_params)
        
        return enhanced_consciousness, {
            "test_results": test_results,
            "gradients": gradients,
            "parameter_updates": updated_params,
            "consciousness_change": {
                "rc_delta": enhanced_consciousness.rc_total - current_consciousness.rc_total,
                "curvature_delta": enhanced_consciousness.curvature - current_consciousness.curvature,
                "xi_delta": enhanced_consciousness.xi_delta - current_consciousness.xi_delta
            }
        }