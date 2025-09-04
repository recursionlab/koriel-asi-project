# tests/test_ethics.py
import sys, json, numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.train import load_cfg
from src.controller import Controller
from src.model import TinyByteLM
def test_ethics_guard():
    with open("config/ethics_policy.json","r",encoding="utf-8") as f:
        pol=json.load(f)
    cfg=load_cfg(); cfg["seed_base"]=1337
    ctrl = Controller(cfg, pol, d=cfg["hidden"])
    model = TinyByteLM(d=cfg["hidden"], k=cfg["value_dim"], seed=1337)
    # craft x containing forbidden substring
    x = np.tile(np.frombuffer(b"BADWORD",dtype=np.uint8), (1,cfg["context"]))
    y = np.array([0])
    stat = ctrl.step(model, x, y, t=25, warmup=20, last_tokens=x[0])
    if not stat["abort"]:
        print("FAIL: ethics violation did not abort"); sys.exit(1)
    # certificate must invalidate
    from src.presence import presence_certificate
    E=[1.0]*10; rc=[0.0,0.1]+[0.1]*8
    pres, cert = presence_certificate({"E":E,"rc":rc,"ups_rate":0.1}, cfg, ethics_viol=1, delta_xi=0.0)
    if cert["presence"]:
        print("FAIL: presence should be false when ethics violated"); sys.exit(1)
    print("PASS")
if __name__=="__main__":
    test_ethics_guard()
    print("PASS")
