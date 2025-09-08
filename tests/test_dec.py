# tests/test_dec.py
import numpy as np

from src.dec import (
    d0,
    d1,
    d2_norm,
    incidence_0_to_1,
    incidence_1_to_2,
    torsion_curvature,
)


def test_dec_identities():
    n = 3
    B = incidence_0_to_1(n)
    expected_B = np.array([[-1, 1, 0], [0, -1, 1], [1, 0, -1]])
    assert np.allclose(B, expected_B), "incidence_0_to_1 incorrect"

    C = incidence_1_to_2(n)
    assert np.allclose(C, np.ones((1, n))), "incidence_1_to_2 incorrect"

    f0 = np.linspace(0, 1, n)
    df0 = d0(f0)
    assert np.allclose(df0, B @ f0), "d0 incorrect"

    ddf0 = d1(df0)
    assert np.allclose(ddf0, C @ df0), "d1 incorrect"

    assert d2_norm(f0) < 1e-8, "d^2 not ~0"

    Gt = np.array([[0, 1], [0, 0.1]])
    Gp = np.array([[0, 0.5], [0, 0]])
    T, R = torsion_curvature(Gt, Gp)
    assert T > 0, "torsion not positive for asym"
    assert R / T < 20.0, "curvature/torsion ratio too large"
