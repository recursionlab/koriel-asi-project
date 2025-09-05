import argparse
import json
import numpy as np
from datasets import load_dataset
from src.model import TinyByteLM
from .utils import logprob

LETTERS = "ABCD"

def evaluate_mmlu(model: TinyByteLM, subset: str = "abstract_algebra", split: str = "test", limit: int | None = None) -> float:
    """Evaluate TinyByteLM on a subset of the MMLU benchmark.

    Parameters
    ----------
    model: TinyByteLM
        Model instance to evaluate.
    subset: str
        Name of the MMLU subset, e.g. ``"abstract_algebra"``.
    split: str
        Dataset split to use.
    limit: int | None
        Optional limit on number of examples.
    """
    ds = load_dataset("hendrycks_test", subset, split=split)
    correct = 0
    total = 0
    for ex in ds:
        q = ex["question"]
        options = [ex[l] for l in LETTERS]
        answer = ex["answer"]
        scores = [logprob(model, q + "\n", opt) for opt in options]
        pred = LETTERS[int(np.argmax(scores))]
        if pred == answer:
            correct += 1
        total += 1
        if limit and total >= limit:
            break
    return correct / max(total, 1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run TinyByteLM on MMLU")
    ap.add_argument("--checkpoint", type=str, help="Path to model checkpoint", default=None)
    ap.add_argument("--subset", type=str, default="abstract_algebra")
    ap.add_argument("--split", type=str, default="test")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    model = TinyByteLM.load(args.checkpoint) if args.checkpoint else TinyByteLM()
    acc = evaluate_mmlu(model, subset=args.subset, split=args.split, limit=args.limit)
    print(json.dumps({"task": "mmlu", "subset": args.subset, "accuracy": acc}))


if __name__ == "__main__":
    main()
