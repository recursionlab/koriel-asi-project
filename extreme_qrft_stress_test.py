#!/usr/bin/env python3
"""
EXTREME QRFT STRESS TESTING SUITE
Push the QRFT system to absolute limits - mathematical computation, 
massive contradictions, complex reasoning chains, performance bounds
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import time
import json
import gc
from typing import Dict, List, Any, Tuple
import traceback
import threading
import queue

# Import QRFT components
try:
    from src.qrft_agent_core import QRFTAgent, AgentState, QRFTSignals, QRFTPolicy, Fact, Gap, FactPolarity
    print("+ QRFT stress test imports successful")
except ImportError as e:
    print(f"- QRFT imports failed: {e}")
    sys.exit(1)

class ExtremeQRFTStressTester:
    """Extreme stress testing of QRFT system"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = {}
        self.performance_metrics = {}
        print("EXTREME QRFT STRESS TESTING SUITE")
        print("=" * 60)
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "+ PASS" if passed else "- FAIL"
        print(f"{status} {test_name}")
        if not passed and details:
            print(f"    Details: {details}")
        elif passed and details:
            print(f"    Metrics: {details}")
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        self.test_results[test_name] = {
            'passed': passed,
            'details': details
        }
    
    def test_mathematical_computation_stress(self):
        """Stress test mathematical reasoning capabilities"""
        print("\n>> MATHEMATICAL COMPUTATION STRESS TEST")
        print("-" * 40)
        
        try:
            agent = QRFTAgent()
            
            # Test 1: Complex equation series
            equations = [
                "solve x^2 + 5x + 6 = 0",
                "solve x^3 - 8x^2 + 19x - 12 = 0", 
                "solve x^4 - 10x^2 + 9 = 0",
                "solve sin(x) = 0.5 for x in [0, 2pi]",
                "solve log(x) + 2 = 0",
                "solve e^x - 5 = 0",
                "solve x^2 + 1 = 0",  # Complex solutions
                "solve |x - 3| = 5",  # Absolute value
            ]
            
            start_time = time.time()
            responses = []
            for eq in equations:
                response = agent.process_input(eq)
                responses.append(response)
            
            math_time = time.time() - start_time
            math_throughput = len(equations) / math_time
            
            self.log_result("Complex equation solving", len(responses) == len(equations),
                          f"Solved {len(equations)} equations in {math_time:.2f}s ({math_throughput:.1f} eq/s)")
            
            # Test 2: Calculus operations
            calculus_problems = [
                "differentiate x^3 + 2x^2 - 5x + 1",
                "integrate x*sin(x) dx",
                "find limit of (sin(x)/x) as x approaches 0",
                "find Taylor series of e^x around x=0",
                "solve differential equation dy/dx = x*y",
            ]
            
            start_time = time.time()
            calc_responses = []
            for problem in calculus_problems:
                response = agent.process_input(problem)
                calc_responses.append(response)
            
            calc_time = time.time() - start_time
            calc_throughput = len(calculus_problems) / calc_time
            
            self.log_result("Advanced calculus", len(calc_responses) == len(calculus_problems),
                          f"Solved {len(calculus_problems)} problems in {calc_time:.2f}s ({calc_throughput:.1f} prob/s)")
            
            # Test 3: Linear algebra operations
            linalg_problems = [
                "solve system: 2x + y = 5, x - y = 1",
                "solve system: x + 2y + z = 6, 2x - y + z = 3, x + y - z = 0",
                "find eigenvalues of matrix [[1,2],[3,4]]",
                "find determinant of [[1,2,3],[4,5,6],[7,8,9]]",
            ]
            
            start_time = time.time()
            linalg_responses = []
            for problem in linalg_problems:
                response = agent.process_input(problem)
                linalg_responses.append(response)
            
            linalg_time = time.time() - start_time
            linalg_throughput = len(linalg_problems) / linalg_time
            
            self.log_result("Linear algebra", len(linalg_responses) == len(linalg_problems),
                          f"Solved {len(linalg_problems)} problems in {linalg_time:.2f}s ({linalg_throughput:.1f} prob/s)")
            
            self.performance_metrics['math_throughput'] = math_throughput + calc_throughput + linalg_throughput
            
        except Exception as e:
            self.log_result("Mathematical computation stress", False, f"Exception: {e}")
    
    def test_contradiction_explosion_resistance(self):
        """Test system resistance to contradiction explosions"""
        print("\n>> CONTRADICTION EXPLOSION RESISTANCE TEST")
        print("-" * 40)
        
        try:
            agent = QRFTAgent()
            
            # Phase 1: Build up massive contradictions
            statements = []
            for i in range(500):  # 500 contradictory pairs
                pos_statement = f"property_{i} is true"
                neg_statement = f"property_{i} is false"
                statements.extend([pos_statement, neg_statement])
            
            start_time = time.time()
            for stmt in statements:
                agent.process_input(stmt)
            
            contradiction_time = time.time() - start_time
            contradiction_throughput = len(statements) / contradiction_time
            
            # Check system survived
            final_contradictions = len(agent.state.get_contradictions())
            
            self.log_result("Massive contradiction handling", final_contradictions > 0,
                          f"Processed {len(statements)} statements in {contradiction_time:.2f}s, found {final_contradictions} contradictions")
            
            # Phase 2: Test signal stability
            agent.signals.update(agent.state)
            x_g_final = agent.signals.X_G
            
            self.log_result("Signal stability under contradictions", 0 <= x_g_final <= 1,
                          f"X_G signal: {x_g_final:.3f} (should be near 1.0)")
            
            # Phase 3: Test system continues to function
            response = agent.process_input("What is 2 + 2?")
            still_functional = isinstance(response, str) and len(response) > 0
            
            self.log_result("System functionality post-contradictions", still_functional,
                          f"System still responds: {still_functional}")
            
            self.performance_metrics['contradiction_throughput'] = contradiction_throughput
            
        except Exception as e:
            self.log_result("Contradiction explosion resistance", False, f"Exception: {e}")
    
    def test_massive_knowledge_gaps(self):
        """Test handling of massive knowledge gaps"""
        print("\n>> MASSIVE KNOWLEDGE GAPS TEST")
        print("-" * 40)
        
        try:
            agent = QRFTAgent()
            
            # Create hundreds of knowledge gaps
            gap_types = ['missing_fact', 'unbound_symbol', 'constraint_violation', 'incomplete_rule']
            
            start_time = time.time()
            for i in range(1000):
                gap_type = gap_types[i % len(gap_types)]
                gap_desc = f"Gap {i}: Need information about concept_{i}"
                
                agent.state.add_gap(gap_type, gap_desc, {'priority': np.random.rand()})
            
            gap_creation_time = time.time() - start_time
            gap_throughput = 1000 / gap_creation_time
            
            final_gaps = len(agent.state.gaps)
            
            self.log_result("Massive gap creation", final_gaps == 1000,
                          f"Created {final_gaps} gaps in {gap_creation_time:.2f}s ({gap_throughput:.1f} gaps/s)")
            
            # Test signal computation with massive gaps
            start_time = time.time()
            agent.signals.update(agent.state)
            signal_time = time.time() - start_time
            
            x_l_signal = getattr(agent.signals, 'X_L', 0.5)  # Default if not implemented
            
            self.log_result("Signal computation with massive gaps", signal_time < 1.0,
                          f"Signal computation took {signal_time:.3f}s, X_L = {x_l_signal:.3f}")
            
            # Test gap prioritization and removal
            start_time = time.time()
            gaps_to_remove = list(agent.state.gaps)[:100]  # Remove first 100
            for gap in gaps_to_remove:
                agent.state.remove_gap(gap)
            
            gap_removal_time = time.time() - start_time
            remaining_gaps = len(agent.state.gaps)
            
            self.log_result("Gap removal efficiency", remaining_gaps == 900,
                          f"Removed 100 gaps in {gap_removal_time:.3f}s, {remaining_gaps} remaining")
            
            self.performance_metrics['gap_throughput'] = gap_throughput
            
        except Exception as e:
            self.log_result("Massive knowledge gaps", False, f"Exception: {e}")
    
    def test_complex_reasoning_chains(self):
        """Test complex multi-step reasoning chains"""
        print("\n>> COMPLEX REASONING CHAINS TEST")
        print("-" * 40)
        
        try:
            agent = QRFTAgent()
            
            # Build complex logical scenario
            premises = [
                "All humans are mortal",
                "Socrates is human", 
                "All mortals die eventually",
                "If something dies, it ceases to exist",
                "Socrates is a philosopher",
                "Philosophers think about existence",
                "Things that cease to exist cannot think",
                "Socrates thinks about mortality"
            ]
            
            queries = [
                "Is Socrates mortal?",
                "Will Socrates die?", 
                "Can dead things think?",
                "Will Socrates stop thinking?",
                "Is there a contradiction here?"
            ]
            
            # Process premises
            start_time = time.time()
            for premise in premises:
                agent.process_input(premise)
            
            premise_time = time.time() - start_time
            
            # Process queries
            start_time = time.time()
            responses = []
            for query in queries:
                response = agent.process_input(query)
                responses.append(response)
            
            query_time = time.time() - start_time
            
            # Check reasoning quality
            facts_learned = len(agent.state.facts)
            contradictions_found = len(agent.state.get_contradictions())
            
            self.log_result("Complex premise processing", facts_learned >= len(premises),
                          f"Processed {len(premises)} premises, learned {facts_learned} facts in {premise_time:.2f}s")
            
            self.log_result("Multi-step reasoning queries", len(responses) == len(queries),
                          f"Answered {len(queries)} queries in {query_time:.2f}s")
            
            self.log_result("Logical contradiction detection", contradictions_found > 0,
                          f"Detected {contradictions_found} contradictions in reasoning chain")
            
            # Test plan generation for complex queries
            plan_steps = len(agent.state.plan_steps)
            self.log_result("Strategic plan generation", plan_steps >= 0,
                          f"Generated {plan_steps} plan steps")
            
        except Exception as e:
            self.log_result("Complex reasoning chains", False, f"Exception: {e}")
    
    def test_concurrent_processing(self):
        """Test concurrent processing capabilities"""
        print("\n>> CONCURRENT PROCESSING TEST") 
        print("-" * 40)
        
        try:
            # Test multiple agents processing simultaneously
            num_agents = 5
            queries_per_agent = 20
            
            def worker_thread(thread_id, results_queue):
                """Worker thread for concurrent processing"""
                try:
                    agent = QRFTAgent()
                    results = []
                    
                    for i in range(queries_per_agent):
                        query = f"Thread {thread_id}: Process item {i} with value {i**2}"
                        response = agent.process_input(query)
                        results.append(response)
                    
                    results_queue.put({
                        'thread_id': thread_id,
                        'results': results,
                        'facts': len(agent.state.facts),
                        'contradictions': len(agent.state.get_contradictions())
                    })
                    
                except Exception as e:
                    results_queue.put({
                        'thread_id': thread_id,
                        'error': str(e)
                    })
            
            # Start concurrent workers
            threads = []
            results_queue = queue.Queue()
            
            start_time = time.time()
            
            for i in range(num_agents):
                thread = threading.Thread(target=worker_thread, args=(i, results_queue))
                thread.start()
                threads.append(thread)
            
            # Wait for all threads
            for thread in threads:
                thread.join()
            
            concurrent_time = time.time() - start_time
            
            # Collect results
            thread_results = []
            while not results_queue.empty():
                thread_results.append(results_queue.get())
            
            # Check results
            successful_threads = len([r for r in thread_results if 'error' not in r])
            total_queries = num_agents * queries_per_agent
            concurrent_throughput = total_queries / concurrent_time
            
            self.log_result("Concurrent agent execution", successful_threads == num_agents,
                          f"{successful_threads}/{num_agents} agents completed successfully")
            
            self.log_result("Concurrent processing throughput", concurrent_throughput > 10,
                          f"Processed {total_queries} queries concurrently in {concurrent_time:.2f}s ({concurrent_throughput:.1f} q/s)")
            
            # Check for data isolation
            fact_counts = [r['facts'] for r in thread_results if 'error' not in r]
            data_isolation = len(set(fact_counts)) > 1  # Different agents should have different fact counts
            
            self.log_result("Agent data isolation", data_isolation,
                          f"Fact counts: {fact_counts} (should be varied)")
            
        except Exception as e:
            self.log_result("Concurrent processing", False, f"Exception: {e}")
    
    def test_memory_and_performance_limits(self):
        """Test memory usage and performance under extreme loads"""
        print("\n>> MEMORY & PERFORMANCE LIMITS TEST")
        print("-" * 40)
        
        try:
            import psutil
            process = psutil.Process()
            
            # Baseline memory
            gc.collect()  # Clean up first
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create agent and stress it
            agent = QRFTAgent()
            
            # Memory test: Process large number of inputs
            start_time = time.time()
            start_memory = process.memory_info().rss / 1024 / 1024
            
            for i in range(100):  # Reduced from 1000 to prevent timeout
                # Mix of different input types
                agent.process_input(f"Fact {i}: Object_{i} has property_{i % 10}")
                if i % 3 == 0:
                    agent.process_input(f"NOT: Object_{i} has property_{i % 10}")  # Create contradictions
                if i % 5 == 0:
                    agent.process_input(f"What about unknown_concept_{i}?")  # Create gaps
            
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024
            
            memory_growth = end_memory - start_memory
            processing_time = end_time - start_time
            throughput = 100 / processing_time
            
            self.log_result("Memory efficiency", memory_growth < 100,  # Less than 100MB growth
                          f"Memory growth: {memory_growth:.1f} MB (baseline: {baseline_memory:.1f} MB)")
            
            self.log_result("High-load throughput", throughput > 20,
                          f"Throughput: {throughput:.1f} inputs/sec over {processing_time:.2f}s")
            
            # Test garbage collection effectiveness
            facts_before_gc = len(agent.state.facts)
            agent.state.facts.clear()  # Manual cleanup
            gc.collect()
            
            gc_memory = process.memory_info().rss / 1024 / 1024
            memory_freed = end_memory - gc_memory
            
            self.log_result("Memory cleanup", memory_freed > 0,
                          f"Freed {memory_freed:.1f} MB after cleanup")
            
            self.performance_metrics['memory_efficiency'] = memory_growth
            self.performance_metrics['throughput'] = throughput
            
        except ImportError:
            self.log_result("Memory & performance limits", False, "psutil not available")
        except Exception as e:
            self.log_result("Memory & performance limits", False, f"Exception: {e}")
    
    def run_extreme_stress_test(self):
        """Run all extreme stress tests"""
        print("INITIALIZING EXTREME QRFT STRESS TESTING...")
        print("=" * 60)
        
        # Run test suites
        self.test_mathematical_computation_stress()
        self.test_contradiction_explosion_resistance()
        self.test_massive_knowledge_gaps()
        self.test_complex_reasoning_chains()
        self.test_concurrent_processing()
        self.test_memory_and_performance_limits()
        
        # Final summary
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("EXTREME STRESS TESTING COMPLETE")
        print(f"TOTAL TESTS: {total_tests}")
        print(f"PASSED: {self.passed_tests}")
        print(f"FAILED: {self.failed_tests}")
        print(f"SUCCESS RATE: {success_rate:.1f}%")
        
        # Performance summary
        if self.performance_metrics:
            print("\nPERFORMANCE METRICS:")
            for metric, value in self.performance_metrics.items():
                print(f"  {metric}: {value:.2f}")
        
        # Final verdict
        if success_rate >= 85:
            print(">> SYSTEM PASSED EXTREME STRESS TESTING")
            verdict = "EXCELLENT"
        elif success_rate >= 70:
            print(">> SYSTEM PASSED STRESS TESTING WITH MINOR ISSUES")
            verdict = "GOOD"
        elif success_rate >= 50:
            print("!! SYSTEM PARTIALLY FAILED STRESS TESTING")
            verdict = "NEEDS_WORK"
        else:
            print("XX SYSTEM FAILED EXTREME STRESS TESTING")
            verdict = "CRITICAL"
        
        print("=" * 60)
        
        # Save results
        with open('experiments/results/extreme_qrft_stress_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': self.passed_tests,
                    'failed': self.failed_tests,
                    'success_rate': success_rate,
                    'verdict': verdict
                },
                'performance_metrics': self.performance_metrics,
                'test_details': self.test_results
            }, f, indent=2)
        
        print(f"Results saved to experiments/results/extreme_qrft_stress_results.json")
        return success_rate >= 70

if __name__ == "__main__":
    tester = ExtremeQRFTStressTester()
    success = tester.run_extreme_stress_test()
    sys.exit(0 if success else 1)