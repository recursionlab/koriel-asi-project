import os, sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.data import load_corpus


def test_load_corpus_large(monkeypatch, tmp_path):
    # Create two ~2MB shards
    shard_bytes = b"x" * (1024 * 1024 * 2)  # 2MB per shard
    for i in range(2):
        (tmp_path / f"shard{i}.txt").write_bytes(shard_bytes)
    monkeypatch.setenv("KORIEL_CORPUS_DIR", str(tmp_path))

    corpus = load_corpus()
    assert len(corpus) == 2
    total_bytes = sum(len(arr) for arr in corpus)
    assert total_bytes >= 4 * 1024 * 1024  # at least a few MB

