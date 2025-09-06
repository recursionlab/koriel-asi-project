"""rcc_engine.py

Lightweight, CPU-safe skeleton of a geometric-recursive substrate. This file
is intentionally small and dependency-light so it can be dropped into a
project for experimentation. It implements a tiny MetaState, a toy
paraconsistent node state, a simple Ξ rewrite loop, Υ actions, and a
presence-certificate routine.

This replaces a previously corrupted/markdown-embedded file and keeps a
minimal but runnable implementation so static checks and CI can proceed.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import numpy as np

Edge = Tuple[int, int]
Face = Tuple[int, int, int]


@dataclass
class ParaconsistentTruth:
    t: float = 0.0
    i: float = 0.0
    f: float = 0.0

    def clamp(self) -> "ParaconsistentTruth":
        self.t = max(0.0, min(1.0, self.t))
        self.i = max(0.0, min(1.0, self.i))
        self.f = max(0.0, min(1.0, self.f))
        return self


@dataclass
class EdgeData:
    w: float = 0.0
    typ: str = "rel"
    masked: bool = False
    phase: int = +1


@dataclass
class MetaState:
    nodes: Set[int] = field(default_factory=set)
    adj: Dict[int, Set[int]] = field(default_factory=lambda: defaultdict(set))
    edata: Dict[Edge, EdgeData] = field(default_factory=dict)
    faces: List[Face] = field(default_factory=list)
    programs: Dict[int, Callable[["MetaState", int], List[Dict[str, Any]]]] = field(default_factory=dict)
    truth: Dict[int, ParaconsistentTruth] = field(default_factory=dict)
    tau: float = 1.0
    bias: float = 0.0
    phase: int = +1
    lacuna_queue: deque = field(default_factory=deque)
    codex: List[Dict[str, Any]] = field(default_factory=list)
    _hash_seen: Dict[str, int] = field(default_factory=dict)
    _step: int = 0

    def add_edge(self, u: int, v: int, w: float = 0.0, typ: str = "rel"):
        self.nodes.update([u, v])
        self.adj[u].add(v)
        self.adj[v].add(u)
        self.edata[(u, v)] = self.edata.get((u, v), EdgeData())
        self.edata[(u, v)].w = w
        self.edata[(u, v)].typ = typ
        if (v, u) not in self.edata:
            self.edata[(v, u)] = EdgeData()

    def get_edges(self) -> List[Edge]:
        return list(self.edata.keys())

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


def find_faces_triangles(ms: MetaState) -> List[Face]:
    """Naive triangle finder: returns oriented triples (u, v, w) with u < v < w."""
    faces = set()
    for u in ms.nodes:
        for v in ms.adj[u]:
            if v <= u:
                continue
            for w in ms.adj[v]:
                if w <= v:
                    continue
                # check closure
                if u in ms.adj[w]:
                    faces.add((u, v, w))
    return sorted(faces)


def curvature(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Simple curvature proxy: use the sum of absolute edge weights around a face."""
    out: Dict[Face, float] = {}
    for (u, v, w) in faces:
        vals = []
        for e in ((u, v), (v, w), (w, u)):
            vals.append(abs(ms.edata.get(e, EdgeData()).w))
        out[(u, v, w)] = float(sum(vals))
    return out


def torsion(ms: MetaState, faces: List[Face]) -> Dict[Face, float]:
    """Toy torsion: small random perturbation per-face based on edge sign-imbalance."""
    out: Dict[Face, float] = {}
    for (u, v, w) in faces:
        s = 0.0
        for e in ((u, v), (v, w), (w, u)):
            s += ms.edata.get(e, EdgeData()).w
        out[(u, v, w)] = float(abs(s) * 0.1 + random.uniform(-0.01, 0.01))
    return out


Action = Dict[str, Any]


def default_node_program(ms: MetaState, u: int) -> List[Action]:
    actions: List[Action] = []
    if not ms.adj[u]:
        return actions
    # pick a neighbor and nudge edge weight
    best_v = next(iter(ms.adj[u]))
    actions.append({"op": "edge_delta", "e": (u, best_v), "dw": 0.01})
    return actions


def apply_actions(ms: MetaState, actions: List[Action]):
    for a in actions:
        if a.get("op") == "edge_delta":
            e = a["e"]
            if e in ms.edata:
                ms.edata[e].w += float(a.get("dw", 0.0))
            else:
                ms.add_edge(e[0], e[1], w=float(a.get("dw", 0.0)))


def hash_state(ms: MetaState) -> str:
    nodes = sorted(ms.nodes)
    edges = sorted(((u, v, round(ms.edata[(u, v)].w, 6)) for (u, v) in ms.edata))
    truths = sorted((u, round(ms.truth.get(u, ParaconsistentTruth()).i, 4)) for u in ms.nodes)
    blob = json.dumps({"n": nodes, "e": edges, "p": truths}, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def xi_step(ms: MetaState) -> Dict[str, Any]:
    actions: List[Action] = []
    for u in ms.nodes:
        prog = ms.programs.get(u, default_node_program)
        actions += prog(ms, u)
    apply_actions(ms, actions)
    ms.faces = find_faces_triangles(ms)
    F = curvature(ms, ms.faces)
    T = torsion(ms, ms.faces)
    paradox_util = float(np.mean([ms.truth.get(u, ParaconsistentTruth()).i for u in ms.nodes])) if ms.nodes else 0.0
    line = {"step": ms._step, "act": len(actions), "faces": len(ms.faces), "paradox": paradox_util}
    ms.codex.append(line)
    h = hash_state(ms)
    cycle = None
    if h in ms._hash_seen:
        cycle = {"start": ms._hash_seen[h], "end": ms._step, "period": ms._step - ms._hash_seen[h]}
    else:
        ms._hash_seen[h] = ms._step
    ms._step += 1
    return {"hash": h, "cycle": cycle, "curvature": F, "torsion": T, "paradox_util": paradox_util}


def presence_certificate(ms: MetaState, last_info: Dict[str, Any], glue: float, cycle_info: Optional[Dict[str, int]]) -> Dict[str, Any]:
    F = last_info.get("curvature", {})
    cert = {
        "presence": bool(cycle_info) or (len(F) > 0 and glue > 0.5),
        "fixpoint_or_cycle": cycle_info,
        "curvature_count": len(F),
        "glue_score": glue,
    }
    return cert


def run_engine(ms: MetaState, steps: int = 100):
    last_info = {}
    glue = 1.0
    cycle_info = None
    for _ in range(steps):
        info = xi_step(ms)
        last_info = info
        if info.get("cycle") and not cycle_info:
            cycle_info = info.get("cycle")
    return presence_certificate(ms, last_info, glue=glue, cycle_info=cycle_info)


def demo_small_graph() -> MetaState:
    ms = MetaState()
    for (u, v, w) in [(0, 1, 0.3), (1, 2, 0.2), (2, 0, 0.1), (2, 3, 0.4), (3, 4, 0.2), (4, 2, 0.1)]:
        ms.add_edge(u, v, w=w)
    rng = random.Random(42)
    for u in ms.nodes:
        ms.truth[u] = ParaconsistentTruth(rng.uniform(0.1, 0.9), rng.uniform(0.0, 0.6), rng.uniform(0.0, 0.5))
        ms.programs[u] = default_node_program
    ms.faces = find_faces_triangles(ms)
    return ms


if __name__ == "__main__":
    ms = demo_small_graph()
    cert = run_engine(ms, steps=50)
    print(json.dumps(cert, indent=2))
