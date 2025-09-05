import sys, numpy as np
from src.train import run

def slope(y):
    n=len(y); x=np.arange(n); xb=x.mean(); yb=np.mean(y)
    num=((x-xb)*(y-yb)).sum(); den=((x-xb)**2).sum()+1e-12
    return float(num/den)

def main():
    m_on_plus,_  = run(seed=1340, rcce_on=True, out_prefix="LPLUS_ON",  lambda_plus=True)
    m_on_skip,_  = run(seed=1340, rcce_on=True, out_prefix="LPLUS_OFF", lambda_plus=False)
    # energy rebound higher when skipping Λ⁺
    E_tail_on  = np.mean(m_on_plus["E"][-10:])
    E_tail_off = np.mean(m_on_skip["E"][-10:])
    if not (E_tail_off > E_tail_on):
        print("FAIL: Lambda+ skip did not increase energy rebound"); sys.exit(1)
    # RC drop worse when skipping Lambda+
    s_on  = slope(m_on_plus["rc"])
    s_off = slope(m_on_skip["rc"])
    if not (s_on > s_off):
        print("FAIL: Lambda+ skip did not worsen RC slope"); sys.exit(1)
    print("PASS")

if __name__=="__main__":
    main()
