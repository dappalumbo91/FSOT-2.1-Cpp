#!/usr/bin/env python3
"""Check the bare-metal demo's serial output against golden/golden_AEB2AD.tsv (50-digit hub mpmath values).
   python tools/check_kernel_serial.py serial.txt
Requires: the "DONE 35" line, all 35 domains in authority order with the golden D_eff, every printed
value (40 significant digits, ternary-rendered) within 1e-38 relative of the golden value, and the closed-form
rows ("CF i name value", all sec.* rows of the golden in order, same names; zero targets compared absolutely)."""
import sys
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 80
ROOT = Path(__file__).resolve().parents[1]
gold_S, gold_D, order, consts, gold_cf = {}, {}, [], {}, []
for line in (ROOT / "golden" / "golden_AEB2AD.tsv").read_text().splitlines():
    f = line.split("\t")
    if f[0] == "domain.S":
        gold_S[f[1]] = Decimal(f[2]); order.append(f[1])
    elif f[0] == "domain.D_eff":
        gold_D[f[1]] = int(f[2])
    elif f[0] == "const":
        consts[f[1]] = Decimal(f[2])
    elif f[0].startswith("sec."):
        gold_cf.append((f[1], Decimal(f[2])))
lines = Path(sys.argv[1]).read_text(errors="replace").splitlines()
seen, worst, bad = [], Decimal(0), 0
for l in lines:
    p = l.split()
    if p[:1] == ["ALPHA"]:
        r = abs(Decimal(p[1]) - consts["ALPHA"]) / consts["ALPHA"]
        worst = max(worst, r); bad += r > Decimal("1e-38")
    if p[:1] == ["S"]:
        name, d, v = p[1], int(p[2].split("=")[1]), Decimal(p[3])
        seen.append(name)
        r = abs(v - gold_S[name]) / abs(gold_S[name])
        worst = max(worst, r)
        if r > Decimal("1e-38") or d != gold_D[name]:
            print("MISMATCH", name, d, v, gold_S[name]); bad += 1
cf_seen, cf_worst = 0, Decimal(0)
for l in lines:
    if not l.startswith("CF "):
        continue
    head, val = l.rsplit(" ", 1)
    _, idx, name = head.split(" ", 2)
    gname, g = gold_cf[int(idx)]
    r = abs(Decimal(val) - g) / (abs(g) if g != 0 else Decimal(1))
    cf_worst = max(cf_worst, r)
    if name != gname or r > Decimal("1e-38") or int(idx) != cf_seen:
        print("CF MISMATCH", idx, name, gname, val, g); bad += 1
    cf_seen += 1
ok = "DONE 35" in lines and seen == order and bad == 0 and cf_seen == len(gold_cf) and f"DONE CF {len(gold_cf)}" in lines
print(f"kernel serial: {len(seen)} domain S values, worst relative error {float(worst):.2e}; {cf_seen}/{len(gold_cf)} closed forms, "
      f"worst {float(cf_worst):.2e} vs 50-digit golden -> {'PASS' if ok else 'FAIL'}")
sys.exit(0 if ok else 1)
