from typing import Any, Dict, List, Tuple

NEG_PREFIXES = ("¬", "not ")


def _strip_outer_parens(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    break
        else:
            return s[1:-1].strip()
    return s


def _normalize_literal(lit: Any) -> Tuple[bool, str]:
    if isinstance(lit, dict):
        atom = str(lit.get("atom", "")).strip()
        pol = bool(lit.get("polarity", True))
        return pol, atom
    if isinstance(lit, tuple) and len(lit) == 2:
        pol = bool(lit[0])
        atom = str(lit[1]).strip()
        return pol, atom
    if isinstance(lit, str):
        s = lit.strip()
        pol = True
        lowered = s.lower()
        if lowered.startswith("not "):
            pol = False
            s = s[4:].strip()
        elif s.startswith("¬"):
            pol = False
            s = s[1:].strip()
        atom = _strip_outer_parens(s)
        return pol, atom
    return True, str(lit).strip()


def detect(clauses: List[Any]) -> Dict[str, Any]:
    pos: Dict[str, List[int]] = {}
    neg: Dict[str, List[int]] = {}
    atoms = set()
    for i, lit in enumerate(clauses):
        pol, atom = _normalize_literal(lit)
        if not atom:
            continue
        atoms.add(atom)
        (pos if pol else neg).setdefault(atom, []).append(i)
    contradictions = sorted([a for a in atoms if a in pos and a in neg])
    witnesses = [
        {"atom": a, "pos": pos.get(a, []), "neg": neg.get(a, [])}
        for a in contradictions
    ]
    total_unique = len(atoms) if atoms else 1
    x_g = (len(contradictions) / total_unique) if total_unique else 0.0
    return {"contradictions": contradictions, "x_g": float(x_g), "witnesses": witnesses}


from typing import Any, Dict, List, Tuple

NEG_PREFIXES = ("¬", "not ")


def _strip_outer_parens(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        for i, ch in enumerate(s):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(s) - 1:
                    break
        else:
            return s[1:-1].strip()
    return s


def _normalize_literal(lit: Any) -> Tuple[bool, str]:
    """Return (polarity, atom) with polarity True for positive, False for negative.

    Supported forms:
      - str: 'P(a)', '¬P(a)', 'not P(a)'
      - tuple: (True/False, 'P(a)')
      - dict: {'atom': 'P(a)', 'polarity': True/False}
    """
    if isinstance(lit, dict):
        atom = str(lit.get("atom", "")).strip()
        pol = bool(lit.get("polarity", True))
        return pol, atom
    if isinstance(lit, tuple) and len(lit) == 2:
        pol = bool(lit[0])
        atom = str(lit[1]).strip()
        return pol, atom
    if isinstance(lit, str):
        s = lit.strip()
        pol = True
        lowered = s.lower()
        if lowered.startswith("not "):
            pol = False
            s = s[4:].strip()
        elif s.startswith("¬"):
            pol = False
            s = s[1:].strip()
        atom = _strip_outer_parens(s)
        return pol, atom
    return True, str(lit).strip()


def detect(clauses: List[Any]) -> Dict[str, Any]:
    """Detect contradictions and compute X_G.

    Returns dict with keys: 'contradictions' (list[str]), 'x_g' (float), 'witnesses' (list[dict]).
    Witness format: {'atom': str, 'pos': [idx...], 'neg': [idx...]}
    """
    pos: Dict[str, List[int]] = {}
    neg: Dict[str, List[int]] = {}
    atoms = set()
    for i, lit in enumerate(clauses):
        pol, atom = _normalize_literal(lit)
        if not atom:
            continue
        atoms.add(atom)
        if pol:
            pos.setdefault(atom, []).append(i)
        else:
            neg.setdefault(atom, []).append(i)

    contradictions = sorted([a for a in atoms if a in pos and a in neg])
    witnesses = [
        {"atom": a, "pos": pos.get(a, []), "neg": neg.get(a, [])}
        for a in contradictions
    ]

    total_unique = len(atoms) if atoms else 1
    x_g = (len(contradictions) / total_unique) if total_unique else 0.0

    return {"contradictions": contradictions, "x_g": float(x_g), "witnesses": witnesses}


if __name__ == "__main__":
    sample = ["P(a)", "¬P(a)", "Q", (True, "R"), {"atom": "not S", "polarity": True}]
    print(detect(sample))
