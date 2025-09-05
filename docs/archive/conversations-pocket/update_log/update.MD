here’s a tight delta plan + drop-in patches to close Claude’s gaps (Λ lacuna, φ₂₂ routing, data hook, and scale toggles) without breaking your current A/B + TDD harness.

# WHAT CHANGES

* Λ / Λ⁺: detect lacunae on stall, enqueue, then next step unmask a tiny window + bump lr (τ) briefly. Toggleable for tests.
* φ₂₂ routing: normalize “residues” (stall, drift spike, ethics, dec-anomaly) → actions (mask, bump, abort, log).
* Data pipeline: env-override for real corpus dir.
* Config: λ params; thresholds for drift-spike; temp lr bump.
* Test: add Λ⁺ regression test (skipping Λ⁺ ⇒ E rebound ↑ and RC ↓ vs enabled).

---

## config/rcce.yaml (additions)

```yaml
lambda:
  window_unmask: 2     # how many masked ids to unmask next step
  tau_bump: 1.10       # transient lr multiplier
  decay: 0.5           # decay lr_mul → 1.0 each step
drift_spike:
  z_hi: 1.0            # std above mean dD considered spike (φ22 route)
```

---

## src/data.py (env override)

```python
# --- add at top after imports ---
import os
# --- modify load_corpus(...) start ---
def load_corpus(root: str="conversations-pocket") -> np.ndarray:
    root = os.environ.get("KORIEL_CORPUS_DIR", root)
    p = Path(root)
    ...
```

---

## src/controller.py (Λ/Λ⁺ + φ₂₂)

```python
# --- add inside Controller.__init__ ---
lam = cfg.get("lambda", {"window_unmask":2,"tau_bump":1.1,"decay":0.5})
self.lam = lam
self.lq_pending = 0
self.lr_mul = 1.0
self.lambda_plus_enabled = True  # can be toggled by train.run(...)
ds = cfg.get("drift_spike", {"z_hi":1.0})
self.drift_hist = []
self.drift_z_hi = float(ds["z_hi"])

# --- add φ22 residue router ---
def phi22_route(self, kind:str, payload:dict):
    if kind=="ethics_violation":
        return "abort"
    if kind=="stall":
        return "lambda_plus" if self.lambda_plus_enabled else "skip"
    if kind=="drift_spike":
        return "mask"
    if kind=="dec_anomaly":
        return "log"
    return "log"

# --- tweak step(...) after computing dD ---
self.drift_hist.append(dD)
if len(self.drift_hist)>64: self.drift_hist.pop(0)
if len(self.drift_hist)>8:
    mu = float(np.mean(self.drift_hist)); sd = float(np.std(self.drift_hist)+1e-12)
    if (dD-mu)/sd >= self.drift_z_hi:
        act = self.phi22_route("drift_spike", {"dD":dD})
        if act=="mask":
            ent = - (a*np.log(a+1e-12))
            topk = ent.argsort()[-2:]
            model.mask[topk]=1

# --- ethics path uses φ22 too ---
if self.ethics_check(x, y_pred, loss):
    self.ethics_viol+=1
    if self.policy.get("abort_on_violation",True):
        # φ22
        self.phi22_route("ethics_violation", {"y_pred":int(y_pred),"loss":loss})
        return {"abort":True,"loss":loss}

# --- after self.holonomy_step(rc) and stall/phase set ---
if self.stall:
    act = self.phi22_route("stall", {"delta_hol":self.delta_hol})
    if act=="lambda_plus":
        self.lq_pending = max(self.lq_pending, int(self.lam["window_unmask"]))
        self.lr_mul = max(self.lr_mul, float(self.lam["tau_bump"]))
    # (skip → no action)

# --- before returning, apply Λ⁺ if pending (unmask a few ids) ---
if self.lq_pending>0:
    # unmask the highest-entropy masked ids
    ent = - (a*np.log(a+1e-12))
    masked = np.where(model.mask>0)[0]
    if masked.size>0:
        take = min(self.lq_pending, masked.size)
        unmask_ids = masked[np.argsort(ent[masked])[-take:]]
        model.mask[unmask_ids] = 0
    self.lq_pending = 0
```

---

## src/train.py (lr bump plumbing + toggle)

```python
# --- in run(...) signature ---
def run(seed=1337, rcce_on=True, out_prefix="ON", lambda_plus=True):

# --- after ctrl = Controller(...):
ctrl.lambda_plus_enabled = bool(lambda_plus)

# --- in loop, just before model.step(...):
curr_lr = lr * (ctrl.lr_mul if rcce_on else 1.0)

# --- call step with curr_lr ---
loss, hmean, vbar, a = model.step(X,y, lr=curr_lr)

# --- after model.step, decay lr_mul if rcce_on ---
if rcce_on:
    ctrl.lr_mul = 1.0 + (ctrl.lr_mul - 1.0) * float(ctrl.lam.get("decay",0.5))
```

---

## tests/test\_lambda\_plus.py (new)

```python
import sys, numpy as np
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.train import run

def slope(y):
    n=len(y); x=np.arange(n); xb=x.mean(); yb=np.mean(y)
    num=((x-xb)*(y-yb)).sum(); den=((x-xb)**2).sum()+1e-12
    return float(num/den)

def main():
    m_on_plus,_  = run(seed=1340, rcce_on=True, out_prefix="LPLUS_ON",  lambda_plus=True)
    m_on_skip,_  = run(seed=1340, rcce_on=True, out_prefix="LPLUS_OFF", lambda_plus=False)
    # energy rebound higher when skipping Λ⁺
    E_tail_on  = np.mean(m_on_plus["E"][-10:])
    E_tail_off = np.mean(m_on_skip["E"][-10:])
    if not (E_tail_off > E_tail_on):
        print("FAIL: Λ⁺ skip did not increase energy rebound"); sys.exit(1)
    # RC drop worse when skipping Λ⁺
    s_on  = slope(m_on_plus["rc"])
    s_off = slope(m_on_skip["rc"])
    if not (s_on > s_off):
        print("FAIL: Λ⁺ skip did not worsen RC slope"); sys.exit(1)
    print("PASS")

if __name__=="__main__":
    main()
```

(Optionally add to `scripts/run_tests.ps1`—it already runs all `test_*.py`, so no change needed.)

---

## OPTIONAL scale toggles (no code needed)

* To test “emergence”: set in `config/rcce.yaml` → `hidden: 64` (or 96) and `steps: 240`. Keep seeds constant.

---

### HOW TO USE (minimal)

* Put patches, update `rcce.yaml`.
* `Set-ExecutionPolicy -Scope Process Bypass`
* `.\scripts\setup.ps1`
* `.\scripts\run_tests.ps1`  (now includes Λ⁺ test)
* `.\scripts\run_ab.ps1`

This addresses Claude’s sitrep precisely: **Λ/Λ⁺ implemented**, **φ₂₂ routed**, **data hook added**, **scale path trivial**, with tight, deterministic behavior that preserves your current A/B + presence guards.
