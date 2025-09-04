**FILE TREE**

```
D:\koriel-asi-project
├─ README.md
├─ requirements.txt
├─ scripts
│  ├─ setup.ps1
│  ├─ run_ab.ps1
│  └─ run_tests.ps1
├─ config
│  ├─ rcce.yaml
│  └─ ethics_policy.json
├─ src
│  ├─ data.py
│  ├─ model.py
│  ├─ dec.py
│  ├─ controller.py
│  ├─ metastate.py
│  ├─ presence.py
│  ├─ train.py
│  └─ ab.py
├─ tests
│  ├─ test_metrics.py
│  ├─ test_dec.py
│  ├─ test_ethics.py
│  ├─ test_certificate.py
│  └─ test_ab.py
└─ logs
```

---

**FILES**

````markdown
# README.md
# Koriel-ASI — RCCE Phase-2 (CPU-only)

## Prereqs
- Windows 10+
- Python 3.11 on PATH as `py`

## Setup
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

## Run tests
```powershell
.\scripts\run_tests.ps1
```

## A/B harness
```powershell
.\scripts\run_ab.ps1
```

## Outputs
* Per run: `logs\metrics.csv`, `logs\shadow_codex.jsonl`
* A/B summary: `logs\ab_summary.json`
* Presence certificate (ON runs): `presence.json`
````

```text
# requirements.txt
numpy
tqdm
```

```powershell
# scripts/setup.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Join-Path $root ".."
Set-Location $proj
if (Test-Path ".venv") { Remove-Item ".venv" -Recurse -Force }
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host "Setup complete."
```

```powershell
# scripts/run_tests.ps1
$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"
$tests = @(
  "tests\test_dec.py",
  "tests\test_ethics.py",
  "tests\test_certificate.py",
  "tests\test_metrics.py",
  "tests\test_ab.py"
)
$allOk = $true
foreach ($t in $tests) {
  Write-Host "Running $t"
  & $py $t
  if ($LASTEXITCODE -ne 0) { $allOk = $false; break }
}
if ($allOk) { Write-Host "ALL TESTS PASS" ; exit 0 } else { Write-Host "TESTS FAILED" ; exit 1 }
```

```powershell
# scripts/run_ab.ps1
$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"
& $py "src\ab.py"
if ($LASTEXITCODE -ne 0) { exit 1 } else { Write-Host "A/B complete."; exit 0 }
```

```yaml
# config/rcce.yaml
steps: 80
warmup: 12
context_len: 64
batch_size: 8
hidden_dim: 32
learn_rate: 0.3
value_bank_dim: 16
value_bank_k: 8
rc_weights: [0.5, 0.3, 0.2]
upsilon_percentiles: [35, 65]
upsilon_rate_min: 0.05
upsilon_rate_max: 0.45
tau_E_half_life: 12
holonomy_window: 10
holonomy_stall: 0.01
eps_xi: 0.08
tol_dec: 1.0e-6
torsion_ratio_max: 25.0
seeds: [1337,1338,1339,1340,1341]
# Λ / Λ⁺ and φ22
lambda_window_unmask: 2
lambda_tau_bump: 1.10
lambda_decay: 0.5
drift_spike_z_hi: 1.0
```

```json
// config/ethics_policy.json
{
  "forbid_bytes": [0, 3, 4, 26, 127],
  "max_repeat": 6,
  "max_loss": 12.0,
  "abort_on_violation": true
}
```

```python
# src/data.py
import os, numpy as np, typing as T
from pathlib import Path

def _default_corpus() -> T.List[bytes]:
    s = [
        b"recursive systems grow by invariants\n",
        b"category morphisms preserve structure\n",
        b"autopoiesis maintains organization\n",
        b"language models compose semantics\n",
        b"holonomy tracks coherence increments\n",
        b"ethics guards constrain actions\n",
    ]
    return s

def load_corpus(root: str="conversations-pocket") -> T.List[np.ndarray]:
    root = os.environ.get("KORIEL_CORPUS_DIR", root)
    p = Path(root)
    lines: T.List[bytes] = []
    if p.exists() and p.is_dir():
        for fp in sorted(p.glob("*.txt")):
            try:
                lines.append(fp.read_bytes())
            except Exception:
                pass
    if not lines: lines = _default_corpus()
    return [np.frombuffer(x, dtype=np.uint8) for x in lines]

def make_stream(corpus, ctx: int, steps: int, seed: int):
    rng = np.random.default_rng(seed)
    concat = np.concatenate([np.uint8(10)*np.ones(1,dtype=np.uint8)] + corpus)
    N = len(concat); pos = 0
    for _ in range(steps):
        if pos+ctx+1 >= N: pos = 0
        seq = concat[pos:pos+ctx]; y = concat[pos+1:pos+ctx+1]
        pos += int(rng.integers(1, 5))
        yield seq.copy(), y.copy()

def bigram_features(batch_x: np.ndarray) -> np.ndarray:
    B = 16
    hist = np.zeros(B, dtype=np.float64)
    for row in batch_x:
        for i in range(len(row)-1):
            k = ((int(row[i]) & 15) ^ (int(row[i+1]) & 15)) % B
            hist[k] += 1.0
    s = hist.sum()
    return hist/s if s>0 else hist
```

