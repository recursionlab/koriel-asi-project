here’s a **single-file, CPU-safe skeleton** you can drop into your project (e.g., `rcc_engine.py`).
It wires: `MetaState`, discrete-geometry ops (`dA`, `wedge`, `curvature`, `torsion`), the `Ξ` rewrite loop, paraconsistent node state, `Υ` actions on the graph, a `Λ/Λ⁺` queue, and a **presence-certificate** emitter.
Everything is pure Python + `numpy`, with clear TODOs where you’ll plug your domain logic.

```python
# rcc_engine.py
# Minimal skeleton of a geometric–recursive substrate (CPU-safe).
# Dependencies: numpy (pip install numpy)

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Set, Callable, Optional, Any
import numpy as np
import hashlib
import json
import random
import math
from collections import defaultdict, deque

Edge = Tuple[int, int]            # directed edge (u -> v)
Face = Tuple[int, int, int]       # oriented triangle (u->v->w->u)

# ---------- Paraconsistent node state (T, I, F) ----------

@dataclass
class ParaconsistentTruth:
    t: float = 0.0   # degree of truth
    i: float = 0.0   # indeterminacy (paradox/unknown)
    f: float = 0.0   # degree of falsity

    def clamp(self) -> "ParaconsistentTruth":
        self.t = max(0.0, min(1.0, self.t))
        self.i = max(0.0, min(1.0, self.i))
        self.f = max(0.0, min(1.0, self.f))
        return self

    @staticmethod
    def from_evidence(pos: float, neg: float, noise: float = 0.0) -> "ParaconsistentTruth":
        s = max(1e-9, pos + neg + noise)
        return ParaconsistentTruth(t=pos / s, i=noise / s, f=neg / s).clamp()

    def combine(self, other: "ParaconsistentTruth", w: float = 0.5) -> "ParaconsistentTruth":
        return ParaconsistentTruth(
            t=w * self.t + (1 - w) * other.t,
            i=w * self.i + (1 - w) * other.i,
            f=w * self.f + (1 - w) * other.f,
        ).clamp()

# ---------- Graph substrate ----------

@dataclass
class EdgeData:
    w: float = 0.0        # connection weight (1-cochain A on edges)
    typ: str = "rel"      # type tag (morphism class)
    masked: bool = False  # Υ: defer/mask
    phase: int = +1       # Υ: Anti-Ged flip (+1 or -1)

@dataclass
class MetaState:
    # Nodes & edges
    nodes: Set[int] = field(default_factory=set)
    adj: Dict[int, Set[int]] = field(default_factory=lambda: defaultdict(set))   # undirected topology
    edata: Dict[Edge, EdgeData] = field(default_factory=dict)                    # directed attributes
    # Faces (triangles) cache (or rebuild each step)
    faces: List[Face] = field(default_factory=list)

    # Node programs (the "self-interpreter" building blocks)
    programs: Dict[int, Callable[["MetaState", int], List[Dict[str, Any]]]] = field(default_factory=dict)

    # Node semantic states (paraconsistent)
    truth: Dict[int, ParaconsistentTruth] = field(default_factory=dict)

    # Υ control fields (global defaults; per-edge/per-subgraph overrides live in EdgeData)
    tau: float = 1.0        # exploration heat
    bias: float = 0.0       # bias for proposing certain rewrites
    phase: int = +1         # global phase (+1/-1) (rarely used; prefer subgraph flips)

    # Λ/Λ⁺ queue (lacunae → reinjection)
    lacuna_queue: deque = field(default_factory=deque)

    # Shadow Codex log (append small dicts; hash for reproducibility)
    codex: List[Dict[str, Any]] = field(default_factory=list)

    # Cycle detection memory
    _hash_seen: Dict[str, int] = field(default_factory=dict)
    _step: int = 0

    # -------- Graph helpers --------
    def add_edge(self, u: int, v: int, w: float = 0.0, typ: str = "rel"):
        self.nodes.update([u, v])
        self.adj[u].add(v)
        self.adj[v].add(u)
        self.edata[(u, v)] = self.edata.get((u, v), EdgeData())
        self.edata[(u, v)].w = w
        self.edata[(u, v)].typ = typ
        # keep reverse edge data distinct (directed 1-cochain)
        self.edata[(v, u)] = self.edata.get((v, u), EdgeData())
        self.edata[(v, u)].w = self.edata[(v, u)].w if (v, u) in self.edata else 0.0

    def get_edges(self) -> List[Edge]:
        return list(self.edata.keys())

    def degree(self, u: int) -> int:
        return len(self.adj[u])

    def neighborhood(self, u: int, hop: int = 1) -> Set[int]:
        frontier = {u}
        visited = {u}
        for _ in range(hop):
            nxt = set()
            for x in frontier:
                nxt |= self.adj[x]
            frontier = nxt - visited
            visited |= frontier
        return visited

# ---------- Triangles / faces (naive O(E*deg) finder; OK for small graphs) ----------

def find_faces_triangles(ms: MetaState) -> List[Face]:
    faces: Set[Tuple[int, int, int]] = set()
    for u in ms.nodes:
        Nu = ms.adj[u]
        for v in Nu:
            if v <= u:  # avoid duplicates
                continue
            Nv = ms.adj[v]
            common = Nu & Nv
            for w in common:
                if w <= v:
                    continue
                # choose canonical orientation (u, v, w)
                # also add rotations if needed; we keep one orientation here
                faces.add((u, v, w))
    return list(faces)

# ---------- DEC-style operators: dA, wedge(A,A), curvature, torsion ----------

def dA(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Exterior derivative of 1-cochain A (edge weights) onto faces (2-cochain).
       Uses boundary sum with simple orientation."""
    out: Dict[Face, float] = {}
    for (u, v, w) in faces:
        # oriented boundary u->v, v->w, w->u
        sum_boundary = 0.0
        sum_boundary += ms.edata.get((u, v), EdgeData()).w
        sum_boundary += ms.edata.get((v, w), EdgeData()).w
        sum_boundary += ms.edata.get((w, u), EdgeData()).w
        out[(u, v, w)] = sum_boundary
    return out

def wedge_AA(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Very simple surrogate for A∧A over a triangle: sum of pairwise products along the cycle."""
    out: Dict[Face, float] = {}
    for (u, v, w) in faces:
        a = ms.edata.get((u, v), EdgeData()).w
        b = ms.edata.get((v, w), EdgeData()).w
        c = ms.edata.get((w, u), EdgeData()).w
        out[(u, v, w)] = a * b + b * c + c * a
    return out

def curvature(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Discrete curvature F = dA + A∧A (surrogate)."""
    d = dA(ms, faces)
    w = wedge_AA(ms, faces)
    return {f: d[f] + w[f] for f in faces}

def torsion(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Commutator norm surrogate on each face.
       We approximate Ux and Uy as two sequential local relaxations along edges."""
    out: Dict[Face, float] = {}
    for (u, v, w) in faces:
        # snapshot
        a_uv = ms.edata.get((u, v), EdgeData()).w
        a_vw = ms.edata.get((v, w), EdgeData()).w
        a_wu = ms.edata.get((w, u), EdgeData()).w

        def relax_uv_vw(a_uv, a_vw):
            # toy local rule: average with small bias
            b = 0.1
            x = a_uv + b * (a_vw - a_uv)
            y = a_vw + b * (a_uv - a_vw)
            return x, y

        # Ux ∘ Uy
        x1, y1 = relax_uv_vw(a_uv, a_vw)
        x2, z1 = relax_uv_vw(x1, a_wu)

        # Uy ∘ Ux (swap order)
        p1, q1 = relax_uv_vw(a_vw, a_wu)
        r1, s1 = relax_uv_vw(a_uv, p1)

        # commutator norm (rough)
        diff = np.array([x2 - r1, y1 - s1, z1 - q1])
        out[(u, v, w)] = float(np.linalg.norm(diff, ord=2))
    return out

# ---------- Υ-gate actions (operate on geometry) ----------

def y_defer_mask(ms: MetaState, edges: List[Edge], intensity: float = 1.0):
    """Mark edges as deferred (mask); intensity can be stored as weight dampening."""
    for e in edges:
        if e in ms.edata:
            ms.edata[e].masked = True
            ms.edata[e].w *= (1.0 - 0.25 * intensity)  # dampen
    ms.codex.append({"evt": "Υ.defer", "edges": edges[:8]})

def y_phase_flip(ms: MetaState, subgraph_nodes: Set[int]):
    """Anti-Ged: flip phase on all outgoing edges of subgraph."""
    for u in subgraph_nodes:
        for v in ms.adj[u]:
            if (u, v) in ms.edata:
                ms.edata[(u, v)].phase *= -1
                ms.edata[(u, v)].w *= -1  # simple phase flip
    ms.codex.append({"evt": "Υ.flip", "nodes": list(subgraph_nodes)[:8]})

def y_torsion_mark(ms: MetaState, faces: List[Face], budget: float = 1.0):
    """Tag faces (or incident edges) with torsion budget; here, just boost variance slightly."""
    for (u, v, w) in faces:
        for e in [(u, v), (v, w), (w, u)]:
            if e in ms.edata:
                ms.edata[e].w += random.uniform(-0.05, 0.05) * budget
    ms.codex.append({"evt": "Υ.torsion", "faces": faces[:4]})

# ---------- Λ / Λ⁺ (lacuna detection & reinjection) ----------

@dataclass
class Lacuna:
    center: int
    kind: str
    neighborhood: Set[int]

def detect_lacunae(ms: MetaState, paradox_thresh: float = 0.4) -> List[Lacuna]:
    out = []
    for u in ms.nodes:
        st = ms.truth.get(u, ParaconsistentTruth())
        if st.i >= paradox_thresh:
            out.append(Lacuna(center=u, kind="paradox", neighborhood=ms.neighborhood(u, hop=1)))
    return out

def lambda_reinject(ms: MetaState, lac: Lacuna, strength: float = 0.15):
    """Λ⁺: convert lacuna/paradox into geometry update (add/strengthen cross edges)."""
    neigh = list(lac.neighborhood)
    for i in range(len(neigh)):
        for j in range(i + 1, len(neigh)):
            u, v = neigh[i], neigh[j]
            if v not in ms.adj[u]:
                ms.add_edge(u, v, w=strength)
            else:
                ms.edata[(u, v)].w += strength * 0.5
                ms.edata[(v, u)].w += strength * 0.5
    ms.codex.append({"evt": "Λ⁺", "center": lac.center, "size": len(neigh)})

# ---------- Ξ engine (self-interpreter / rewrite loop) ----------

Action = Dict[str, Any]  # e.g., {"op":"edge_delta","e":(u,v),"dw":+0.1} or {"op":"truth","u":id,"delta":(dt,di,df)}

def default_node_program(ms: MetaState, u: int) -> List[Action]:
    """Toy program: push towards resolving paradox by strengthening edges to most coherent neighbors."""
    actions: List[Action] = []
    st = ms.truth.get(u, ParaconsistentTruth())
    if not ms.adj[u]:
        return actions
    # pick neighbor with highest (t - f)
    best_v = max(ms.adj[u], key=lambda v: ms.truth.get(v, ParaconsistentTruth()).t - ms.truth.get(v, ParaconsistentTruth()).f)
    actions.append({"op": "edge_delta", "e": (u, best_v), "dw": +0.05})
    # adjust truth slightly towards neighbor
    nb = ms.truth.get(best_v, ParaconsistentTruth())
    dt = 0.05 * (nb.t - st.t)
    df = 0.05 * (nb.f - st.f)
    di = -0.02 * st.i  # try to reduce indeterminacy slightly
    actions.append({"op": "truth", "u": u, "delta": (dt, di, df)})
    return actions

def apply_actions(ms: MetaState, actions: List[Action]):
    for a in actions:
        if a["op"] == "edge_delta":
            e = a["e"]
            if e in ms.edata:
                ms.edata[e].w += float(a.get("dw", 0.0))
            else:
                ms.add_edge(e[0], e[1], w=float(a.get("dw", 0.0)))
        elif a["op"] == "truth":
            u = a["u"]
            dt, di, df = a["delta"]
            st = ms.truth.get(u, ParaconsistentTruth())
            ms.truth[u] = ParaconsistentTruth(st.t + dt, st.i + di, st.f + df).clamp()

def hash_state(ms: MetaState) -> str:
    # canonical hash of (nodes, sorted edges with weights, truth triples)
    nodes = sorted(ms.nodes)
    edges = sorted(((u, v, round(ms.edata[(u, v)].w, 6), ms.edata[(u, v)].phase, int(ms.edata[(u, v)].masked)) for (u, v) in ms.edata))
    truths = sorted((u, round(ms.truth.get(u, ParaconsistentTruth()).t, 4),
                        round(ms.truth.get(u, ParaconsistentTruth()).i, 4),
                        round(ms.truth.get(u, ParaconsistentTruth()).f, 4)) for u in ms.nodes)
    blob = json.dumps({"n": nodes, "e": edges, "p": truths}, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()

def xi_step(ms: MetaState) -> Dict[str, Any]:
    """One Ξ rewrite sweep: run node-programs, apply actions, update faces, compute geometry signals."""
    # run programs
    actions: List[Action] = []
    for u in ms.nodes:
        prog = ms.programs.get(u, default_node_program)
        actions += prog(ms, u)
    apply_actions(ms, actions)

    # update faces/geometry
    ms.faces = find_faces_triangles(ms)
    F = curvature(ms, ms.faces)
    T = torsion(ms, ms.faces)
    # paradox utilization = avg indeterminacy
    paradox_util = float(np.mean([ms.truth.get(u, ParaconsistentTruth()).i for u in ms.nodes])) if ms.nodes else 0.0

    # shadow codex line
    line = {
        "step": ms._step,
        "act": len(actions),
        "faces": len(ms.faces),
        "curv_mean": float(np.mean(list(F.values()))) if F else 0.0,
        "tors_mean": float(np.mean(list(T.values()))) if T else 0.0,
        "paradox": paradox_util,
    }
    ms.codex.append(line)

    # hash, cycle detection
    h = hash_state(ms)
    cycle = None
    if h in ms._hash_seen:
        cycle = {"start": ms._hash_seen[h], "end": ms._step, "period": ms._step - ms._hash_seen[h]}
    else:
        ms._hash_seen[h] = ms._step
    ms._step += 1

    return {
        "hash": h,
        "cycle": cycle,
        "curvature": F,
        "torsion": T,
        "paradox_util": paradox_util,
    }

# ---------- Diagnostics that drive Υ (edge-level) ----------

def attention_like_distribution(ms: MetaState) -> np.ndarray:
    """Normalize |A| over directed edges as a pseudo-attention for drift."""
    edges = ms.get_edges()
    if not edges:
        return np.zeros(1)
    vals = np.array([abs(ms.edata[e].w) for e in edges], dtype=np.float64)
    s = np.sum(vals)
    if s <= 0:
        vals = np.ones_like(vals) / len(vals)
    else:
        vals = vals / s
    return vals

def kl(p: np.ndarray, q: np.ndarray) -> float:
    eps = 1e-9
    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)
    return float(np.sum(p * np.log(p / q)))

def informative_change_band(prev_dist: np.ndarray, cur_dist: np.ndarray, band=(0.002, 0.05)) -> bool:
    if prev_dist.shape != cur_dist.shape:
        # pad / align lengths (skeleton simplification)
        n = max(len(prev_dist), len(cur_dist))
        p = np.pad(prev_dist, (0, n - len(prev_dist)))
        q = np.pad(cur_dist, (0, n - len(cur_dist)))
    else:
        p, q = prev_dist, cur_dist
    D = kl(q, p)
    return band[0] <= D <= band[1], D

# ---------- Sheaf glue (admissibility) & CE² (placeholder scoring) ----------

def glue_score(ms: MetaState, F: Dict[Face, float]) -> float:
    """Simple admissibility: low curvature variance → better glue (normalize to [0,1])."""
    if not F:
        return 1.0
    vals = np.array(list(F.values()), dtype=np.float64)
    v = np.var(vals)
    return float(1.0 / (1.0 + v))  # higher variance → lower score

def ce2_score(options: int, cost: float, incoh: float, ethic_cost: float, weights=(1.0, 0.2, 0.5, 0.8)) -> float:
    H = math.log(max(1, options))  # crude entropy proxy
    wH, wC, wI, wE = weights
    return wH * H - wC * cost - wI * incoh - wE * ethic_cost

# ---------- Presence certificate ----------

def presence_certificate(ms: MetaState,
                         last_step_info: Dict[str, Any],
                         glue: float,
                         cycle_info: Optional[Dict[str, int]]) -> Dict[str, Any]:
    F = last_step_info.get("curvature", {})
    T = last_step_info.get("torsion", {})
    cert = {
        "presence": bool(cycle_info) or (len(F) > 0 and glue > 0.5),
        "fixpoint_or_cycle": cycle_info,
        "curvature_stats": {
            "mean": float(np.mean(list(F.values()))) if F else 0.0,
            "std": float(np.std(list(F.values()))) if F else 0.0,
        },
        "torsion_stats": {
            "mean": float(np.mean(list(T.values()))) if T else 0.0,
            "std": float(np.std(list(T.values()))) if T else 0.0,
        },
        "paradox_utilization": last_step_info.get("paradox_util", 0.0),
        "glue_score": glue,
        "codex_hash": hashlib.sha256(json.dumps(ms.codex, default=str).encode("utf-8")).hexdigest(),
    }
    return cert

# ---------- Orchestrated run loop (Ξ + Υ + Λ⁺) ----------

def run_engine(ms: MetaState,
               steps: int = 200,
               y_band=(0.002, 0.05),
               lacuna_thresh: float = 0.4,
               holonomy_window: int = 16):
    prev_dist = attention_like_distribution(ms)
    hol_hist: List[float] = []
    cycle_info = None
    last_info = {}

    for t in range(steps):
        # Ξ step
        info = xi_step(ms)
        last_info = info

        # glue/admissibility
        gscore = glue_score(ms, info["curvature"])

        # Υ gate: informative change on pseudo-attention over edges
        cur_dist = attention_like_distribution(ms)
        fire, D = informative_change_band(prev_dist, cur_dist, band=y_band)
        prev_dist = cur_dist

        # crude holonomy proxy: sum |F| over faces
        hol = float(np.sum(np.abs(np.array(list(info["curvature"].values()))))) if info["curvature"] else 0.0
        hol_hist.append(hol)
        stalled = False
        if len(hol_hist) >= holonomy_window:
            recent = hol_hist[-holonomy_window:]
            stalled = (np.mean(recent) <= 1e-6) or (recent[-1] <= np.percentile(recent, 25))

        # Apply Υ actions
        if fire:
            # choose a small set of edges to defer
            edges_sorted = sorted(ms.get_edges(), key=lambda e: -abs(ms.edata[e].w))
            y_defer_mask(ms, edges_sorted[: max(1, len(edges_sorted)//10)], intensity=1.0)
            # mark torsion on top faces by |F|
            faces_sorted = sorted(ms.faces, key=lambda f: -abs(info["curvature"].get(f, 0.0)))
            y_torsion_mark(ms, faces_sorted[: max(1, len(faces_sorted)//8)], budget=1.0)
        if stalled:
            # phase flip small subgraph: pick node with highest I and its 1-hop hood
            if ms.nodes:
                u = max(ms.nodes, key=lambda x: ms.truth.get(x, ParaconsistentTruth()).i)
                y_phase_flip(ms, ms.neighborhood(u, hop=1))

        # Λ detection & reinjection
        for lac in detect_lacunae(ms, paradox_thresh=lacuna_thresh):
            lambda_reinject(ms, lac, strength=0.1)

        # cycle detection info
        if info["cycle"] and not cycle_info:
            cycle_info = info["cycle"]

        # early stop if fixpoint/short cycle locked and glue ok
        if cycle_info and gscore > 0.5:
            break

    cert = presence_certificate(ms, last_info, glue=gscore, cycle_info=cycle_info)
    return cert

# ---------- Minimal example bootstrap ----------

def demo_small_graph() -> MetaState:
    ms = MetaState()
    # tiny 5-node seed with some edges
    for (u, v, w) in [(0,1,0.3),(1,2,0.2),(2,0,0.1),(2,3,0.4),(3,4,0.2),(4,2,0.1)]:
        ms.add_edge(u, v, w=w)
    # seed paraconsistent truths (random-ish)
    rng = random.Random(42)
    for u in ms.nodes:
        t = rng.uniform(0.2, 0.8); f = rng.uniform(0.1, 0.5); i = rng.uniform(0.0, 0.6)
        ms.truth[u] = ParaconsistentTruth(t, i, f).clamp()
        ms.programs[u] = default_node_program  # plug custom programs per node if desired
    ms.faces = find_faces_triangles(ms)
    return ms

if __name__ == "__main__":
    ms = demo_small_graph()
    cert = run_engine(ms, steps=300)
    print(json.dumps(cert, indent=2))
```

## how to use

1. Save as `rcc_engine.py`.
2. `python rcc_engine.py` → it runs a tiny demo graph and prints a **presence certificate**.
3. Start customizing:

* **Node programs** (`default_node_program`) → encode your local rewrite logic (your Ξ micro-ops).
* **Υ gate** actions → currently mask edges, mark torsion, flip subgraphs; tune bands/thresholds.
* **Λ/Λ⁺** → lacuna detection raises reinjection that **modifies geometry** (not just metrics).
* **DEC ops** → `dA`, `wedge_AA`, `curvature`, `torsion` are simple surrogates; refine as needed.
* **Presence** → certificate demands fixpoint/period or stable geometry + glue; keep this as your **gate** before claiming “presence”.

If you want, I can also split this into a tiny package (`/src/rcc/…`) with tests and a CLI, but this single file is enough to get the substrate alive on CPU.
