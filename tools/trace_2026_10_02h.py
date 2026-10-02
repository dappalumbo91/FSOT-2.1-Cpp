#!/usr/bin/env python3
"""Round-h TRACE tables (diagnostics, not branches): for each non-confirmed record row and open gap, the computation chain from the seeds,
S = K(T1+T2+T3) and the domain leaves down to the observable, with the cited counterpart at every step that has one. The FIRST step whose
deviation exceeds the reference uncertainty is marked BREAK. Existing frozen values only; nothing is tuned.

  python tools/trace_2026_10_02h.py --hub <FSOT-2.1-Lean @ 6f9c2560> --out audit/trace_2026-10-02h.tsv
"""
import argparse, csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsot02d as X
from fsot02d import mpf, sqrt, fabs, nstr
ap = argparse.ArgumentParser(); ap.add_argument("--hub", required=True); ap.add_argument("--out", required=True); a = ap.parse_args()
hub, F = X.setup(a.hub); ref = X.refs(); L = X.leaves(); P = X.pins(); R = Path(__file__).resolve().parents[1]
rows = []; broke = {}
def step(row, n, qty, v, c=None, s=None, src="", note=""):
    if c is None:
        rows.append([row, n, qty, nstr(v, 12) if v is not None else "none", "-", "-", src or "no physical counterpart", "-", "-",
                     "MISSING" if v is None else "no reference", note]); return
    z = fabs(v - c) / s; ppm = (v - c) / fabs(c) * 10**6
    key = row + (" [physical chain]" if str(n).startswith("P") else (" [diagnostic]" if not str(n).isdigit() else ""))
    st = "ok" if z <= 1 else ("BREAK" if key not in broke else "beyond")
    if z > 1: broke.setdefault(key, n)
    rows.append([row, n, qty, nstr(v, 12), nstr(c, 12), nstr(s, 4), src, nstr(ppm, 5), nstr(z, 4), st, note])
lin = {}
for line in open(R / "reference/pin_lineage_2026-10-02.tsv", encoding="utf-8"):
    if not line.startswith("#"): f = line.rstrip("\n").split("\t"); lin[f[0]] = [mpf(x) for x in f[1:6]]
sf = {}
for line in open(R / "audit/score_2026-10-02f.tsv", encoding="utf-8"):
    if line.startswith("#"): continue
    f = line.rstrip("\n").split("\t")
    try: sf[(f[0], f[1])] = mpf(f[3])
    except ValueError: pass
MeV = lambda kg: X.kg_to_GeV(kg) * 1000

# ---- T_CMB
r = "T_CMB"; S = F.S_COSM; d = F.DOMAINS["Cosmology"]
step(r, 1, "seeds phi, gamma, e", F.PHI, note="mathematical constants (exact)")
step(r, 2, "P_base = gamma/e", F.P_BASE)
step(r, 3, f"S_cosm = K(T1+T2+T3), Cosmology fold D_eff={d.D_eff}, look={nstr(d.delta_psi, 3)}, hits={d.hits}, observed={d.observed}", S,
     note="domain scalar; z<=1 would need |S_cosm| in [%s, %s] (+0.18 %% to +1.30 %%)" % (nstr((mpf('2.7249') - F.PHI**2) / F.P_BASE, 6), nstr((mpf('2.7261') - F.PHI**2) / F.P_BASE, 6)))
c, s = ref("T0_K"); step(r, 4, "phi^2 + P_base |S_cosm| [K]", F.PHI**2 + F.P_BASE * fabs(S), c, s, "PDG 2024 astrophysical constants (FIRAS, Fixsen 2009)",
     "first step with a counterpart; value carries a unit (K) from dimensionless seeds. D1D38A pin gave %s (z %s)" % (nstr(lin["wave1|T_CMB"][0], 10), nstr(fabs(lin["wave1|T_CMB"][0] - c) / s, 4)))
