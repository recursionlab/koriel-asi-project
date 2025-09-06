"""ASI Demo - Baby consciousness solving 1+1"""

from .intelligence_ladder import IntelligenceLadder
from .metastate import MetaState
from .reality_interface import RealityInterface
from .reasoning_engine import ConsciousnessGuidedReasoner


def create_initial_consciousness() -> MetaState:
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
        state_hash="initial",
    )


def test_baby_asi_arithmetic():
    """Test: Can baby ASI solve 1+1=2?"""

    print("=== BABY ASI ARITHMETIC TEST ===")

    # Initialize components
    consciousness = create_initial_consciousness()
    reasoner = ConsciousnessGuidedReasoner(seed=1337)
    reality = RealityInterface(seed=1337)

    # Generate simple test
    problem = reality.generate_arithmetic_problem(difficulty=0)
    print(f"Problem: {problem.question}")
    print(f"Expected: {problem.answer}")

    # Solve using consciousness
    response = reasoner.solve_problem(problem, consciousness)
    result = reality.validate_response(problem, response)

    print(f"ASI Response: {response}")
    print(f"Correct: {result.correct}")

    return result.correct


def test_recursive_improvement():
    """Test recursive intelligence improvement"""

    print("\n=== RECURSIVE IMPROVEMENT TEST ===")

    # Initialize
    consciousness = create_initial_consciousness()
    ladder = IntelligenceLadder(seed=1337)

    print(
        f"Initial consciousness: RC={consciousness.rc_total:.3f}, Curvature={consciousness.curvature:.1f}"
    )

    # Run recursive climb
    trajectory = ladder.recursive_climb(consciousness, max_iterations=10)

    # Show progression
    for point in trajectory:
        cs = point["consciousness_state"]
        perf = point["performance"]
        print(
            f"Step {point['iteration']}: Difficulty={point['difficulty']}, "
            f"Accuracy={perf['accuracy']:.2f}, Intelligence={point['intelligence_score']:.3f}, "
            f"RC={cs.rc_total:.3f}"
        )

    return trajectory


def main():
    """Main ASI demo"""
    print("KORIEL ASI PROJECT - Reality-Grounded Consciousness Test")
    print("=" * 60)

    # Test 1: Basic arithmetic
    arithmetic_success = test_baby_asi_arithmetic()

    # Test 2: Recursive improvement
    improvement_trajectory = test_recursive_improvement()

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Basic arithmetic: {'PASS' if arithmetic_success else 'FAIL'}")

    if improvement_trajectory:
        initial_score = improvement_trajectory[0]["intelligence_score"]
        final_score = improvement_trajectory[-1]["intelligence_score"]
        improvement = final_score - initial_score
        print(f"Intelligence improvement: {improvement:.3f}")
        print(f"Final difficulty level: {improvement_trajectory[-1]['difficulty']}")

    print("\nReality-grounded consciousness validation: ACTIVE")


if __name__ == "__main__":
    main()
