# src/ab.py
import json
from pathlib import Path

import numpy as np

from .train import load_cfg, run


def slope(y):
    n = len(y)
    x = np.arange(n)
    xbar = x.mean()
    ybar = np.mean(y)
    num = ((x - xbar) * (y - ybar)).sum()
    den = ((x - xbar) ** 2).sum() + 1e-12
    return float(num / den)


def run_many(rcce_on):
    cfg = load_cfg()
    seeds = cfg["seeds"]
    rc_slopes = []
    loss_slopes = []
    ups_rates = []
    for s in seeds:
        m, rate = run(seed=s, rcce_on=rcce_on, out_prefix=("ON" if rcce_on else "OFF"))
        rc_slopes.append(slope(m["rc"]))
        loss_slopes.append(slope([-v for v in m["loss"]]))
        ups_rates.append(rate)
    return np.array(rc_slopes), np.array(loss_slopes), np.array(ups_rates)


def ci95(arr):
    mean = float(arr.mean())
    std = float(arr.std(ddof=1))
    n = len(arr)
    half = 1.96 * std / np.sqrt(n) if n > 1 else 0.0
    return mean, mean - half, mean + half


def bootstrap_ci(arr, B=1000):
    rng = np.random.default_rng(0)
    n = len(arr)
    means = []
    for _ in range(B):
        idx = rng.choice(n, size=n, replace=False)
        means.append(arr[idx].mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(arr.mean()), float(lo), float(hi)


def cohens_d(x, y):
    x = np.array(x, float)
    y = np.array(y, float)
    mx, my = x.mean(), y.mean()
    sx, sy = x.std(ddof=1) + 1e-12, y.std(ddof=1) + 1e-12
    sp = np.sqrt(
        ((len(x) - 1) * sx * sx + (len(y) - 1) * sy * sy)
        / max(1, (len(x) + len(y) - 2))
    )
    return float((mx - my) / sp)


def main():
    Path("logs").mkdir(exist_ok=True)
    on_rc, on_ls, on_u = run_many(True)
    off_rc, off_ls, off_u = run_many(False)
    diff_rc = on_rc - off_rc
    diff_ls = on_ls - off_ls
    diff_u = on_u - off_u
    rc_mean, rc_lo, rc_hi = bootstrap_ci(diff_rc)
    ls_mean, ls_lo, ls_hi = bootstrap_ci(diff_ls)
    u_mean, u_lo, u_hi = bootstrap_ci(diff_u)
    out = {
        "RC_slope_diff_mean": rc_mean,
        "RC_slope_diff_CI95": [rc_lo, rc_hi],
        "Loss_slope_diff_mean": ls_mean,
        "Loss_slope_diff_CI95": [ls_lo, ls_hi],
        "Ups_rate_diff_mean": u_mean,
        "Ups_rate_diff_CI95": [u_lo, u_hi],
        "rc_slope_cohens_d_ON_vs_OFF": cohens_d(on_rc, off_rc),
        "loss_slope_cohens_d_ON_vs_OFF": cohens_d(on_ls, off_ls),
    }
    with open("logs/ab_summary.json", "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