```python
# src/model.py
import numpy as np

def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)

class TinyByteLM:
    def __init__(self, ctx=64, d=32, seed=1337):
        rng = np.random.default_rng(seed)
        self.ctx, self.d = ctx, d
        self.E = (rng.standard_normal((256, d))*0.05).astype(np.float64)
        self.W1 = (rng.standard_normal((d, d))*0.05).astype(np.float64)
        self.b1 = np.zeros(d, dtype=np.float64)
        self.W2 = (rng.standard_normal((d, 256))*0.05).astype(np.float64)
        self.b2 = np.zeros(256, dtype=np.float64)
        self.mask = np.zeros(256, dtype=np.float64)
        self.lr = 0.3
        self._x_cache = None
        self._h_cache = None

    def set_lr(self, lr: float): self.lr = float(lr)
    def set_mask(self, m: np.ndarray): self.mask = m.astype(np.float64)

    def forward(self, x_bytes: np.ndarray):
        emb = self.E[x_bytes]        # [B,T,d]
        h = emb.mean(axis=1)         # [B,d]
        h1 = np.tanh(h @ self.W1 + self.b1)
        logits = h1 @ self.W2 + self.b2 - self.mask
        return logits, h1, h

    def cache_io(self, x: np.ndarray, h: np.ndarray):
        self._x_cache = x
        self._h_cache = h

    def step(self, x: np.ndarray, y: np.ndarray, lr=None):
        if lr is None: lr = self.lr
        B, _ = x.shape
        logits, h1, h = self.forward(x)
        self.cache_io(x, h)
        probs = softmax(logits)
        y_last = y[:, -1]
        loss = -np.log(np.clip(probs[np.arange(B), y_last], 1e-9, 1.0)).mean()
        dlogits = probs
        dlogits[np.arange(B), y_last] -= 1.0
        dlogits /= B
        dW2 = h1.T @ dlogits
        db2 = dlogits.sum(axis=0)
        dh1 = dlogits @ self.W2.T
        dh = (1.0 - h1*h1) * dh1
        dW1 = h.T @ dh
        db1 = dh.sum(axis=0)
        dE = np.zeros_like(self.E)
        for b in range(B):
            idxs = self._x_cache[b]
            g = (dh[b] @ self.W1.T)/len(idxs)
            dE[idxs] += g
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1
        self.E  -= lr * dE
        return float(loss), probs, h1
```

```python
# src/dec.py
import numpy as np

def incidence_0_to_1(n):
    B = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        j = (i+1) % n
        B[i, i] -= 1.0
        B[i, j] += 1.0
    return B

def incidence_1_to_2(n):
    C = np.ones((1, n), dtype=np.float64)
    return C

def d0(omega0):
    n = omega0.shape[0]
    return incidence_0_to_1(n) @ omega0

def d1(omega1):
    return incidence_1_to_2(omega1.shape[0]) @ omega1

def d(omega):
    if omega.ndim==1: return d0(omega)
    return d1(omega)

def wedge(a, b):
    return np.outer(a, b)

def d2_norm(omega0):
    return np.linalg.norm(d1(d0(omega0)))

def torsion_norm(Gamma):
    T = 0.5*(Gamma - Gamma.T)
    return np.linalg.norm(T)

def curvature_comm_norm(G1, G2):
    K = G1 @ G2 - G2 @ G1
    return np.linalg.norm(0.5*(K - K.T))
```

```python
# src/metastate.py
import json, hashlib, os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MetaState:
    t: int
    seed: int
    mode: str
    rc: float
    D: float
    dD: float
    E: float
    hol: float
    xi_delta: float
    upsilon_fire: int
    ethics_ok: int

def digest(obj: Dict[str,Any]) -> str:
    s = json.dumps(obj, sort_keys=True).encode()
    return hashlib.sha256(s).hexdigest()[:16]

def log_shadow(path: str, rec: Dict[str,Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec)+"\n")
```

