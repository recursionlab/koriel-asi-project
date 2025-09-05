# src/train.py
"""Training entry point for TinyByteLM.

This module exposes two public helpers:

``load_cfg`` – read the YAML configuration file used across tests and
``run`` – perform a short training run returning collected metrics.  The
original file mixed runtime logic inside ``load_cfg`` and ended with an
unfinished ``if __name__ == '__main__'`` block which raised an
``IndentationError`` during test collection.  The implementation here is a
clean, test‑friendly rewrite that keeps side effects contained inside
``run`` and ``main``.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
from tqdm import tqdm

from .controller import Controller
from .data import load_corpus, make_stream
from .model import TinyByteLM

try:  # Optional dependency used only when ``main`` is executed directly
    import yaml
except Exception:  # pragma: no cover - yaml is part of requirements
    yaml = None


def load_cfg(path: str = "config/rcce.yaml") -> Dict:
    """Load training configuration from ``path``.

    The helper lives in ``src.train`` so tests can easily pull in the same
    configuration that the training script uses.
    """

    if yaml is None:  # pragma: no cover - defensive check
        raise RuntimeError("pyyaml is required to load configuration")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(
    *,
    seed: int = 1337,
    rcce_on: bool = True,
    corpus_dir: str | None = None,
    dataset: str | None = None,
    out_prefix: str = "RUN",
    lambda_plus: bool = False,
    return_model: bool = False,
) -> Tuple[Dict[str, list], float, TinyByteLM | None]:
    """Execute a training loop and collect metrics.

    Parameters mirror the expectations of the test-suite.  When ``return_model``
    is ``True`` the trained model instance is included in the returned tuple.
    """

    cfg = load_cfg()
    cfg["seed_base"] = seed
    np.random.seed(seed)

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    with open("config/ethics_policy.json", "r", encoding="utf-8") as f:
        policy = json.load(f)

    data = load_corpus(
        "conversations-pocket" if corpus_dir is None else corpus_dir, dataset=dataset
    )
    ctx = cfg["context_len"]
    steps = cfg["steps"]
    warm = cfg["warmup"]

    model = TinyByteLM(ctx=ctx, d=cfg["hidden_dim"], seed=seed)
    ctrl = Controller(cfg, policy, d=cfg["hidden_dim"])
    ctrl.lambda_plus_enabled = bool(lambda_plus)

    metrics: Dict[str, list] = {
        "t": [],
        "loss": [],
        "rc": [],
        "D": [],
        "dD": [],
        "E": [],
        "ups": [],
        "T": [],
        "R": [],
    }

    last_tokens = np.concatenate(data)[:ctx] if data else np.zeros(ctx, dtype=np.uint8)
    lr = cfg["learn_rate"]
    gen: Iterable[Tuple[np.ndarray, np.ndarray]] = make_stream(data, ctx, steps, seed)

    for t, (X, y) in enumerate(tqdm(gen, total=steps, disable=True), start=1):
        # Reshape to batch dimension 1 for the TinyByteLM interface.
        X = X.reshape(1, -1)
        y = y.reshape(1, -1)

        if rcce_on:
            stat = ctrl.step(model, X, y, t, warm, last_tokens)
            if stat["abort"]:
                last_tokens = X[0]
                continue
            curr_lr = lr * ctrl.lr_mul
            loss, hmean, vbar, a = model.step(X, y, lr=curr_lr)
            rc, D, dD = stat["rc"], stat["D"], stat["dD"]
            E, ups, T, R = stat["E"], stat["ups"], stat["T"], stat["R"]
        else:
            curr_lr = lr
            loss, hmean, vbar, a = model.step(X, y, lr=curr_lr)
            from .controller import cos, kl, wasserstein1_proxy

            S = ctrl.symbolic_vec(last_tokens)
            rc = (
                cfg["rc_weights"][0] * cos(hmean, ctrl.v_prev)
                if ctrl.v_prev is not None
                else 0.0
            )
            rc += cfg["rc_weights"][1] * math.exp(
                -wasserstein1_proxy(S, ctrl.S_prev) if ctrl.S_prev is not None else 0.0
            )
            rc += (
                cfg["rc_weights"][2] * cos(vbar, ctrl.Vbar_prev)
                if ctrl.Vbar_prev is not None
                else 0.0
            )
            rc /= sum(cfg["rc_weights"])

            ctrl.v_prev, ctrl.S_prev, ctrl.Vbar_prev = hmean, S, vbar
            D = kl(a, ctrl.a_prev) if ctrl.a_prev is not None else 0.0
            ctrl.a_prev = a
            dD = D - ctrl.D_hist[-1]
            ctrl.D_hist.append(D)
            ctrl.dD_hist.append(dD)
            E = ctrl.E.update(loss)
            ctrl.rc_hist.append(rc)
            ups, T, R = 0, 0.0, 0.0

        if rcce_on:
            # decay Λ⁺ learning-rate multiplier
            ctrl.lr_mul = 1.0 + (ctrl.lr_mul - 1.0) * float(ctrl.lam.get("decay", 0.5))

        metrics["t"].append(t)
        metrics["loss"].append(loss)
        metrics["rc"].append(rc)
        metrics["D"].append(D)
        metrics["dD"].append(dD)
        metrics["E"].append(E)
        metrics["ups"].append(ups)
        metrics["T"].append(T)
        metrics["R"].append(R)

        last_tokens = X[0]

    # Persist metrics for reproducibility/debugging
    csvp = logs_dir / f"metrics_{out_prefix}_{seed}.csv"
    with csvp.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(list(metrics.keys()))
        for i in range(len(metrics["t"])):
            w.writerow([metrics[k][i] for k in metrics.keys()])

    ups_rate = float(sum(metrics["ups"]) / max(1, len(metrics["ups"])))

    if return_model:
        return metrics, ups_rate, model
    return metrics, ups_rate


def main() -> None:  # pragma: no cover - exercised via CLI
    """CLI front-end for manual experiments."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Train TinyByteLM and optionally benchmark",
    )
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument(
        "--rcce-off", action="store_true", help="Disable RCCE controller"
    )
    parser.add_argument(
        "--save", type=str, default=None, help="Save checkpoint to path"
    )
    parser.add_argument("--eval-task", choices=["mmlu", "arc"], default=None)
    parser.add_argument(
        "--eval-subset", type=str, default=None, help="Subset name for benchmark"
    )
    parser.add_argument(
        "--eval-limit", type=int, default=None, help="Limit number of eval examples"
    )
    parser.add_argument(
        "--lambda-plus", action="store_true", help="Enable Lambda+ during training"
    )

    args = parser.parse_args()

    metrics, ups_rate, model = run(
        seed=args.seed,
        rcce_on=not args.rcce_off,
        out_prefix="RUN",
        lambda_plus=args.lambda_plus,
        return_model=True,
    )

    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        assert model is not None
        model.save(args.save)

    if args.eval_task:
        if args.eval_task == "mmlu":
            from benchmarks.mmlu import evaluate_mmlu

            acc = evaluate_mmlu(
                model,
                subset=args.eval_subset or "abstract_algebra",
                limit=args.eval_limit,
            )
        else:
            from benchmarks.arc import evaluate_arc

            acc = evaluate_arc(
                model, dataset=args.eval_subset or "ARC-Easy", limit=args.eval_limit
            )
        print(json.dumps({"benchmark": args.eval_task, "accuracy": acc}))


if __name__ == "__main__":  # pragma: no cover
    main()
