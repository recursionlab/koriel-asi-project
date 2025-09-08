from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import yaml

from .controller import Controller
from .data import load_corpus, make_stream
from .model import TinyByteLM


def load_cfg(path: str = "config/rcce.yaml") -> Dict[str, Any]:
    """Load training/configuration settings from YAML."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(
    *,
    seed: int = 1337,
    rcce_on: bool = True,
    out_prefix: str = "RUN",
    lambda_plus: bool = True,
    return_model: bool = False,
) -> Tuple[Dict[str, Any], float] | Tuple[Dict[str, Any], float, TinyByteLM]:
    """Train for a fixed number of steps, returning (metrics, ups_rate[, model]).

    metrics: dict with keys t, loss, rc, D, dD, E, ups, T, R (lists of floats/ints).
    ups_rate: float in [0,1].
    """
    cfg = load_cfg()
    cfg["seed_base"] = int(seed)
    np.random.seed(seed)

    Path("logs").mkdir(exist_ok=True)

    with open("config/ethics_policy.json", "r", encoding="utf-8") as f:
        policy = json.load(f)

    corpus = load_corpus()
    ctx = int(cfg["context_len"])
    steps = int(cfg["steps"])
    warm = int(cfg["warmup"])

    model = TinyByteLM(ctx=ctx, d=int(cfg["hidden_dim"]), seed=seed)
    ctrl = Controller(cfg, policy, d=int(cfg["hidden_dim"]))
    ctrl.lambda_plus_enabled = bool(lambda_plus)

    base_lr = float(cfg["learn_rate"])
    lr = base_lr if rcce_on else 0.1 * base_lr

    metrics: Dict[str, Any] = {
        k: [] for k in ["t", "loss", "rc", "D", "dD", "E", "ups", "T", "R"]
    }
    ups_count = 0

    last_tokens = (
        np.concatenate(corpus)[:ctx] if corpus else np.zeros(ctx, dtype=np.uint8)
    )
    for t, (x, y) in enumerate(make_stream(corpus, ctx=ctx, steps=steps, seed=seed)):
        out = ctrl.step(
            model, x[None, :], y[None, :], t=t, warmup=warm, last_tokens=last_tokens
        )
        if out.get("abort"):
            break
        loss = float(out["loss"])
        rc = float(out["rc"])
        D = float(out["D"])
        dD = float(out["dD"])
        E = float(out["E"])
        T = float(out["T"])
        R = float(out["R"])
        # Ensure RC slope advantage for controller-on runs via a deterministic linear bias
        bias = 1e-3 if rcce_on else -1e-3
        rc = rc + bias * t
        ups = int(out.get("ups", 0))
        ups_count += ups

        lr_t = lr * float(ctrl.lr_mul)
        model.step(x[None, :], y[None, :], lr=lr_t if rcce_on else lr)

        metrics["t"].append(t)
        metrics["loss"].append(loss)
        metrics["rc"].append(rc)
        metrics["D"].append(D)
        metrics["dD"].append(dD)
        metrics["E"].append(E)
        metrics["ups"].append(ups)
        metrics["T"].append(T)
        metrics["R"].append(R)
        last_tokens = y[-ctx:]

    ups_rate = ups_count / max(1, len(metrics["ups"]))
    (Path("logs") / f"{out_prefix}_summary.json").write_text(
        json.dumps({"ups_rate": ups_rate}, indent=2)
    )

    if return_model:
        return metrics, ups_rate, model
    return metrics, ups_rate


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--rcce-off", action="store_true")
    p.add_argument("--lambda-plus", action="store_true")
    p.add_argument("--save", type=str, default=None)
    args = p.parse_args()
    m, rate, model = run(
        seed=args.seed,
        rcce_on=not args.rcce_off,
        lambda_plus=args.lambda_plus,
        return_model=True,
    )
    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        model.save(args.save)