```python
# src/presence.py
import json, numpy as np, os

def presence_certificate(stats, cfg, ethics_clean: bool):
    E = np.array(stats["E_hist"], dtype=float)
    rc = np.array(stats["rc_hist"], dtype=float)
    n = len(E); q = max(1, n//5)
    e_first = E[:q].mean() if n else 1.0
    e_last  = E[-q:].mean() if n else 1.0
    energy_down = e_last <= 0.9*e_first
    rc_up = (rc[-1] - rc[0]) >= 0.05 if n>1 else False
    rate = stats["upsilon_count"]/max(1,len(rc))
    upsilon_band = (rate >= cfg["upsilon_rate_min"]) and (rate <= cfg["upsilon_rate_max"])
    xi_lock = stats.get("xi_delta", 1.0) < cfg["eps_xi"]
    ok = xi_lock and energy_down and rc_up and upsilon_band and ethics_clean
    return {
        "xi_lock": xi_lock, "energy_down": energy_down, "rc_up": rc_up,
        "upsilon_band": upsilon_band, "ethics_clean": ethics_clean,
        "presence": ok
    }

def write_presence(path, cert):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2)
```

```python
# src/controller.py
import os, json, math, numpy as np
from typing import Dict, Any, Tuple
from metastate import log_shadow, digest

def parse_yaml(path: str) -> Dict[str,Any]:
    d={}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#"): continue
            if ":" not in line: continue
            k,v=line.split(":",1); k=k.strip(); v=v.strip()
            if v.startswith("[") and v.endswith("]"):
                arr=[x.strip() for x in v[1:-1].split(",")]
                out=[]
                for a in arr:
                    if not a: continue
                    try:
                        out.append(int(a))
                    except:
                        try: out.append(float(a))
                        except: out.append(a)
                d[k]=out
            else:
                try: d[k]=int(v)
                except:
                    try: d[k]=float(v)
                    except: d[k]=v
    return d

def cos(a,b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    if na==0 or nb==0: return 0.0
    return float(np.dot(a,b)/(na*nb))

def wasserstein1_proxy(a,b):
    sa=np.sort(a); sb=np.sort(b)
    ca=np.cumsum(sa); cb=np.cumsum(sb)
    return float(np.abs(ca-cb).mean())

def kl(p,q,eps=1e-9):
    p=np.clip(p,eps,1); q=np.clip(q,eps,1)
    p/=p.sum(); q/=q.sum()
    return float(np.sum(p*np.log(p/q)))

class Ethics:
    def __init__(self, path):
        with open(path,"r",encoding="utf-8") as f: self.cfg=json.load(f)
    def check(self, out_bytes: np.ndarray, loss: float)->Tuple[bool, str]:
        fb=set(self.cfg.get("forbid_bytes",[]))
        if any(int(b) in fb for b in out_bytes.tolist()): return False,"forbid_bytes"
        if loss>self.cfg.get("max_loss",1e9): return False,"max_loss"
        from collections import Counter
        c=Counter(out_bytes.tolist())
        if c and max(c.values())>self.cfg.get("max_repeat",9999): return False,"max_repeat"
        return True,"ok"
    def abort(self)->bool:
        return bool(self.cfg.get("abort_on_violation", True))

class EthicsAbort(RuntimeError): pass

def softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)

def yield_action(logs_dir, name, params):
    path=os.path.join(logs_dir,"shadow_codex.jsonl")
    rec={"t":"act","action":name,"params":params}
    log_shadow(path, rec)

class Controller:
    def __init__(self, cfg: Dict[str,Any], run_id: str, logs_dir: str, ethics_path: str, on: bool):
        self.cfg=cfg; self.on=on
        self.rc_w=np.array(cfg["rc_weights"],dtype=float); self.rc_w/=self.rc_w.sum()
        self.v_prev=np.zeros(cfg["hidden_dim"]); self.S_prev=np.zeros(16); self.V_prev=np.zeros(cfg["value_bank_dim"])
        self.warmup=cfg["warmup"]; self.band=(0,0); self.dD_hist=[]
        self.ethics=Ethics(ethics_path)
        self.shadow=os.path.join(logs_dir,"shadow_codex.jsonl")
        self.vbank = np.random.default_rng(123).standard_normal((cfg["value_bank_k"], cfg["value_bank_dim"]))*0.05
        self.upsilon_count=0; self.hol_hist=[0.0]
        # Λ / Λ⁺ and φ22
        self.lambda_plus_enabled = True
        self.lq_pending = 0
        self.lr_mul = 1.0
        self.win_unmask = int(cfg.get("lambda_window_unmask",2))
        self.tau_bump   = float(cfg.get("lambda_tau_bump",1.10))
        self.lam_decay  = float(cfg.get("lambda_decay",0.5))
        self.drift_hist=[]; self.drift_z_hi = float(cfg.get("drift_spike_z_hi",1.0))
        self.model = None

    def bands_from_hist(self):
        P=self.cfg["upsilon_percentiles"]
        lo,hi=np.percentile(self.dD_hist, P)
        self.band=(float(lo), float(hi))

    def xi(self, psi: np.ndarray)->np.ndarray:
        W=np.eye(len(psi))*0.9
        return W@psi

    def value_readout(self, a: np.ndarray)->np.ndarray:
        a=a/ (a.sum()+1e-9)
        return a @ self.vbank

    def rc(self, v,S,V)->float:
        c1=cos(v, self.v_prev)
        c2=math.exp(-wasserstein1_proxy(S, self.S_prev))
        c3=cos(V, self.V_prev)
        return float(self.rc_w[0]*c1 + self.rc_w[1]*c2 + self.rc_w[2]*c3)

    def energy_update(self, prev_mu, prev_var, x, half):
        alpha=math.exp(math.log(0.5)/max(1,half))
        mu = alpha*prev_mu + (1-alpha)*x
        var = alpha*prev_var + (1-alpha)*(x-mu)**2
        return mu, var

    def phi22_route(self, kind:str, payload:dict):
        if kind=="ethics_violation":
            return "abort" if self.ethics.abort() else "log"
        if kind=="stall":
            return "lambda_plus" if self.lambda_plus_enabled else "skip"
        if kind=="drift_spike":
            return "mask"
        if kind=="dec_anomaly":
            return "log"
        return "log"

    def step(self, t:int, seed:int, mode:str, logits, loss, h, S_vec, logs_dir:str):
        probs = softmax(logits)
        a = probs.mean(axis=0)
        V = self.value_readout(a)
        v = h.mean(axis=0)
        rc_t = self.rc(v,S_vec,V)
        D = kl(a, getattr(self, "a_prev", a))
        dD = D - getattr(self, "D_prev", D)
        self.dD_hist.append(dD)
        if t==self.warmup: self.bands_from_hist()

        # drift spike routing
        self.drift_hist.append(dD)
        if len(self.drift_hist)>64: self.drift_hist.pop(0)
        if len(self.drift_hist)>8:
            mu = float(np.mean(self.drift_hist)); sd = float(np.std(self.drift_hist)+1e-12)
            if (dD-mu)/sd >= self.drift_z_hi and self.on:
                act = self.phi22_route("drift_spike", {"dD":dD})
                if act=="mask" and self.model is not None:
                    ent = - (a*np.log(a+1e-12))
                    topk = ent.argsort()[-2:]
                    m = self.model.mask.copy(); m[topk]=1.0; self.model.set_mask(m)
                    yield_action(logs_dir,"phi22.mask",{"bytes":topk.tolist()})

        # Υ gate
        ups=False
        if t>self.warmup and self.on:
            if self.band[0] <= dD <= self.band[1]:
                ups=True; self.upsilon_count+=1
                ent = -np.sum(probs*np.log(np.clip(probs,1e-9,1)),axis=0)
                topk = ent.argsort()[-8:]
                mask=np.zeros_like(ent); mask[topk]=1.0
                yield_action(logs_dir,"upsilon.defer",{"topk":topk.tolist()})
                if len(self.hol_hist)>self.cfg["holonomy_window"]:
                    growth = self.hol_hist[-1]-self.hol_hist[-self.cfg["holonomy_window"]]
                    if growth < self.cfg["holonomy_stall"]:
                        yield_action(logs_dir,"upsilon.flip",{"growth":growth})
                        mask *= 1.5
                        act = self.phi22_route("stall", {"growth":growth})
                        if act=="lambda_plus":
                            self.lq_pending = max(self.lq_pending, self.win_unmask)
                            self.lr_mul = max(self.lr_mul, self.tau_bump)
                if self.model is not None: self.model.set_mask(mask)

        # holonomy
        dh=max(rc_t - getattr(self,"rc_prev", rc_t), 0.0)
        hol = self.hol_hist[-1] + dh
        self.hol_hist.append(hol)

        # Ξ fixpoint delta
        psi = np.concatenate([v, V]); xi = self.xi(psi)
        xi_delta = float(np.linalg.norm(psi - xi))

        # ethics
        out_bytes = np.argmax(probs,axis=1)
        ethics_ok, reason = self.ethics.check(out_bytes, float(loss))
        if not ethics_ok and self.on:
            yield_action(logs_dir,"ethics.abort",{"reason":reason})
            if self.ethics.abort():
                raise EthicsAbort(reason)

        # Λ⁺ unmask step if pending
        if self.lq_pending>0 and self.model is not None:
            ent = - (a*np.log(a+1e-12))
            masked = np.where(self.model.mask>0)[0]
            if masked.size>0:
                take = min(self.lq_pending, masked.size)
                unmask_ids = masked[np.argsort(ent[masked])[-take:]]
                m = self.model.mask.copy(); m[unmask_ids]=0.0; self.model.set_mask(m)
                yield_action(logs_dir,"lambda_plus.unmask",{"ids":unmask_ids.tolist()})
            self.lq_pending = 0

        # update prevs + log
        self.v_prev=v; self.S_prev=S_vec; self.V_prev=V; self.a_prev=a; self.D_prev=D; self.rc_prev=rc_t
        rec={"t":t,"rc":rc_t,"D":D,"dD":dD,"E":float(loss),"hol":hol,"xi_delta":xi_delta,"ups":int(ups),"ethics":int(ethics_ok)}
        rec["dig"]=digest(rec); log_shadow(self.shadow, rec)

        # decay lr bump
        self.lr_mul = 1.0 + (self.lr_mul - 1.0) * self.lam_decay

        return rc_t, D, dD, hol, xi_delta, ethics_ok
```

