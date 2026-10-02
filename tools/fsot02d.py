"""Shared inputs for the 2026-10-02d tools (DERIVATIONS_2026-10-02d). Leaves from golden/seed_leaves_6f9c2560.tsv; constants from the hub fsot_compute."""
import csv, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def setup(hub):
    hub = Path(hub).resolve(); sys.path.insert(0, str(hub / "vendor"))
    import fsot_compute as F  # noqa
    return hub, F

from mpmath import mpf, sqrt, pi, ln, fabs, nstr  # noqa: E402

def refs():
    out = {}
    for line in open(ROOT / "reference/published_2026-10-02.tsv", encoding="utf-8"):
        if line.startswith("#") or not line.strip(): continue
        f = line.rstrip("\n").split("\t"); f += [""] * (9 - len(f)); out[f[0]] = f
    def ref(k):
        f = out[k]
        if f[1] == "direct": return mpf(f[2]), mpf(f[3])
        p = f[1].split(":")[1].split("/"); (ca, sa), (cb, sb) = ref(p[0]), ref(p[1]); c = ca / cb
        return c, fabs(c) * sqrt((sa / ca) ** 2 + (sb / cb) ** 2)
    return ref

def leaves():
    d = {}
    for line in open(ROOT / "golden/seed_leaves_6f9c2560.tsv", encoding="utf-8"):
        if line.startswith("#"): continue
        f = line.rstrip("\n").split("\t"); d[f[0]] = mpf(f[-1])
    return d

def pins():
    d = {}
    for line in open(ROOT / "reference/pin_lineage_2026-10-02.tsv", encoding="utf-8"):
        if line.startswith("#"): continue
        f = line.rstrip("\n").split("\t"); d[f[0]] = mpf(f[5])
    return d

C_LIGHT, E_CHARGE, H_PLANCK = mpf(299792458), mpf("1.602176634e-19"), mpf("6.62607015e-34")
HBAR_EVS = H_PLANCK / (2 * pi * E_CHARGE)
HBARC_GEV_FM = H_PLANCK * C_LIGHT / (2 * pi * E_CHARGE) / mpf(10) ** 9 * mpf(10) ** 15
def kg_to_GeV(m): return m * C_LIGHT**2 / E_CHARGE / mpf(10) ** 9

def sec67(hub, F):
    """Damian's sec. 67 Nuclear muN entries: recomputed value (fsot_compute) and stored database Value."""
    db = json.load(open(hub / "vendor/fsot_aggregate/FSOT_Mathematical_Database_Unified.json", encoding="utf-8"))
    db = {e["Index"]: e for e in (db if isinstance(db, list) else db["entries"]) if isinstance(e, dict) and "Index" in e}
    forms = {1036: ("H-2", F.C_EFF ** -6 / F.A_BLEED ** 9), 1037: ("He-3", F.P_VAR ** -7 - 1 / F.C_FACTOR), 1038: ("Li-7", F.K ** 4 / F.P_BASE ** 3),
             1039: ("B-11", F.S_QUANT ** -7 + F.S_QUANT ** -6), 1040: ("C-13", F.PHI - F.G_CAT), 1041: ("N-14", F.OMEGA ** -7 + F.B_IN ** 6),
             1042: ("F-19", F.PHI ** 2), 1043: ("Na-23", F.PI - F.G_CAT), 1044: ("Al-27", F.PI ** 2 / F.E), 1045: ("P-31", F.S_QUANT ** -2 - F.CHAOS ** 3),
             1046: ("Mn-55", F.G_CAT ** -3 + F.OMEGA ** 3)}
    out = {}
    for i, (nm, v) in forms.items():
        e = db[i]; stored = mpf(e["Value"])
        use = v if fabs(v - stored) / fabs(stored) <= mpf("1e-12") else stored
        out[nm] = dict(index=i, formula=e["Description_Formula"], recomputed=v, stored=stored, value=use,
                       source="recomputed" if use is v else "stored (recompute differs)")
    return out

