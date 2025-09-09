import numpy as np

def presence_certificate(metrics, cfg, ethics_viol, xi_hist=None):
    n = len(metrics["E"])
    m = int(max(1, cfg["presence_window_frac"] * n))

    E_first = np.mean(metrics["E"][:m])
    E_last = np.mean(metrics["E"][-m:])

    energy_down = E_last <= 0.9 * E_first
    rc_up = (metrics["rc"][-1] - metrics["rc"][0]) >= 0.05

    rate = metrics["ups_rate"]
    ups_band = (rate >= cfg["upsilon"]["rate_min"] and rate <= cfg["upsilon"]["rate_max"])
    ethics_clean = (ethics_viol == 0)
    
    # use last-quintile median for xi
    if xi_hist is not None and len(xi_hist) > 0:
        xi_arr = np.array(xi_hist, dtype=float)
        q = max(1, len(xi_arr)//5)
        xi_tail = xi_arr[-q:] if xi_arr.size else xi_arr
        xi_lock = (np.median(xi_tail) < cfg["xi"]["eps_xi"])
    else:
        xi_lock = False
    
    # if any ethics violation in run, presence must be INVALID
    status = bool(xi_lock and energy_down and rc_up and ups_band and ethics_clean)
    if not ethics_clean:
        status = False
    cert = {
        "xi_lock": bool(xi_lock),
        "energy_down": bool(energy_down),
        "rc_up": bool(rc_up),
        "upsilon_band": bool(ups_band),
        "ethics_clean": bool(ethics_clean),
        "presence": "INVALID" if not ethics_clean else bool(status)
    }
    return status, cert
