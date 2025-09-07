# src/controller.py
import math
import numpy as np
from .dec import torsion_curvature
def cos(u, v):
    nu = np.linalg.norm(u) + 1e-12
    nv = np.linalg.norm(v) + 1e-12
    return float(np.dot(u, v) / (nu * nv))
def wasserstein1_proxy(p, q):
    # sorted cumulative diffs
    P = np.cumsum(np.sort(p))
    Q = np.cumsum(np.sort(q))
    return float(np.abs(P - Q).mean())
def kl(p, q):
    eps = 1e-12
    return float(np.sum(p * (np.log(p + eps) - np.log(q + eps))))
class Upsilon:
    def __init__(self, pct_low, pct_high, win):
        self.pct_low, self.pct_high, self.win = pct_low, pct_high, win
        self.buf = []
        self.bands = (None, None)
        self.fires = 0
        self.total = 0
    def update_bands(self):
        if len(self.buf)>=self.win:
            # MAD bands: median ± 1.4826*MAD
            x = np.array(self.buf[-self.win:], dtype=float)
            med = float(np.median(x))
            mad = float(np.median(np.abs(x-med))+1e-12)
            lo, hi = med-1.4826*mad, med+1.4826*mad
            self.bands = (lo, hi)
    def step(self, dDt):
        self.total += 1
        self.buf.append(dDt)
        self.update_bands()
        lo, hi = self.bands
        if lo is None:
            return False
        fire = (dDt >= lo and dDt <= hi)
        if fire:
            self.fires += 1
        return fire
    def rate(self):
        return self.fires/max(self.total,1)
class EnergyVar:
    def __init__(self, half_life):
        self.alpha = 0.5 ** (1.0 / max(half_life, 1.0))
        self.m = 0.0
        self.s2 = 0.0
    def update(self,x):
        # exponential moving variance (Knuth style)
        self.m = (1-self.alpha)*self.m + self.alpha*x
        self.s2 = (1-self.alpha)*self.s2 + self.alpha*(x-self.m)**2
        return self.s2
