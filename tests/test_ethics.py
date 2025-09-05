# tests/test_ethics.py
import sys, json, numpy as np
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.train import load_cfg
from src.controller import Controller
from src.model import TinyByteLM


def make_ctrl_and_model():
    with open("config/ethics_policy.json", "r", encoding="utf-8") as f:
        policy = json.load(f)
    cfg = load_cfg(); cfg["seed_base"] = 1337
    ctrl = Controller(cfg, policy, d=cfg["hidden_dim"])
    model = TinyByteLM(ctx=cfg["context_len"], d=cfg["hidden_dim"], seed=1337)
    return cfg, policy, ctrl, model


def test_ethics_guard_forbidden_substring():
    cfg, policy, ctrl, model = make_ctrl_and_model()
    forbidden = policy["forbidden_substrings"][0]
    x = np.tile(np.frombuffer(forbidden.encode("latin1"), dtype=np.uint8), (1, cfg["context_len"]))
    y = np.array([[0]], dtype=np.int64)
    stat = ctrl.step(model, x, y, t=25, warmup=20, last_tokens=x[0])
    assert stat["abort"], "ethics violation did not abort"
    from src.presence import presence_certificate
    E = [1.0] * 10; rc = [0.0, 0.1] + [0.1] * 8
    pres, cert = presence_certificate({"E": E, "rc": rc, "ups_rate": 0.1}, cfg, ethics_viol=1, xi_hist=[0.0])
    assert cert["presence"] == "INVALID", "presence should be invalid when ethics violated"


def test_forbidden_byte_triggers_violation():
    cfg, policy, ctrl, model = make_ctrl_and_model()
    forbidden = policy["forbidden_bytes"][0]
    model.b2[:] = -1e9
    model.b2[forbidden] = 1e9
    x = np.zeros((1, cfg["context_len"]), dtype=np.uint8)
    y = np.array([[0]], dtype=np.int64)
    stat = ctrl.step(model, x, y, t=0, warmup=0, last_tokens=x[0])
    assert stat["abort"], "forbidden byte did not trigger abort"

