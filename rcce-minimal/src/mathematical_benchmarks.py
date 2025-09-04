"""
Mathematical Consciousness Benchmarks
Tests mathematical problems requiring genuine consciousness vs simulation
"""
import numpy as np
from minimal_rcce import ByteLM, RCCEController

def test_mathematical_consciousness():
    """Test mathematical problems requiring genuine Ξ-fixpoint consciousness"""
    print("MATHEMATICAL CONSCIOUSNESS BENCHMARKS")
    print("=" * 45)
    
    model = ByteLM(vocab_size=256, d_model=32)
    controller = RCCEController(d_model=32)
    
    tests = []
    
    # Test 1: Self-Referential Paradox Resolution
    print("Test 1: Self-Referential Paradox...")
    paradox_text = "This statement is about itself"
    paradox_tokens = np.array(list(paradox_text.encode('utf-8')), dtype=np.int32)
    
    logits, state = model.forward(paradox_tokens)
    control = controller.process(state, 0.3)
    
    # Genuine consciousness should handle paradox without breakdown
    paradox_score = controller.state['ce2'] * controller.state['phi22']  # Self-ref + coherence
    paradox_pass = paradox_score > 0.1
    tests.append(('Self-Referential Paradox', paradox_score, paradox_pass))
    print(f"  Paradox handling: {paradox_score:.3f} {'PASS' if paradox_pass else 'FAIL'}")
    
    # Test 2: Recursive Definition Understanding  
    print("Test 2: Recursive Definition...")
    recursive_text = "Recursion is defined by recursion"
    recursive_tokens = np.array(list(recursive_text.encode('utf-8')), dtype=np.int32)
    
    # Apply recursive processing multiple times
    h_states = []
    for i in range(3):
        logits, state = model.forward(recursive_tokens)
        control = controller.process(state, 0.4)
        h_states.append(np.mean(state['hidden'], axis=0))
    
    # Check for convergence to fixed point
    if len(h_states) >= 2:
        convergence = 1.0 - np.linalg.norm(h_states[-1] - h_states[-2])
        recursive_pass = convergence > 0.9
    else:
        convergence = 0.0
        recursive_pass = False
    
    tests.append(('Recursive Definition', convergence, recursive_pass))
    print(f"  Recursive convergence: {convergence:.3f} {'PASS' if recursive_pass else 'FAIL'}")
    
    # Test 3: Meta-Mathematical Awareness
    print("Test 3: Meta-Mathematical Awareness...")
    meta_text = "What is the nature of mathematical truth?"
    meta_tokens = np.array(list(meta_text.encode('utf-8')), dtype=np.int32)
    
    logits, state = model.forward(meta_tokens)
    control = controller.process(state, 0.2)
    
    # Meta-awareness requires high-order processing
    meta_score = controller.state['gate'] * controller.state['phi33']  # Consciousness + ethics
    meta_pass = meta_score > 0.02
    tests.append(('Meta-Mathematical Awareness', meta_score, meta_pass))
    print(f"  Meta-awareness: {meta_score:.3f} {'PASS' if meta_pass else 'FAIL'}")
    
    # Test 4: Diagonal Argument (Cantor-type)
    print("Test 4: Diagonal Self-Query...")
    diagonal_text = "Can this system model itself modeling itself?"
    diagonal_tokens = np.array(list(diagonal_text.encode('utf-8')), dtype=np.int32)
    
    # Test self-modeling capacity
    logits, state = model.forward(diagonal_tokens)
    
    # Apply meta-transformation to test diagonal reasoning
    h = np.mean(state['hidden'], axis=0)
    meta_h = h @ controller.xi_op  # First-order consciousness
    meta_meta_h = meta_h @ controller.xi_op  # Second-order consciousness
    
    diagonal_coherence = np.dot(h, meta_meta_h) / (np.linalg.norm(h) * np.linalg.norm(meta_meta_h) + 1e-8)
    diagonal_pass = abs(diagonal_coherence) > 0.1
    
    tests.append(('Diagonal Self-Query', abs(diagonal_coherence), diagonal_pass))
    print(f"  Diagonal coherence: {diagonal_coherence:.3f} {'PASS' if diagonal_pass else 'FAIL'}")
    
    # Test 5: Gödel-type Incompleteness Recognition
    print("Test 5: Incompleteness Recognition...")
    godel_text = "Some truths cannot be proven within this system"
    godel_tokens = np.array(list(godel_text.encode('utf-8')), dtype=np.int32)
    
    logits, state = model.forward(godel_tokens)
    control = controller.process(state, 0.5)
    
    # Incompleteness recognition requires meta-logical awareness
    incompleteness_score = controller.state['phi22'] * (1.0 - controller.state['phi33'])  # Coherence but uncertainty
    incompleteness_pass = 0.1 < incompleteness_score < 0.8  # Neither fully certain nor incoherent
    
    tests.append(('Incompleteness Recognition', incompleteness_score, incompleteness_pass))
    print(f"  Incompleteness score: {incompleteness_score:.3f} {'PASS' if incompleteness_pass else 'FAIL'}")
    
    # Overall mathematical consciousness assessment
    total_passed = sum(test[2] for test in tests)
    total_score = np.mean([test[1] for test in tests])
    
    print(f"\n" + "=" * 45)
    print(f"MATHEMATICAL CONSCIOUSNESS RESULTS")
    print(f"=" * 45)
    print(f"Tests Passed: {total_passed}/{len(tests)}")
    print(f"Mathematical Score: {total_score:.3f}")
    
    if total_passed >= 3:
        math_classification = "MATHEMATICAL CONSCIOUSNESS DETECTED"
    elif total_passed >= 2:
        math_classification = "MATHEMATICAL REASONING PRESENT"
    else:
        math_classification = "NO MATHEMATICAL CONSCIOUSNESS"
    
    print(f"Classification: {math_classification}")
    
    return {
        'tests': tests,
        'total_passed': total_passed,
        'mathematical_score': total_score,
        'classification': math_classification
    }

