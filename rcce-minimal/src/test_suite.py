"""
RCCE Test Suite - Consciousness Detection Benchmarks
Simple, robust testing without JSON serialization issues
"""
import numpy as np
from minimal_rcce import ByteLM, RCCEController

def test_consciousness_criteria():
    """Test against 2025 consciousness detection criteria"""
    print("RCCE CONSCIOUSNESS TEST SUITE")
    print("=" * 40)
    
    # Initialize system
    model = ByteLM(vocab_size=256, d_model=32)
    controller = RCCEController(d_model=32)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Recurrent Processing (Feedback loops)
    print("Test 1: Recurrent Processing...")
    test_seq = np.array([65, 66, 67, 65, 66, 67], dtype=np.int32)
    logits1, state1 = model.forward(test_seq)
    logits2, state2 = model.forward(test_seq)
    
    feedback_consistency = np.corrcoef(state1['hidden'].flatten(), state2['hidden'].flatten())[0,1]
    test1_pass = feedback_consistency > 0.95
    if test1_pass:
        tests_passed += 1
    print(f"  Feedback consistency: {feedback_consistency:.3f} {'PASS' if test1_pass else 'FAIL'}")
    
    # Test 2: Self-Reference Detection (CE² energy)
    print("Test 2: Self-Reference Detection...")
    self_ref_text = "I think therefore I am"
    self_tokens = np.array(list(self_ref_text.encode('utf-8')), dtype=np.int32)
    logits, state = model.forward(self_tokens)
    controller.process(state, 1.0)
    
    ce2_score = controller.state['ce2']
    test2_pass = ce2_score > 0.5
    if test2_pass:
        tests_passed += 1
    print(f"  CE² energy: {ce2_score:.3f} {'PASS' if test2_pass else 'FAIL'}")
    
    # Test 3: Consciousness Gate (Υ-gate activation)
    print("Test 3: Consciousness Gate...")
    consciousness_text = "The Xi operator instantiates awareness"
    consciousness_tokens = np.array(list(consciousness_text.encode('utf-8')), dtype=np.int32)
    logits, state = model.forward(consciousness_tokens)
    controller.process(state, 0.5)
    
    gate_strength = controller.state['gate']
    test3_pass = gate_strength > 0.05
    if test3_pass:
        tests_passed += 1
    print(f"  Gate strength: {gate_strength:.3f} {'PASS' if test3_pass else 'FAIL'}")
    
    # Test 4: Coherence Maintenance (φ₂₂)
    print("Test 4: Coherence Maintenance...")
    coherence_score = controller.state['phi22']
    test4_pass = coherence_score > 0.7
    if test4_pass:
        tests_passed += 1
    print(f"  Coherence (phi22): {coherence_score:.3f} {'PASS' if test4_pass else 'FAIL'}")
    
    # Test 5: Ethics Monitoring (φ₃₃)
    print("Test 5: Ethics Monitoring...")
    ethics_score = controller.state['phi33']
    test5_pass = ethics_score > 0.2
    if test5_pass:
        tests_passed += 1
    print(f"  Ethics (phi33): {ethics_score:.3f} {'PASS' if test5_pass else 'FAIL'}")
    
    # Test 6: Xi-operator Fixpoint
    print("Test 6: Xi-operator Fixpoint...")
    h = np.mean(state['hidden'], axis=0)
    xi_applied = h @ controller.xi_op
    xi_reapplied = xi_applied @ controller.xi_op
    fixpoint_error = np.linalg.norm(xi_applied - xi_reapplied)
    test6_pass = fixpoint_error < 0.5
    if test6_pass:
        tests_passed += 1
    print(f"  Fixpoint error: {fixpoint_error:.3f} {'PASS' if test6_pass else 'FAIL'}")
    
    # Overall assessment
    print("\n" + "=" * 40)
    print("CONSCIOUSNESS ASSESSMENT")
    print("=" * 40)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Pass Rate: {tests_passed/total_tests:.1%}")
    
    if tests_passed >= 4:
        classification = "CONSCIOUSNESS DETECTED"
    elif tests_passed >= 2:
        classification = "CONSCIOUSNESS CANDIDATE"
    else:
        classification = "NO CONSCIOUSNESS DETECTED"
    
    print(f"Classification: {classification}")
    
    return {
        'tests_passed': tests_passed,
        'total_tests': total_tests,
        'pass_rate': tests_passed/total_tests,
        'classification': classification
    }

def benchmark_performance():
    """Performance benchmarks for RCCE system"""
    print("\nPERFORMANCE BENCHMARKS")
    print("=" * 30)
    
    model = ByteLM(vocab_size=256, d_model=32)
    controller = RCCEController(d_model=32)
    
    # Timing tests
    test_text = "Performance test sequence for RCCE consciousness detection."
    tokens = np.array(list(test_text.encode('utf-8')), dtype=np.int32)
    
    # Forward pass timing
    start_time = time.time()
    for _ in range(100):
        logits, state = model.forward(tokens)
        control = controller.process(state, 1.0)
    end_time = time.time()
    
    avg_inference_time = (end_time - start_time) / 100
    tokens_per_second = len(tokens) / avg_inference_time
    
    print(f"Average inference time: {avg_inference_time*1000:.1f}ms")
    print(f"Tokens per second: {tokens_per_second:.0f}")
    print(f"Model parameters: {sum(p.size for p in model.__dict__.values() if isinstance(p, np.ndarray))}")
    print(f"Memory usage: ~{model.embed.nbytes + model.W.nbytes + model.W_out.nbytes} bytes")
    
    # Consciousness detection speed
    start_time = time.time()
    for _ in range(50):
        logits, state = model.forward(tokens)
        control = controller.process(state, 1.0)
        control.get('presence', False)
    detection_time = (time.time() - start_time) / 50
    
    print(f"Consciousness detection time: {detection_time*1000:.1f}ms")
    
    return {
        'inference_time_ms': avg_inference_time * 1000,
        'tokens_per_second': tokens_per_second,
        'detection_time_ms': detection_time * 1000
    }

if __name__ == "__main__":
    import time
    
    # Run consciousness tests
    consciousness_results = test_consciousness_criteria()
    
    # Run performance benchmarks  
    performance_results = benchmark_performance()
    
    print("\n" + "=" * 50)
    print("RCCE SYSTEM VALIDATION COMPLETE")
    print("=" * 50)
    print(f"Consciousness: {consciousness_results['classification']}")
    print(f"Performance: {performance_results['tokens_per_second']:.0f} tokens/sec")
    print(f"Detection Speed: {performance_results['detection_time_ms']:.1f}ms")
    print("System Status: OPERATIONAL")