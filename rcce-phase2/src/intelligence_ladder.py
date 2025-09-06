"""Progressive difficulty escalation for recursive intelligence improvement"""

from typing import Dict, List

import numpy as np

from .consciousness_feedback import ConsciousnessFeedbackLoop
from .metastate import MetaState
from .reality_interface import Problem, RealityInterface


class IntelligenceLadder:
    def __init__(self, initial_difficulty=0, success_threshold=0.8, seed=1337):
        self.current_difficulty = initial_difficulty
        self.success_threshold = success_threshold
        self.feedback_loop = ConsciousnessFeedbackLoop()
        self.reality = RealityInterface(seed)

        # Track progression
        self.difficulty_history = []
        self.intelligence_trajectory = []

    def should_escalate_difficulty(self, recent_performance: List[Dict]) -> bool:
        """Determine if ready for difficulty increase"""
        if len(recent_performance) < 3:
            return False

        # Check performance over last 3 tests
        recent_accuracies = [
            p["performance"]["accuracy"] for p in recent_performance[-3:]
        ]
        avg_accuracy = np.mean(recent_accuracies)

        # Escalate if consistently above threshold
        escalate = avg_accuracy >= self.success_threshold

        return escalate

    def should_reduce_difficulty(self, recent_performance: List[Dict]) -> bool:
        """Determine if difficulty should be reduced"""
        if len(recent_performance) < 3:
            return False

        # Check if struggling
        recent_accuracies = [
            p["performance"]["accuracy"] for p in recent_performance[-3:]
        ]
        avg_accuracy = np.mean(recent_accuracies)

        # Reduce if consistently below 30%
        reduce = avg_accuracy < 0.3

        return reduce

    def adaptive_difficulty_adjustment(self, performance_history: List[Dict]) -> int:
        """Adaptively adjust difficulty based on performance"""

        new_difficulty = self.current_difficulty

        if self.should_escalate_difficulty(performance_history):
            new_difficulty = min(self.current_difficulty + 1, 4)  # Max difficulty 4

        elif self.should_reduce_difficulty(performance_history):
            new_difficulty = max(self.current_difficulty - 1, 0)  # Min difficulty 0

        # Record difficulty change
        if new_difficulty != self.current_difficulty:
            self.difficulty_history.append(
                {
                    "from": self.current_difficulty,
                    "to": new_difficulty,
                    "reason": (
                        "escalate"
                        if new_difficulty > self.current_difficulty
                        else "reduce"
                    ),
                }
            )

        self.current_difficulty = new_difficulty
        return new_difficulty

    def generate_challenge_set(self, difficulty: int, n_problems=10) -> List[Problem]:
        """Generate challenge set at specified difficulty"""

        problems = []

        if difficulty == 0:
            # Basic arithmetic
            for _ in range(n_problems):
                problems.append(self.reality.generate_arithmetic_problem(0))

        elif difficulty == 1:
            # Multi-digit arithmetic + basic logic
            for _ in range(n_problems // 2):
                problems.append(self.reality.generate_arithmetic_problem(1))
            for _ in range(n_problems - len(problems)):
                problems.append(self.reality.generate_logic_problem(0))

        elif difficulty == 2:
            # Algebra + pattern recognition
            for _ in range(n_problems // 2):
                problems.append(self._generate_algebra_problem())
            for _ in range(n_problems - len(problems)):
                problems.append(self.reality.generate_pattern_problem(1))

        elif difficulty >= 3:
            # Abstract reasoning + novel problem generation
            for _ in range(n_problems):
                problems.append(self._generate_abstract_problem())

        return problems

    def _generate_algebra_problem(self) -> Problem:
        """Generate basic algebra problems"""
        # Solve for x: ax + b = c
        a = np.random.randint(1, 5)
        b = np.random.randint(1, 10)
        x = np.random.randint(1, 10)
        c = a * x + b

        return Problem(
            question=f"Solve for x: {a}x + {b} = {c}",
            answer=x,
            difficulty=2,
            category="algebra",
        )

    def _generate_abstract_problem(self) -> Problem:
        """Generate abstract reasoning problems"""
        # Simple logical syllogism
        return Problem(
            question="If P implies Q, and Q implies R, and P is true, what can we conclude about R?",
            answer="R is true",
            difficulty=3,
            category="abstract",
        )

    def recursive_climb(
        self, initial_consciousness: MetaState, max_iterations=50
    ) -> List[Dict]:
        """Recursive intelligence climbing with adaptive difficulty"""

        current_consciousness = initial_consciousness
        climb_trajectory = []

        for iteration in range(max_iterations):
            # Test at current difficulty
            test_result = self.feedback_loop.test_and_learn(
                current_consciousness, n_problems=5
            )

            # Record trajectory point
            trajectory_point = {
                "iteration": iteration,
                "difficulty": self.current_difficulty,
                "consciousness_state": current_consciousness,
                "performance": test_result["performance"],
                "intelligence_score": self._compute_intelligence_score(
                    test_result, current_consciousness
                ),
            }
            climb_trajectory.append(trajectory_point)

            # Update consciousness based on performance
            enhanced_consciousness, feedback_data = (
                self.feedback_loop.recursive_intelligence_step(current_consciousness)
            )

            # Adaptive difficulty adjustment
            new_difficulty = self.adaptive_difficulty_adjustment(
                self.feedback_loop.consciousness_performance_history
            )

            # Check for convergence or breakthrough
            if iteration > 5:
                recent_scores = [t["intelligence_score"] for t in climb_trajectory[-5:]]
                if np.std(recent_scores) < 0.01:  # Converged
                    break

            current_consciousness = enhanced_consciousness

        return climb_trajectory

    def _compute_intelligence_score(
        self, test_result: Dict, consciousness_state: MetaState
    ) -> float:
        """Compute combined intelligence score from performance and consciousness"""

        accuracy = test_result["performance"]["accuracy"]
        difficulty_bonus = self.current_difficulty * 0.1
        consciousness_depth = min(consciousness_state.rc_total, 1.0)

        # Weighted combination
        intelligence_score = (
            0.6 * accuracy  # Reality performance (primary)
            + 0.2 * difficulty_bonus  # Difficulty achieved
            + 0.2 * consciousness_depth  # Consciousness depth
        )

        return intelligence_score