def compute(hub, F, GF_override=None):
    L, P = leaves(), pins()
    E, PHI, CF, THS = F.E, F.PHI, F.C_FACTOR, F.THETA_S
    v = (THS + E**3) / CF**6 / 1000 * PHI
    GF = 1 / (sqrt(2) * v * v) if GF_override is None else GF_override
    MZ, MW = L["m_Z_MeV"] / 1000, L["m_W_MeV"] / 1000
    s2, al = L["sin2_theta_W_MSbar"], 1 / L["alpha_inv"]
    als = 2 * (F.POOF / F.PSI_CON) ** 2
    G0 = GF * MZ**3 / (6 * sqrt(2) * pi)
    def width(T3, Q, Nc, quark):
        return Nc * G0 * ((T3 - 2 * Q * s2) ** 2 + T3**2) * (1 + 3 * Q**2 * al / (4 * pi)) * ((1 + als / pi) if quark else 1)
    nu = width(mpf(1) / 2, 0, 1, False); ee = width(-mpf(1) / 2, -1, 1, False)
    up = width(mpf(1) / 2, mpf(2) / 3, 3, True); dn = width(-mpf(1) / 2, -mpf(1) / 3, 3, True)
    had = 2 * up + 3 * dn; inv = 3 * nu
    A1 = 3 * ee + inv + had
    r = dict(GF=GF, v=v, MZ=MZ, MW=MW, s2=s2, alpha=al, alpha_s=als, Gamma_nunu=nu, Gamma_ee=ee, Gamma_uu=up, Gamma_dd=dn, Gamma_had=had, Gamma_inv=inv,
             Gamma_Z_A1=A1, Gamma_Z_A2=3 * ee + inv + P["wave5|R_ell"] * ee, Gamma_Z_A3=ee / P["wave8|BR_Z_ee"], Gamma_Z_A4=inv / P["wave8|BR_Z_inv"])
    r["GZ_over_MZ_A1"] = A1 / MZ
    r["sigma_had0_nb"] = 12 * pi * ee * had / (MZ**2 * A1**2) * HBARC_GEV_FM**2 * mpf(10) ** 7
    r["R_ell_A1"] = had / ee
    r["Gamma_W"] = GF * MW**3 / (6 * sqrt(2) * pi) * (3 + 2 * 3 * (1 + als / pi))
    me, mmu, mtau = kg_to_GeV(L["m_e_kg"]), kg_to_GeV(L["m_mu_kg"]), L["m_tau_MeV"] / 1000
    x = (me / mmu) ** 2
    Fx = 1 - 8 * x + 8 * x**3 - x**4 - 12 * x**2 * ln(x)
    Gmu = GF**2 * mmu**5 / (192 * pi**3) * Fx * (1 + al / (2 * pi) * (mpf(25) / 4 - pi**2))
    r["tau_mu"] = HBAR_EVS / (Gmu * mpf(10) ** 9)
    r["BR_tau_e_external"] = mpf("0.1782")
    r["tau_tau"] = r["tau_mu"] * (mmu / mtau) ** 5 * r["BR_tau_e_external"]
    mup = L["mu_p_over_mu_N"]
    r["mu_p"] = mup; r["mu_n"] = -mpf(2) / 3 * mup; r["mu_t"] = mup
    s67 = sec67(hub, F); r["sec67"] = s67; r["mu_h"] = s67["He-3"]["value"]
    r["ge_bare"] = 2 * (1 + (E / pi - ln(2)) / E**5); r["gp_bare"] = (F.A_IN * F.P_NEW / F.P_BASE) ** 2
    PD = mpf("0.0576"); muS = mup + r["mu_n"]
    r["mu_d_2N"] = muS - mpf(3) / 2 * (muS - mpf(1) / 2) * PD
    r["mu_d_2N_PD0"] = muS
    return r