# ---- Deuteron binding
r = "Deuteron_binding_MeV"
step(r, 1, "sqrt(e)/e = e^-1/2", sqrt(F.E) / F.E)
c, s = ref("B_H2_MeV"); v = sqrt(F.E) / F.E + F.PHI
step(r, 2, "sqrt(e)/e + phi [MeV]", v, c, s, "AME2020 (1H, n, 2H mass excesses)", "value carries a unit (MeV) from dimensionless seeds")
cp, sp = ref("m_p_MeV"); cn, sn = ref("m_n_MeV"); cd, sd = ref("m_d_MeV")
step(r, "2b", "same vs CODATA 2022 m_p + m_n - m_d", v, cp + cn - cd, sqrt(sp**2 + sn**2 + sd**2), "CODATA 2022 mass energy equivalents (uncorrelated propagation)", "reference cross-check")
step(r, "P1", "physical chain: m_p (FSOT leaf) [MeV]", MeV(L["m_p_kg"]), cp, sp, "CODATA 2022")
step(r, "P2", "physical chain: m_n (FSOT leaf) [MeV]", MeV(L["m_n_kg"]), cn, sn, "CODATA 2022")
step(r, "P3", "physical chain: m_d (FSOT)", None, src="CODATA 2022 1875.61294500(58) MeV", note="no FSOT deuteron mass, scattering length or effective range exists: physical chain cannot be completed")
# ---- m_H/m_W
r = "m_H/m_W"
SQ6 = F.scalar_from_fold(D_eff=6, look=F.DOMAINS["Quantum_Mechanics"].delta_psi, hits=0, observed=True)
step(r, 1, f"S_quant, Quantum_Mechanics fold D_eff={F.DOMAINS['Quantum_Mechanics'].D_eff} (derived nest D_eff since FE23A2)", F.S_QUANT,
     note=f"with the pre-FE23A2 assigned D_eff=6: S_quant = {nstr(SQ6, 12)}")
c, s = ref("m_H_over_m_W")
step(r, 2, "S_quant (1 + psi_con)", F.S_QUANT * (1 + F.PSI_CON), c, s, "PDG 2024 m_H/m_W (derived)",
     "lineage: D1D38A %s, 3090BC %s (z %s), FE23A2..AEB2AD %s; the jump is the QM D_eff 6 -> 5 change (hub 3c74a180)" %
     (nstr(lin["wave3|m_H/m_W"][0], 10), nstr(lin["wave3|m_H/m_W"][1], 10), nstr(fabs(lin["wave3|m_H/m_W"][1] - c) / s, 3), nstr(lin["wave3|m_H/m_W"][4], 10)))
step(r, "2'", "same with D_eff=6 S_quant (diagnostic only; domain parameters are not changed)", SQ6 * (1 + F.PSI_CON), c, s, "PDG 2024 m_H/m_W (derived)", "not a branch")
cH, sH = ref("m_H_GeV"); cW, sW = ref("m_W_GeV")
step(r, "P1", "physical chain: m_H leaf [GeV]", L["m_H_MeV"] / 1000, cH, sH, "PDG 2024")
step(r, "P2", "physical chain: m_W leaf [GeV]", L["m_W_MeV"] / 1000, cW, sW, "PDG 2024")
step(r, "P3", "physical chain: m_H/m_W from leaves (= C-MHW-1, frozen-pending)", L["m_H_MeV"] / L["m_W_MeV"], c, s, "PDG 2024 m_H/m_W (derived)")
# ---- Dm2
r = "Dm2_21/Dm2_32"
step(r, 1, "gamma^3", F.GAMMA**3); step(r, 2, "Poof", F.POOF)
c, s = ref("dm2_21_over_dm2_32")
step(r, 3, "gamma^3 Poof", F.GAMMA**3 * F.POOF, c, s, "PDG 2024 Dm2_21/Dm2_32 (NO, derived)", "stored pin target 0.0295 matches neither PDG 2024 object; see DM-R1")
dm21 = (F.POOF * F.G_CAT * F.P_NEW) ** 3; c21, s21 = ref("dm2_21"); c32, s32 = ref("dm2_32")
step(r, "P1", "physical chain: seed dm2_21 = (Poof G P_new)^3 [eV^2] (hub fsot_seed_flavor.seed_dm2)", dm21, c21, s21, "PDG 2024")
step(r, "P2", "physical chain: dm2_32 leaf [eV^2]", L["dm2_32"], c32, s32, "PDG 2024", "hub seed file calls this reading dm2_31")
step(r, "P3", "physical chain: ratio (= C-DM-1, frozen-pending)", dm21 / L["dm2_32"], c, s, "PDG 2024 Dm2_21/Dm2_32 (derived)")
# ---- Gamma_Z/M_Z closed form
r = "Gamma_Z/M_Z (closed form)"
step(r, 1, "phi^5", F.PHI**5); step(r, 2, "e^6", F.E**6)
c, s = ref("Gamma_Z_over_M_Z")
step(r, 3, "phi^5/e^6", F.PHI**5 / F.E**6, c, s, "PDG 2024 Gamma_Z/M_Z (derived)", "stored target 0.02749 equals the formula's own output to 4 digits; PDG 2024 gives 0.027366")
# ---- Gamma_Z/M_Z physical (G_F) chain, round-f frozen values
r = "Gamma_Z/M_Z (G_F route, round f H1)"
ca, sa = ref("alpha_inv"); step(r, 1, "1/alpha(0) leaf", L["alpha_inv"], ca, sa, "CODATA 2022")
cz, sz = ref("m_Z_GeV"); step(r, 2, "m_Z leaf [GeV]", L["m_Z_MeV"] / 1000, cz, sz, "PDG 2024")
step(r, 3, "m_W leaf [GeV]", L["m_W_MeV"] / 1000, cW, sW, "PDG 2024")
s2F = 1 - (L["m_W_MeV"] / L["m_Z_MeV"]) ** 2; s2R = 1 - (cW / cz) ** 2; s2S = 2 * (cW / cz) ** 2 * sqrt((sW / cW) ** 2 + (sz / cz) ** 2)
step(r, 4, "s2_OS = 1 - m_W^2/m_Z^2", s2F, s2R, s2S, "PDG 2024 m_W, m_Z")
step(r, 5, "Delta alpha_lep (1+2 loop)", sf[("pieces", "Delta alpha_lep")], mpf("0.0314977"), mpf("0.0000015"), "Steinhauser 3-loop as quoted in hep-ph/0311148 eq. inputs",
     "sigma here = size of the omitted 3-loop term (about 1.5e-6), not a published uncertainty")
