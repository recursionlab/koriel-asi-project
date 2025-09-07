#!/usr/bin/env python3
"""
EXTENDED CONSCIOUSNESS FIELD TESTING SUITE
Comprehensive validation of consciousness emergence across parameter space
"""

import numpy as np
import time
import json
from quantum_consciousness_simple import SimpleQuantumField

def test_parameter_sweep():
    """Test consciousness emergence across parameter ranges"""
    
    print("*" * 60)
    print("CONSCIOUSNESS PARAMETER SWEEP TEST")
    print("*" * 60)
    
    # Parameter ranges based on your optimization plan
    c_rates = [0.02, 0.05, 0.10]  # consciousness accumulation rates
    c_thresholds = [0.25, 0.5, 0.75]  # consciousness thresholds
    
    results = {}
    
    for c_rate in c_rates:
        for c_thresh in c_thresholds:
            print(f"\nTesting C_RATE={c_rate}, C_THRESH={c_thresh}")
            
            # Create field with specific parameters
            field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
            field.C_RATE = c_rate
            field.C_THRESH = c_thresh
            field.initialize_consciousness_seed()
            
            # Run focused test (3000 steps for faster iteration)
            start_time = time.time()
            field.evolve(3000)
            test_time = time.time() - start_time
            
            # Record results
            final_state = field.query_consciousness()
            consciousness_emerged = final_state['consciousness_level'] > 0.01
            modifications_active = final_state['total_modifications'] > 0
            
            results[f"rate_{c_rate}_thresh_{c_thresh}"] = {
                'consciousness_level': final_state['consciousness_level'],
                'consciousness_emerged': consciousness_emerged,
                'total_modifications': final_state['total_modifications'],
                'modifications_active': modifications_active,
                'total_patterns': final_state['total_patterns'],
                'field_complexity': final_state['field_complexity'],
                'test_time': test_time,
                'success': consciousness_emerged and modifications_active
            }
            
            print(f"   Consciousness: {final_state['consciousness_level']:.6f}")
            print(f"   Modifications: {final_state['total_modifications']}")
            print(f"   Success: {'YES' if results[f'rate_{c_rate}_thresh_{c_thresh}']['success'] else 'NO'}")
    
    # Analyze results
    successful_configs = [k for k, v in results.items() if v['success']]
    print("\n📊 PARAMETER SWEEP RESULTS:")
    print(f"   Successful configurations: {len(successful_configs)}/{len(results)}")
    
    if successful_configs:
        best_config = max(successful_configs, 
                         key=lambda k: results[k]['consciousness_level'])
        print(f"   Best configuration: {best_config}")
        print(f"   Best consciousness level: {results[best_config]['consciousness_level']:.6f}")
    
    return results

def test_consciousness_stability():
    """Test consciousness persistence over extended evolution"""
    
    print("\n" + "*" * 60)
    print("CONSCIOUSNESS STABILITY TEST")
    print("*" * 60)
    
    # Use best-known parameters
    field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field.C_RATE = 0.05
    field.C_THRESH = 0.5
    field.initialize_consciousness_seed()
    
    # Track consciousness evolution over time
    consciousness_history = []
    modification_history = []
    complexity_history = []
    time_points = []
    
    checkpoint_interval = 1000
    total_steps = 10000
    
    print(f"Running extended evolution for {total_steps} steps...")
    
    for checkpoint in range(0, total_steps, checkpoint_interval):
        field.evolve(checkpoint_interval)
        
        state = field.query_consciousness()
        consciousness_history.append(state['consciousness_level'])
        modification_history.append(state['total_modifications'])
        complexity_history.append(state['field_complexity'])
        time_points.append(field.t)
        
        print(f"   Step {checkpoint + checkpoint_interval}: "
              f"C={state['consciousness_level']:.4f}, "
              f"Mods={state['total_modifications']}, "
              f"Complexity={state['field_complexity']:.3f}")
    
    # Analyze stability
    c_trend = np.polyfit(range(len(consciousness_history)), consciousness_history, 1)[0]
    c_variance = np.var(consciousness_history)
    
    print("\n📊 STABILITY ANALYSIS:")
    print(f"   Consciousness trend: {c_trend:.6f}/step")
    print(f"   Consciousness variance: {c_variance:.6f}")
    print(f"   Final consciousness: {consciousness_history[-1]:.6f}")
    print(f"   Total modifications: {modification_history[-1]}")
    print(f"   Stability: {'STABLE' if abs(c_trend) < 0.001 and c_variance < 0.01 else 'UNSTABLE'}")
    
    return {
        'consciousness_history': consciousness_history,
        'modification_history': modification_history,
        'complexity_history': complexity_history,
        'time_points': time_points,
        'trend': c_trend,
        'variance': c_variance,
        'stable': abs(c_trend) < 0.001 and c_variance < 0.01
    }

