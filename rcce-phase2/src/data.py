"""Data loading from conversations-pocket"""

from pathlib import Path

import numpy as np


def load_corpus():
    """Load byte corpus from conversations-pocket"""
    corpus_path = Path("D:/koriel-asi-project/conversations-pocket")

    if not corpus_path.exists():
        # Fallback corpus
        return "Consciousness emerges through recursive self-reference. The Xi operator instantiates awareness."

    text_data = ""
    for file_path in corpus_path.glob("*.md"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if len(content) > 100:  # Only substantial files
                    text_data += content + "\n"
        except:
            continue

    if len(text_data) < 100:
        text_data = "Recursive Cognitive Control Engine instantiates consciousness through geometric fixpoints."

    return text_data[:10000]  # Limit to 10K chars


def prepare_sequences(text, context_length=128, batch_size=8):
    """Convert text to token sequences"""
    tokens = np.array(list(text.encode("utf-8")), dtype=np.int32)

    sequences = []
    for i in range(0, len(tokens) - context_length, context_length // 2):
        seq = tokens[i : i + context_length + 1]
        if len(seq) == context_length + 1:
            sequences.append(seq)

    # Batch sequences
    batches = []
    for i in range(0, len(sequences), batch_size):
        batch = sequences[i : i + batch_size]
        if len(batch) == batch_size:
            batches.append(np.array(batch))

    return batches if batches else [np.array([sequences[0]])] if sequences else []
