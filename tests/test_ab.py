# tests/test_ab.py
import sys, json
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.ab import main
def test_ab():
    main()
    p = Path("logs/ab_summary.json")
    if not p.exists():
        print("FAIL: ab_summary.json missing"); sys.exit(1)
    j = json.loads(p.read_text())
    for k in ["RC_slope_diff_mean","Loss_slope_diff_mean","Ups_rate_diff_mean"]:
        v = j.get(k,None)
        if not isinstance(v,(int,float)):
            print("FAIL: CI fields not numeric"); sys.exit(1)
    print("PASS")
if __name__=="__main__":
    test_ab()
    print("PASS")
