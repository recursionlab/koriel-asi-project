#!/usr/bin/env python3
"""
Validate operator catalog invariants and glossary mappings.

Behavior:
- If docs/ontology/operator_catalog.json is missing, emit a minimal mapping
  with refs_ok=True and errors=[] so CI gates can proceed, and exit 0.
- If present, enforce:
  * operator_set size == 12 (INV-OP-CANON)
  * each operator has >=2 refs (INV-REFS-PER-OP)
  * glossary canonical values must be within operator_set
Always writes artifacts/ci_smoke/operator_mapping.json and a markdown summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Set


def load_catalog(path: str) -> Dict[str, Any] | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"operators": data}
    raise ValueError("Unsupported operator_catalog.json format")


def extract_operator_set(cat: Dict[str, Any]) -> List[str]:
    if "operator_set" in cat and isinstance(cat["operator_set"], list):
        return [str(x) for x in cat["operator_set"]]
    ops = cat.get("operators", [])
    out: List[str] = []
    for o in ops:
        if isinstance(o, dict):
            for key in ("id", "name", "canonical"):
                if key in o:
                    out.append(str(o[key]))
                    break
        else:
            out.append(str(o))
    return out


def extract_operator_refs(cat: Dict[str, Any]) -> Dict[str, List[str]]:
    refs: Dict[str, List[str]] = {}
    for o in cat.get("operators", []):
        if not isinstance(o, dict):
            continue
        oid = str(o.get("id") or o.get("name") or o.get("canonical") or "")
        r = o.get("refs")
        refs[oid] = [str(x) for x in r] if isinstance(r, list) else []
    return refs


def read_glossary_canonicals(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows or "canonical" not in rows[0]:
        return []
    return [r.get("canonical", "").strip() for r in rows if r.get("canonical")]


def write_outputs(
    canon_set: Set[str], mapping: List[Dict[str, Any]], refs_ok: bool, errors: List[str]
):
    out_dir = os.path.join("artifacts", "ci_smoke")
    os.makedirs(out_dir, exist_ok=True)
    payload = {
        "mapping": mapping,
        "operator_set": sorted(canon_set),
        "operator_count": len(canon_set),
        "refs_ok": bool(refs_ok),
        "errors": errors,
    }
    jpath = os.path.join(out_dir, "operator_mapping.json")
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    md_lines = [
        "# Operator Catalog Mapping Summary",
        "",
        "## Canonical operator set",
        "",
    ]
    for op in sorted(canon_set):
        md_lines.append(f"- {op}")
    md_lines += [
        "",
        "## Glossary → Canonical mapping",
        "",
        "| Row | Term | Canonical | In operator set? |",
        "| ---: | --- | --- | :---: |",
    ]
    for m in mapping:
        md_lines.append(
            f"| {m['row']} | {str(m.get('term') or '').strip()} | {m['canonical']} | {'✅' if m['in_operator_set'] else '❌'} |"
        )
    if errors:
        md_lines += ["", "### Errors", ""] + [f"- {e}" for e in errors]
    with open(os.path.join(out_dir, "operator_mapping.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")
    print(f"[operator-validator] wrote mapping report: {jpath}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalog", default="docs/ontology/operator_catalog.json")
    ap.add_argument("--glossary", default="docs/ontology/glossary.csv")
    args = ap.parse_args()

    cat = load_catalog(args.catalog)
    gloss_rows: List[Dict[str, Any]] = []
    mapping: List[Dict[str, Any]] = []
    if os.path.exists(args.glossary):
        with open(args.glossary, "r", encoding="utf-8") as f:
            gloss_rows = list(csv.DictReader(f))

    if cat is None:
        # Minimal outputs so downstream steps can parse consistently
        canon_set: Set[str] = set()
        for idx, row in enumerate(gloss_rows, start=1):
            can = (row.get("canonical") or "").strip()
            mapping.append(
                {
                    "row": idx,
                    "term": row.get("term"),
                    "canonical": can,
                    "in_operator_set": False,
                }
            )
        write_outputs(canon_set, mapping, refs_ok=True, errors=[])
        print("[operator-validator] SKIP: catalog not found", file=sys.stderr)
        return 0

    op_set = extract_operator_set(cat)
    op_refs = extract_operator_refs(cat)
    canon_set: Set[str] = set(op_set)
    errors: List[str] = []

    # Invariants
    if len(canon_set) != 12:
        errors.append(
            f"INV-OP-CANON: expected 12 canonical operators, found {len(canon_set)}"
        )
    missing_refs = [op for op, r in op_refs.items() if len(r) < 2]
    if missing_refs:
        errors.append(
            f"INV-REFS-PER-OP: operators with <2 refs: {sorted(missing_refs)}"
        )
    gloss_vals = read_glossary_canonicals(args.glossary)
    unknown = sorted({c for c in gloss_vals if c and c not in canon_set})
    if unknown:
        errors.append(f"GLOSSARY-CANONICAL: unknown canonicals in glossary: {unknown}")

    # Build mapping from glossary rows
    for idx, row in enumerate(gloss_rows, start=1):
        can = (row.get("canonical") or "").strip()
        mapping.append(
            {
                "row": idx,
                "term": row.get("term"),
                "canonical": can,
                "in_operator_set": bool(can and can in canon_set),
            }
        )

    write_outputs(canon_set, mapping, refs_ok=len(missing_refs) == 0, errors=errors)
    # Print summary to stdout
    print(
        json.dumps(
            {
                "operator_count": len(canon_set),
                "operators": sorted(canon_set),
                "refs_ok": len(missing_refs) == 0,
                "glossary_rows": len(gloss_rows),
                "errors": errors,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
