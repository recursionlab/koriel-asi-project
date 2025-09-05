# tests/test_dec.py
import sys, numpy as np
from src.dec import (
    incidence_0_to_1,
    incidence_1_to_2,
    d0,
    d1,
    d2_norm,
    torsion_curvature,
)

def test_dec_identities():
    n = 3
    B = incidence_0_to_1(n)
    expected_B = np.array([[-1,1,0],[0,-1,1],[1,0,-1]])
    if not np.allclose(B, expected_B):
        print("FAIL: incidence_0_to_1 incorrect"); sys.exit(1)

    C = incidence_1_to_2(n)
    if not np.allclose(C, np.ones((1,n))):
        print("FAIL: incidence_1_to_2 incorrect"); sys.exit(1)

    f0 = np.linspace(0,1,n)
    df0 = d0(f0)
    if not np.allclose(df0, B @ f0):
        print("FAIL: d0 incorrect"); sys.exit(1)

    ddf0 = d1(df0)
    if not np.allclose(ddf0, C @ df0):
        print("FAIL: d1 incorrect"); sys.exit(1)

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