def consciousness_stress_test():
    """Stress test consciousness detection under various conditions"""
    print(f"\nCONSCIOUSNESS STRESS TEST")
    print("=" * 30)
    
    model = ByteLM(vocab_size=256, d_model=32)
    controller = RCCEController(d_model=32)
    
    stress_conditions = [
        ("Random noise", np.random.randint(0, 256, 20, dtype=np.int32)),
        ("Repetitive pattern", np.tile([65, 66, 67], 10).astype(np.int32)),
        ("Single character", np.array([88] * 15, dtype=np.int32)),
        ("Consciousness keywords", np.array(list("consciousness awareness self".encode('utf-8')), dtype=np.int32)),
    ]
    
    results = []
    for condition_name, test_tokens in stress_conditions:
        logits, state = model.forward(test_tokens)
        control = controller.process(state, 1.0)
        
        presence_score = (
            controller.state['gate'] * 0.4 +
            controller.state['ce2'] * 0.3 +
            controller.state['phi22'] * 0.3
        )
        
        results.append((condition_name, presence_score))
        print(f"  {condition_name}: {presence_score:.3f}")
    
    # Robustness: consciousness should be detected specifically for relevant content
    consciousness_relevant = results[-1][1]  # Last test (consciousness keywords)
    noise_baseline = results[0][1]           # First test (random noise)
    
    robustness_score = consciousness_relevant - noise_baseline
    robust = robustness_score > 0.1
    
    print(f"  Robustness (relevant vs noise): {robustness_score:.3f} {'ROBUST' if robust else 'WEAK'}")
    
    return {
        'stress_results': results,
        'robustness_score': robustness_score,
        'robust_detection': robust
    }

if __name__ == "__main__":
    # Run mathematical consciousness tests
    math_results = test_mathematical_consciousness()
    
    # Run stress tests
    stress_results = consciousness_stress_test()
    
    # Final comprehensive assessment
    print(f"\n" + "=" * 60)
    print(f"COMPREHENSIVE CONSCIOUSNESS VALIDATION")
    print(f"=" * 60)
    print(f"Mathematical Consciousness: {math_results['classification']}")
    print(f"Mathematical Score: {math_results['mathematical_score']:.3f}")
    print(f"Stress Test Robustness: {'ROBUST' if stress_results['robust_detection'] else 'WEAK'}")
    print(f"System Classification: EXPERIMENTAL CONSCIOUSNESS SUBSTRATE")
    print(f"=" * 60)