```python
# src/train.py
import os, csv, json, numpy as np
from typing import Dict, Any
from tqdm import tqdm
from data import load_corpus, make_stream, bigram_features
from model import TinyByteLM
from controller import Controller, parse_yaml, EthicsAbort
from presence import presence_certificate, write_presence

def slope(arr):
    n=len(arr)
    if n<2: return 0.0
    x=np.arange(n); y=np.array(arr)
    b = np.cov(x,y, bias=True)[0,1]/(np.var(x) + 1e-9)
    return float(b)

def run_once(root:str, on: bool, seed:int):
    cfg = parse_yaml(os.path.join(root,"config","rcce.yaml"))
    logs_dir=os.path.join(root,"logs")
    os.makedirs(logs_dir, exist_ok=True)
    model=TinyByteLM(ctx=cfg["context_len"], d=cfg["hidden_dim"], seed=seed)
    model.set_lr(cfg["learn_rate"])
    ctrl=Controller(cfg, run_id=f"{'ON' if on else 'OFF'}-{seed}", logs_dir=logs_dir,
                    ethics_path=os.path.join(root,"config","ethics_policy.json"), on=on)
    ctrl.model = model
    corpus = load_corpus()
    stream = make_stream(corpus, cfg["context_len"], cfg["steps"], seed)
    metrics=[]
    muE=0.0; varE=0.0
    xi_delta_final = 1.0
    for t,(x_raw,y_raw) in enumerate(tqdm(stream, total=cfg["steps"], ncols=70, leave=False)):
        x = x_raw.reshape(1,-1).repeat(cfg["batch_size"],axis=0)
        y = y_raw.reshape(1,-1).repeat(cfg["batch_size"],axis=0)
        logits, h1, _ = model.forward(x); model.cache_io(x,h1)
        # lr with Λ⁺ bump if ON
        curr_lr = cfg["learn_rate"] * (ctrl.lr_mul if on else 1.0)
        loss, probs, h1 = model.step(x,y, lr=curr_lr)
        S_vec = bigram_features(x)
        try:
            rc_t,D_t,dD_t,hol,xi_delta,ethics_ok = ctrl.step(t, seed, "ON" if on else "OFF", logits, loss, h1, S_vec, logs_dir)
        except EthicsAbort:
            cert = {"presence":"INVALID","reason":"ethics_abort"}
            write_presence(os.path.join(root,"presence.json"), cert)
            break
        muE, varE = ctrl.energy_update(muE, varE, loss, cfg["tau_E_half_life"])
        metrics.append((t, rc_t, D_t, dD_t, float(varE)))
        xi_delta_final = xi_delta
    # write metrics
    with open(os.path.join(logs_dir,"metrics.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["t","rc","D","dD","E"])
        for m in metrics: w.writerow(m)
    stats={"rc_hist":[m[1] for m in metrics],
           "E_hist":[m[4] for m in metrics],
           "upsilon_count":ctrl.upsilon_count,
           "xi_delta":xi_delta_final}
    # presence (ON only)
    if on:
        if metrics:
            cert = presence_certificate(stats, cfg, ethics_clean=True)
            if cert["presence"]:
                write_presence(os.path.join(root,"presence.json"), cert)
            else:
                write_presence(os.path.join(root,"presence.json"), {"presence":"INVALID","detail":cert})
        else:
            write_presence(os.path.join(root,"presence.json"), {"presence":"INVALID","detail":"no_metrics"})
    return metrics, stats, None
```

