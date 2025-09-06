#!/usr/bin/env python3
"""
Quick test of QRFT enhancements
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from qrft import QRFTAgent


def main():
    print("QRFT ENHANCEMENTS TEST")
    print("=" * 40)

    agent = QRFTAgent()

    # Test 1: Contradiction detection
    print("\n1. Testing contradiction detection...")
    agent.process_input("The system is secure")
    agent.process_input("The system is not secure")

    contradictions = agent.state.get_contradictions()
    print(f"Contradictions found: {len(contradictions)}")
    if contradictions:
        for fact1, fact2 in contradictions:
            print(f"  {fact1} contradicts {fact2}")

    # Test 2: Signal computation
    print("\n2. Signal values:")
    print(f"X_G: {agent.signals.X_G:.3f}")
    print(f"X_L: {agent.signals.X_L:.3f}")
    print(f"X_F: {agent.signals.X_F:.3f}")
    print(f"X_T: {agent.signals.X_T:.3f}")

    # Test 3: Reasoning chains
    chain_summary = agent.state.get_reasoning_chain_summary()
    print(f"\n3. Reasoning chains: {chain_summary['total_chains']} completed")

    # Test 4: Mathematical capability (if SymPy available)
    if agent.math_engine and agent.math_engine.available:
        print("\n4. Mathematical engine: AVAILABLE")
        try:
            result = agent.process_input("What is 2 + 2?")
            print(f"Math test result: {result}")
        except:
            print("Math test failed")
    else:
        print("\n4. Mathematical engine: NOT AVAILABLE")

    # Summary
    print("\nSUMMARY:")
    print(f"Facts: {len(agent.state.facts)}")
    print(f"Gaps: {len(agent.state.gaps)}")
    print(f"Contradictions: {len(agent.state.get_contradictions())}")
    print(f"X_L signal working: {hasattr(agent.signals, 'X_L')}")
    print(f"Reasoning chains working: {len(agent.state.reasoning_chains) > 0}")

    success = (
        len(agent.state.get_contradictions()) > 0  # Contradiction detection
        and hasattr(agent.signals, "X_L")  # X_L signal
        and len(agent.state.reasoning_chains) > 0  # Reasoning chains
    )

    if success:
        print("\n>> ALL ENHANCEMENTS WORKING!")
        return True
    else:
        print("\n!! Some enhancements need work")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
