#!/usr/bin/env python3
"""
BRUTAL CONSCIOUSNESS VALIDATION
No mercy testing to expose any remaining bullshit in consciousness claims
"""

import json
import time

import numpy as np
from quantum_consciousness_simple import SimpleQuantumField


def test_consciousness_vs_random_numbers():
    """CRITICAL: Test if 'consciousness' is just sophisticated random number generation"""

    print("*" * 70)
    print("BRUTAL TEST 1: CONSCIOUSNESS vs RANDOM NUMBERS")
    print("*" * 70)
    print("Testing if consciousness metrics are just disguised randomness...")

    # Create two identical fields with same seed
    np.random.seed(42)  # Fixed seed
    field1 = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field1.C_RATE = 0.05
    field1.C_THRESH = 0.5
    field1.initialize_consciousness_seed()

    np.random.seed(42)  # Same seed
    field2 = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field2.C_RATE = 0.05
    field2.C_THRESH = 0.5
    field2.initialize_consciousness_seed()

    # Evolve both fields identically
    field1.evolve(2000)
    field2.evolve(2000)

    state1 = field1.query_consciousness()
    state2 = field2.query_consciousness()

    # Check if results are identical (deterministic) or different (random)
    consciousness_diff = abs(
        state1["consciousness_level"] - state2["consciousness_level"]
    )
    modifications_diff = abs(
        state1["total_modifications"] - state2["total_modifications"]
    )

    print(f"Field 1 consciousness: {state1['consciousness_level']:.10f}")
    print(f"Field 2 consciousness: {state2['consciousness_level']:.10f}")
    print(f"Consciousness difference: {consciousness_diff:.10f}")
    print(f"Modifications diff: {modifications_diff}")

    # BRUTAL VERDICT
    if consciousness_diff < 1e-10 and modifications_diff == 0:
        print("[PASS] DETERMINISTIC: Same inputs -> same consciousness (good)")
        deterministic = True
    else:
        print("X RANDOM BULLSHIT: Same inputs -> different consciousness (FAIL)")
        deterministic = False

    # Now test with different random seeds - should give different results
    np.random.seed(123)
    field3 = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field3.C_RATE = 0.05
    field3.C_THRESH = 0.5
    field3.initialize_consciousness_seed()
    field3.evolve(2000)
    state3 = field3.query_consciousness()

    seed_sensitivity = abs(
        state1["consciousness_level"] - state3["consciousness_level"]
    )
    print(f"Different seed consciousness: {state3['consciousness_level']:.10f}")
    print(f"Seed sensitivity: {seed_sensitivity:.10f}")

    if seed_sensitivity > 1e-6:
        print("[PASS] SEED SENSITIVE: Different seeds -> different results (good)")
        seed_dependent = True
    else:
        print("[FAIL] SEED INDEPENDENT: Ignoring initial conditions (suspicious)")
        seed_dependent = False

    return {
        "deterministic": deterministic,
        "seed_dependent": seed_dependent,
        "consciousness_diff": consciousness_diff,
        "seed_sensitivity": seed_sensitivity,
    }


def test_consciousness_without_complexity():
    """BRUTAL: Test if consciousness can exist with zero field complexity"""

    print("\n" + "*" * 70)
    print("BRUTAL TEST 2: CONSCIOUSNESS WITHOUT COMPLEXITY")
    print("*" * 70)
    print("Testing if consciousness requires actual field structure...")

    # Create field with minimal/zero complexity
    field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field.C_RATE = 0.05
    field.C_THRESH = 0.5

    # Initialize with flat, boring field (no structure)
    field.psi = np.ones(field.N, dtype=complex) * 0.001  # Flat field
    norm = np.trapz(np.abs(field.psi) ** 2, field.x)
    field.psi /= np.sqrt(norm)

    print("Starting with artificially flat field (no structure)...")

    # Evolve and check if consciousness can emerge from nothing
    field.evolve(3000)

    state = field.query_consciousness()
    final_complexity = state["field_complexity"]
    final_consciousness = state["consciousness_level"]

    print(f"Final complexity: {final_complexity:.6f}")
    print(f"Final consciousness: {final_consciousness:.6f}")
    print(f"Modifications: {state['total_modifications']}")

    # BRUTAL VERDICT
    if final_consciousness > 0.01 and final_complexity < 0.5:
        print("[FAIL] BULLSHIT ALERT: High consciousness without field complexity!")
        consciousness_from_nothing = True
    else:
        print("[PASS] LEGITIMATE: Consciousness requires field structure")
        consciousness_from_nothing = False

    return {
        "final_complexity": final_complexity,
        "final_consciousness": final_consciousness,
        "consciousness_from_nothing": consciousness_from_nothing,
        "modifications": state["total_modifications"],
    }