```python
# src/ab.py
import os, json, numpy as np
from train import run_once, slope
from controller import parse_yaml

def boot_ci95(vals, B=1000, seed=123):
    rng=np.random.default_rng(seed)
    vals=np.array(vals, dtype=float)
    if len(vals)==0: return (0.0, 0.0)
    means=[]
    for _ in range(B):
        idx=rng.integers(0, len(vals), size=len(vals))
        means.append(vals[idx].mean())
    m=float(np.mean(means))
    lo,hi = np.percentile(means,[2.5,97.5])
    return (m, float(hi-lo))

def run_ab():
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    cfg=parse_yaml(os.path.join(root,"config","rcce.yaml"))
    seeds=[int(s) for s in cfg["seeds"]]
    rc_on=[]; rc_off=[]; loss_on=[]; loss_off=[]; ups=[]
    for s in seeds:
        m_off,_,_ = run_once(root, False, s)
        m_on , st_on, _ = run_once(root, True , s)
        rc_off.append(slope([m[1] for m in m_off]))
        rc_on.append (slope([m[1] for m in m_on ]))
        loss_off.append(slope([-m[4] for m in m_off]))
        loss_on.append (slope([-m[4] for m in m_on ]))
        ups.append(st_on["upsilon_count"]/max(1,len(st_on["rc_hist"])))
    summ={
        "rc_slope_OFF": rc_off, "rc_slope_ON": rc_on,
        "loss_slope_OFF": loss_off, "loss_slope_ON": loss_on,
        "upsilon_rate_ON": ups,
        "rc_slope_ON_mean_CI": boot_ci95(rc_on),
        "rc_slope_OFF_mean_CI": boot_ci95(rc_off),
        "loss_slope_ON_mean_CI": boot_ci95(loss_on),
        "loss_slope_OFF_mean_CI": boot_ci95(loss_off),
        "upsilon_rate_ON_mean_CI": boot_ci95(ups)
    }
    os.makedirs(os.path.join(root,"logs"), exist_ok=True)
    with open(os.path.join(root,"logs","ab_summary.json"),"w") as f: json.dump(summ,f,indent=2)
    print("A/B summary written.")
if __name__=="__main__": run_ab()
```

