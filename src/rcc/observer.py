# src/rcc/observer.py
"""
Observer/controller surface for RCCE.
Controls: temperature (tau), bias (b), mask (m), phase (s) via Υ.
"""
from dataclasses import dataclass
import numpy as np

@dataclass
class ObserverState:
    tau: float
    b: np.ndarray
    m: np.ndarray
    s: int = +1

def update_mask(mask: np.ndarray, a: np.ndarray, top_k: int) -> np.ndarray:
    u = 1.0/len(a)
    score = -np.abs(a - u)          # defer near-uniform keys
    idx = np.argsort(score)[-top_k:]
    newm = mask.copy()
    newm[idx] += 0.6
    return newm

def control_step(obs: ObserverState, a, hat_a, D, H, dD, holonomy_growth,
                 ell=0.002, uu=0.08, tau_stall=0.0, k_focus=0.9, k_entropy=0.2, k_prior=0.5):
    Y = False
    if ell <= dD <= uu:
        obs.m = update_mask(obs.m, a, max(4, len(a)//12))
        if holonomy_growth <= tau_stall:
            obs.s *= -1
        Y = True
    # Λ⁺ reinjection is handled by caller (needs access to priors & policy)
    # update tau & bias
    obs.tau = max(0.15, obs.tau * np.exp(-k_focus*D + k_entropy*H))
    obs.b = obs.b + k_prior*(a - hat_a)
    return obs, Y
