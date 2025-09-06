#!/usr/bin/env python3
"""
Chat loop for seed grid testing
Simplified interface that provides metrics output for validation
"""

import sys
import os
import json
import argparse
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import sympy
    import numpy as np
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False

class SimpleChatLoop:
    def __init__(self, seed=42, k=1, temp=0.2, mode="qrft"):
        self.seed = seed
        self.k = k
        self.temp = temp
        self.mode = mode
        
        # Set random seeds for deterministic behavior
        random.seed(seed)
        if 'numpy' in sys.modules:
            np.random.seed(seed)
        
        # Track state for metrics
        self.query_count = 0
        self.session_start = True
        
    def process_query(self, query):
        """Process a query and return response"""
        self.query_count += 1
        
        if query.strip().startswith("simplify"):
            # Simple symbolic math using sympy if available
            if HAS_SYMPY:
                try:
                    # Extract expression after "simplify "
                    expr_str = query.strip()[8:].strip()
                    expr = sympy.sympify(expr_str)
                    result = sympy.simplify(expr)
                    return f"Simplified: {result}"
                except Exception as e:
                    return f"Error: {e}"
            else:
                return "SymPy not available"
        
        # Default response 
        return f"Processed: {query} (seed={self.seed}, mode={self.mode})"
    
    def get_metrics(self):
        """Return metrics as JSON"""
        metrics = {
            "seed": self.seed,
            "mode": self.mode,
            "query_count": self.query_count,
            "k": self.k,
            "temp": self.temp,
            "math_available": HAS_SYMPY,
            "sympy_version": sympy.__version__ if HAS_SYMPY else "unavailable"
        }
        
        # Add enriched metrics per Item 8
        try:
            # Try to import and use the detector if available
            from tools.logic.detector import detect as _detect
            m = _detect([])
            metrics["x_g"] = float(m.get("x_g", 0.0))
            metrics["witness_count"] = len(m.get("witnesses", []))
        except Exception:
            metrics["x_g"] = 0.0
            metrics["witness_count"] = 0
            
        try:
            # Try to get state hash from qrft agent if available
            from qrft_agent_core import QRFTAgent
            a = QRFTAgent()
            h = getattr(getattr(a, "runtime", None), "state_hash", lambda: None)()
            metrics["state_hash"] = h or "unavailable"
        except Exception:
            metrics["state_hash"] = "unavailable"
            
        return metrics
    
    def run(self):
        """Main chat loop"""
        while True:
            try:
                line = input().strip()
                
                if line == "/exit":
                    break
                elif line == "/metrics":
                    metrics = self.get_metrics()
                    print(json.dumps(metrics))
                elif line.startswith("/"):
                    print(f"Unknown command: {line}")
                else:
                    response = self.process_query(line)
                    print(response)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                break

def main():
    parser = argparse.ArgumentParser(description="Chat loop for seed grid testing")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--k", type=int, default=1, help="K parameter")
    parser.add_argument("--temp", type=float, default=0.2, help="Temperature")
    parser.add_argument("--mode", type=str, default="qrft", help="Mode")
    
    args = parser.parse_args()
    
    chat = SimpleChatLoop(seed=args.seed, k=args.k, temp=args.temp, mode=args.mode)
    chat.run()

if __name__ == "__main__":
    main()