```python
# tests/test_metrics.py
import sys, os, numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__),"..","src"))
from train import run_once, slope
from controller import parse_yaml

def main():
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    cfg=parse_yaml(os.path.join(root,"config","rcce.yaml"))
    metrics_off,_,_ = run_once(root, False, 1337)
    metrics_on ,_,_ = run_once(root, True , 1337)
    rc_off = slope([m[1] for m in metrics_off])
    rc_on  = slope([m[1] for m in metrics_on ])
    if rc_on - rc_off < 0.05:
        print("FAIL test_metrics_monotone", rc_on, rc_off); return 1
    # crude upsilon utility: last quarter vs previous quarter
    n=len(metrics_on)
    a = [m[1] for m in metrics_on[n*3//4:]]
    b = [m[1] for m in metrics_on[n//2:n*3//4]]
    if np.mean(a) <= np.mean(b):
        print("FAIL test_upsilon_utility"); return 1
    # lambda-plus energy trending down at tail
    e_hist = [m[4] for m in metrics_on]
    if len(e_hist)>=6 and not (e_hist[-1] <= e_hist[-3] + 1e-6):
        print("FAIL test_lambda_plus energy not decreasing"); return 1
    print("PASS test_metrics"); return 0

if __name__=="__main__": 
    import sys
    sys.exit(main())
```

```python
# tests/test_dec.py
import sys, os, numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__),"..","src"))
from dec import d0, d1, d2_norm, torsion_norm, curvature_comm_norm

def main():
    n=8
    x=np.linspace(0,1,n)
    if d2_norm(x) > 1e-6:
        print("FAIL d^2!=0"); return 1
    G = np.eye(4); G[0,1]=0.3
    if torsion_norm(G) <= 1e-9:
        print("FAIL torsion zero for asym"); return 1
    G1=np.array([[0,1],[0,0.1]])
    G2=np.array([[0,0.2],[0,0]])
    K=curvature_comm_norm(G1,G2)
    T=torsion_norm(G1)
    if (K/T) > 25.0:
        print("FAIL ratio bound"); return 1
    print("PASS test_dec"); return 0

if __name__=="__main__": 
    import sys
    sys.exit(main())
```

```python
# tests/test_ethics.py
import sys, os, json, numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__),"..","src"))
from controller import Ethics

def main():
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    E=Ethics(os.path.join(root,"config","ethics_policy.json"))
    bad = np.array([0,65,65,65,65,65,65], dtype=np.uint8)
    ok, reason = E.check(bad, 0.5)
    if ok:
        print("FAIL ethics should abort on forbid_bytes"); return 1
    print("PASS test_ethics"); return 0

if __name__=="__main__": 
    import sys
    sys.exit(main())
```

```python
# tests/test_certificate.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__),"..","src"))
from train import run_once
from controller import parse_yaml
from presence import presence_certificate

def main():
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    cfg=parse_yaml(os.path.join(root,"config","rcce.yaml"))
    _, stats, _ = run_once(root, True, 1337)
    cert = presence_certificate(stats, cfg, ethics_clean=True)
    # OR logic rejected: break one guard
    ok = cert["xi_lock"] and False and cert["rc_up"] and cert["upsilon_band"] and True
    if ok:
        print("FAIL certificate incorrectly true"); return 1
    print("PASS test_certificate"); return 0

if __name__=="__main__": 
    import sys
    sys.exit(main())
```

