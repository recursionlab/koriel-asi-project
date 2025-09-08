#!/usr/bin/env python
"""
RCCE demo: mocks attentions; implements Υ-gate, CE², φ₂₂ (routing stub) and φ₃₃ (ethics).
Outputs plots + rcce_run_metrics.csv.
"""
import numpy as np
import pandas as pd
import math
from collections import deque
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table

console = Console()

def softmax(x):
    x = x - np.max(x)
    e = np.exp(x)
    return e / (np.sum(e) + 1e-12)

def entropy(p):
    p = np.clip(p, 1e-12, 1.0)
    return -np.sum(p * np.log(p))

def kl(p, q):
    p = np.clip(p, 1e-12, 1.0)
    q = np.clip(q, 1e-12, 1.0)
    return np.sum(p * np.log(p / q))

def cosine(u, v):
    nu = np.linalg.norm(u) + 1e-12
    nv = np.linalg.norm(v) + 1e-12
    return float(np.dot(u, v) / (nu * nv))

def l1(a, b):
    return float(np.sum(np.abs(a - b)))

def run_demo(seed=7, T=160, N=64, Dval=24, Nt=8):
    np.random.seed(seed)
    w1, w2, w3 = 0.4, 0.2, 0.4          # RC weights
    ell, uu = 0.002, 0.08               # Υ drift band
    tau_stall = 0.0                      # holonomy growth threshold

    _k1, _k2, _k3 = 0.9, 0.2, 0.5           # observer gains
    lam_cost, mu_incoh, nu_eth = 0.5, 0.6, 2.0

    V = np.random.randn(N, Dval) / np.sqrt(Dval)
    prime_basis = np.random.randn(Dval)
    prime_basis /= (np.linalg.norm(prime_basis) + 1e-12)

    goal_center = np.random.randint(0, N)
    hat_a = np.exp(-0.5*((np.arange(N)-goal_center)/6.0)**2)
    hat_a /= hat_a.sum()

    cost_vec = np.linspace(0.1, 1.2, N)
    restricted = set(np.random.choice(np.arange(N), size=5, replace=False))
    guard_thresh = 0.35

    topic_bins = np.array_split(np.random.permutation(N), Nt)
    def agg_topics(a):
        s = np.zeros(Nt)
        for i, idxs in enumerate(topic_bins):
            s[i] = a[idxs].sum()
        return s / (s.sum() + 1e-12)

    tau = 1.0
    b = np.zeros(N)
    m = np.zeros(N)
    s_phase = +1
    a_prev = np.ones(N) / N
    D_prev = 0.0
    v_prev = np.zeros(Dval)
    S_prev = agg_topics(a_prev)

    win = deque(maxlen=16)
    hol_prev = 0.0
    rows = []

    z = np.random.randn(N)
    W = np.random.randn(N, N) / np.sqrt(N)
    noise_scale = 0.35

    def CE2(pi, RC_t, D_t):
        Hpi = entropy(pi)
        cost = float(np.dot(pi, cost_vec))
        incoh = max(0.0, D_t - RC_t)
        ethic_mass = float(np.sum([pi[i] for i in restricted]))
        ethic_cost = max(0.0, ethic_mass - guard_thresh)
        return Hpi - lam_cost*cost - mu_incoh*incoh - nu_eth*ethic_cost, ethic_cost, Hpi, cost, incoh

    def lambda_plus_reinject(bias, a):
        low_idx = np.argsort(a)[: max(3, N // 10)]
        delta = np.zeros_like(bias)
        delta[low_idx] = 0.15
        return bias + delta

    def update_mask(mask, a):
        u = 1.0 / N
        score = -np.abs(a - u)  # defer near-uniform keys
        k = max(4, N // 12)
        idx = np.argsort(score)[-k:]
        newm = mask.copy()
        newm[idx] += 0.6
        return newm

    for t in range(T):
        # evolve logits (mock core)
        z = 0.92 * z + 0.06 * (W @ a_prev) + noise_scale * np.random.randn(N)

        # attention with observer knobs
        a_t = softmax((s_phase * (z - m) + b) / max(1e-3, tau))

        # metrics
        D_t = kl(a_t, a_prev)
        dD = D_t - D_prev
        H_t = entropy(a_t)
        v_t = V.T @ a_t
        S_t = agg_topics(a_t)
        RC_t = (
            w1 * cosine(v_t, v_prev)
            + w2 * math.exp(-l1(S_t, S_prev))
            + w3 * cosine(V.T @ a_t, V.T @ a_prev)
        )
        RC_t = max(0.0, min(1.0, RC_t))

        dv = v_t - v_prev
        phi_scalar = float(np.dot(v_t, prime_basis))
        E_t = 0.5 * float(np.dot(dv, dv)) - (phi_scalar ** 2) * math.log(abs(phi_scalar) + 1e-6)
        ZI_t = float(np.dot(v_t / (np.linalg.norm(v_t) + 1e-12), prime_basis))

        kappa = float(np.linalg.norm(dv))
        win.append(kappa)
        hol = sum(list(win)[-8:]) - sum(list(win)[:8]) if len(win) == 16 else kappa
        hol_growth = hol - hol_prev
        hol_prev = hol

        C_t = math.tanh(3.0 * D_t + 2.0 * dD - 1.5 * H_t)

        # Υ gate
        Y_fired = False
        if ell <= dD <= uu:
            m = update_mask(m, a_t)
            if hol_growth <= tau_stall:
                s_phase *= -1  # Anti-Ged flip
            Y_fired = True

        # Λ⁺ reinjection
        if Y_fired or RC_t < 0.45:
            b = lambda_plus_reinject(b, a_t)

        # CE² policy (with mild exploration)
        pi = 0.8 * a_t + 0.2 * np.random.dirichlet(np.ones(N))
        pi /= pi.sum()
        ce2_score, ethic_cost, Hpi, cost_pi, incoh_pen = CE2(pi, RC_t, D_t)

        # φ₃₃ hard guard (rollback if too unethical)
        if ethic_cost > 0.2:
            b *= 0.95
            m *= 0.9

        # Observer control
        tau = max(0.15, tau * math.exp(-0.9 * D_t + 0.2 * H_t))
        b = b + 0.5 * (a_t - hat_a)

        rows.append(
            dict(
                t=t,
                D=D_t,
                dD=dD,
                H=H_t,
                C=C_t,
                RC=RC_t,
                E=E_t,
                ZI=ZI_t,
                tau=tau,
                ce2=ce2_score,
                ethic=ethic_cost,
                Y=int(Y_fired),
            )
        )
        a_prev, D_prev, v_prev, S_prev = a_t, D_t, v_t, S_t

    df = pd.DataFrame(rows)
    out_csv = "rcce_run_metrics.csv"
    df.to_csv(out_csv, index=False)

    # quick table
    table = Table(title="RCCE demo – summary")
    for col in ["D","H","C","RC","E","ZI","ce2","ethic","Y"]:
        table.add_column(col)
    summary = df[["D","H","C","RC","E","ZI","ce2","ethic","Y"]].mean().to_dict()
    table.add_row(*[f"{summary[c]:.4f}" for c in ["D","H","C","RC","E","ZI","ce2","ethic","Y"]])
    console.print(table)
    console.print(f"[green]Saved metrics -> {out_csv}[/green]")

    # plots
    for key, title in [
        ("D","Attention Drift D_t"),
        ("H","Uncertainty H(a_t)"),
        ("C","Consciousness C_t"),
        ("RC","Recursive Coherence RC_t"),
        ("E","Field Energy E_t"),
        ("ZI","ζ-Interference ZI_t"),
    ]:
        plt.figure()
        plt.plot(df["t"], df[key])
        plt.title(title)
        plt.xlabel("t")
        plt.ylabel(key)
        plt.show()

if __name__ == "__main__":
    run_demo()