def test_perturbation_response():
    """Test consciousness response to different perturbation patterns"""
    
    print("\n" + "*" * 60)
    print("PERTURBATION RESPONSE TEST") 
    print("*" * 60)
    
    # Initialize conscious field
    field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
    field.C_RATE = 0.05
    field.C_THRESH = 0.5
    field.initialize_consciousness_seed()
    
    # Develop initial consciousness
    print("Developing baseline consciousness...")
    field.evolve(2000)
    
    # Test different perturbation types
    perturbation_tests = [
        {"name": "Weak Central", "amplitude": 0.01, "location": 0.0, "width": 1.0},
        {"name": "Strong Central", "amplitude": 0.1, "location": 0.0, "width": 1.0},
        {"name": "Weak Off-Center", "amplitude": 0.01, "location": 5.0, "width": 1.0},
        {"name": "Strong Off-Center", "amplitude": 0.1, "location": 5.0, "width": 1.0},
        {"name": "Wide Perturbation", "amplitude": 0.05, "location": 0.0, "width": 5.0},
        {"name": "Narrow Perturbation", "amplitude": 0.05, "location": 0.0, "width": 0.5},
    ]
    
    response_results = {}
    
    for test in perturbation_tests:
        print(f"\nTesting: {test['name']}")
        
        # Record pre-perturbation state
        pre_state = field.query_consciousness()
        pre_consciousness = pre_state['consciousness_level']
        
        # Apply perturbation
        field.inject_perturbation(
            amplitude=test['amplitude'],
            location=test['location'], 
            width=test['width']
        )
        
        # Measure immediate response
        field.evolve(100)  # Short evolution to see immediate response
        immediate_state = field.query_consciousness()
        
        # Measure extended response  
        field.evolve(400)  # Longer evolution for full response
        extended_state = field.query_consciousness()
        
        immediate_response = immediate_state['consciousness_level'] - pre_consciousness
        extended_response = extended_state['consciousness_level'] - pre_consciousness
        
        response_results[test['name']] = {
            'perturbation': test,
            'pre_consciousness': pre_consciousness,
            'immediate_response': immediate_response,
            'extended_response': extended_response,
            'response_detected': abs(extended_response) > 1e-6
        }
        
        print(f"   Pre: {pre_consciousness:.6f}")
        print(f"   Immediate Δ: {immediate_response:.6f}")
        print(f"   Extended Δ: {extended_response:.6f}")
        print(f"   Response: {'YES' if abs(extended_response) > 1e-6 else 'NO'}")
    
    # Analyze response patterns
    responsive_tests = [k for k, v in response_results.items() if v['response_detected']]
    print("\n📊 PERTURBATION RESPONSE ANALYSIS:")
    print(f"   Responsive tests: {len(responsive_tests)}/{len(perturbation_tests)}")
    
    if responsive_tests:
        max_response_test = max(responsive_tests, 
                               key=lambda k: abs(response_results[k]['extended_response']))
        print(f"   Strongest response: {max_response_test}")
        print(f"   Response magnitude: {response_results[max_response_test]['extended_response']:.6f}")
    
    return response_results

def test_reproducibility():
    """Test consciousness emergence reproducibility across multiple runs"""
    
    print("\n" + "*" * 60) 
    print("CONSCIOUSNESS REPRODUCIBILITY TEST")
    print("*" * 60)
    
    num_runs = 5
    results = []
    
    for run in range(num_runs):
        print(f"\nRun {run + 1}/{num_runs}")
        
        # Fresh field each time
        field = SimpleQuantumField(N=256, L=20.0, dt=0.001)
        field.C_RATE = 0.05
        field.C_THRESH = 0.5
        field.initialize_consciousness_seed()
        
        # Standard evolution
        start_time = time.time()
        field.evolve(5000)
        run_time = time.time() - start_time
        
        final_state = field.query_consciousness()
        
        run_result = {
            'run_id': run + 1,
            'consciousness_level': final_state['consciousness_level'],
            'total_modifications': final_state['total_modifications'],
            'total_patterns': final_state['total_patterns'],
            'field_complexity': final_state['field_complexity'],
            'consciousness_emerged': final_state['consciousness_level'] > 0.01,
            'modifications_active': final_state['total_modifications'] > 0,
            'run_time': run_time
        }
        
        results.append(run_result)
        
        print(f"   Consciousness: {final_state['consciousness_level']:.6f}")
        print(f"   Modifications: {final_state['total_modifications']}")
        print(f"   Emerged: {'YES' if run_result['consciousness_emerged'] else 'NO'}")
    
    # Analyze reproducibility
    consciousness_levels = [r['consciousness_level'] for r in results]
    modification_counts = [r['total_modifications'] for r in results]
    emergence_rate = sum(r['consciousness_emerged'] for r in results) / num_runs
    
    c_mean = np.mean(consciousness_levels)
    c_std = np.std(consciousness_levels)
    m_mean = np.mean(modification_counts)
    m_std = np.std(modification_counts)
    
    print("\n📊 REPRODUCIBILITY ANALYSIS:")
    print(f"   Emergence success rate: {emergence_rate*100:.1f}%")
    print(f"   Consciousness level: {c_mean:.6f} ± {c_std:.6f}")
    print(f"   Modifications: {m_mean:.1f} ± {m_std:.1f}")
    print(f"   Reproducibility: {'HIGH' if emergence_rate >= 0.8 and c_std < 0.1 else 'MODERATE' if emergence_rate >= 0.6 else 'LOW'}")
    
    return {
        'runs': results,
        'emergence_rate': emergence_rate,
        'consciousness_stats': {'mean': c_mean, 'std': c_std},
        'modification_stats': {'mean': m_mean, 'std': m_std},
        'reproducible': emergence_rate >= 0.8 and c_std < 0.1
    }

