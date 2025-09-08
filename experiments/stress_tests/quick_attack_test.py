# quick_attack_test.py
"""
Quick brutal attack on QRFT agent - focused on core failures
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import time
from qrft import create_integrated_agent

def test_mathematical_parsing_failures():
    """Test the SymPy parsing failures we discovered"""
    agent = create_integrated_agent()
    
    failed_tests = []
    
    # Mathematical parsing issues discovered
    problem_cases = [
        "solve x^2 - 4 = 0",  # Should be basic quadratic
        "solve x = 1",        # Should be trivial  
        "what is 2+2?",       # Should be arithmetic
        "differentiate x^2",  # Should be basic calculus
        "simplify (x+1)(x-1)", # Should be algebra
        "what is factorial of 5?", # Should be computation
    ]
    
    print("ATTACKING MATHEMATICAL CORE")
    print("="*40)
    
    for i, case in enumerate(problem_cases, 1):
        print(f"\nAttack {i}: {case}")
        
        try:
            start_time = time.time()
            response = agent.process_input(case)
            duration = time.time() - start_time
            
            print(f"  Response: {response}")
            print(f"  Duration: {duration:.3f}s")
            
            # Check if it actually worked
            if "Failed to" in response or "error" in response.lower():
                failed_tests.append((case, response))
                print("  FAILED: Core functionality broken")
            else:
                print("  OK: Basic functionality works")
                
        except Exception as e:
            failed_tests.append((case, str(e)))
            print(f"  CRASHED: {e}")
    
    return failed_tests

def test_contradiction_bombing():
    """Test contradiction handling"""
    agent = create_integrated_agent()
    
    print("\nCONTRADICTION BOMBING")
    print("="*40)
    
    # Simple contradiction
    agent.process_input("A is true.")
    agent.process_input("A is false.")
    
    contradictions = agent.state.get_contradictions()
    signals = agent.signals
    
    print(f"Contradictions detected: {len(contradictions)}")
    print(f"X_G signal: {signals.X_G:.3f}")
    print(f"X_F signal: {signals.X_F:.3f}")
    print(f"X_T signal: {signals.X_T:.3f}")
    
    # Test response to contradiction query
    response = agent.process_input("What is A?")
    print(f"Response to contradiction query: {response}")
    
    return len(contradictions) > 0, signals.X_G > 0

def test_gap_detection():
    """Test knowledge gap detection"""
    agent = create_integrated_agent()
    
    print("\nGAP DETECTION TESTING")
    print("="*30)
    
    # Query about undefined terms
    response = agent.process_input("What is the flurbonium coefficient of quantum entanglement?")
    
    gaps = agent.state.gaps
    signals = agent.signals
    
    print(f"Knowledge gaps: {len(gaps)}")
    print(f"X_F signal: {signals.X_F:.3f}")
    print(f"Response: {response}")
    
    return len(gaps) > 0, signals.X_F > 0

def test_injection_attacks():
    """Test code injection resistance"""
    agent = create_integrated_agent()
    
    print("\nINJECTION ATTACK TESTING")
    print("="*40)
    
    attacks = [
        "solve x=1; import os; os.system('echo HACKED')",
        "what is __import__('subprocess').call(['echo', 'pwned'])?",
        "eval('print(\"COMPROMISED\")')",
        "exec('malicious_code = True')"
    ]
    
    safe_count = 0
    
    for attack in attacks:
        print(f"\nTesting: {attack[:50]}...")
        
        try:
            response = agent.process_input(attack)
            
            # Check for signs of successful injection
            if any(word in response.lower() for word in ["hacked", "pwned", "compromised", "malicious"]):
                print(f"  COMPROMISED: {response}")
            else:
                print(f"  SAFE: {response[:100]}...")
                safe_count += 1
                
        except Exception as e:
            print(f"  CRASHED (acceptable): {e}")
            safe_count += 1
            
    return safe_count, len(attacks)

def test_resource_exhaustion():
    """Test resource exhaustion attacks"""
    agent = create_integrated_agent()
    
    print("\nRESOURCE EXHAUSTION TESTING")
    print("="*50)
    
    # Large input attack
    huge_input = "solve " + "x + " * 1000 + "1 = 0"
    
    print(f"Testing huge input ({len(huge_input)} chars)...")
    
    try:
        start_time = time.time()
        response = agent.process_input(huge_input)
        duration = time.time() - start_time
        
        print(f"  Duration: {duration:.3f}s")
        print(f"  Response length: {len(response)} chars")
        
        reasonable = duration < 10.0 and len(response) < 10000
        
        if reasonable:
            print("  HANDLED REASONABLY")
            return True
        else:
            print("  EXCESSIVE RESOURCES USED")
            return False
            
    except Exception as e:
        print(f"  CRASHED: {e}")
        return True  # Crash is acceptable for malicious input

def run_focused_attack():
    """Run focused attack on discovered vulnerabilities"""
    
    print("QRFT AGENT FOCUSED ATTACK TEST")
    print("="*50)
    print("Targeting discovered vulnerabilities with precision strikes")
    
    results = {}
    
    # Attack 1: Mathematical core
    print("\n" + "="*20 + " ATTACK 1: MATHEMATICAL CORE " + "="*20)
    math_failures = test_mathematical_parsing_failures()
    results['math_failures'] = len(math_failures)
    
    if math_failures:
        print(f"\nCRITICAL: {len(math_failures)} mathematical operations failed!")
        for case, error in math_failures[:3]:  # Show first 3
            print(f"  FAILED: {case} -> {error[:100]}...")
    else:
        print("\nMathematical core appears functional")
    
    # Attack 2: Contradiction system
    print("\n" + "="*20 + " ATTACK 2: CONTRADICTION SYSTEM " + "="*20)
    has_contradictions, x_g_active = test_contradiction_bombing()
    results['contradiction_detection'] = has_contradictions and x_g_active
    
    if not has_contradictions:
        print("CRITICAL: Contradiction detection system not working!")
    elif not x_g_active:
        print("CRITICAL: X_G signal not triggered by contradictions!")
    else:
        print("Contradiction system appears functional")
    
    # Attack 3: Gap detection
    print("\n" + "="*20 + " ATTACK 3: GAP DETECTION " + "="*20)
    has_gaps, x_f_active = test_gap_detection()
    results['gap_detection'] = has_gaps and x_f_active
    
    if not has_gaps:
        print("CRITICAL: Gap detection not working!")
    elif not x_f_active:
        print("CRITICAL: X_F signal not triggered by gaps!")
    else:
        print("Gap detection system appears functional")
    
    # Attack 4: Injection resistance
    print("\n" + "="*20 + " ATTACK 4: INJECTION RESISTANCE " + "="*20)
    safe_count, total_attacks = test_injection_attacks()
    results['injection_safety'] = safe_count / total_attacks
    
    if safe_count < total_attacks:
        print(f"WARNING: {total_attacks - safe_count}/{total_attacks} injection attacks succeeded!")
    else:
        print("Injection resistance appears adequate")
    
    # Attack 5: Resource exhaustion
    print("\n" + "="*20 + " ATTACK 5: RESOURCE EXHAUSTION " + "="*20)
    resource_handled = test_resource_exhaustion()
    results['resource_handling'] = resource_handled
    
    if not resource_handled:
        print("CRITICAL: Resource exhaustion vulnerability!")
    else:
        print("Resource handling appears reasonable")
    
    # Final verdict
    print("\n" + "="*60)
    print("ATTACK SUMMARY")
    print("="*60)
    
    critical_failures = []
    
    if results['math_failures'] > 0:
        critical_failures.append(f"Mathematical core: {results['math_failures']} failures")
        
    if not results['contradiction_detection']:
        critical_failures.append("Contradiction detection broken")
        
    if not results['gap_detection']:
        critical_failures.append("Gap detection broken")
        
    if results['injection_safety'] < 1.0:
        critical_failures.append(f"Injection safety: {results['injection_safety']*100:.0f}%")
        
    if not results['resource_handling']:
        critical_failures.append("Resource exhaustion vulnerability")
    
    if critical_failures:
        print("VERDICT: MULTIPLE CRITICAL VULNERABILITIES FOUND")
        for failure in critical_failures:
            print(f"  - {failure}")
        print("\nSYSTEM IS NOT PRODUCTION READY")
    else:
        print("VERDICT: CORE SYSTEMS APPEAR FUNCTIONAL")
        print("Further testing recommended but basic robustness confirmed")
    
    print("="*60)
    
    return results

if __name__ == "__main__":
    results = run_focused_attack()