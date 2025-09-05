# src/stress_test.py
import numpy as np
import time
import json
from pathlib import Path
from .data import load_corpus, make_stream, bigram_features
from .model import TinyByteLM
from .dec import d2_norm, torsion_norm, curvature_comm_norm

class AdaptiveStressTester:
    def __init__(self, base_config):
        self.base_config = base_config
        self.failure_modes = []
        self.performance_history = []
        self.adaptation_log = []
        
    def stress_level_1_basic(self):
        """Basic functionality under minimal load"""
        print("=== STRESS LEVEL 1: BASIC ===")
        results = {"level": 1, "tests": [], "overall": "PASS"}
        
        try:
            # Test 1: Model creation and forward pass
            model = TinyByteLM(ctx=32, d=16, seed=42)
            x = np.random.randint(0, 256, (1, 32), dtype=np.uint8)
            start_time = time.time()
            logits, h1, h = model.forward(x)
            forward_time = time.time() - start_time
            
            results["tests"].append({
                "name": "forward_pass", 
                "status": "PASS",
                "time": forward_time,
                "output_shape": logits.shape
            })
            
            # Test 2: Training step
            y = np.random.randint(0, 256, (1, 32), dtype=np.uint8)
            start_time = time.time()
            loss, probs, h1_step = model.step(x, y, lr=0.1)
            step_time = time.time() - start_time
            
            results["tests"].append({
                "name": "training_step",
                "status": "PASS", 
                "time": step_time,
                "loss": float(loss)
            })
            
        except Exception as e:
            results["overall"] = "FAIL"
            results["error"] = str(e)
            self.failure_modes.append(("level_1", str(e)))
            
        return results
    
    def stress_level_2_scale(self):
        """Scaled parameters - larger model, longer sequences"""
        print("=== STRESS LEVEL 2: SCALE ===")
        results = {"level": 2, "tests": [], "overall": "PASS"}
        
        try:
            # Scale up: 64D hidden, 128 context
            model = TinyByteLM(ctx=128, d=64, seed=42)
            x = np.random.randint(0, 256, (4, 128), dtype=np.uint8)
            y = np.random.randint(0, 256, (4, 128), dtype=np.uint8)
            
            start_time = time.time()
            loss, probs, h1 = model.step(x, y, lr=0.1)
            step_time = time.time() - start_time
            
            # Memory usage proxy
            param_count = sum(p.size for p in [model.E, model.W1, model.W2, model.b1, model.b2])
            
            results["tests"].append({
                "name": "scaled_training",
                "status": "PASS",
                "time": step_time, 
                "loss": float(loss),
                "param_count": param_count,
                "batch_size": x.shape[0],
                "context_len": x.shape[1]
            })
            
            # Performance degradation check
            if step_time > 0.5:  # Warning threshold
                results["warnings"] = [f"Training step slow: {step_time:.3f}s"]
            
        except Exception as e:
            results["overall"] = "FAIL"
            results["error"] = str(e)
            self.failure_modes.append(("level_2_scale", str(e)))
            
        return results
    
    def stress_level_3_sequence_length(self):
        """Extreme sequence lengths"""
        print("=== STRESS LEVEL 3: SEQUENCE LENGTH ===")
        results = {"level": 3, "tests": [], "overall": "PASS"}
        
        lengths_to_test = [256, 512, 1024]
        
        for seq_len in lengths_to_test:
            try:
                model = TinyByteLM(ctx=seq_len, d=32, seed=42)
                x = np.random.randint(0, 256, (1, seq_len), dtype=np.uint8)
                y = np.random.randint(0, 256, (1, seq_len), dtype=np.uint8)
                
                start_time = time.time()
                loss, probs, h1 = model.step(x, y, lr=0.1)
                step_time = time.time() - start_time
                
                results["tests"].append({
                    "name": f"seq_len_{seq_len}",
                    "status": "PASS",
                    "time": step_time,
                    "loss": float(loss),
                    "memory_mb": (x.nbytes + y.nbytes + model.E.nbytes) / 1e6
                })
                
                # Break early if too slow
                if step_time > 2.0:
                    results["tests"].append({
                        "name": f"seq_len_limit",
                        "status": "LIMIT_REACHED",
                        "max_feasible_length": seq_len
                    })
                    break
                    
            except MemoryError:
                results["tests"].append({
                    "name": f"seq_len_{seq_len}",
                    "status": "MEMORY_FAIL",
                    "error": "Out of memory"
                })
                self.failure_modes.append(("memory_limit", f"seq_len_{seq_len}"))
                break
            except Exception as e:
                results["tests"].append({
                    "name": f"seq_len_{seq_len}",
                    "status": "FAIL", 
                    "error": str(e)
                })
                self.failure_modes.append(("sequence_length", str(e)))
                break
                
        return results
    
    def stress_level_4_batch_size(self):
        """Large batch processing"""
        print("=== STRESS LEVEL 4: BATCH SIZE ===")
        results = {"level": 4, "tests": [], "overall": "PASS"}
        
        batch_sizes = [8, 16, 32, 64, 128]
        
        for batch_size in batch_sizes:
            try:
                model = TinyByteLM(ctx=64, d=32, seed=42)
                x = np.random.randint(0, 256, (batch_size, 64), dtype=np.uint8)
                y = np.random.randint(0, 256, (batch_size, 64), dtype=np.uint8)
                
                start_time = time.time()
                loss, probs, h1 = model.step(x, y, lr=0.1)
                step_time = time.time() - start_time
                
                throughput = batch_size / step_time  # samples/sec
                
                results["tests"].append({
                    "name": f"batch_{batch_size}",
                    "status": "PASS",
                    "time": step_time,
                    "throughput": throughput,
                    "loss": float(loss)
                })
                
                # Performance cliff detection
                if len(results["tests"]) > 1:
                    prev_throughput = results["tests"][-2]["throughput"]
                    if throughput < prev_throughput * 0.5:  # 50% drop
                        results["warnings"] = results.get("warnings", [])
                        results["warnings"].append(f"Throughput cliff at batch_size={batch_size}")
                
            except Exception as e:
                results["tests"].append({
                    "name": f"batch_{batch_size}",
                    "status": "FAIL",
                    "error": str(e)
                })
                self.failure_modes.append(("batch_size", str(e)))
                break
                
        return results
    
    def stress_level_5_mathematical_stability(self):
        """Mathematical operations under extreme conditions"""
        print("=== STRESS LEVEL 5: MATHEMATICAL STABILITY ===")
        results = {"level": 5, "tests": [], "overall": "PASS"}
        
        try:
            # Test DEC operations with extreme values
            omega_large = np.array([1e6, -1e6, 1e6, -1e6])
            omega_small = np.array([1e-10, 1e-10, 1e-10, 1e-10])
            omega_mixed = np.array([1e6, 1e-10, -1e6, 1e-10])
            
            for name, omega in [("large", omega_large), ("small", omega_small), ("mixed", omega_mixed)]:
                try:
                    d2_result = d2_norm(omega)
                    results["tests"].append({
                        "name": f"dec_{name}",
                        "status": "PASS" if np.isfinite(d2_result) else "NUMERICAL_FAIL",
                        "d2_norm": float(d2_result)
                    })
                except Exception as e:
                    results["tests"].append({
                        "name": f"dec_{name}", 
                        "status": "FAIL",
                        "error": str(e)
                    })
                    
            # Test geometry with ill-conditioned matrices
            G_singular = np.array([[1, 2], [2, 4]])  # Singular matrix
            G_large_cond = np.array([[1, 1e-10], [1e-10, 1]])  # High condition number
            
            for name, G in [("singular", G_singular), ("ill_conditioned", G_large_cond)]:
                try:
                    torsion = torsion_norm(G)
                    curvature = curvature_comm_norm(G, np.eye(2))
                    
                    results["tests"].append({
                        "name": f"geometry_{name}",
                        "status": "PASS" if all(np.isfinite([torsion, curvature])) else "NUMERICAL_FAIL",
                        "torsion": float(torsion),
                        "curvature": float(curvature)
                    })
                except Exception as e:
                    results["tests"].append({
                        "name": f"geometry_{name}",
                        "status": "FAIL", 
                        "error": str(e)
                    })
                    
        except Exception as e:
            results["overall"] = "FAIL"
            results["error"] = str(e)
            self.failure_modes.append(("mathematical_stability", str(e)))
            
        return results
    
    def run_full_stress_test(self):
        """Execute all stress levels and generate adaptation recommendations"""
        print("🔥 STARTING ADAPTIVE STRESS TEST SEQUENCE 🔥")
        
        all_results = []
        
        # Execute stress levels progressively
        stress_functions = [
            self.stress_level_1_basic,
            self.stress_level_2_scale, 
            self.stress_level_3_sequence_length,
            self.stress_level_4_batch_size,
            self.stress_level_5_mathematical_stability
        ]
        
        for stress_func in stress_functions:
            result = stress_func()
            all_results.append(result)
            
            # Immediate failure analysis
            if result["overall"] == "FAIL":
                print(f"❌ FAILURE at {stress_func.__name__}")
                self.analyze_failure_preconditions(result)
                
        # Generate comprehensive report
        self.generate_adaptation_recommendations(all_results)
        return all_results
    
    def analyze_failure_preconditions(self, failure_result):
        """Analyze what led to the failure and suggest structural changes"""
        failure_analysis = {
            "timestamp": time.time(),
            "level": failure_result["level"],
            "error": failure_result.get("error", "Unknown"),
            "preconditions": [],
            "structural_recommendations": []
        }
        
        # Pattern matching for common failure modes
        error_str = str(failure_result.get("error", "")).lower()
        
        if "memory" in error_str:
            failure_analysis["preconditions"].extend([
                "Insufficient memory management",
                "Unbounded array growth",
                "No memory pooling or streaming"
            ])
            failure_analysis["structural_recommendations"].extend([
                "Implement gradient checkpointing",
                "Add memory-mapped data loading", 
                "Create streaming batch processor",
                "Add memory usage monitoring"
            ])
            
        if "time" in error_str or any(t.get("time", 0) > 1.0 for t in failure_result.get("tests", [])):
            failure_analysis["preconditions"].extend([
                "Computational complexity too high",
                "No optimization passes",
                "Inefficient numpy operations"
            ])
            failure_analysis["structural_recommendations"].extend([
                "Vectorize operations further", 
                "Implement computational graph optimization",
                "Add caching for repeated computations",
                "Profile and optimize hot paths"
            ])
            
        if "numerical" in error_str:
            failure_analysis["preconditions"].extend([
                "Numerical instability in core operations",
                "No stability safeguards", 
                "Missing normalization steps"
            ])
            failure_analysis["structural_recommendations"].extend([
                "Add numerical stability checks",
                "Implement adaptive precision",
                "Add normalization layers",
                "Use numerically stable algorithms"
            ])
            
        self.adaptation_log.append(failure_analysis)
        return failure_analysis
    
    def generate_adaptation_recommendations(self, all_results):
        """Generate system-wide structural adaptations based on stress test results"""
        print("\n📊 GENERATING STRUCTURAL ADAPTATION RECOMMENDATIONS")
        
        recommendations = {
            "immediate_fixes": [],
            "architectural_changes": [],
            "performance_optimizations": [],
            "reliability_improvements": []
        }
        
        # Analyze performance patterns
        has_memory_issues = any("memory" in str(r.get("error", "")).lower() for r in all_results if r["overall"] == "FAIL")
        has_speed_issues = any(t.get("time", 0) > 1.0 for r in all_results for t in r.get("tests", []))
        has_numerical_issues = any("numerical" in str(t.get("status", "")) for r in all_results for t in r.get("tests", []))
        
        if has_memory_issues:
            recommendations["architectural_changes"].extend([
                "Implement streaming data pipeline",
                "Add gradient accumulation for large batches",
                "Create model sharding system"
            ])
            
        if has_speed_issues:
            recommendations["performance_optimizations"].extend([
                "Implement JIT compilation with numba",
                "Add multi-threading for independent operations", 
                "Create computational graph optimization"
            ])
            
        if has_numerical_issues:
            recommendations["reliability_improvements"].extend([
                "Add numerical stability monitoring",
                "Implement adaptive numerical precision",
                "Create fallback algorithms for edge cases"
            ])
            
        # Save recommendations for implementation
        with open("logs/adaptation_recommendations.json", "w") as f:
            json.dump(recommendations, f, indent=2)
            
        return recommendations

def main():
    tester = AdaptiveStressTester({})
    results = tester.run_full_stress_test()
    
    print(f"\n🎯 STRESS TEST COMPLETE")
    print(f"Failure modes detected: {len(tester.failure_modes)}")
    print(f"Adaptation recommendations generated: logs/adaptation_recommendations.json")
    
    return results

if __name__ == "__main__":
    main()