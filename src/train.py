# src/train.py
import os, csv, json, math, numpy as np
from pathlib import Path
from tqdm import tqdm
from .data import load_corpus, make_stream
from .model import TinyByteLM
from .controller import Controller
from .metastate import ShadowCodex
from .presence import presence_certificate
def load_cfg():
    import yaml
    with open("config/rcce.yaml","r",encoding="utf-8") as f:
        return yaml.safe_load(f)
def run(seed=1337, rcce_on=True, out_prefix="ON", lambda_plus=True,
        corpus_dir: str | None = None, dataset: str | None = None):
    import yaml
    cfg = load_cfg(); cfg["seed_base"]=seed
    np.random.seed(seed)
    logs_dir = Path("logs"); logs_dir.mkdir(exist_ok=True)
    sc = ShadowCodex(logs_dir/f"shadow_codex_{out_prefix}_{seed}.jsonl")
    with open("config/ethics_policy.json","r",encoding="utf-8") as f:
        policy=json.load(f)
    data = load_corpus(corpus_dir or "conversations-pocket", dataset=dataset)
    ctx = cfg["context_len"]; batch = cfg["batch_size"]; steps = cfg["steps"]; warm = cfg["warmup"]
    model = TinyByteLM(ctx=ctx, d=cfg["hidden_dim"], seed=seed)
    ctrl = Controller(cfg, policy, d=cfg["hidden_dim"])
    ctrl.lambda_plus_enabled = bool(lambda_plus)
    metrics = {"t":[], "loss":[], "rc":[], "D":[], "dD":[], "E":[], "ups":[], "T":[], "R":[]}
    last_tokens = np.concatenate(data)[:ctx] if data else np.zeros(ctx, dtype=np.uint8)
    lr = cfg["learn_rate"]
    gen = make_stream(data, ctx, steps, seed)
    for t,(X,y) in enumerate(tqdm(gen, total=steps, disable=True), start=1):
        # Reshape single sequences to batch format
        X = X.reshape(1, -1)
        y = y.reshape(1, -1)
        if rcce_on:
            stat = ctrl.step(model, X, y, t, warm, last_tokens)
            if stat["abort"]:
                sc.append({"t":t,"action":"abort_ethics","loss":stat["loss"]})
                continue
        # Apply lr multiplier for Λ⁺ tau bump
        curr_lr = lr * (ctrl.lr_mul if rcce_on else 1.0)
        loss, hmean, vbar, a = model.step(X,y, lr=curr_lr)
        if not rcce_on:
            # baseline metrics
            from .controller import cos, wasserstein1_proxy, kl
            S = ctrl.symbolic_vec(last_tokens)
            rc = (cfg["rc_weights"][0]*cos(hmean, ctrl.v_prev) if ctrl.v_prev is not None else 0.0
                 + cfg["rc_weights"][1]*math.exp(-wasserstein1_proxy(S, ctrl.S_prev) if ctrl.S_prev is not None else 0.0)
                 + cfg["rc_weights"][2]*cos(vbar, ctrl.Vbar_prev) if ctrl.Vbar_prev is not None else 0.0)/sum(cfg["rc_weights"])
            ctrl.v_prev, ctrl.S_prev, ctrl.Vbar_prev = hmean, S, vbar
            D = kl(a, ctrl.a_prev) if ctrl.a_prev is not None else 0.0
            ctrl.a_prev=a; dD = D - ctrl.D_hist[-1]; ctrl.D_hist.append(D); ctrl.dD_hist.append(dD)
            E = ctrl.E.update(loss); ctrl.rc_hist.append(rc); ups=0
            ctrl.conn_prev = model.W1.copy()
            T,R = 0.0,0.0
        else:
            rc=stat["rc"]; D=stat["D"]; dD=stat["dD"]; E=stat["E"]; ups=stat["ups"]; T=stat["T"]; R=stat["R"]
        
        # Decay lr multiplier after step
        if rcce_on:
            ctrl.lr_mul = 1.0 + (ctrl.lr_mul - 1.0) * float(ctrl.lam.get("decay",0.5))
        metrics["t"].append(t); metrics["loss"].append(loss); metrics["rc"].append(rc)
        metrics["D"].append(D); metrics["dD"].append(dD); metrics["E"].append(E)
        metrics["ups"].append(ups); metrics["T"].append(T); metrics["R"].append(R)
        sc.append({"t":t,"action":"step","params":{"lr":lr},"digests":{},"ethics":ctrl.ethics_viol})
        last_tokens = X[0]
    # write CSV
    csvp = logs_dir/f"metrics_{out_prefix}_{seed}.csv"
    with csvp.open("w",newline="") as f:
        w=csv.writer(f); w.writerow(list(metrics.keys()))
        for i in range(len(metrics["t"])):
            w.writerow([metrics[k][i] for k in metrics.keys()])
    # presence
    ups_rate = sum(metrics["ups"])/max(1,len(metrics["ups"]))
    v_for_xi = ctrl.v_prev if ctrl.v_prev is not None else np.zeros(cfg["hidden_dim"])
    delta_xi = float(np.linalg.norm(v_for_xi - ctrl.xi(v_for_xi)))
    pres, cert = presence_certificate({"E":metrics["E"],"rc":metrics["rc"],"ups_rate":ups_rate}, cfg, ctrl.ethics_viol, [delta_xi])
    if rcce_on and pres:
        pj = {"presence":True, **cert}
        print(json.dumps(pj))
        with open(logs_dir/f"presence_{out_prefix}_{seed}.json","w") as f: json.dump(pj,f)
    elif rcce_on:
        print("INVALID")
    return metrics, ups_rate
if __name__=="__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus-dir", help="Directory of .txt shards to use as corpus")
    ap.add_argument("--dataset", help="HuggingFace dataset name to stream")
    args = ap.parse_args()
    run(corpus_dir=args.corpus_dir, dataset=args.dataset)
