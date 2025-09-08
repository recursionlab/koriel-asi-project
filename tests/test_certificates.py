# tests/test_certificate.py
from src.presence import presence_certificate
from src.train import load_cfg


def test_certificate():
    cfg = load_cfg()
    # all good
    E = [1.0] * 10 + [0.5] * 10
    rc = [0.0] + [0.06] * 19
    pres, cert = presence_certificate(
        {"E": E, "rc": rc, "ups_rate": 0.1}, cfg, ethics_viol=0, xi_hist=[0.0]
    )
    assert pres, "presence should be true"
    # fail one guard -> must be false (AND only)
    pres2, cert2 = presence_certificate(
        {"E": E, "rc": rc, "ups_rate": 0.9}, cfg, ethics_viol=0, xi_hist=[0.0]
    )
    assert not pres2, "OR-logic detected"
