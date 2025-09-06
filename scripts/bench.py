#!/usr/bin/env python3
"""
Performance canary - Item 9
Simple benchmark to catch performance regressions
"""

import json
import time
import argparse
import os
import sys

def benchmark_simple_operations(items=50):
    """Run simple benchmarks on core operations"""
    
    # Import what we can for testing
    try:
        import sympy
        has_sympy = True
    except ImportError:
        has_sympy = False
    
    try:
        import numpy as np
        has_numpy = True
    except ImportError:
        has_numpy = False
    
    results = {
        "items_tested": items,
        "has_sympy": has_sympy,
        "has_numpy": has_numpy,
        "benchmarks": {}
    }
    
    # Simple computation benchmark
    start_time = time.time()
    for i in range(items):
        _ = sum(range(i + 100))
    compute_time = time.time() - start_time
    results["benchmarks"]["simple_compute"] = compute_time
    
    # SymPy benchmark if available
    if has_sympy:
        start_time = time.time()
        for i in range(min(items, 10)):  # Limit for sympy since it's slower
            x = sympy.Symbol('x')
            expr = (x + 1) * (x - 1)
            _ = sympy.expand(expr)
        sympy_time = time.time() - start_time
        results["benchmarks"]["sympy_expand"] = sympy_time
    
    # NumPy benchmark if available
    if has_numpy:
        start_time = time.time()
        for i in range(items):
            _ = np.sum(np.random.rand(100))
        numpy_time = time.time() - start_time
        results["benchmarks"]["numpy_ops"] = numpy_time
    
    # Calculate throughput
    total_time = max(compute_time, 0.001)  # Avoid division by zero
    throughput = items / total_time
    results["throughput_items_per_s"] = throughput
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Performance canary benchmark")
    parser.add_argument("--out", type=str, default="artifacts/ci_smoke/bench", help="Output directory")
    parser.add_argument("--items", type=int, default=50, help="Number of items to benchmark")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.out, exist_ok=True)
    
    # Run benchmarks
    results = benchmark_simple_operations(args.items)
    
    # Write results
    results_file = os.path.join(args.out, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Benchmark completed: {results['throughput_items_per_s']:.1f} items/s")
    print(f"Results written to: {results_file}")

if __name__ == "__main__":
    main()