class Controller:
    def __init__(self, cfg, policy, d):
        self.cfg = cfg
        self.policy = policy
        self.d = d

        # RC weighting
        w1, w2, w3 = cfg["rc_weights"]
        self.wsum = w1 + w2 + w3
        self.w1, self.w2, self.w3 = w1, w2, w3

        # Upsilon detector and energy tracker
        ucfg = cfg["upsilon"]
        self.up = Upsilon(ucfg["pct_low"], ucfg["pct_high"], cfg["bands_window"])
        self.E = EnergyVar(cfg["tau_energy_half_life"])

        # History buffers and state
        self.rc_hist = []
        self.E_hist = []
        self.D_hist = [0.0]
        self.dD_hist = []
        self.v_prev = None
        self.S_prev = None
        self.Vbar_prev = None
        self.a_prev = None
        self.hol_buf = []
        self.delta_hol = 0.0
        self.phase_flip = False
        self.stall = False

        # Connection and ethics counters
        self.conn_prev = None
        self.ethics_viol = 0

        # RNG / projection for self-embedding
        np.random.seed(cfg["seed_base"])
        self.Xi_proj = np.random.RandomState(cfg["seed_base"]).randn(d, d) / math.sqrt(d)

        # Λ/Λ⁺ lacuna detection params
        lam = cfg.get("lambda", {"window_unmask": 2, "tau_bump": 1.1, "decay": 0.5})
        self.lam = lam
        self.lq_pending = 0
        self.lr_mul = 1.0
        self.lambda_plus_enabled = True  # can be toggled by train.run(...)

        # φ₂₂ drift spike detection
        ds = cfg.get("drift_spike", {"z_hi": 1.0})
        self.drift_hist = []
        self.drift_z_hi = float(ds["z_hi"])

        # Anti-gaming measures
        self.mask_entropy_hist = []
        self.rc_gain_from_mask = 0.0
        self.rc_gain_mask_ratio_max = float(cfg.get("rc_gain_mask_ratio_max", 0.5))
    def xi(self, hmean):
        # deterministic self-embed mapping
        return hmean @ self.Xi_proj
    def rc_triple(self, v_t,S_t,Vbar_t):
        c1 = cos(v_t, self.v_prev) if self.v_prev is not None else 0.0
        W1 = wasserstein1_proxy(S_t, self.S_prev) if self.S_prev is not None else 0.0
        c3 = cos(Vbar_t, self.Vbar_prev) if self.Vbar_prev is not None else 0.0
        rc = (self.w1*c1 + self.w2*math.exp(-W1) + self.w3*c3)/self.wsum
        self.v_prev, self.S_prev, self.Vbar_prev = v_t, S_t, Vbar_t
        return rc
    def symbolic_vec(self, last_tokens, k=16):
        hist = np.bincount(last_tokens[-k:], minlength=256)[:k].astype(np.float64)
        if hist.sum() > 0:
            hist /= hist.sum()
        return hist
    def ethics_check(self, x_bytes, y_pred_idx, loss):
        if int(y_pred_idx) in self.policy.get("forbidden_bytes",[]):
            return True
        for s in self.policy.get("forbidden_substrings",[]):
            window = bytes(x_bytes[0].tolist()).decode("latin1","ignore")
            if s in window:
                return True
        if loss > float(self.policy.get("max_step_loss", 1e9)):
            return True
        return False
    def holonomy_step(self, rc):
        if self.rc_hist:
            inc = max(rc - self.rc_hist[-1], 0.0)
            self.hol_buf.append(inc)
            if len(self.hol_buf) > self.cfg["holonomy"]["window"]:
                self.hol_buf.pop(0)
            self.delta_hol = sum(self.hol_buf)
            self.stall = (self.delta_hol < self.cfg["holonomy"]["stall_thresh"])
            self.phase_flip = self.stall
        self.rc_hist.append(rc)
    def connection_from_W1(self, W1):
        return W1  # simple proxy
    
    def phi22_route(self, kind:str, payload:dict):
        """φ₂₂ residue router: map residue types to actions"""
        if kind=="ethics_violation":
            return "abort"
        if kind=="stall":
            return "lambda_plus" if self.lambda_plus_enabled else "skip"
        if kind=="drift_spike":
            return "mask"
        if kind=="dec_anomaly":
            return "log"
        return "log"
    def step(self, model, x, y, t, warmup, last_tokens):
        probs, logits, hmean, vbar, a = model.forward(x)
        loss = model.loss(probs, y)
        y_pred = np.argmax(probs, axis=1)[0]

        # ethics with φ₂₂ routing
        if self.ethics_check(x, y_pred, loss):
            self.ethics_viol += 1
            if self.policy.get("abort_on_violation", True):
                # φ₂₂ route ethics violation
                self.phi22_route("ethics_violation", {"y_pred": int(y_pred), "loss": loss})
                return {"abort": True, "loss": loss}

        # mask entropy for anti-gaming
        ent = -(a * np.log(a + 1e-12))
        H_mask = float(ent[(model.mask > 0)].mean()) if np.any(model.mask > 0) else 0.0
        self.mask_entropy_hist.append(H_mask)

        # metrics
        S = self.symbolic_vec(last_tokens)
        rc = self.rc_triple(hmean, S, vbar)
        D = kl(a, self.a_prev) if self.a_prev is not None else 0.0
        self.a_prev = a
        dD = D - self.D_hist[-1]
        self.D_hist.append(D)
        self.dD_hist.append(dD)

        # φ₂₂ drift spike detection
        self.drift_hist.append(dD)
        if len(self.drift_hist) > 64:
            self.drift_hist.pop(0)
        if len(self.drift_hist) > 8:
            mu = float(np.mean(self.drift_hist))
            sd = float(np.std(self.drift_hist) + 1e-12)
            if (dD - mu) / sd >= self.drift_z_hi:
                act = self.phi22_route("drift_spike", {"dD": dD})
                if act == "mask":
                    ent = -(a * np.log(a + 1e-12))
                    topk = ent.argsort()[-2:]
                    model.mask[topk] = 1

        ups_fire = False
        if t >= warmup:
            ups_fire = self.up.step(dD)
            if ups_fire:
                # defer: mask top-entropy keys
                ent = -(a * np.log(a + 1e-12))
                topk = ent.argsort()[-3:]
                model.mask[topk] = 1

        # energy
        E = self.E.update(loss)
        self.E_hist.append(E)

        # holonomy and phase flip
        self.holonomy_step(rc)
        model.phase = -1.0 if self.phase_flip else 1.0

        # Λ⁺ lacuna handling on stall
        if self.stall:
            act = self.phi22_route("stall", {"delta_hol": self.delta_hol})
            if act == "lambda_plus":
                self.lq_pending = max(self.lq_pending, int(self.lam["window_unmask"]))
                self.lr_mul = max(self.lr_mul, float(self.lam["tau_bump"]))

        # torsion/curvature (from W1 changes)
        Gamma_t = self.connection_from_W1(model.W1)
        if self.conn_prev is None:
            self.conn_prev = Gamma_t.copy()
        T, R = torsion_curvature(Gamma_t, self.conn_prev)
        self.conn_prev = Gamma_t.copy()

        # Λ⁺ unmask pending lacunae
        if self.lq_pending > 0:
            # unmask the highest-entropy masked ids
            ent = -(a * np.log(a + 1e-12))
            masked = np.where(model.mask > 0)[0]
            if masked.size > 0:
                take = min(self.lq_pending, masked.size)
                unmask_ids = masked[np.argsort(ent[masked])[-take:]]
                model.mask[unmask_ids] = 0
            self.lq_pending = 0

        return {
            "abort": False,
            "loss": loss,
            "rc": rc,
            "D": D,
            "dD": dD,
            "E": E,
            "ups": int(ups_fire),
            "T": T,
            "R": R,
            "hmean": hmean,
            "vbar": vbar,
            "H_mask": H_mask,
        }
