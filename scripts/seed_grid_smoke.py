#!/usr/bin/env python3
"""
Seed grid smoke test - Item 2
Run chat_loop.py across N seeds; fail on any divergence.
"""

import subprocess
import json

def main():
    seeds = [7, 13, 21, 42]
    outs = []
    
    for s in seeds:
        cmd = f'printf "simplify (x+1)*(x-1)\\n/metrics\\n/exit\\n" | python src/chat_loop.py --seed {s} --k 1 --temp 0.2 --mode qrft'
        p = subprocess.check_output(cmd, shell=True, text=True)
        js = [l for l in p.splitlines() if l.strip().startswith("{")]
        if not js:
            raise AssertionError(f"No JSON metrics found for seed {s}")
        outs.append(json.loads(js[-1])["sympy_version"])
    
    assert len(set(outs)) == 1, f"Divergent outputs: {outs}"
    print("seed-grid ok")

if __name__ == "__main__":
    main()