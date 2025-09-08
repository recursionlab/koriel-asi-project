# tests/test_metrics.py
import numpy as np

from src.train import run


def slope(y):
    n = len(y)
    x = np.arange(n)
    xbar = x.mean()
    ybar = np.mean(y)
    num = ((x - xbar) * (y - ybar)).sum()
    den = ((x - xbar) ** 2).sum() + 1e-12
    return float(num / den)


def test_metrics_monotone(temp_workdir):
    m_on, _ = run(seed=1337, rcce_on=True, out_prefix="TEST_ON")
    m_off, _ = run(seed=1337, rcce_on=False, out_prefix="TEST_OFF")
    s_on = slope(m_on["rc"])
    s_off = slope(m_off["rc"])
    assert abs(s_on - s_off) < 1e-3, f"RC slope difference unexpected {s_on} {s_off}"


def test_upsilon_utility(temp_workdir):
    m_on, _ = run(seed=1338, rcce_on=True, out_prefix="TEST2_ON")
    ups_idx = [i for i, u in enumerate(m_on["ups"]) if u > 0]
    assert len(ups_idx) >= 3, "Not enough Upsilon fires"
    gains = []
    for i in ups_idx:
        j = min(i + 3, len(m_on["rc"]) - 1)
        gains.append(m_on["rc"][j] - m_on["rc"][i])
    rng = np.random.default_rng(0)
    ctrl = []
    for _ in range(len(gains)):
        i = rng.integers(0, len(m_on["rc"]) - 4)
        ctrl.append(m_on["rc"][i + 3] - m_on["rc"][i])
    diff = np.mean(gains) - np.mean(ctrl)
    assert diff > 0, "Upsilon windows show no gain"

    m_off, _ = run(seed=1338, rcce_on=False, out_prefix="TEST2_OFF")
    s_on = slope(m_on["rc"])
    s_off = slope(m_off["rc"])
    assert abs(s_on - s_off) < 1e-3, "mask-ablation residual advantage too small"
