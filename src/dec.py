# src/dec.py
import numpy as np

def incidence_0_to_1(n):
    B = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        j = (i+1) % n
        B[i, i] -= 1.0
        B[i, j] += 1.0
    return B

def incidence_1_to_2(n):
    C = np.ones((1, n), dtype=np.float64)
    return C

def d0(omega0):
    n = omega0.shape[0]
    return incidence_0_to_1(n) @ omega0

def d1(omega1):
    return incidence_1_to_2(omega1.shape[0]) @ omega1

def d(omega):
    if omega.ndim==1: return d0(omega)
    return d1(omega)

def wedge(a, b):
    return np.outer(a, b)

def d2_norm(omega0):
    return np.linalg.norm(d1(d0(omega0)))

def torsion_norm(Gamma):
    T = 0.5*(Gamma - Gamma.T)
    return np.linalg.norm(T)

def curvature_comm_norm(G1, G2):
    K = G1 @ G2 - G2 @ G1
    return np.linalg.norm(0.5*(K - K.T))

def torsion_curvature(Gamma_curr, Gamma_prev):
    T = torsion_norm(Gamma_curr)
    R = curvature_comm_norm(Gamma_curr, Gamma_prev)
    return T, R