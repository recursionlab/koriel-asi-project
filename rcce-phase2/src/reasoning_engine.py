"""Consciousness-guided reasoning engine"""
import numpy as np
from typing import Dict, Any
from .reality_interface import Problem, RealityInterface
from .metastate import MetaState, ShadowCodex
from .dec import DEC

class ConsciousnessGuidedReasoner:
    def __init__(self, d_model=32, seed=1337):
        np.random.seed(seed)
        self.d_model = d_model
        self.dec = DEC()
        self.reality = RealityInterface(seed)
        self.codex = ShadowCodex()
        
        # Reasoning state
        self.reasoning_state = np.random.randn(d_model)
        self.consciousness_history = []
        
    def consciousness_to_reasoning_weights(self, metastate: MetaState) -> Dict[str, float]:
        """Convert consciousness metrics to reasoning guidance weights"""
        
        # Higher consciousness → more systematic reasoning
        systematic_weight = min(metastate.rc_total, 1.0)
        
        # Higher curvature → explore alternative approaches  
        exploration_weight = min(metastate.curvature / 1000.0, 1.0)
        
        # Lower energy → more focused attention
        focus_weight = max(0.1, 1.0 - metastate.energy)
        
        # Torsion → non-linear thinking capacity
        nonlinear_weight = min(metastate.torsion * 10.0, 1.0)
        
        return {
            "systematic": systematic_weight,
            "exploration": exploration_weight, 
            "focus": focus_weight,
            "nonlinear": nonlinear_weight
        }
        
    def solve_problem(self, problem: Problem, consciousness_state: MetaState) -> str:
        """Use consciousness state to guide problem solving"""
        
        # Get reasoning weights from consciousness
        weights = self.consciousness_to_reasoning_weights(consciousness_state)
        
        # Update reasoning state based on consciousness
        self.reasoning_state *= (1.0 - 0.1 * weights["exploration"])
        self.reasoning_state += 0.1 * weights["systematic"] * np.random.randn(self.d_model)
        
        # Problem-specific reasoning
        if problem.category == "arithmetic":
            return self._solve_arithmetic(problem, weights)
        elif problem.category == "logic":
            return self._solve_logic(problem, weights)
        elif problem.category == "pattern":
            return self._solve_pattern(problem, weights)
        else:
            return "unknown"
            
    def _solve_arithmetic(self, problem: Problem, weights: Dict[str, float]) -> str:
        """Solve arithmetic problems with consciousness guidance"""
        
        # Parse the arithmetic expression
        question = problem.question.strip()
        
        # Systematic approach weight influences parsing accuracy
        if weights["systematic"] > 0.5:
            # More careful parsing
            try:
                # Handle basic operations
                if " + " in question:
                    parts = question.split(" + ")
                    a, b = int(parts[0]), int(parts[1])
                    result = a + b
                elif " - " in question:
                    parts = question.split(" - ")
                    a, b = int(parts[0]), int(parts[1])
                    result = a - b
                elif " * " in question:
                    parts = question.split(" * ")
                    a, b = int(parts[0]), int(parts[1])
                    result = a * b
                else:
                    # Fallback: try to evaluate as expression
                    result = eval(question)
                    
                return str(result)
            except Exception:
                return "0"
        else:
            # Less systematic - more prone to errors
            try:
                # Quick and dirty evaluation
                result = eval(question)
                
                # Add noise based on low systematic weight
                if weights["systematic"] < 0.3:
                    noise = np.random.randint(-1, 2)
                    result += noise
                    
                return str(result)
            except Exception:
                return "0"
                
    def _solve_logic(self, problem: Problem, weights: Dict[str, float]) -> str:
        """Solve logic problems with consciousness guidance"""
        
        # Focus weight influences logical precision
        if weights["focus"] > 0.7:
            # High focus → correct logical inference
            if "All A are B" in problem.question and "X is A" in problem.question:
                return "X is B"
        
        # Lower focus → potential logical errors
        return "unknown"
        
    def _solve_pattern(self, problem: Problem, weights: Dict[str, float]) -> str:
        """Solve pattern problems with consciousness guidance"""
        
        # Nonlinear thinking helps with patterns
        if weights["nonlinear"] > 0.5:
            # Extract sequence from question
            try:
                import re
                numbers = re.findall(r'\d+', problem.question)
                if len(numbers) >= 3:
                    seq = [int(n) for n in numbers]
                    # Simple arithmetic progression detection
                    diff = seq[1] - seq[0]
                    if len(seq) > 2 and seq[2] - seq[1] == diff:
                        next_val = seq[-1] + diff
                        return str(next_val)
            except Exception:
                pass
                
        return "0"
        
    def test_and_learn(self, consciousness_state: MetaState, n_problems=5) -> Dict[str, Any]:
        """Test reasoning ability and update based on performance"""
        
        # Generate problems at current difficulty level
        difficulty = int(consciousness_state.rc_total * 2)  # 0-2 difficulty range
        problems = self.reality.generate_test_battery(difficulty, n_problems)
        
        results = []
        for problem in problems:
            response = self.solve_problem(problem, consciousness_state)
            result = self.reality.validate_response(problem, response)
            results.append(result)
            
            # Log to shadow codex
            self.codex.log(MetaState(
                t=len(self.consciousness_history),
                action=f"solve_{problem.category}",
                loss=0.0 if result.correct else 1.0,
                rc_embedding=consciousness_state.rc_embedding,
                rc_graph=consciousness_state.rc_graph,
                rc_value=consciousness_state.rc_value,
                rc_total=consciousness_state.rc_total,
                drift=consciousness_state.drift,
                d_drift=consciousness_state.d_drift,
                energy=consciousness_state.energy,
                holonomy_delta=consciousness_state.holonomy_delta,
                xi_delta=consciousness_state.xi_delta,
                upsilon_active=consciousness_state.upsilon_active,
                lambda_plus_active=consciousness_state.lambda_plus_active,
                phi33_violations=consciousness_state.phi33_violations,
                curvature=consciousness_state.curvature,
                torsion=consciousness_state.torsion,
                state_hash=f"test_{len(results)}"
            ))
        
        # Compute performance
        performance = self.reality.compute_performance_score(results)
        
        # Store for feedback
        self.consciousness_history.append({
            "consciousness_state": consciousness_state,
            "performance": performance,
            "results": results
        })
        
        return {
            "performance": performance,
            "results": results,
            "difficulty_attempted": difficulty
        }