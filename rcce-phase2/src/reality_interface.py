"""Reality interface for math problem generation and validation"""

import random
from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np


@dataclass
class Problem:
    question: str
    answer: Any
    difficulty: int
    category: str


@dataclass
class TestResult:
    correct: bool
    response: Any
    expected: Any
    problem_id: str


class RealityInterface:
    def __init__(self, seed=1337):
        random.seed(seed)
        np.random.seed(seed)
        self.problem_bank = []
        self.difficulty_levels = {
            0: "basic_arithmetic",
            1: "multi_digit",
            2: "algebra",
            3: "calculus",
            4: "abstract",
        }

    def generate_arithmetic_problem(self, difficulty=0):
        """Generate arithmetic problems by difficulty"""
        if difficulty == 0:
            # Basic single digit
            a, b = random.randint(1, 9), random.randint(1, 9)
            op = random.choice(["+", "-", "*"])
            if op == "+":
                return Problem(f"{a} + {b}", a + b, 0, "arithmetic")
            elif op == "-" and a >= b:
                return Problem(f"{a} - {b}", a - b, 0, "arithmetic")
            else:
                return Problem(f"{a} * {b}", a * b, 0, "arithmetic")

        elif difficulty == 1:
            # Multi-digit
            a, b = random.randint(10, 99), random.randint(10, 99)
            op = random.choice(["+", "-"])
            if op == "+":
                return Problem(f"{a} + {b}", a + b, 1, "arithmetic")
            else:
                return Problem(f"{max(a,b)} - {min(a,b)}", abs(a - b), 1, "arithmetic")

    def generate_logic_problem(self, difficulty=0):
        """Generate logical reasoning problems"""
        if difficulty == 0:
            # Basic logical inference
            premises = ["All A are B", "X is A"]
            conclusion = "X is B"
            return Problem(
                f"Given: {premises[0]}, {premises[1]}. Conclude:",
                conclusion,
                0,
                "logic",
            )

    def generate_pattern_problem(self, difficulty=0):
        """Generate pattern recognition problems"""
        if difficulty == 0:
            # Simple sequence
            seq = [2, 4, 6, 8]
            return Problem(f"Continue sequence: {seq} → ?", 10, 0, "pattern")

    def validate_response(self, problem: Problem, response: str) -> TestResult:
        """Validate response against ground truth"""
        try:
            if problem.category == "arithmetic":
                parsed_response = float(response.strip())
                correct = abs(parsed_response - problem.answer) < 1e-6
            elif problem.category == "logic":
                correct = response.strip().lower() in [
                    "x is b",
                    "x is b.",
                    "conclusion: x is b",
                ]
            elif problem.category == "pattern":
                parsed_response = int(response.strip())
                correct = parsed_response == problem.answer
            else:
                correct = False

            return TestResult(
                correct=correct,
                response=response,
                expected=problem.answer,
                problem_id=f"{problem.category}_{problem.difficulty}",
            )
        except:
            return TestResult(
                correct=False,
                response=response,
                expected=problem.answer,
                problem_id=f"{problem.category}_{problem.difficulty}",
            )

    def generate_test_battery(self, difficulty_level=0, n_problems=10):
        """Generate battery of tests at given difficulty"""
        problems = []
        for _ in range(n_problems // 3):
            problems.append(self.generate_arithmetic_problem(difficulty_level))
        for _ in range(n_problems // 3):
            problems.append(self.generate_logic_problem(min(difficulty_level, 0)))
        for _ in range(n_problems - len(problems)):
            problems.append(self.generate_pattern_problem(min(difficulty_level, 0)))

        return problems

    def compute_performance_score(self, results: List[TestResult]) -> Dict[str, float]:
        """Compute performance metrics from test results"""
        if not results:
            return {"accuracy": 0.0, "n_tests": 0}

        accuracy = sum(1 for r in results if r.correct) / len(results)

        by_category = {}
        for result in results:
            cat = result.problem_id.split("_")[0]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(result.correct)

        category_scores = {
            f"{cat}_accuracy": sum(scores) / len(scores)
            for cat, scores in by_category.items()
        }

        return {"accuracy": accuracy, "n_tests": len(results), **category_scores}