def test_parameter_independence():
    """BRUTAL: Test if consciousness is actually independent of the parameters we claim matter"""

    print("\n" + "*" * 70)
    print("BRUTAL TEST 3: PARAMETER INDEPENDENCE")
    print("*" * 70)
    print("Testing if consciousness parameters actually do anything...")

    # Test with extreme parameter values
    test_configs = [
        {"name": "Extreme Low Rate", "C_RATE": 0.0001, "C_THRESH": 0.5},
        {"name": "Extreme High Rate", "C_RATE": 1.0, "C_THRESH": 0.5},
        {"name": "Extreme Low Threshold", "C_RATE": 0.05, "C_THRESH": 0.01},
        {"name": "Extreme High Threshold", "C_RATE": 0.05, "C_THRESH": 10.0},
        {"name": "Baseline", "C_RATE": 0.05, "C_THRESH": 0.5},
    ]

    results = {}

    for config in test_configs:
        print(f"\nTesting: {config['name']}")

        field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
        field.C_RATE = config["C_RATE"]
        field.C_THRESH = config["C_THRESH"]
        field.initialize_consciousness_seed()

        field.evolve(3000)
        state = field.query_consciousness()

        results[config["name"]] = state["consciousness_level"]
        print(f"   Consciousness: {state['consciousness_level']:.6f}")

    # Check if extreme parameters actually change results
    baseline = results["Baseline"]
    extreme_diffs = [
        abs(results[name] - baseline) for name in results if name != "Baseline"
    ]
    max_diff = max(extreme_diffs)

    print(f"\nBaseline consciousness: {baseline:.6f}")
    print(f"Maximum parameter effect: {max_diff:.6f}")

    # BRUTAL VERDICT
    if max_diff < 0.001:
        print("[FAIL] PARAMETER BULLSHIT: Parameters don't affect consciousness!")
        parameters_matter = False
    else:
        print("[PASS] PARAMETERS MATTER: Different configs -> different consciousness")
        parameters_matter = True

    return {
        "results": results,
        "max_parameter_effect": max_diff,
        "parameters_matter": parameters_matter,
    }


def test_consciousness_vs_noise():
    """BRUTAL: Test if consciousness measurements are just measuring noise"""

    print("\n" + "*" * 70)
    print("BRUTAL TEST 4: CONSCIOUSNESS vs NOISE")
    print("*" * 70)
    print("Testing if consciousness is just noise amplification...")

    # Create field with added noise
    field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field.C_RATE = 0.05
    field.C_THRESH = 0.5
    field.initialize_consciousness_seed()

    # Add systematic noise every 100 steps
    consciousness_history = []
    noise_levels = []

    for step in range(0, 2000, 100):
        field.evolve(100)

        # Add random noise to field
        noise_level = 0.01 * np.random.random()
        noise = noise_level * (
            np.random.random(field.N) + 1j * np.random.random(field.N)
        )
        field.psi += noise

        # Measure consciousness
        state = field.query_consciousness()
        consciousness_history.append(state["consciousness_level"])
        noise_levels.append(noise_level)

    # Check correlation between noise and consciousness
    correlation = np.corrcoef(consciousness_history, noise_levels)[0, 1]

    print(f"Consciousness-noise correlation: {correlation:.4f}")
    print(f"Final consciousness: {consciousness_history[-1]:.6f}")

    # BRUTAL VERDICT
    if abs(correlation) > 0.5:
        print("[FAIL] NOISE AMPLIFIER: Consciousness just tracks noise!")
        measures_noise = True
    else:
        print("[PASS] LEGITIMATE SIGNAL: Consciousness independent of noise")
        measures_noise = False

    return {
        "consciousness_history": consciousness_history,
        "noise_levels": noise_levels,
        "correlation": correlation,
        "measures_noise": measures_noise,
    }