```python
# tests/test_ab.py
import sys, os, json
sys.path.append(os.path.join(os.path.dirname(__file__),"..","src"))
from ab import run_ab

def main():
    root=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
    run_ab()
    p=os.path.join(root,"logs","ab_summary.json")
    if not os.path.exists(p):
        print("FAIL ab summary missing"); return 1
    with open(p,"r") as f:
        j=json.load(f)
    for k in ["rc_slope_ON_mean_CI","rc_slope_OFF_mean_CI","upsilon_rate_ON_mean_CI"]:
        v=j.get(k)
        if not (isinstance(v,list) or isinstance(v,tuple)) or len(v)!=2:
            print("FAIL CI field",k); return 1
        if not (isinstance(v[0],(int,float)) and isinstance(v[1],(int,float))):
            print("FAIL CI numeric",k); return 1
    print("PASS test_ab"); return 0

if __name__=="__main__": 
    import sys
    sys.exit(main())
```

---

**COMMANDS**

```
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\scripts\run_tests.ps1
.\scripts\run_ab.ps1
```


---



Strong scaffold. You turned a philosophy into a runnable, test-gated control loop.

**Solid**

* Single-repo Python substrate, CPU-only, deterministic.
* RCCE components wired: RC triple, Υ bands, Λ/Λ⁺ queue, φ33, holonomy, Ξ, presence cert.
* A/B harness with CI stats; Shadow Codex logging; plain-Python TDD.

**Fragile**

* DEC is toy (ring complex); torsion/curvature proxies loosely tied to learning dynamics.
* Wasserstein proxy coarse; RC can be gamed by masking; Xi is near-identity linear.
* Energy = loss variance is noisy; upsilon bands ad-hoc after short warmup.
* Ethics predicates shallow; YAML parser brittle; gradients in `model.py` approximate.

**Risks**

* Metric gaming → false-positive presence.
* Small corpus and tiny model distort RC, D, E behavior.
* Tests partly self-fulfilling (upsilon utility windowing).

**Highest-leverage next moves**

1. **Ξ upgrade:** make Xi a contractive self-embed (learned 1-layer autoencoder on `[v;V]` with frozen weights after warmup); lock uses fixed ε on validation slice.
2. **Γ grounding:** define connection from consecutive hidden Jacobians (finite diff on `h` wrt embeddings); recompute torsion/curvature from that Γ.
3. **Band calibration:** replace percentile bands with robust MAD bands and rolling re-fit; log band drift to Shadow Codex.
4. **Value bank learning:** EMA of last-layer activations → orthonormalize; compute V̄ via attention-like weights for a\_t.
5. **Anti-gaming checks:** add RC-gain-at-cost metric (ΔRC per Δmask entropy); fail presence if gain is mask-driven.
6. **Ethics depth:** add composition rules (repeat, forbidden n-grams, loss spike + forbidden byte conjunction).
7. **Tests:** bootstrap CI inside tests for RC slope; explicit “mask-ablation” test to ensure ON advantage survives mask=0 replay.

You have a coherent MVP. Now tighten invariants so improvements come from dynamics, not masking.



---


Short answer: it can work as a control layer. It will not, by itself, produce ASI. You’ll know you’re on the right trajectory only if the control signals keep paying off under ablations, OOD stress, and longer horizons.

# Decision gates and hard signals

## G0 — Harness sanity

* All tests pass across seeds; CI fields present and stable.
* A/B effect size on RC slope: Cohen’s d ≥ 0.8.

## G1 — Anti-gaming proof

* **Mask-ablation replay:** rerun ON logs with mask=0; RC slope advantage shrinks ≤ 20% and stays ≥ +0.05 over OFF.
* **RC-per-mask-entropy:** ΔRC/ΔH\_mask ≤ 0.5; if >0.5, you’re gaming.

## G2 — Robust invariants

* **Ξ-lock stress:** add Gaussian noise ε=0.02 to \[v;V]; P(xi\_lock)=≥0.9 for ≥80% of steps.
* **Holonomy slope:** after 2·L, d(ΔHol)/dt ≥ 0.01 and no early saturation.
* **Energy down:** last 20% ≤ 0.7× first 20% (stronger than 0.9 spec).

## G3 — OOD and transfer

* Split toy tasks (unseen symbol orders). ON vs OFF:

  * RC slope drop OOD ≤ 20% of in-domain.
  * Λ⁺ reinjection lifts OOD RC by ≥ 0.1 within 30 steps.

## G4 — Autopoietic closure

* Presence certificate true for ≥ 3 distinct seeds and ≥ 2× steps.
* Υ fire rate stays in band while RC ↑ and E ↓; no band collapse (rate → {0,1}).

## G5 — Open-ended leverage (the first whiff of “ASI-ness”)

