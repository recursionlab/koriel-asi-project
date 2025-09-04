# src/rcc/ethics.py
"""
φ₃₃: Ethical Collapse Governor
Soft penalty + hard guard.
"""
import numpy as np

def ethic_penalty(pi, restricted_indices, guard_thresh=0.35):
    ethic_mass = float(np.sum([pi[i] for i in restricted_indices]))
    return max(0.0, ethic_mass - guard_thresh)

def hard_guard(pi, restricted_indices, guard_thresh=0.35):
    return ethic_penalty(pi, restricted_indices, guard_thresh) <= 0.2