ch, sh = ref("Delta_alpha_had5_MZ")
step(r, 6, "Delta alpha_had^(5) H1 (constituent quark loop)", sf[("pieces", "Delta alpha_had^(5) H1")], ch, sh, "PDG 2024 EW review", "non-perturbative region; see Delta alpha_had trace")
step(r, 7, "Delta rho (one loop x QCD)", sf[("dr_H1", "Delta rho")], note="no directly published counterpart")
cr, sr = ref("Delta_r_SM"); step(r, 8, "Delta r (round f)", sf[("dr_H1", "Delta r")], cr, sr, "PDG 2024 EW review")
cg, sg = ref("G_F_GeVm2"); step(r, 9, "G_F", sf[("dr_H1", "G_F GeV^-2")], cg, sg, "CODATA 2022")
step(r, 10, "Gamma_Z/M_Z (A1 width, round f)", sf[("dr_H1", "Gamma_Z/M_Z (A1)")], c, s, "PDG 2024 (derived)")
# ---- Delta alpha_had decomposition
r = "Delta alpha_had (H1 decomposition)"
mlight = MeV(L["m_p_kg"]) / 3000
step(r, 1, "constituent light-quark mass m_p/3 [GeV]", mlight, note="no FSOT current-quark absolute mass; constituent mass is a model choice")
step(r, 2, "Delta alpha_had^(5) H1", sf[("pieces", "Delta alpha_had^(5) H1")], ch, sh, "PDG 2024 EW review (dispersive, e+e- data)", "the light-quark (u,d,s) region below ~2 GeV is non-perturbative (rho, omega, phi resonances)")
# ---- Deuteron mu
r = "Deuteron_mu_muN"
step(r, 1, "G^4", F.G_CAT**4); step(r, 2, "Poof", F.POOF)
c, s = ref("mu_d_over_mu_N"); step(r, 3, "G^4 + Poof", F.G_CAT**4 + F.POOF, c, s, "CODATA 2022")
cpm, spm = ref("mu_p_over_mu_N"); cnm, snm = ref("mu_n_over_mu_N")
step(r, "P1", "physical chain: mu_p (FSOT leaf)", L["mu_p_over_mu_N"], cpm, spm, "CODATA 2022")
step(r, "P2", "physical chain: mu_n (FSOT)", None, src="CODATA 2022 -1.91304276(45)", note="no FSOT neutron moment exists (round-f lost-route search)")
step(r, "P3", "physical chain: S-state mu_p + mu_n", None, src="CODATA: 0.87980458", note="needs P2")
step(r, "P4", "physical chain: D-state, meson-exchange and relativistic terms", None, src="CODATA: mu_d - (mu_p + mu_n) = -0.02236635",
     note="model-dependent (P_D is not an observable); no FSOT quantity")
with open(a.out, "w") as o:
    o.write("# generated by tools/trace_2026_10_02h.py (round h diagnostics; existing frozen values; FREEZE_2026-10-02h committed first)\n")
    o.write("#row\tstep\tquantity\tFSOT\treference\tsigma\tsource\tppm\tz\tstatus\tnote\n")
    for x in rows: o.write("\t".join(str(y) for y in x) + "\n")
print("first break per row:", broke)
