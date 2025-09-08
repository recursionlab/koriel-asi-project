#!/usr/bin/env python3
"""
FINAL QRFT VALIDATION REPORT
Comprehensive assessment of QRFT deterministic agent capabilities
Focus on what works, identify limitations, provide actionable feedback
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import json
import time

try:
    from qrft import (
        AgentState,
        Fact,
        FactPolarity,
        Gap,
        QRFTAgent,
        QRFTPolicy,
        QRFTSignals,
    )

    _ = (QRFTAgent, AgentState, QRFTSignals, QRFTPolicy, Fact, Gap, FactPolarity)
    print("+ QRFT validation imports successful")
except ImportError as e:
    print(f"- QRFT imports failed: {e}")
    sys.exit(1)


class QRFTValidationReport:
    """Generate comprehensive QRFT validation report"""

    def __init__(self):
        self.results = {
            "strengths": [],
            "weaknesses": [],
            "performance_metrics": {},
            "recommendations": [],
            "test_results": {},
        }
        print("QRFT DETERMINISTIC AGENT - FINAL VALIDATION REPORT")
        print("=" * 60)

    def test_core_architecture(self):
        """Test core architectural components"""
        print("\n>> CORE ARCHITECTURE VALIDATION")
        print("-" * 40)

        try:
            agent = QRFTAgent()

            # Test 1: Component initialization
            components_working = []
            components_working.append(
                hasattr(agent, "state") and isinstance(agent.state, AgentState)
            )
            components_working.append(
                hasattr(agent, "signals") and isinstance(agent.signals, QRFTSignals)
            )
            components_working.append(
                hasattr(agent, "policy") and isinstance(agent.policy, QRFTPolicy)
            )
            components_working.append(hasattr(agent, "process_input"))

            if all(components_working):
                self.results["strengths"].append(
                    "Clean architectural separation: AgentState, QRFTSignals, QRFTPolicy"
                )
                self.results["test_results"]["architecture"] = "PASS"
                print("+ Core architecture: ROBUST")
            else:
                self.results["weaknesses"].append(
                    "Missing core architectural components"
                )
                self.results["test_results"]["architecture"] = "FAIL"
                print("- Core architecture: INCOMPLETE")

            # Test 2: State management
            initial_facts = len(agent.state.facts)
            agent.state.add_fact("test", ("arg1",), FactPolarity.POSITIVE, "validation")
            post_add_facts = len(agent.state.facts)

            if post_add_facts > initial_facts:
                self.results["strengths"].append(
                    "Fact storage and retrieval working correctly"
                )
                print("+ Fact management: WORKING")
            else:
                self.results["weaknesses"].append(
                    "Fact storage mechanism not functioning"
                )
                print("- Fact management: BROKEN")

            # Test 3: Gap management
            initial_gaps = len(agent.state.gaps)
            agent.state.add_gap("test_gap", "Testing gap functionality")
            post_add_gaps = len(agent.state.gaps)

            if post_add_gaps > initial_gaps:
                self.results["strengths"].append("Knowledge gap tracking implemented")
                print("+ Gap management: WORKING")
            else:
                self.results["weaknesses"].append("Gap tracking not implemented")
                print("- Gap management: MISSING")

        except Exception as e:
            self.results["weaknesses"].append(f"Core architecture test failed: {e}")
            print(f"- Architecture test failed: {e}")

    def test_signal_computation(self):
        """Test QRFT signal computation"""
        print("\n>> SIGNAL COMPUTATION VALIDATION")
        print("-" * 40)

        try:
            agent = QRFTAgent()

            # Add some contradictory facts
            agent.state.add_fact("secure", ("system",), FactPolarity.POSITIVE, "test")
            agent.state.add_fact("secure", ("system",), FactPolarity.NEGATIVE, "test")

            # Add some gaps
            agent.state.add_gap("missing_info", "Need more data")

            # Update signals
            agent.signals.update(agent.state)

            # Test X_G (contradiction signal)
            x_g = getattr(agent.signals, "X_G", None)
            if x_g is not None and 0 <= x_g <= 1:
                self.results["strengths"].append(
                    f"X_G contradiction signal implemented (value: {x_g:.3f})"
                )
                print(f"+ X_G signal: {x_g:.3f}")
            else:
                self.results["weaknesses"].append(
                    "X_G contradiction signal not working"
                )
                print("- X_G signal: MISSING")

            # Test X_T (view mismatch signal)
            x_t = getattr(agent.signals, "X_T", None)
            if x_t is not None and 0 <= x_t <= 1:
                self.results["strengths"].append(
                    f"X_T view mismatch signal implemented (value: {x_t:.3f})"
                )
                print(f"+ X_T signal: {x_t:.3f}")
            else:
                self.results["weaknesses"].append("X_T signal not fully implemented")
                print("- X_T signal: LIMITED")

            # Test X_L (gap signal)
            x_l = getattr(agent.signals, "X_L", None)
            if x_l is not None:
                print(f"+ X_L signal: {x_l:.3f}")
            else:
                print("- X_L signal: NOT IMPLEMENTED")
                self.results["weaknesses"].append("X_L gap signal not implemented")

        except Exception as e:
            self.results["weaknesses"].append(f"Signal computation failed: {e}")
            print(f"- Signal computation failed: {e}")

    def test_policy_decision_making(self):
        """Test policy decision making"""
        print("\n>> POLICY DECISION VALIDATION")
        print("-" * 40)

        try:
            agent = QRFTAgent()

            # Test decision variety
            decisions = set()
            test_scenarios = [
                # Scenario 1: Clean state
                lambda: None,
                # Scenario 2: Add contradictions
                lambda: [
                    agent.state.add_fact("P", (), FactPolarity.POSITIVE, "test"),
                    agent.state.add_fact("P", (), FactPolarity.NEGATIVE, "test"),
                ],
                # Scenario 3: Add gaps
                lambda: agent.state.add_gap("missing", "Need info"),
            ]

            for i, scenario in enumerate(test_scenarios):
                agent = QRFTAgent()  # Fresh agent
                if scenario:
                    scenario()

                agent.signals.update(agent.state)
                decision = agent.policy.decide_action(agent.signals, agent.state)
                decisions.add(decision)
                print(f"  Scenario {i+1}: {decision}")

            if len(decisions) > 1:
                self.results["strengths"].append(
                    f"Policy generates diverse decisions: {list(decisions)}"
                )
                print(f"+ Policy diversity: {len(decisions)} different decisions")
            else:
                self.results["weaknesses"].append("Policy always makes same decision")
                print("- Policy diversity: LIMITED")

        except Exception as e:
            self.results["weaknesses"].append(f"Policy testing failed: {e}")
            print(f"- Policy testing failed: {e}")

    def test_input_processing_pipeline(self):
        """Test complete input processing"""
        print("\n>> INPUT PROCESSING VALIDATION")
        print("-" * 40)

        try:
            agent = QRFTAgent()

            # Test basic processing
            test_inputs = [
                "Hello world",
                "What is the answer?",
                "Alice loves Bob",
                "Alice does not love Bob",
                "Solve x = 5",
            ]

            responses = []
            start_time = time.time()

            for inp in test_inputs:
                response = agent.process_input(inp)
                responses.append(response)

            processing_time = time.time() - start_time
            throughput = len(test_inputs) / processing_time

            # Check all inputs got responses
            valid_responses = all(isinstance(r, str) and len(r) > 0 for r in responses)

            if valid_responses:
                self.results["strengths"].append(
                    "Input processing pipeline working correctly"
                )
                self.results["performance_metrics"]["throughput"] = throughput
                print(f"+ Input processing: WORKING ({throughput:.1f} inputs/sec)")
            else:
                self.results["weaknesses"].append(
                    "Input processing produces invalid responses"
                )
                print("- Input processing: BROKEN")

            # Test state updates
            step_count = agent.state.step_count
            if step_count == len(test_inputs):
                self.results["strengths"].append("Step counting accurate")
                print("+ Step counting: ACCURATE")
            else:
                self.results["weaknesses"].append(
                    f"Step counting wrong: {step_count} vs {len(test_inputs)}"
                )
                print(f"- Step counting: INACCURATE ({step_count}/{len(test_inputs)})")

        except Exception as e:
            self.results["weaknesses"].append(f"Input processing failed: {e}")
            print(f"- Input processing failed: {e}")

    def test_deterministic_behavior(self):
        """Test deterministic behavior"""
        print("\n>> DETERMINISTIC BEHAVIOR VALIDATION")
        print("-" * 40)

        try:
            # Test same input gives same output
            input_text = "Test deterministic behavior"

            agent1 = QRFTAgent()
            agent2 = QRFTAgent()

            response1 = agent1.process_input(input_text)
            response2 = agent2.process_input(input_text)

            if response1 == response2:
                self.results["strengths"].append("Deterministic behavior confirmed")
                print("+ Deterministic: CONFIRMED")
            else:
                self.results["weaknesses"].append("Non-deterministic behavior detected")
                print("- Deterministic: FAILED")
                print(f"  Response 1: {response1[:50]}...")
                print(f"  Response 2: {response2[:50]}...")

        except Exception as e:
            self.results["weaknesses"].append(f"Determinism test failed: {e}")
            print(f"- Determinism test failed: {e}")

    def generate_recommendations(self):
        """Generate actionable recommendations"""
        print("\n>> RECOMMENDATIONS")
        print("-" * 40)

        if "X_L gap signal not implemented" in [w for w in self.results["weaknesses"]]:
            self.results["recommendations"].append(
                "PRIORITY 1: Implement X_L gap signal computation in QRFTSignals class"
            )

        if (
            len([w for w in self.results["weaknesses"] if "contradiction" in w.lower()])
            > 0
        ):
            self.results["recommendations"].append(
                "PRIORITY 2: Fix contradiction detection - ensure Fact.__eq__ and FactPolarity comparison works"
            )

        if "mathematical" in " ".join(self.results["weaknesses"]).lower():
            self.results["recommendations"].append(
                "PRIORITY 3: Add mathematical computation module - SymPy integration for equation solving"
            )

        if "Policy always makes same decision" in self.results["weaknesses"]:
            self.results["recommendations"].append(
                "PRIORITY 4: Enhance policy decision logic - make signals properly influence action selection"
            )

        # Always include architecture improvements
        self.results["recommendations"].extend(
            [
                "ENHANCEMENT: Add mathematical reasoning module for equation solving",
                "ENHANCEMENT: Implement proper paraconsistent logic for contradiction handling",
                "ENHANCEMENT: Add reasoning chain tracking for complex multi-step problems",
                "TESTING: Add automated regression tests for all core functionality",
            ]
        )

        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"{i}. {rec}")

    def generate_final_assessment(self):
        """Generate final assessment"""
        print("\n" + "=" * 60)
        print("FINAL ASSESSMENT")
        print("=" * 60)

        strengths_count = len(self.results["strengths"])
        weaknesses_count = len(self.results["weaknesses"])
        total_issues = strengths_count + weaknesses_count

        if total_issues > 0:
            strength_ratio = strengths_count / total_issues
        else:
            strength_ratio = 0

        print(f"\nSTRENGTHS ({strengths_count}):")
        for strength in self.results["strengths"]:
            print(f"  + {strength}")

        print(f"\nWEAKNESSES ({weaknesses_count}):")
        for weakness in self.results["weaknesses"]:
            print(f"  - {weakness}")

        print("\nPERFORMACE METRICS:")
        for metric, value in self.results["performance_metrics"].items():
            print(f"  {metric}: {value:.2f}")

        # Overall verdict
        if strength_ratio >= 0.8:
            verdict = (
                "EXCELLENT - System is production ready with minor enhancements needed"
            )
            grade = "A"
        elif strength_ratio >= 0.6:
            verdict = "GOOD - System is functional but needs significant improvements"
            grade = "B"
        elif strength_ratio >= 0.4:
            verdict = "FAIR - System has potential but needs major work"
            grade = "C"
        else:
            verdict = "POOR - System needs fundamental redesign"
            grade = "D"

        print(f"\nOVERALL GRADE: {grade}")
        print(f"VERDICT: {verdict}")
        print(
            f"STRENGTH RATIO: {strength_ratio:.1%} ({strengths_count}/{total_issues})"
        )

        self.results["final_assessment"] = {
            "grade": grade,
            "verdict": verdict,
            "strength_ratio": strength_ratio,
            "strengths_count": strengths_count,
            "weaknesses_count": weaknesses_count,
        }

        return grade in ["A", "B"]

    def run_full_validation(self):
        """Run complete validation suite"""
        print("INITIALIZING COMPREHENSIVE QRFT VALIDATION...")
        print("=" * 60)

        # Run all tests
        self.test_core_architecture()
        self.test_signal_computation()
        self.test_policy_decision_making()
        self.test_input_processing_pipeline()
        self.test_deterministic_behavior()

        # Generate analysis
        self.generate_recommendations()
        success = self.generate_final_assessment()

        # Save complete report
        with open("experiments/results/qrft_final_validation_report.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(
            "\nComplete validation report saved to experiments/results/qrft_final_validation_report.json"
        )
        print("=" * 60)

        return success


if __name__ == "__main__":
    validator = QRFTValidationReport()
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)