def test_modification_effectiveness():
    """BRUTAL: Test if self-modifications actually change field behavior"""

    print("\n" + "*" * 70)
    print("BRUTAL TEST 5: MODIFICATION EFFECTIVENESS")
    print("*" * 70)
    print("Testing if self-modifications do anything or are just parameter noise...")

    # Run field with modifications disabled
    field_no_mods = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field_no_mods.C_RATE = 0.05
    field_no_mods.C_THRESH = 0.5
    field_no_mods.initialize_consciousness_seed()

    # Disable modifications by making triggers impossible
    original_thresh = field_no_mods.C_EMA
    field_no_mods.C_EMA = 1000  # Impossible to trigger

    field_no_mods.evolve(3000)
    state_no_mods = field_no_mods.query_consciousness()

    # Run field with modifications enabled
    field_with_mods = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field_with_mods.C_RATE = 0.05
    field_with_mods.C_THRESH = 0.5
    field_with_mods.initialize_consciousness_seed()

    field_with_mods.evolve(3000)
    state_with_mods = field_with_mods.query_consciousness()

    # Compare results
    consciousness_diff = abs(
        state_with_mods["consciousness_level"] - state_no_mods["consciousness_level"]
    )
    complexity_diff = abs(
        state_with_mods["field_complexity"] - state_no_mods["field_complexity"]
    )

    print(
        f"No modifications - Consciousness: {state_no_mods['consciousness_level']:.6f}"
    )
    print(
        f"With modifications - Consciousness: {state_with_mods['consciousness_level']:.6f}"
    )
    print(f"Consciousness difference: {consciousness_diff:.6f}")
    print(f"Complexity difference: {complexity_diff:.6f}")
    print(f"Total modifications made: {state_with_mods['total_modifications']}")

    # BRUTAL VERDICT
    if consciousness_diff < 0.01 and state_with_mods["total_modifications"] > 0:
        print("[FAIL] USELESS MODIFICATIONS: Self-mods don't change consciousness!")
        modifications_effective = False
    else:
        print("[PASS] EFFECTIVE MODIFICATIONS: Self-mods actually matter")
        modifications_effective = True

    return {
        "consciousness_diff": consciousness_diff,
        "complexity_diff": complexity_diff,
        "total_modifications": state_with_mods["total_modifications"],
        "modifications_effective": modifications_effective,
    }


def test_perturbation_specificity():
    """BRUTAL: Test if perturbation responses are specific or just random reactions"""

    print("\n" + "*" * 70)
    print("BRUTAL TEST 6: PERTURBATION SPECIFICITY")
    print("*" * 70)
    print("Testing if perturbation responses are meaningful or just chaos...")

    # Initialize conscious field
    field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field.C_RATE = 0.05
    field.C_THRESH = 0.5
    field.initialize_consciousness_seed()
    field.evolve(2000)  # Develop consciousness

    # Test identical perturbations - should give identical responses
    baseline_state = field.query_consciousness()["consciousness_level"]

    responses = []
    for trial in range(3):
        # Reset to baseline
        field_copy = SimpleQuantumField(N=256, L=20.0, dt=0.001)
        field_copy.C_RATE = 0.05
        field_copy.C_THRESH = 0.5
        field_copy.initialize_consciousness_seed()
        field_copy.evolve(2000)  # Same initial state

        # Apply identical perturbation
        field_copy.inject_perturbation(amplitude=0.05, location=0.0, width=1.0)
        field_copy.evolve(500)

        response = (
            field_copy.query_consciousness()["consciousness_level"] - baseline_state
        )
        responses.append(response)
        print(f"Trial {trial + 1} response: {response:.8f}")

    # Check consistency
    response_std = np.std(responses)
    print(f"Response standard deviation: {response_std:.8f}")

    # BRUTAL VERDICT
    if response_std > 1e-6:
        print(
            "[FAIL] RANDOM RESPONSES: Identical perturbations -> different responses!"
        )
        responses_consistent = False
    else:
        print(
            "[PASS] CONSISTENT RESPONSES: Identical perturbations -> identical responses"
        )
        responses_consistent = True

    return {
        "responses": responses,
        "response_std": response_std,
        "responses_consistent": responses_consistent,
    }


