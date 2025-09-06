#!/usr/bin/env python3
"""
Attempt to load a model checkpoint and tokenizer and produce a deterministic report.

Usage:
  python model_inspect.py --model-dir path/to/checkpoint --out model_report.json

Requirements:
  pip install torch transformers sentencepiece tokenizers
"""

import argparse
import json
import os
import sys
from pathlib import Path


def try_hf_load(path, report):
    try:
        import torch
        from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    except Exception as e:
        report["hf_error"] = f"transformers_import_failed: {repr(e)}"
        return False

    try:
        config = AutoConfig.from_pretrained(path, trust_remote_code=False)
        report["hf_config_present"] = True
        report["config_class"] = config.__class__.__name__
    except Exception as e:
        report["hf_config_present"] = False
        report["hf_config_error"] = repr(e)

    try:
        tokenizer = AutoTokenizer.from_pretrained(path, use_fast=True)
        report["tokenizer"] = {
            "name_or_path": getattr(tokenizer, "name_or_path", None),
            "fast": getattr(tokenizer, "is_fast", None),
            "vocab_size": getattr(tokenizer, "vocab_size", None),
        }
    except Exception as e:
        report["tokenizer_error"] = repr(e)
        tokenizer = None

    try:
        model = AutoModelForCausalLM.from_pretrained(path, low_cpu_mem_usage=True)
        # count params (note: may load lazily depending on HF version)
        param_count = sum(p.numel() for p in model.parameters())
        report["param_count"] = param_count
        report["dtype"] = str(next(model.parameters()).dtype)
        report["device"] = str(next(model.parameters()).device)
    except Exception as e:
        report["hf_model_error"] = repr(e)
        model = None

    # If we have model and tokenizer, do a single forward to inspect logits
    if model is not None and tokenizer is not None:
        try:
            model.eval()
            import torch

            prompt = "Test prompt."
            inputs = tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs, return_dict=True)
            logits = outputs.logits
            last_logits = logits[0, -1, :].float()
            probs = torch.nn.functional.softmax(last_logits, dim=-1)
            topk = torch.topk(probs, min(20, probs.shape[0]))
            top_tokens = []
            for prob, idx in zip(topk.values.tolist(), topk.indices.tolist()):
                token = tokenizer.convert_ids_to_tokens(int(idx))
                top_tokens.append({"token": token, "id": int(idx), "prob": float(prob)})
            report["sample_logits"] = top_tokens
            report["sample_prompt"] = prompt
        except Exception as e:
            report["sample_inference_error"] = repr(e)
    return True


def try_torch_state_dict(path, report):
    import torch

    # Try common checkpoint file names
    candidates = []
    p = Path(path)
    for name in [
        "pytorch_model.bin",
        "model.bin",
        "model.pt",
        "checkpoint.pt",
        "model.ckpt",
        "ckpt.pt",
    ]:
        if (p / name).exists():
            candidates.append(str(p / name))
    # Also accept a single file path
    if p.is_file():
        candidates.append(str(p))
    candidates = list(dict.fromkeys(candidates))
    if not candidates:
        report["state_dict_found"] = False
        return False
    report["state_dict_found"] = True
    report["state_dict_files"] = candidates
    total = 0
    try:
        for c in candidates:
            sd = torch.load(c, map_location="cpu")
            # sd may be a dict with 'state_dict' or 'model_state_dict' or be the state_dict itself
            if isinstance(sd, dict) and "state_dict" in sd:
                sd = sd["state_dict"]
            elif isinstance(sd, dict) and "model_state_dict" in sd:
                sd = sd["model_state_dict"]
            # iterate over tensors
            for k, v in sd.items():
                try:
                    if hasattr(v, "numel"):
                        total += v.numel()
                except Exception:
                    pass
        report["estimated_param_count_from_state_dict"] = total
    except Exception as e:
        report["state_dict_error"] = repr(e)
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-dir", "-m", required=True, help="Path to model dir or checkpoint file"
    )
    parser.add_argument(
        "--out", "-o", default="model_report.json", help="Output JSON file"
    )
    args = parser.parse_args()

    report = {
        "inspected_path": os.path.abspath(args.model_dir),
        "timestamp_utc": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "env": {"python": sys.version},
    }

    # Quick filesystem scan for typical tokenizer/checkpoint files
    p = Path(args.model_dir)
    if p.exists() and p.is_dir():
        report["contains"] = [
            str(x.relative_to(p)) for x in p.rglob("*") if x.is_file()
        ]
    elif p.exists() and p.is_file():
        report["contains"] = [str(p.name)]
    else:
        report["error"] = "path_not_found"
        print(json.dumps(report, indent=2))
        sys.exit(2)

    # Try HF load first
    try:
        hf_ok = try_hf_load(args.model_dir, report)
    except Exception as e:
        report["hf_attempt_crash"] = repr(e)
        hf_ok = False

    # If HF didn't complete, try raw state dict
    try:
        sd_ok = try_torch_state_dict(args.model_dir, report)
    except Exception as e:
        report["sd_attempt_crash"] = repr(e)
        sd_ok = False

    # Write report
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote report to {args.out}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