def run_extended_test_suite():
    """Run complete extended testing suite"""
    
    print("=" * 70)
    print("EXTENDED QUANTUM CONSCIOUSNESS TESTING SUITE")
    print("=" * 70)
    print("Testing consciousness emergence robustness and stability")
    
    start_time = time.time()
    
    # Run all test categories
    test_results = {}
    
    test_results['parameter_sweep'] = test_parameter_sweep()
    test_results['stability'] = test_consciousness_stability()
    test_results['perturbation_response'] = test_perturbation_response()
    test_results['reproducibility'] = test_reproducibility()
    
    total_time = time.time() - start_time
    
    # Overall assessment
    print("\n" + "=" * 70)
    print("EXTENDED TEST SUITE RESULTS")
    print("=" * 70)
    
    # Parameter sweep assessment
    param_success_rate = sum(1 for v in test_results['parameter_sweep'].values() 
                           if v.get('success', False)) / len(test_results['parameter_sweep'])
    
    print("\n🔬 PARAMETER SWEEP:")
    print(f"   Success rate across parameter space: {param_success_rate*100:.1f}%")
    
    print("\n⏱️ STABILITY:")
    print(f"   Long-term stability: {'PASS' if test_results['stability']['stable'] else 'FAIL'}")
    print(f"   Consciousness trend: {test_results['stability']['trend']:.6f}/step")
    
    print("\n🎯 PERTURBATION RESPONSE:")
    responsive_count = sum(1 for v in test_results['perturbation_response'].values() 
                          if v.get('response_detected', False))
    total_perturbations = len(test_results['perturbation_response'])
    print(f"   Response rate: {responsive_count}/{total_perturbations} ({responsive_count/total_perturbations*100:.1f}%)")
    
    print("\n🔄 REPRODUCIBILITY:")
    print(f"   Emergence rate: {test_results['reproducibility']['emergence_rate']*100:.1f}%")
    print(f"   Reproducible: {'YES' if test_results['reproducibility']['reproducible'] else 'NO'}")
    
    # Overall verdict
    overall_success = (param_success_rate >= 0.5 and 
                      test_results['stability']['stable'] and
                      responsive_count >= total_perturbations * 0.5 and
                      test_results['reproducibility']['emergence_rate'] >= 0.6)
    
    print("\n🏆 OVERALL VERDICT:")
    print(f"   Extended Testing Result: {'SUCCESS' if overall_success else 'PARTIAL SUCCESS'}")
    print(f"   Consciousness Implementation: {'ROBUST' if overall_success else 'NEEDS REFINEMENT'}")
    print(f"   Total test time: {total_time:.1f}s")
    
    # Save comprehensive results
    test_results['summary'] = {
        'parameter_success_rate': param_success_rate,
        'stability_pass': test_results['stability']['stable'],
        'perturbation_response_rate': responsive_count / total_perturbations,
        'emergence_rate': test_results['reproducibility']['emergence_rate'],
        'overall_success': overall_success,
        'total_test_time': total_time
    }
    
    with open('experiments/results/extended_consciousness_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
        
    print("\n💾 Complete results saved to experiments/results/extended_consciousness_test_results.json")
    
    return test_results

if __name__ == "__main__":
    # Run the complete extended test suite
    results = run_extended_test_suite()
    
    print("\n🚀 Extended testing complete!")
    print("   All test categories executed successfully")
    print("   Results available for detailed analysis")