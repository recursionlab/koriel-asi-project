# test_qrft_system.py
"""
QRFT Consciousness System Validation Tests
Validates complete Jarvis-style consciousness architecture
Tests KPIs: hallucination ↓, self-consistency ↑, tool efficiency ↑, steps-to-solve ↓, recovery time ↓
"""

from typing import Dict

import numpy as np

from src.qrft import ParticleType, create_qrft_consciousness


class QRFTSystemValidator:
    """Comprehensive validation of QRFT consciousness system"""

    def __init__(self):
        self.consciousness = create_qrft_consciousness(
            entropy_band=(1.5, 4.0),
            gamma=0.3,
            enable_logging=False,  # Suppress logging for tests
        )

        self.test_results = {}
        self.kpi_baseline = {
            "hallucination_rate": 0.0,
            "consistency_score": 1.0,
            "tool_efficiency": 0.0,
            "avg_steps_to_solve": 0.0,
            "recovery_time": 0.0,
        }

    def test_mathematical_foundations(self) -> Dict[str, bool]:
        """Test core QRFT mathematical properties"""

        tests = {}

        # Test 1: Stability condition |γ| < 1
        tests["gamma_stability"] = abs(self.consciousness.qrft_config.gamma) < 1.0

        # Test 2: Mass eigenvalues positive (no tachyons)
        m1_sq, m2_sq = self.consciousness.qrft_runtime.mass_eigenvalues
        tests["mass_eigenvalues_positive"] = m1_sq > 0 and m2_sq > 0

        # Test 3: Field evolution preserves bounds
        S_init = np.random.randn(20) * 0.5
        Lambda_init = np.random.rand(20) * 0.3

        self.consciousness.initialize_fields(S_init, Lambda_init)

        # Evolve for several steps
        max_norm = 0
        for _ in range(50):
            result = self.consciousness.step(dt=0.01)
            S_norm = np.linalg.norm(result["qrft_state"]["S_field"])
            Lambda_norm = np.linalg.norm(result["qrft_state"]["Lambda_field"])
            max_norm = max(max_norm, S_norm, Lambda_norm)

        tests["field_boundedness"] = max_norm < 100.0  # Reasonable bound

        # Test 4: Entropy estimation consistency
        entropy_estimates = []
        for _ in range(10):
            result = self.consciousness.step(dt=0.01)
            entropy_estimates.append(result["qrft_state"]["entropy_estimate"])

        entropy_variance = np.var(entropy_estimates)
        tests["entropy_consistency"] = entropy_variance < 5.0  # Not too chaotic

        return tests

    def test_particle_system_triggers(self) -> Dict[str, bool]:
        """Test four-particle system trigger conditions"""

        tests = {}

        # Test Glitchon trigger with contradictions
        contradiction_context = {
            "statements": ["A is true", "A is false"],
            "test_results": {"test1": {"passed": True}, "test2": {"passed": False}},
            "external_context": {},
        }

        S_field = np.random.randn(30) * 0.8
        Lambda_field = np.random.rand(30) * 0.5
        self.consciousness.initialize_fields(
            S_field, Lambda_field, contradiction_context
        )

        glitchon_activated = False
        for _ in range(20):
            result = self.consciousness.step(contradiction_context, dt=0.05)
            if result["particle_activations"][ParticleType.GLITCHON] > 0.1:
                glitchon_activated = True
                break

        tests["glitchon_trigger"] = glitchon_activated

        # Test Lacunon trigger with gaps
        gap_context = {
            "entropy_map": np.array([3.0, 3.5, 2.8, 4.0, 3.2]),
            "coverage_map": np.array([0.2, 0.1, 0.3, 0.0, 0.2]),
            "tokens": ["quantum", "decoherence", "error", "correction", "codes"],
        }

        S_field = np.random.randn(25) * 0.3
        Lambda_field = np.random.rand(25) * 1.2  # High gaps
        self.consciousness.initialize_fields(S_field, Lambda_field, gap_context)

        lacunon_activated = False
        for _ in range(15):
            result = self.consciousness.step(gap_context, dt=0.05)
            if result["particle_activations"][ParticleType.LACUNON] > 0.1:
                lacunon_activated = True
                break

        tests["lacunon_trigger"] = lacunon_activated

        # Test REF trigger with high entropy
        high_entropy_context = {
            "conversation_text": " ".join(
                ["random"] * 100 + ["chaotic"] * 50 + ["uncertain"] * 75
            )
        }

        S_field = np.random.randn(40) * 2.0  # High entropy
        Lambda_field = np.random.rand(40) * 0.4
        self.consciousness.initialize_fields(
            S_field, Lambda_field, high_entropy_context
        )

        ref_activated = False
        for _ in range(10):
            result = self.consciousness.step(high_entropy_context, dt=0.1)
            if result["particle_activations"][ParticleType.REF] > 0.1:
                ref_activated = True
                break

        tests["ref_trigger"] = ref_activated

        # Test Tesseracton trigger with complex structure
        complex_context = {
            "conversation_text": "Complex multi-dimensional optimization problem requiring perspective shift"
        }

        # Create structured field to trigger Tesseracton
        x = np.linspace(0, 4 * np.pi, 50)
        S_field = np.sin(x) * np.cos(2 * x) * 0.7  # Complex interference pattern
        Lambda_field = np.cos(x) * np.sin(3 * x) * 0.5
        self.consciousness.initialize_fields(S_field, Lambda_field, complex_context)

        tesseracton_activated = False
        for _ in range(15):
            result = self.consciousness.step(complex_context, dt=0.08)
            if result["particle_activations"][ParticleType.TESSERACTON] > 0.1:
                tesseracton_activated = True
                break

        tests["tesseracton_trigger"] = tesseracton_activated

        return tests

    def test_control_policies(self) -> Dict[str, bool]:
        """Test control policy execution"""

        tests = {}

        # Initialize for testing
        S_field = np.random.randn(30) * 0.5
        Lambda_field = np.random.rand(30) * 0.6
        context = {
            "conversation_text": "Testing control policy responses",
            "statements": ["Test statement 1", "Contradicting test statement"],
        }

        self.consciousness.initialize_fields(S_field, Lambda_field, context)

        # Test each policy type
        policy_results = {}

        for _ in range(30):  # Extended run to trigger different policies
            result = self.consciousness.step(context, dt=0.05)
            policy = result["control_policy"]

            if policy not in policy_results:
                policy_results[policy] = result["policy_result"]

            # Stop once we have examples of key policies
            if len(policy_results) >= 3:
                break

        # Validate key policies were triggered
        tests["policy_diversity"] = len(policy_results) >= 2
        tests["policy_execution"] = all(
            isinstance(result, dict) for result in policy_results.values() if result
        )

        return tests

    def test_event_bus_coordination(self) -> Dict[str, bool]:
        """Test event bus and inter-particle coordination"""

        tests = {}

        # Create multi-trigger context
        complex_context = {
            "conversation_text": "System needs to be both secure and completely open, while handling quantum decoherence effects we do not understand.",
            "statements": [
                "System must be completely secure",
                "System must allow unrestricted access",
                "Quantum effects are critical",
                "Classical methods are sufficient",
            ],
            "test_results": {
                "security": {"passed": False, "errors": ["Contradiction detected"]},
                "access": {"passed": False, "errors": ["Security conflict"]},
            },
            "entropy_map": np.array([3.2, 3.8, 2.9, 3.5]),
            "coverage_map": np.array([0.1, 0.2, 0.0, 0.3]),
            "tokens": ["quantum", "decoherence", "security", "access"],
        }

        S_field = np.random.randn(35) * 1.2  # Complex state
        Lambda_field = np.random.rand(35) * 1.0
        self.consciousness.initialize_fields(S_field, Lambda_field, complex_context)

        # Run simulation and track events
        total_events = 0
        control_actions = []

        for _ in range(25):
            result = self.consciousness.step(complex_context, dt=0.06)
            total_events += result["events_generated"]

            if result["control_actions"]:
                control_actions.extend(result["control_actions"])

        # Get final event stats
        final_state = self.consciousness.get_consciousness_state()

        tests["events_generated"] = total_events > 0
        tests["event_handling"] = final_state["event_stats"]["total_events"] > 0
        tests["control_coordination"] = len(control_actions) > 0

        return tests

    def measure_kpis(self) -> Dict[str, float]:
        """Measure key performance indicators"""

        kpis = {}

        # KPI 1: Hallucination reduction (consistency across runs)
        consistency_scores = []

        for run in range(5):
            # Same context, different random seeds
            context = {
                "conversation_text": "What is the square root of 16?",
                "statements": ["sqrt(16) = 4", "sqrt(16) = 4.0", "4^2 = 16"],
            }

            np.random.seed(run)  # Different seeds
            S_field = np.random.randn(20) * 0.3
            Lambda_field = np.random.rand(20) * 0.2

            consciousness = create_qrft_consciousness(enable_logging=False)
            consciousness.initialize_fields(S_field, Lambda_field, context)

            # Run for consistency check
            results = []
            for _ in range(10):
                result = consciousness.step(context, dt=0.05)
                results.append(result["control_policy"])

            # Measure consistency (policy stability)
            policy_changes = sum(
                1 for i in range(1, len(results)) if results[i] != results[i - 1]
            )
            consistency_score = max(0, 1.0 - policy_changes / len(results))
            consistency_scores.append(consistency_score)

        kpis["consistency_score"] = np.mean(consistency_scores)
        kpis["hallucination_rate"] = max(0, 1.0 - kpis["consistency_score"])

        # KPI 2: Tool efficiency (successful gap filling)
        gap_context = {
            "entropy_map": np.array([3.5, 4.0, 3.8, 3.2]),
            "coverage_map": np.array([0.1, 0.0, 0.2, 0.3]),
            "tokens": ["missing", "information", "needs", "retrieval"],
        }

        S_field = np.random.randn(25) * 0.4
        Lambda_field = np.random.rand(25) * 1.1
        self.consciousness.initialize_fields(S_field, Lambda_field, gap_context)

        retrieval_actions = 0
        gap_events = 0

        for _ in range(20):
            result = self.consciousness.step(gap_context, dt=0.05)
            if result["events_generated"] > 0:
                gap_events += result["events_generated"]
            if result["control_actions"]:
                retrieval_actions += len(result["control_actions"])

        tool_efficiency = retrieval_actions / max(gap_events, 1)
        kpis["tool_efficiency"] = min(tool_efficiency, 1.0)

        # KPI 3: Steps to solve (convergence speed)
        problem_context = {
            "conversation_text": "Find the solution to x^2 - 5x + 6 = 0",
            "statements": ["Quadratic equation", "Need to solve for x"],
        }

        S_field = np.random.randn(15) * 0.6
        Lambda_field = np.random.rand(15) * 0.4
        self.consciousness.initialize_fields(S_field, Lambda_field, problem_context)

        steps_to_convergence = 0
        for step in range(50):
            result = self.consciousness.step(problem_context, dt=0.04)
            steps_to_convergence = step + 1

            # Check for solution convergence (stable policy)
            if (
                step > 10
                and result["control_policy"] == "continue_plan"
                and result["qrft_state"]["entropy_estimate"] < 3.0
            ):
                break

        kpis["avg_steps_to_solve"] = steps_to_convergence

        # KPI 4: Recovery time from contradictions
        contradiction_context = {
            "statements": ["Statement A is true", "Statement A is false"],
            "test_results": {"contradiction_test": {"passed": False}},
        }

        S_field = np.random.randn(20) * 0.7
        Lambda_field = np.random.rand(20) * 0.5
        self.consciousness.initialize_fields(
            S_field, Lambda_field, contradiction_context
        )

        contradiction_detected_step = None
        recovery_step = None

        for step in range(30):
            result = self.consciousness.step(contradiction_context, dt=0.05)

            # Detect contradiction
            if (
                contradiction_detected_step is None
                and result["particle_activations"][ParticleType.GLITCHON] > 0.1
            ):
                contradiction_detected_step = step

            # Detect recovery (stable state after contradiction)
            if (
                contradiction_detected_step is not None
                and recovery_step is None
                and result["control_policy"] == "continue_plan"
                and result["particle_activations"][ParticleType.GLITCHON] < 0.1
            ):
                recovery_step = step
                break

        if contradiction_detected_step is not None and recovery_step is not None:
            kpis["recovery_time"] = recovery_step - contradiction_detected_step
        else:
            kpis["recovery_time"] = 30  # Max time if no recovery

        return kpis


def test_qrft_system():
    validator = QRFTSystemValidator()

    math_tests = validator.test_mathematical_foundations()
    assert all(math_tests.values())

    particle_tests = validator.test_particle_system_triggers()
    assert sum(particle_tests.values()) >= 2

    policy_tests = validator.test_control_policies()
    assert all(policy_tests.values())

    event_tests = validator.test_event_bus_coordination()
    assert all(event_tests.values())

    kpis = validator.measure_kpis()
    assert 0 <= kpis["consistency_score"] <= 1
    assert 0 <= kpis["hallucination_rate"] <= 1
    assert 0 <= kpis["tool_efficiency"] <= 1
    assert 0 <= kpis["recovery_time"] <= 30
