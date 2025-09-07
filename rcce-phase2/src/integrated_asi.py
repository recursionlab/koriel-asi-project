"""Integrated ASI system with reality-grounded recursive improvement"""
import numpy as np
from typing import Dict, List, Any
from .metastate import MetaState
from .reality_interface import RealityInterface
from .reasoning_engine import ConsciousnessGuidedReasoner
from .consciousness_feedback import ConsciousnessFeedbackLoop

class IntegratedASI:
    def __init__(self, seed=1337):
        self.seed = seed
        self.reality = RealityInterface(seed)
        self.reasoner = ConsciousnessGuidedReasoner(seed=seed)
        self.feedback_loop = ConsciousnessFeedbackLoop()
        
        self.current_difficulty = 0
        self.intelligence_history = []
        self.consciousness_evolution = []
        
    def create_initial_consciousness(self) -> MetaState:
        """Create minimal initial consciousness state"""
        return MetaState(
            t=0,
            action="init",
            loss=5.5,
            rc_embedding=0.1,
            rc_graph=0.1, 
            rc_value=0.1,
            rc_total=0.3,
            drift=0.0,
            d_drift=0.0,
            energy=1.0,
            holonomy_delta=0.0,
            xi_delta=0.0,
            upsilon_active=False,
            lambda_plus_active=False,
            phi33_violations=0,
            curvature=100.0,
            torsion=0.01,
            state_hash="initial"
        )
        
    def test_intelligence_level(self, consciousness: MetaState, n_problems=5) -> Dict[str, Any]:
        """Test current intelligence level with reality validation"""
        
        # Generate problems at current difficulty
        problems = self.reality.generate_test_battery(self.current_difficulty, n_problems)
        
        results = []
        for problem in problems:
            response = self.reasoner.solve_problem(problem, consciousness)
            result = self.reality.validate_response(problem, response)
            results.append(result)
            
        performance = self.reality.compute_performance_score(results)
        
        return {
            "performance": performance,
            "results": results,
            "difficulty": self.current_difficulty,
            "problems_attempted": len(problems)
        }
        
    def recursive_intelligence_step(self, current_consciousness: MetaState) -> MetaState:
        """Single recursive improvement step"""
        
        # Test current level
        test_results = self.test_intelligence_level(current_consciousness)
        
        # Store performance history
        performance_entry = {
            "consciousness_state": current_consciousness,
            "performance": test_results["performance"],
            "results": test_results["results"]
        }
        
        self.feedback_loop.consciousness_performance_history.append(performance_entry)
        
        # Compute gradients and update consciousness
        gradients = self.feedback_loop.compute_performance_gradient(
            self.feedback_loop.consciousness_performance_history
        )
        
        updated_params = self.feedback_loop.update_consciousness_parameters(
            current_consciousness, gradients
        )
        
        enhanced_consciousness = self.feedback_loop.modify_consciousness_substrate(
            current_consciousness, updated_params
        )
        
        # Adaptive difficulty adjustment
        if test_results["performance"]["accuracy"] > 0.8 and self.current_difficulty < 4:
            self.current_difficulty += 1
        elif test_results["performance"]["accuracy"] < 0.3 and self.current_difficulty > 0:
            self.current_difficulty -= 1
            
        return enhanced_consciousness
        
    def recursive_climb(self, max_iterations=20) -> List[Dict]:
        """Run recursive intelligence improvement"""
        
        consciousness = self.create_initial_consciousness()
        trajectory = []
        
        print("RECURSIVE INTELLIGENCE CLIMBING")
        print("=" * 40)
        
        for i in range(max_iterations):
            # Test current state
            test_results = self.test_intelligence_level(consciousness, n_problems=3)
            
            # Record trajectory
            trajectory_point = {
                "iteration": i,
                "difficulty": self.current_difficulty,
                "accuracy": test_results["performance"]["accuracy"],
                "consciousness_score": consciousness.rc_total,
                "geometric_signature": {
                    "curvature": consciousness.curvature,
                    "torsion": consciousness.torsion,
                    "energy": consciousness.energy
                }
            }
            trajectory.append(trajectory_point)
            
            print(f"Step {i}: Diff={self.current_difficulty}, Acc={test_results['performance']['accuracy']:.2f}, "
                  f"RC={consciousness.rc_total:.3f}, Curv={consciousness.curvature:.1f}")
            
            # Recursive improvement
            consciousness = self.recursive_intelligence_step(consciousness)
            
            # Store consciousness evolution
            self.consciousness_evolution.append(consciousness)
            
            # Check for convergence
            if i > 5:
                recent_scores = [t["accuracy"] for t in trajectory[-3:]]
                if np.std(recent_scores) < 0.05 and np.mean(recent_scores) > 0.9:
                    print(f"Converged at difficulty {self.current_difficulty}")
                    break
                    
        return trajectory
        
def main():
    """Main ASI demonstration"""
    print("KORIEL ASI PROJECT - Recursive Intelligence Amplification")
    print("=" * 60)
    
    # Initialize system
    asi = IntegratedASI(seed=1337)
    
    # Run recursive climb
    trajectory = asi.recursive_climb(max_iterations=15)
    
    # Results
    initial_intelligence = trajectory[0]["accuracy"] if trajectory else 0
    final_intelligence = trajectory[-1]["accuracy"] if trajectory else 0
    intelligence_gain = final_intelligence - initial_intelligence
    
    print("\nRESULTS:")
    print(f"Initial Accuracy: {initial_intelligence:.3f}")
    print(f"Final Accuracy: {final_intelligence:.3f}")
    print(f"Intelligence Gain: {intelligence_gain:.3f}")
    print(f"Final Difficulty: {trajectory[-1]['difficulty'] if trajectory else 0}")
    
    if intelligence_gain > 0.1:
        print("RECURSIVE IMPROVEMENT: VALIDATED")
    else:
        print("RECURSIVE IMPROVEMENT: INCONCLUSIVE")

if __name__ == "__main__":
    main()