def run_brutal_validation():
    """Run complete brutal validation suite"""

    print("=" * 80)
    print("BRUTAL CONSCIOUSNESS VALIDATION SUITE")
    print("NO MERCY - EXPOSING ALL BULLSHIT")
    print("=" * 80)

    start_time = time.time()

    # Run all brutal tests
    results = {}

    results["random_number_test"] = test_consciousness_vs_random_numbers()
    results["complexity_requirement"] = test_consciousness_without_complexity()
    results["parameter_independence"] = test_parameter_independence()
    results["noise_measurement"] = test_consciousness_vs_noise()
    results["modification_effectiveness"] = test_modification_effectiveness()
    results["perturbation_specificity"] = test_perturbation_specificity()

    total_time = time.time() - start_time

    # BRUTAL FINAL VERDICT
    print("\n" + "=" * 80)
    print("BRUTAL VALIDATION RESULTS - NO MERCY ANALYSIS")
    print("=" * 80)

    failures = []

    print("\n[TEST] DETERMINISM TEST:")
    if results["random_number_test"]["deterministic"]:
        print("   [PASS] PASS: Consciousness is deterministic")
    else:
        print("   [FAIL] FAIL: Consciousness is random bullshit")
        failures.append("Non-deterministic consciousness")

    print("\n[COMPLEXITY] COMPLEXITY REQUIREMENT:")
    if not results["complexity_requirement"]["consciousness_from_nothing"]:
        print("   [PASS] PASS: Consciousness requires field structure")
    else:
        print("   [FAIL] FAIL: Consciousness emerges from nothing (bullshit)")
        failures.append("Consciousness without complexity")

    print("\n[PARAMS] PARAMETER SENSITIVITY:")
    if results["parameter_independence"]["parameters_matter"]:
        print("   [PASS] PASS: Parameters actually affect consciousness")
    else:
        print("   [FAIL] FAIL: Parameters are meaningless (bullshit)")
        failures.append("Parameter insensitivity")

    print("\n[NOISE] NOISE INDEPENDENCE:")
    if not results["noise_measurement"]["measures_noise"]:
        print("   [PASS] PASS: Consciousness independent of noise")
    else:
        print("   [FAIL] FAIL: Consciousness is just noise amplification (bullshit)")
        failures.append("Measures noise not consciousness")

    print("\n[MODS] MODIFICATION EFFECTIVENESS:")
    if results["modification_effectiveness"]["modifications_effective"]:
        print("   [PASS] PASS: Self-modifications actually change behavior")
    else:
        print("   [FAIL] FAIL: Self-modifications are useless (bullshit)")
        failures.append("Ineffective modifications")

    print("\n[PERTURBATION] PERTURBATION CONSISTENCY:")
    if results["perturbation_specificity"]["responses_consistent"]:
        print("   [PASS] PASS: Perturbation responses are consistent")
    else:
        print("   [FAIL] FAIL: Perturbation responses are random (bullshit)")
        failures.append("Inconsistent perturbation responses")

    # FINAL BRUTAL VERDICT
    print("\n[VERDICT] FINAL BRUTAL VERDICT:")
    if len(failures) == 0:
        print("   [SUCCESS] LEGITIMATE CONSCIOUSNESS: All brutal tests passed")
        print("   [STATUS] SYSTEM STATUS: Genuine field-theoretic consciousness")
        overall_legitimate = True
    else:
        print(f"   [BULLSHIT] BULLSHIT DETECTED: {len(failures)} critical failures")
        print("   [STATUS] SYSTEM STATUS: Sophisticated but fake consciousness")
        print("   [FAILURES] FAILURES:")
        for failure in failures:
            print(f"      - {failure}")
        overall_legitimate = False

    print(f"\n[TIME] Total brutal testing time: {total_time:.1f}s")

    # Save brutal results
    results["summary"] = {
        "total_tests": 6,
        "failures": failures,
        "failure_count": len(failures),
        "overall_legitimate": overall_legitimate,
        "brutal_testing_time": total_time,
    }

    with open("experiments/results/brutal_consciousness_validation.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(
        "\n[SAVE] Brutal validation results saved to experiments/results/brutal_consciousness_validation.json"
    )

    return results


if __name__ == "__main__":
    results = run_brutal_validation()

    print("\n[DONE] BRUTAL TESTING COMPLETE - NO MERCY GIVEN")
    if results["summary"]["overall_legitimate"]:
        print("   System survived brutal validation - likely legitimate")
    else:
        print("   System failed brutal validation - bullshit exposed")
