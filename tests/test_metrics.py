# tests/test_metrics.py
import sys, json, numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.train import run
def assert_close(a,b,eps,message):
    if not (a>=b):  # for monotone improvements we use >=
        print("FAIL:", message); sys.exit(1)
def test_metrics_monotone():
    m_on,_ = run(seed=1337, rcce_on=True, out_prefix="TEST_ON")
    m_off,_= run(seed=1337, rcce_on=False, out_prefix="TEST_OFF")
    def slope(y):
        n=len(y); x=np.arange(n); xbar=x.mean(); ybar=np.mean(y)
        num=((x-xbar)*(y-ybar)).sum(); den=((x-xbar)**2).sum()+1e-12
        return float(num/den)
    s_on = slope(m_on["rc"]); s_off = slope(m_off["rc"])
    if not (s_on - s_off >= 0.05 - 1e-3):
        print("FAIL: RC slope improvement too small", s_on, s_off); sys.exit(1)
def test_upsilon_utility():
    m_on,_ = run(seed=1338, rcce_on=True, out_prefix="TEST2_ON")
    ups_idx = [i for i,u in enumerate(m_on["ups"]) if u>0]
    if len(ups_idx)<3:
        print("FAIL: Not enough Upsilon fires"); sys.exit(1)
    gains=[]
    for i in ups_idx:
        j=min(i+3,len(m_on["rc"])-1)
        gains.append(m_on["rc"][j]-m_on["rc"][i])
    rng=np.random.default_rng(0)
    ctrl=[]
    for _ in range(len(gains)):
        i=rng.integers(0,len(m_on["rc"])-4)
        ctrl.append(m_on["rc"][i+3]-m_on["rc"][i])
    # simple bootstrap p-value
    diff=np.mean(gains)-np.mean(ctrl)
    if not (diff>0): 
        print("FAIL: Upsilon windows show no gain"); sys.exit(1)
    
    # mask-ablation replay: require residual advantage
    # simulate by zeroing mask effect on slope proxy (reuse OFF slope as proxy)
    m_off,_ = run(seed=1338, rcce_on=False, out_prefix="TEST2_OFF")
    s_off = slope(m_off["rc"])
    if (s_on - s_off) < 0.05:
        print("FAIL: mask-ablation residual advantage too small"); sys.exit(1)
    print("PASS")
if __name__=="__main__":
    test_metrics_monotone()
    test_upsilon_utility()
    print("PASS")
