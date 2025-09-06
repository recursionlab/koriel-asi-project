import json
import os
from pathlib import Path

import torch
from torch.utils.data import Dataset


def load_corpus_bytes(paths: list[str]) -> bytes:
    """Load and concatenate all text files from given paths into bytes."""
    corpus = []

    for path_str in paths:
        path = Path(path_str)
        if path.is_dir():
            # Recursively find all .txt and .md files
            for ext in ["*.txt", "*.md"]:
                for file_path in path.rglob(ext):
                    try:
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            corpus.append(f.read())
                    except Exception as e:
                        print(f"Skipping {file_path}: {e}")
        elif path.is_file():
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    corpus.append(f.read())
            except Exception as e:
                print(f"Skipping {path}: {e}")

    # Join with newlines and encode to bytes
    full_text = "\n".join(corpus)
    return full_text.encode("utf-8", errors="ignore")


class ByteDataset(Dataset):
    """Dataset for byte-level language modeling with sliding windows."""

    def __init__(self, corpus_bytes: bytes, block_size: int = 128):
        self.data = torch.tensor(list(corpus_bytes), dtype=torch.long)
        self.block_size = block_size

    def __len__(self):
        return max(0, len(self.data) - self.block_size)

    def __getitem__(self, idx):
        # Get sequence of length block_size + 1
        chunk = self.data[idx : idx + self.block_size + 1]
        x = chunk[:-1]  # input tokens
        y = chunk[1:]  # target tokens (shifted by 1)
        return x, y


def save_corpus_cache(corpus_bytes: bytes, block_size: int, cache_dir: str):
    """Save corpus bytes and metadata to cache."""
    os.makedirs(cache_dir, exist_ok=True)

    # Save raw bytes
    with open(os.path.join(cache_dir, "corpus.bin"), "wb") as f:
        f.write(corpus_bytes)

    # Save metadata
    meta = {
        "block_size": block_size,
        "corpus_length": len(corpus_bytes),
        "vocab_size": 256,
    }
    with open(os.path.join(cache_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)


def load_corpus_cache(cache_dir: str):
    """Load corpus bytes and metadata from cache."""
    # Load raw bytes
    with open(os.path.join(cache_dir, "corpus.bin"), "rb") as f:
        corpus_bytes = f.read()

    # Load metadata
    with open(os.path.join(cache_dir, "meta.json"), "r") as f:
        meta = json.load(f)

    return corpus_bytes, meta


def get_dataset(
    data_paths: list[str], block_size: int = 128, cache_dir: str = "data/processed"
):
    """Get ByteDataset, using cache if available."""
    cache_corpus = os.path.join(cache_dir, "corpus.bin")
    cache_meta = os.path.join(cache_dir, "meta.json")

    # Check if cache exists and is fresh
    if os.path.exists(cache_corpus) and os.path.exists(cache_meta):
        try:
            corpus_bytes, meta = load_corpus_cache(cache_dir)
            if meta["block_size"] == block_size:
                print(f"Loaded corpus from cache: {len(corpus_bytes)} bytes")
                return ByteDataset(corpus_bytes, block_size), meta
        except Exception as e:
            print(f"Cache load failed: {e}, rebuilding...")

    # Build fresh corpus
    print("Building corpus from source files...")
    corpus_bytes = load_corpus_bytes(data_paths)
    save_corpus_cache(corpus_bytes, block_size, cache_dir)

    meta = {
        "block_size": block_size,
        "corpus_length": len(corpus_bytes),
        "vocab_size": 256,
    }

    print(f"Built corpus: {len(corpus_bytes)} bytes")
    return ByteDataset(corpus_bytes, block_size), meta
