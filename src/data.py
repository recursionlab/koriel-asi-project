# src/data.py
import os
import typing as T
from pathlib import Path

import numpy as np

try:
    from datasets import load_dataset  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dataset = None


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


def load_corpus(
    root: str = "conversations-pocket",
    *,
    dataset: str | None = None,
    text_column: str = "text"
) -> T.List[np.ndarray]:
    """Load a text corpus from disk or HuggingFace Datasets.

    Priority is given to the ``dataset`` argument if provided; otherwise, the environment variable
    ``KORIEL_CORPUS_DATASET`` is used. When a dataset is selected, the HuggingFace dataset is
    streamed and each record's ``text_column`` is converted to a byte array.

    Otherwise, ``root`` (or ``KORIEL_CORPUS_DIR``) is treated as a directory of
    ``.txt`` shards and read recursively.
    """

    ds_name = (
        dataset if dataset is not None else os.environ.get("KORIEL_CORPUS_DATASET")
    )
    lines: T.List[bytes] = []
    if ds_name and load_dataset is not None:
        try:
            ds = load_dataset(ds_name, split="train", streaming=True)
            for ex in ds:
                txt = ex.get(text_column)
                if isinstance(txt, str):
                    lines.append(txt.encode("utf-8"))
        except Exception:
            lines = []

    if not lines:
        root = os.environ.get("KORIEL_CORPUS_DIR", root)
        p = Path(root)
        if p.is_dir():
            for fp in sorted(p.rglob("*.txt")):
                try:
                    lines.append(fp.read_bytes())
                except Exception:
                    pass

    if not lines:
        lines = _default_corpus()

    return [np.frombuffer(x, dtype=np.uint8) for x in lines]


def make_stream(corpus, ctx: int, steps: int, seed: int):
    rng = np.random.default_rng(seed)
    concat = np.concatenate([np.uint8(10) * np.ones(1, dtype=np.uint8)] + corpus)
    N = len(concat)
    pos = 0
    for _ in range(steps):
        if pos + ctx + 1 >= N:
            pos = 0
        seq = concat[pos : pos + ctx]
        y = concat[pos + 1 : pos + ctx + 1]
        pos += int(rng.integers(1, 5))
        yield seq.copy(), y.copy()
