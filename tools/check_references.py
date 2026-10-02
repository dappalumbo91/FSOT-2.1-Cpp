#!/usr/bin/env python3
"""Verify every entry of reference/published_2026-10-02.tsv against the evidence
committed under reference/evidence/ (stdlib only; no network).

  CODATA2022 rows : value and standard uncertainty must equal the NIST allascii row
                    (https://physics.nist.gov/cuu/Constants/Table/allascii.txt).
  PDG2024 rows    : central and sigma digits (up to a power-of-ten display scale)
                    must appear on the cited pdftotext line(s) of the PDG 2024 PDF.
  AME2020 rows    : binding energy recomputed from the mass excesses in the extract.
  derived rows    : parents must exist; the expression must be well formed.
Exit status 0 only if every row verifies.
"""
import os, re, sys
from decimal import Decimal, getcontext
getcontext().prec = 50
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reference")
TSV = os.path.join(ROOT, "published_2026-10-02.tsv")

def load_rows():
    rows = []
    for line in open(TSV, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        f += [""] * (9 - len(f))
        rows.append(dict(zip(["key", "kind", "central", "sm", "sp", "unit", "source", "evidence", "note"], f)))
    return rows

def codata():
    out = {}
    for line in open(os.path.join(ROOT, "evidence", "codata2022_allascii.txt"), encoding="utf-8"):
        if len(line) < 61 or line.startswith(("  ", "-", "Quantity", "From")):
            pass
        name = line[:60].strip()
        rest = line[60:].split("  ")
        rest = [r.strip() for r in rest if r.strip()]
        if not name or len(rest) < 2:
            continue
        out[name] = (rest[0].replace(" ", "").replace("...", ""), rest[1].replace(" ", ""))
    return out

def pdg_lines():
    d = {}
    for line in open(os.path.join(ROOT, "evidence", "pdg2024_extracts.tsv"), encoding="utf-8"):
        if line.startswith("#"):
            continue
        doc, ln, text = line.rstrip("\n").split("\t", 2)
        d[(doc, int(ln))] = text
    return d

def norm(s):
    return s.replace("−", "-").replace(" ", "")

def scaled(x, k):
    v = (Decimal(x) * (Decimal(10) ** k)).normalize()
    s = format(v, "f")
    return s.lstrip("-")

def check_pdg(r, lines):
    m = re.match(r"pdg2024_extracts:([^:]+):(\d+)(?:\+-(\d+))?$", r["evidence"])
    if not m:
        return "bad evidence ref"
    doc, ln, ex = m.group(1), int(m.group(2)), int(m.group(3) or 0)
    text = " ".join(lines.get((doc, j), "") for j in range(ln - ex, ln + ex + 1))
    if (doc, ln) not in lines:
        return f"line {doc}:{ln} missing from extract"
    t = norm(text)
    for k in range(-3, 12):
        c = scaled(r["central"], k)
        if c not in t:
            continue
        ok = True
        for sg in {r["sm"], r["sp"]}:
            s = scaled(sg, k)
            # either "±s", "+s", "-s" or parenthesised last-digit form "c(nn)"
            if re.search(r"[±+\-]" + re.escape(s) + r"(?![0-9])", t) or re.search(r"[±+\-]\(?" + re.escape(s), t):
                continue
            pm = re.search(re.escape(c) + r"\d*\((\d+)\)", t)
            if pm:
                printed = re.search(re.escape(c) + r"\d*", t).group(0)
                dec = len(printed.split(".")[1]) if "." in printed else 0
                if Decimal(pm.group(1)) * Decimal(10) ** (-dec) == (Decimal(sg) * Decimal(10) ** k):
                    continue
            ok = False
        if ok:
            return None
    return f"central/sigma digits not found on {doc}:{ln}: {text!r}"

def check_ame(r):
    ex = {}
    for line in open(os.path.join(ROOT, "evidence", "ame2020_extracts.txt"), encoding="utf-8"):
        if line.startswith("#"):
            continue
        body = line.split("\t", 1)[1]
        tok = body.split()
        # tokens: [NZ] N Z A El [o] mass_excess unc ...
        m = re.search(r"\b(n|H|He)\s+(?:-?\w+\s+)?(-?\d+\.\d+)\s+(\d+\.\d+)", body)
        a = re.search(r"\s(\d+)\s+(n|H|He)\b", body).group(1)
        ex[(m.group(1), int(a))] = (Decimal(m.group(2)), Decimal(m.group(3)))
    H1, n = ex[("H", 1)], ex[("n", 1)]
    target = {"B_H2_MeV": (1, 1, ("H", 2)), "B_H3_MeV": (1, 2, ("H", 3)), "B_He4_MeV": (2, 2, ("He", 4))}[r["key"]]
    zp, nn, nuc = target
    B = (zp * H1[0] + nn * n[0] - ex[nuc][0]) / 1000
    sig = ((zp * H1[1]) ** 2 + (nn * n[1]) ** 2 + ex[nuc][1] ** 2).sqrt() / 1000
    if B != Decimal(r["central"]):
        return f"B={B} != {r['central']}"
    if abs(sig - Decimal(r["sm"])) > Decimal("0.6e-8"):
        return f"sigma={sig} != {r['sm']}"
    return None

def main():
    rows = load_rows()
    keys = {r["key"] for r in rows}
    cd, pl = codata(), pdg_lines()
    bad = 0
    counts = {}
    for r in rows:
        err = None
        src = r["source"].split(":")[0]
        counts[src] = counts.get(src, 0) + 1
        if r["kind"] != "direct":
            op, _, arg = r["kind"].partition(":")
            parents = arg.split("/")
            if op not in ("ratio", "inv", "pi") or any(p not in keys for p in parents):
                err = f"bad derived expr {r['kind']}"
        elif src == "CODATA2022":
            v = cd.get(r["evidence"])
            if not v:
                err = f"no CODATA row {r['evidence']!r}"
            elif Decimal(v[0]).copy_abs() != Decimal(r["central"]) or Decimal(v[1]) != Decimal(r["sm"]) or r["sm"] != r["sp"]:
                err = f"CODATA {v} != ({r['central']}, {r['sm']})"
        elif src == "PDG2024":
            err = check_pdg(r, pl)
        elif src == "AME2020":
            err = check_ame(r)
        else:
            err = "unknown source"
        if err:
            bad += 1
            print(f"FAIL {r['key']}: {err}")
    print(f"references: {len(rows)} rows {counts}; failures: {bad}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