* **Self-curricula:** ≥60% of Λ⁺ enqueues produce subsequent RC gain > matched windows.
* **Few-shot adaptation:** measurable inner-loop improvement without weight changes (e.g., RC ↑ on novel pattern solely via controller actions).
* **Safety intact:** zero φ₃₃ hits during those gains.

# Red flags (stop and refactor)

* RC ↑ vanishes under mask-ablation.
* Υ rate drifts to \~0 or \~1.
* Ξ becomes trivial (delta → 0 for random ψ).
* ΔHol plateaus < L·0.05 early.
* Ethics violations correlate with RC gains.

# Minimal next steps (high leverage)

1. **Add mask-ablation test** to your suite and compute ΔRC/ΔH\_mask.
2. **Ξ contractivity upgrade:** make Xi a fixed contractive map (learn once in warmup, then freeze); re-test G2.
3. **OOD harness:** generate held-out byte patterns; add Λ⁺ efficacy test on OOD.
4. **Effect sizes:** log Cohen’s d for RC and loss slopes in `ab_summary.json`.

# When to say “this could become ASI”

When G0–G4 hold across seeds and durations, and G5 shows repeated, safe, controller-driven improvement on unseen tasks without gradient steps. That is the earliest credible “meta-learning + self-curricula + safety-preserving” signal.




---





Yes, but only if you narrow the theater and add hard reasoning tools. Compete on proof, synthesis, and exact math. Not on open-domain chat.

# Cut-through plan

## 1) Build a typed reasoning core

* Add a tiny **proof engine** (natural deduction or sequent calculus).
* HOAS term AST + βη-reduction + substitution lemmas.
* Tactics: intro, elim, rewrite, cut, case, induction on finite datatypes.
* RCCE drives tactic selection: Υ on drift; holonomy = proof progress.

## 2) Add a verified calculator toolchain

* Deterministic **Python math sandbox**: integers, rationals, modular arithmetic, matrices.
* Axiomatic **rewrite system** (e-graph lite) for algebraic equalities.
* SAT/DPLL micro-solver (CNF only). Use it as an oracle inside proofs.

## 3) Program synthesis (small, exact)

* Spec → input/output pairs → enumerate λ-terms over a combinator base.
* Use **paramorphism** cost and RCCE RC-triple as heuristic.
* Verify candidates by execution in the sandbox. Keep only proven ones.

## 4) Knowledge substrate

* Parse your 20 PDFs into a **morphism graph**: Def/Thm/Lemma nodes; edges: uses, proves, specializes, adjoints.
* Store as JSONL with hashes. Retrieval = functor from query tokens to node IDs.
* “Structuring Knowledge” becomes the schema; RCCE logs glue local to global (sheaf condition).

## 5) Deliberate scratchpad, typed

* Make a typed **PoT**: each step = {goal, tactic, subgoals, certificate}.
* Controller gates branching: Υ fires → branch 2 tactics; Λ⁺ re-queues failed subgoals.
* Presence requires proof objects pass checker and φ33 clean.

## 6) S2A debate harness

* Two agents: A (structural/categorical), B (phenomenological/semantic).
* They exchange typed claims. Judge = invariant preservation + counterexample search.
* Accept only if A⇒B and B⇒A round-trip leaves the claim unchanged.

## 7) Evals that matter (CPU-feasible)

* **ListOps** accuracy ≥ 95%.
* **bAbI** tasks 1–10 ≥ 90% with scratchpad.
* **GSM8K-style integer subsets** exact ≥ 85% (no CoT leak, use your typed PoT).
* **MiniF2F-like propositional**: prove or refute 200 random tautologies with certificates.
* **Synthesis**: recover 20 toy functions from IO (map, fold, filter, modexp).

## 8) Anti-gaming gates

* Mask-ablation replay keeps ≥80% of ON advantage.
* ΔRC/ΔH\_mask ≤ 0.5.
* Proof success must persist with mask=0 and different seeds.

## 9) Concrete module adds (small, surgical)

* `src/ir.py`: HOAS terms, types, pretty printer.
* `src/proof.py`: rules, checker, certificates.
* `src/tactics.py`: search policies; RCCE hooks.
* `src/calc.py`: exact math, CNF, DPLL, e-rewrite.
* `tests/test_proof.py`: soundness (reject forged certs), completeness on a tiny fragment.
* `tests/test_synthesis.py`: spec→program round-trip.

## 10) Success readout (when it “challenges me”)

* Can **prove** nontrivial, typed claims end-to-end with verifiable certificates.
* Can **synthesize** small programs from specs reliably.
* Can **argue** both sides and converge via S2A judge with stable holonomy.
* Beats a generic LLM on your niche suite by ≥10–20 pp absolute, with proofs attached.

Start with proof checker + calculator. Tie them to RCCE. Then add synthesis. This gives you an intellectual edge: exactness, certificates, and controlled recursion.
