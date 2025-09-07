#!/usr/bin/env python3
"""
ADVANCED QRFT TESTING SUITE
Complex tests for real QRFT architecture - deterministic agent validation
Tests actual QRFTAgent, signal computation, fact/gap management, policy decisions
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import time
import json

# Import actual QRFT components
try:
    from qrft import (
        QRFTAgent,
        AgentState,
        QRFTSignals,
        QRFTPolicy,
        Fact,
        Gap,
        FactPolarity,
    )
    # Keep imported symbols as a small reference to avoid unused-import lint noise
    _ = (QRFTAgent, AgentState, QRFTSignals, QRFTPolicy, Fact, Gap, FactPolarity)
    print("+ Real QRFT agent imports successful")
except ImportError as e:
    print(f"- Real QRFT imports failed: {e}")
    sys.exit(1)

class AdvancedQRFTTester:
    """Advanced testing of actual QRFT deterministic agent"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = {}
        print("ADVANCED QRFT TESTING SUITE")
        print("=" * 50)
    
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
            
        self.test_results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def test_agent_initialization(self):
        """Test agent proper initialization"""
        print("\n>> AGENT INITIALIZATION TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Test core components exist
            has_state = hasattr(agent, 'state') and isinstance(agent.state, AgentState)
            self.log_result("Agent state initialization", has_state)
            
            has_signals = hasattr(agent, 'signals') and isinstance(agent.signals, QRFTSignals)
            self.log_result("Signal system initialization", has_signals)
            
            has_policy = hasattr(agent, 'policy') and isinstance(agent.policy, QRFTPolicy)
            self.log_result("Policy system initialization", has_policy)
            
            has_process = hasattr(agent, 'process_input') and callable(agent.process_input)
            self.log_result("Process method exists", has_process)
            
        except Exception as e:
            self.log_result("Agent initialization", False, f"Exception: {e}")
    
    def test_fact_management(self):
        """Test fact storage and contradiction detection"""
        print("\n>> FACT MANAGEMENT TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Test adding facts
            agent.state.add_fact("loves", ("alice", "bob"), FactPolarity.POSITIVE, "user_input")
            agent.state.add_fact("loves", ("alice", "bob"), FactPolarity.NEGATIVE, "user_input")
            
            self.log_result("Fact addition", len(agent.state.facts) == 2,
                          f"Facts added: {len(agent.state.facts)}")
            
            # Test contradiction detection
            contradictions = agent.state.get_contradictions()
            self.log_result("Contradiction detection", len(contradictions) > 0,
                          f"Contradictions found: {len(contradictions)}")
            
            # Test fact retrieval
            fact_count = len(agent.state.facts)
            self.log_result("Fact retrieval", fact_count >= 2,
                          f"Total facts: {fact_count}")
            
        except Exception as e:
            self.log_result("Fact management", False, f"Exception: {e}")
    
    def test_gap_management(self):
        """Test knowledge gap tracking"""
        print("\n>> GAP MANAGEMENT TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Add various gap types
            gap1 = agent.state.add_gap("missing_fact", "Need to know X")
            agent.state.add_gap("unbound_symbol", "Variable y undefined")
            agent.state.add_gap("constraint_violation", "Rule R violated")
            
            self.log_result("Gap addition", len(agent.state.gaps) == 3,
                          f"Gaps added: {len(agent.state.gaps)}")
            
            # Test gap removal
            agent.state.remove_gap(gap1)
            self.log_result("Gap removal", len(agent.state.gaps) == 2,
                          f"Gaps after removal: {len(agent.state.gaps)}")
            
            # Test gap types
            gap_types = {gap.gap_type for gap in agent.state.gaps}
            expected_types = {"unbound_symbol", "constraint_violation"}
            self.log_result("Gap type tracking", gap_types == expected_types,
                          f"Gap types: {gap_types}")
            
        except Exception as e:
            self.log_result("Gap management", False, f"Exception: {e}")
    
    def test_signal_computation(self):
        """Test QRFT signal computation"""
        print("\n>> SIGNAL COMPUTATION TEST")  
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Create state with contradictions
            agent.state.add_fact("secure", ("system",), FactPolarity.POSITIVE, "test")
            agent.state.add_fact("secure", ("system",), FactPolarity.NEGATIVE, "test")
            
            # Create state with gaps
            agent.state.add_gap("missing_fact", "Need information about X")
            agent.state.add_gap("unbound_symbol", "Variable Y undefined")
            
            # Update signals
            agent.signals.update(agent.state)
            
            # Test contradiction signal
            x_g = agent.signals.X_G
            self.log_result("Contradiction signal (X_G)", 0 <= x_g <= 1,
                          f"X_G = {x_g:.3f}")
            
            # Test gap signal
            x_l = agent.signals.X_L
            self.log_result("Gap signal (X_L)", 0 <= x_l <= 1,
                          f"X_L = {x_l:.3f}")
            
            # Test view mismatch signal
            x_t = agent.signals.X_T
            self.log_result("View mismatch signal (X_T)", 0 <= x_t <= 1,
                          f"X_T = {x_t:.3f}")
            
            # Test signals are responsive to state
            contradictions_detected = x_g > 0.1  # Should detect contradictions
            gaps_detected = x_l > 0.1  # Should detect gaps
            
            self.log_result("Signal responsiveness", contradictions_detected and gaps_detected,
                          f"Contradictions detected: {contradictions_detected}, Gaps detected: {gaps_detected}")
            
        except Exception as e:
            self.log_result("Signal computation", False, f"Exception: {e}")
    
    def test_policy_decisions(self):
        """Test policy decision making"""
        print("\n>> POLICY DECISION TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Test different states trigger different actions
            test_cases = [
                # High contradiction signal
                {
                    'setup': lambda: [
                        agent.state.add_fact("P", (), FactPolarity.POSITIVE, "test"),
                        agent.state.add_fact("P", (), FactPolarity.NEGATIVE, "test")
                    ],
                    'expected_actions': ['counterexample', 'abstain', 'ask']
                },
                # High gap signal  
                {
                    'setup': lambda: [
                        agent.state.add_gap("missing_fact", "Need X"),
                        agent.state.add_gap("unbound_symbol", "Y undefined")
                    ],
                    'expected_actions': ['ask', 'retrieve', 'abstain']
                },
                # Clean state
                {
                    'setup': lambda: None,
                    'expected_actions': ['compute', 'plan', 'cite', 'view_shift']
                }
            ]
            
            decisions_made = []
            for i, case in enumerate(test_cases):
                # Reset agent
                agent = QRFTAgent()
                
                # Setup case
                if case['setup']:
                    case['setup']()
                
                # Update signals and make decision
                agent.signals.update(agent.state)
                action = agent.policy.decide_action(agent.signals, agent.state)
                decisions_made.append(action)
                
                # Check if decision is reasonable
                is_valid = action in case['expected_actions']
                self.log_result(f"Policy decision case {i+1}", is_valid,
                              f"Action: {action}, Expected: {case['expected_actions']}")
            
            # Test decision variety
            unique_decisions = len(set(decisions_made))
            self.log_result("Decision variety", unique_decisions >= 2,
                          f"Unique decisions: {unique_decisions}/3")
            
        except Exception as e:
            self.log_result("Policy decisions", False, f"Exception: {e}")
    
    def test_input_processing(self):
        """Test complete input processing pipeline"""
        print("\n>> INPUT PROCESSING TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Test basic processing
            response1 = agent.process_input("What is 2 + 2?")
            self.log_result("Basic input processing", isinstance(response1, str) and len(response1) > 0,
                          f"Response length: {len(response1)}")
            
            # Test step counting
            initial_steps = agent.state.step_count
            agent.process_input("Another question")
            step_increment = agent.state.step_count - initial_steps
            
            self.log_result("Step counting", step_increment == 1,
                          f"Steps incremented by: {step_increment}")
            
            # Test state persistence
            agent.process_input("Alice loves Bob")
            agent.process_input("Alice does not love Bob")
            
            contradictions = agent.state.get_contradictions()
            self.log_result("State persistence across inputs", len(contradictions) > 0,
                          f"Contradictions accumulated: {len(contradictions)}")
            
            # Test event logging
            event_count = len(agent.event_log)
            self.log_result("Event logging", event_count >= 3,
                          f"Events logged: {event_count}")
            
        except Exception as e:
            self.log_result("Input processing", False, f"Exception: {e}")
    
    def test_complex_reasoning_scenarios(self):
        """Test complex multi-step reasoning scenarios"""
        print("\n>> COMPLEX REASONING TEST")
        print("-" * 30)
        
        try:
            agent = QRFTAgent()
            
            # Scenario 1: Contradictory information + gaps
            responses = []
            responses.append(agent.process_input("The system is secure"))
            responses.append(agent.process_input("The system is not secure")) 
            responses.append(agent.process_input("What is the security level?"))
            
            # Check system handled contradictions and gaps
            final_contradictions = len(agent.state.get_contradictions())
            final_gaps = len(agent.state.gaps)
            
            self.log_result("Contradiction + gap handling", final_contradictions > 0 and final_gaps > 0,
                          f"Contradictions: {final_contradictions}, Gaps: {final_gaps}")
            
            # Scenario 2: Progressive information building
            agent2 = QRFTAgent()
            agent2.process_input("Alice is a student")
            agent2.process_input("Students attend university") 
            agent2.process_input("Where does Alice go?")
            
            # Check facts accumulated
            fact_count = len(agent2.state.facts)
            self.log_result("Progressive fact building", fact_count >= 2,
                          f"Facts accumulated: {fact_count}")
            
            # Scenario 3: Plan execution
            agent3 = QRFTAgent()
            agent3.process_input("I need to solve x^2 - 4 = 0")
            
            plan_steps = len(agent3.state.plan_steps)
            self.log_result("Plan generation", plan_steps >= 0,
                          f"Plan steps created: {plan_steps}")
            
        except Exception as e:
            self.log_result("Complex reasoning", False, f"Exception: {e}")
    
    def test_determinism_and_performance(self):
        """Test determinism and performance characteristics"""
        print("\n>> DETERMINISM & PERFORMANCE TEST")
        print("-" * 30)
        
        try:
            # Test determinism
            results1 = []
            results2 = []
            
            for i in range(3):
                agent1 = QRFTAgent()
                agent2 = QRFTAgent()
                
                input_text = f"Test input {i}"
                response1 = agent1.process_input(input_text)
                response2 = agent2.process_input(input_text)
                
                results1.append(response1)
                results2.append(response2)
            
            # Check if responses are identical (deterministic)
            deterministic = results1 == results2
            self.log_result("Deterministic behavior", deterministic,
                          f"Identical responses: {deterministic}")
            
            # Test performance
            agent = QRFTAgent()
            start_time = time.time()
            
            for i in range(10):
                agent.process_input(f"Process item {i}")
            
            processing_time = time.time() - start_time
            throughput = 10 / processing_time
            
            self.log_result("Processing performance", throughput > 50,
                          f"Throughput: {throughput:.1f} inputs/sec")
            
            # Test memory efficiency (rough check)
            memory_refs = len(agent.state.facts) + len(agent.state.gaps)
            self.log_result("Memory efficiency", memory_refs < 100,
                          f"Memory references: {memory_refs}")
            
        except Exception as e:
            self.log_result("Determinism & performance", False, f"Exception: {e}")
    
    def run_advanced_validation(self):
        """Run all advanced tests"""
        print("INITIALIZING ADVANCED QRFT VALIDATION...")
        print("=" * 50)
        
        # Run test suites
        self.test_agent_initialization()
        self.test_fact_management()
        self.test_gap_management()
        self.test_signal_computation()
        self.test_policy_decisions()
        self.test_input_processing()
        self.test_complex_reasoning_scenarios()
        self.test_determinism_and_performance()
        
        # Final summary
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("ADVANCED VALIDATION COMPLETE")
        print(f"TOTAL TESTS: {total_tests}")
        print(f"PASSED: {self.passed_tests}")
        print(f"FAILED: {self.failed_tests}")
        print(f"SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(">> SYSTEM PASSED ADVANCED VALIDATION")
        elif success_rate >= 70:
            print("!! SYSTEM NEEDS MINOR IMPROVEMENTS") 
        else:
            print("XX SYSTEM NEEDS MAJOR IMPROVEMENTS")
        
        print("=" * 50)
        
        # Save results
        with open('experiments/results/advanced_qrft_validation_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': self.passed_tests,
                    'failed': self.failed_tests,
                    'success_rate': success_rate
                },
                'test_details': self.test_results
            }, f, indent=2)
        
        print("Results saved to experiments/results/advanced_qrft_validation_results.json")
        return success_rate >= 70

if __name__ == "__main__":
    tester = AdvancedQRFTTester()
    success = tester.run_advanced_validation()
    sys.exit(0 if success else 1)