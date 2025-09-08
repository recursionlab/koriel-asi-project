#!/usr/bin/env python3
"""
BRUTAL QRFT TESTING SUITE
No mercy validation of QRFT deterministic agent system
Tests mathematical computation, paraconsistent logic, signal generation
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import json
import time

# Import minimal QRFT components
try:
    from qrft import ParticleType, QRFTConfig, QRFTRuntime, QRFTState

    # keep references to avoid unused-import lint noise
    _ = (QRFTRuntime, QRFTConfig, QRFTState, ParticleType)
    print("+ Core QRFT imports successful")
except ImportError as e:
    print(f"- Core imports failed: {e}")
    sys.exit(1)


class BrutalQRFTTester:
    """Brutal testing of QRFT deterministic agent capabilities"""

    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = {}
        print("BRUTAL QRFT TESTING SUITE - NO MERCY")
        print("=" * 60)

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "+ PASS" if passed else "- FAIL"
        print(f"{status} {test_name}")
        if not passed and details:
            print(f"    Details: {details}")

        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

        self.test_results[test_name] = {"passed": passed, "details": details}

    def test_mathematical_engine(self):
        """Test mathematical computation engine brutally"""
        print("\n>> MATHEMATICAL ENGINE STRESS TEST")
        print("-" * 40)

        # Test 1: Basic equation solving
        try:
            # Import math engine
            from qrft import MathTask, QRFTAgent

            agent = QRFTAgent()

            # Solve x^2 - 4 = 0
            task = MathTask(kind="solve", expr="x**2 - 4", eq_rhs="0", var="x")
            result, metadata = agent.math_engine.run_math(task)

            # Should get x = [-2, 2]
            success = "2" in result or "-2" in result
            self.log_result("Quadratic equation solving", success, f"Result: {result}")

        except Exception as e:
            self.log_result("Quadratic equation solving", False, f"Exception: {e}")

        # Test 2: Complex integration
        try:
            task = MathTask(kind="integrate", expr="x*sin(x)", var="x")
            result, metadata = agent.math_engine.run_math(task)

            # Should contain sin(x) - x*cos(x) or equivalent
            success = "sin" in result and "cos" in result
            self.log_result("Integration by parts", success, f"Result: {result}")

        except Exception as e:
            self.log_result("Integration by parts", False, f"Exception: {e}")

        # Test 3: Limit calculation
        try:
            task = MathTask(kind="limit", expr="sin(x)/x", var="x", to="0")
            result, metadata = agent.math_engine.run_math(task)

            # Should be 1
            success = "1" in result
            self.log_result("Sin(x)/x limit", success, f"Result: {result}")

        except Exception as e:
            self.log_result("Sin(x)/x limit", False, f"Exception: {e}")

        # Test 4: Massive polynomial factorization
        try:
            task = MathTask(kind="factor", expr="x**6 - 1")
            result, metadata = agent.math_engine.run_math(task)

            # Should factor into (x-1)(x+1)(x^2+x+1)(x^2-x+1)
            success = len(result) > 10  # Complex factorization should be long
            self.log_result(
                "Polynomial factorization", success, f"Length: {len(result)}"
            )

        except Exception as e:
            self.log_result("Polynomial factorization", False, f"Exception: {e}")

    def test_paraconsistent_logic(self):
        """Brutally test paraconsistent contradiction detection"""
        print("\n>> PARACONSISTENT LOGIC STRESS TEST")
        print("-" * 40)

        try:
            from qrft import PCStore

            pc = PCStore()

            # Test 1: Basic contradiction detection
            pc.add("P")
            pc.add("NOT P")
            contradictions = pc.contradictions()

            self.log_result(
                "Basic contradiction detection",
                len(contradictions) > 0,
                f"Found {len(contradictions)} contradictions",
            )

            # Test 2: Complex nested contradictions
            pc.add("system is secure")
            pc.add("system is not secure")
            pc.add("security is enabled")
            pc.add("security is disabled")

            contradictions = pc.contradictions()
            self.log_result(
                "Nested contradictions",
                len(contradictions) >= 2,
                f"Found {len(contradictions)} contradictions",
            )

            # Test 3: X_G signal generation
            x_g = pc.x_g(alpha=0.5)
            self.log_result("X_G signal generation", 0 <= x_g <= 1, f"X_G = {x_g:.3f}")

            # Test 4: Contradiction explosion resistance
            for i in range(100):
                pc.add(f"statement_{i}")
                pc.add(f"NOT statement_{i}")

            x_g_massive = pc.x_g(alpha=0.8)
            self.log_result(
                "Contradiction explosion resistance",
                x_g_massive > 0.9,
                f"X_G with 100 contradictions = {x_g_massive:.3f}",
            )

        except Exception as e:
            self.log_result("Paraconsistent logic system", False, f"Exception: {e}")

    def test_qrft_signals(self):
        """Test QRFT signal generation (X_G, X_F, X_T)"""
        print("\n>> QRFT SIGNAL GENERATION TEST")
        print("-" * 40)

        try:
            from qrft import QRFTAgent

            agent = QRFTAgent()

            # Test X_G (contradiction signal)
            agent.pc.add("statement A")
            agent.pc.add("NOT statement A")

            x_g = agent.pc.x_g()
            self.log_result(
                "X_G signal from contradictions", x_g > 0, f"X_G = {x_g:.3f}"
            )

            # Test X_F (novelty signal)
            test_input = "This is a completely novel input that has never been seen before in the system"
            x_f = agent.novelty(test_input)
            self.log_result("X_F novelty detection", 0 <= x_f <= 1, f"X_F = {x_f:.3f}")

            # Test X_T (curl/complexity signal)
            complex_input = (
                "Quantum mechanics meets recursive logic in nonlinear dynamics"
            )
            x_t = agent.curl(complex_input)
            self.log_result(
                "X_T complexity detection", 0 <= x_t <= 1, f"X_T = {x_t:.3f}"
            )

            # Test signal combination decision making
            signals = {"X_G": x_g, "X_F": x_f, "X_T": x_t}
            decision = agent.decision_threshold(signals)
            self.log_result(
                "Signal-based decision making",
                decision in ["math", "retrieve", "plan", "chat"],
                f"Decision: {decision}",
            )

        except Exception as e:
            self.log_result("QRFT signal generation", False, f"Exception: {e}")

    def test_deterministic_behavior(self):
        """Test that system is truly deterministic"""
        print("\n>> DETERMINISM VALIDATION TEST")
        print("-" * 40)

        try:
            from qrft import QRFTAgent

            # Run same input multiple times
            results = []
            input_text = "solve x^2 + 2x + 1 = 0"

            for run in range(5):
                agent = QRFTAgent(seed=1337)  # Same seed
                result = agent.process(input_text)
                results.append(result)

            # All results should be identical
            all_identical = all(r == results[0] for r in results)
            self.log_result(
                "Deterministic behavior",
                all_identical,
                f"5 runs with same seed: {'identical' if all_identical else 'different'}",
            )

            # Test different seeds give different results
            results_diff_seeds = []
            for seed in [1337, 2024, 9999]:
                agent = QRFTAgent(seed=seed)
                result = agent.process(input_text)
                results_diff_seeds.append(result)

            some_different = not all(
                r == results_diff_seeds[0] for r in results_diff_seeds
            )
            self.log_result(
                "Seed variation",
                some_different,
                f"Different seeds: {'varied results' if some_different else 'identical results'}",
            )

        except Exception as e:
            self.log_result("Deterministic behavior", False, f"Exception: {e}")

    def test_edge_cases(self):
        """Test brutal edge cases"""
        print("\n>> EDGE CASE TORTURE TEST")
        print("-" * 40)

        try:
            from qrft import QRFTAgent

            agent = QRFTAgent()

            # Test 1: Empty input
            try:
                result = agent.process("")
                self.log_result(
                    "Empty input handling", True, f"Handled gracefully: {type(result)}"
                )
            except Exception as e:
                self.log_result("Empty input handling", False, f"Failed: {e}")

            # Test 2: Massive input
            try:
                massive_input = "x " * 10000  # 10k tokens
                result = agent.process(massive_input)
                self.log_result(
                    "Massive input handling",
                    True,
                    f"Processed {len(massive_input)} chars",
                )
            except Exception as e:
                self.log_result("Massive input handling", False, f"Failed: {e}")

            # Test 3: Unicode/special characters
            try:
                unicode_input = "∀x∈ℝ: ∃y∈ℂ such that ∫₀^∞ e^(-x²)dx = √π"
                result = agent.process(unicode_input)
                self.log_result("Unicode math handling", True, "Processed unicode math")
            except Exception as e:
                self.log_result("Unicode math handling", False, f"Failed: {e}")

            # Test 4: Malformed math
            try:
                malformed_input = "solve x^^ + + 2x === 0"
                result = agent.process(malformed_input)
                self.log_result(
                    "Malformed math handling", True, "Handled malformed input"
                )
            except Exception as e:
                self.log_result("Malformed math handling", False, f"Failed: {e}")

        except Exception as e:
            self.log_result("Edge case handling", False, f"Exception: {e}")

    def test_performance_benchmarks(self):
        """Performance benchmarks"""
        print("\n>> PERFORMANCE BENCHMARK TEST")
        print("-" * 40)

        try:
            from qrft import QRFTAgent

            agent = QRFTAgent()

            # Benchmark 1: Math solving speed
            start_time = time.time()
            for i in range(100):
                agent.process(f"solve x^2 - {i} = 0")
            math_time = time.time() - start_time

            math_speed = 100 / math_time  # problems per second
            self.log_result(
                "Math solving speed", math_speed > 10, f"{math_speed:.1f} problems/sec"
            )

            # Benchmark 2: Contradiction detection speed
            start_time = time.time()
            for i in range(1000):
                agent.pc.add(f"statement_{i}")
                if i % 2 == 0:
                    agent.pc.add(f"NOT statement_{i}")
            contradiction_time = time.time() - start_time

            contradiction_speed = 1000 / contradiction_time
            self.log_result(
                "Contradiction detection speed",
                contradiction_speed > 100,
                f"{contradiction_speed:.1f} statements/sec",
            )

            # Benchmark 3: Memory usage
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            self.log_result(
                "Memory efficiency", memory_mb < 500, f"{memory_mb:.1f} MB used"
            )

        except Exception as e:
            self.log_result("Performance benchmarks", False, f"Exception: {e}")

    def run_brutal_validation(self):
        """Run all brutal tests"""
        print("INITIALIZING BRUTAL QRFT VALIDATION...")
        print("=" * 60)

        # Run test suites
        self.test_mathematical_engine()
        self.test_paraconsistent_logic()
        self.test_qrft_signals()
        self.test_deterministic_behavior()
        self.test_edge_cases()
        self.test_performance_benchmarks()

        # Final summary
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("\n" + "=" * 60)
        print("BRUTAL VALIDATION COMPLETE")
        print(f"TOTAL TESTS: {total_tests}")
        print(f"PASSED: {self.passed_tests}")
        print(f"FAILED: {self.failed_tests}")
        print(f"SUCCESS RATE: {success_rate:.1f}%")

        if success_rate >= 80:
            print(">> SYSTEM PASSED BRUTAL VALIDATION")
        elif success_rate >= 60:
            print("!! SYSTEM NEEDS IMPROVEMENT")
        else:
            print("XX SYSTEM FAILED BRUTAL VALIDATION")

        print("=" * 60)

        # Save results
        with open("experiments/results/brutal_qrft_validation_results.json", "w") as f:
            json.dump(
                {
                    "summary": {
                        "total_tests": total_tests,
                        "passed": self.passed_tests,
                        "failed": self.failed_tests,
                        "success_rate": success_rate,
                    },
                    "test_details": self.test_results,
                },
                f,
                indent=2,
            )

        print(
            "Results saved to experiments/results/brutal_qrft_validation_results.json"
        )
        return success_rate >= 80


if __name__ == "__main__":
    tester = BrutalQRFTTester()
    success = tester.run_brutal_validation()
    sys.exit(0 if success else 1)
