import argparse
import json
import numpy as np
from datasets import load_dataset
from src.model import TinyByteLM
from .utils import logprob


def evaluate_arc(model: TinyByteLM, dataset: str = "ARC-Easy", split: str = "test", limit: int | None = None) -> float:
    """Evaluate TinyByteLM on the AI2 Reasoning Challenge (ARC)."""
    ds = load_dataset("ai2_arc", dataset, split=split)
    correct = 0
    total = 0
    for ex in ds:
        q = ex["question"]
        options = ex["choices"]["text"]
        labels = ex["choices"]["label"]
        answer = ex["answerKey"]
        scores = [logprob(model, q + "\n", opt) for opt in options]
        pred = labels[int(np.argmax(scores))]
        if pred == answer:
            correct += 1
        total += 1
        if limit and total >= limit:
            break
    return correct / max(total, 1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run TinyByteLM on ARC")
    ap.add_argument("--checkpoint", type=str, default=None, help="Path to model checkpoint")
    ap.add_argument("--dataset", type=str, default="ARC-Easy", help="ARC subset: ARC-Easy or ARC-Challenge")
    ap.add_argument("--split", type=str, default="test")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    model = TinyByteLM.load(args.checkpoint) if args.checkpoint else TinyByteLM()
    acc = evaluate_arc(model, dataset=args.dataset, split=args.split, limit=args.limit)
    print(json.dumps({"task": "arc", "dataset": args.dataset, "accuracy": acc}))


if __name__ == "__main__":
    main()
