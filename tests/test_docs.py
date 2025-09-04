# tests/test_dec.py
import sys, numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.dec import d_0_to_1, d_1_to_2, d2_norm, torsion_curvature
def test_dec_identities():
    f0 = np.linspace(0,1,33)
    if not (d2_norm(f0) < 1e-8):
        print("FAIL: d^2 not ~0"); sys.exit(1)
    Gt = np.array([[0,1],[0,0.1]])
    Gp = np.array([[0,0.5],[0,0]])
    T,R = torsion_curvature(Gt,Gp)
    if not (T>0): 
        print("FAIL: torsion not positive for asym"); sys.exit(1)
    if not (R/T < 20.0):
        print("FAIL: curvature/torsion ratio too large"); sys.exit(1)
    print("PASS")
if __name__=="__main__":
    test_dec_identities()
    print("PASS")
