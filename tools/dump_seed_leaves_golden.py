#!/usr/bin/env python3
"""Run the hub's own seed-check scripts and record each committed leaf value (golden for the C++ port).

The leaves are the formulas Damian committed to FSOT-2.1-Lean on 2026-09-29..10-01
(`scripts/*_seed_check.py`, documented in `docs/TOE_ACCURACY_GOALS.md`). They are not in the
pinned engine `vendor/fsot_compute.py`, so the original C++ port (which ports only the engine)
did not carry them. This tool does not re-derive anything: it executes each hub script unchanged
(with the hub's pinned `vendor/fsot_compute.py`, sha256 AEB2AD...) and parses the value it prints.

Output TSV: leaf_id  script  script_sha256  printed_key  value(50 significant digits)
Usage: tools/dump_seed_leaves_golden.py --hub <FSOT-2.1-Lean checkout at ledger_b_data_commit> --out golden/seed_leaves_6f9c2560.tsv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# leaf_id, script, regex on stdout (group 1 = value), transform
#   transform "v" = value as printed; "1+v" = 1 + printed delta;
#   ("rel", meas) = meas * (1 + printed relative error)
LEAVES = [
    ("alpha_inv", "alpha_interface_seed_check.py", r"^C_factor\^2 / P_base: interface=\S+ alpha_inv=(\S+)", "v"),
    ("g_e", "electron_g_seed_check.py", r"^A_bleed\*G_Catalan\^2\*P_base/P_new: g=(\S+)", "v"),
    ("m_e_kg", "electron_mass_seed_check.py", r"^mass=(\S+)", "v"),
    ("R_inf", "electron_mass_seed_check.py", r"^Rydberg rel=(\S+)", ("rel", "10973731.568157")),
    ("a_0", "electron_mass_seed_check.py", r"^Bohr radius rel=(\S+)", ("rel", "5.29177210544e-11")),
    ("lambda_C", "electron_mass_seed_check.py", r"^Compton rel=(\S+)", ("rel", "2.42631023538e-12")),
    ("r_e", "electron_mass_seed_check.py", r"^classical radius rel=(\S+)", ("rel", "2.8179403205e-15")),
    ("sigma_T", "electron_mass_seed_check.py", r"^Thomson rel=(\S+)", ("rel", "6.6524587051e-29")),
    ("E_h", "electron_mass_seed_check.py", r"^Hartree rel=(\S+)", ("rel", "4.359744722206e-18")),
    ("mu_B", "electron_mass_seed_check.py", r"^Bohr magneton rel=(\S+)", ("rel", "9.2740100657e-24")),
    ("m_p_over_m_e", "proton_mass_seed_check.py", r"^ratio=(\S+)", "v"),
    ("m_p_kg", "proton_mass_seed_check.py", r"^mass=(\S+)", "v"),
    ("mu_N", "proton_mass_seed_check.py", r"^nuclear_magneton=(\S+)", "v"),
    ("m_n_over_m_p", "neutron_mass_seed_check.py", r"^delta=(\S+)", "1+v"),
    ("m_n_kg", "neutron_mass_seed_check.py", r"^mass=(\S+)", "v"),
    ("G_N", "newton_g_seed_check.py", r"^G=(\S+)", "v"),
    ("g_p", "proton_g_seed_check.py", r"^g=(\S+)", "v"),
    ("m_mu_over_m_e", "muon_mass_seed_check.py", r"^ratio=(\S+)", "v"),
    ("m_mu_kg", "muon_mass_seed_check.py", r"^mass=(\S+)", "v"),
    ("u_over_m_e", "atomic_mass_seed_check.py", r"^ratio=(\S+)", "v"),
    ("u_kg", "atomic_mass_seed_check.py", r"^u=(\S+)", "v"),
    ("M_12C", "atomic_mass_seed_check.py", r"^molar=(\S+)", "v"),
    ("m_Z_MeV", "z_boson_seed_check.py", r"^z_MeV=(\S+)", "v"),
    ("m_tau_MeV", "tau_mass_seed_check.py", r"^tau_MeV=(\S+)", "v"),
    ("r_p_fm", "proton_radius_seed_check.py", r"^radius_fm=(\S+)", "v"),
    ("m_pi_pm_MeV", "charged_pion_seed_check.py", r"^mass=(\S+)", "v"),
    ("m_D_pm_MeV", "d_meson_seed_check.py", r"^mass=(\S+)", "v"),
    ("m_K_pm_MeV", "charged_kaon_seed_check.py", r"^mass=(\S+)", "v"),
    ("m_c_over_m_b", "charm_bottom_seed_check.py", r"^ratio=(\S+)", "v"),
    ("m_W_MeV", "w_boson_seed_check.py", r"^mass=(\S+)", "v"),
    ("m_W_over_m_Z", "w_over_z_seed_check.py", r"^ratio=(\S+)", "v"),
    ("m_pi_over_m_p", "pion_proton_seed_check.py", r"^ratio=(\S+)", "v"),
    ("mu_p_over_mu_N", "proton_moment_seed_check.py", r"^moment=(\S+)", "v"),
    ("m_n_minus_m_p_MeV", "neutron_proton_diff_seed_check.py", r"^difference=(\S+)", "v"),
    ("m_H_MeV", "higgs_mass_seed_check.py", r"^base_MeV=(\S+)", "v"),
    ("m_t_over_m_W", "top_w_seed_check.py", r"^ratio=(\S+)", "v"),
    ("sin2_theta_W_MSbar", "weak_mixing_seed_check.py", r"^value=(\S+)", "v"),
    ("m_tau_over_m_e", "tau_electron_seed_check.py", r"^ratio=(\S+)", "v"),
    ("dm2_32", "atmospheric_neutrino_seed_check.py", r"^atm=(\S+)", "v"),
    ("B_He4_MeV", "helium4_binding_seed_check.py", r"^leaf_vs_rounded=(\S+)", "v"),
    ("B_H3_MeV", "triton_binding_seed_check.py", r"^leaf_vs_rounded=(\S+)", "v"),
] + [
    (f"CKM_{k}", "ckm_magnitude_seed_check.py", rf"^{k}=(\S+) gap=", "v")
    for k in ("V_ud", "V_us", "V_ub", "V_cd", "V_cs", "V_cb", "V_td", "V_ts", "V_tb")
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub", required=True)
    ap.add_argument("--out", default=str(ROOT / "golden" / "seed_leaves_6f9c2560.tsv"))
    ap.add_argument("--python", default=sys.executable)
    a = ap.parse_args()
    hub = Path(a.hub).resolve()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    sha = hashlib.sha256((hub / "vendor" / "fsot_compute.py").read_bytes()).hexdigest().upper()
    if sha != pin["authority_sha256"]:
        sys.exit(f"PIN MISMATCH: hub vendor/fsot_compute.py is {sha[:6]}, expected {pin['pin_prefix']}")
    sys.path.insert(0, str(hub / "vendor"))
    import fsot_compute as F  # noqa: E402  (sets mp.prec = 169)
    mp = F.mp
    outputs: dict[str, str] = {}
    lines = [f"#seed_leaves\thub_vendor_sha256={sha}\tmp_prec={mp.prec}"]
    for leaf, script, rx, tf in LEAVES:
        path = hub / "scripts" / script
        if script not in outputs:
            r = subprocess.run([a.python, str(path)], capture_output=True, text=True, cwd=hub)
            if r.returncode != 0:
                sys.exit(f"{script} failed:\n{r.stderr}")
            outputs[script] = r.stdout
        m = re.search(rx, outputs[script], re.M)
        if not m:
            sys.exit(f"{leaf}: pattern not found in {script} output")
        v = F.mpf(m.group(1))
        if tf == "1+v":
            v = 1 + v
        elif isinstance(tf, tuple):
            v = F.mpf(tf[1]) * (1 + v)
        ssha = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
        lines.append(f"{leaf}\t{script}\t{ssha}\t{m.group(0).split('=')[0]}\t{mp.nstr(v, 50, strip_zeros=False, min_fixed=1, max_fixed=0)}")
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(lines) - 1} leaves from {len(outputs)} hub scripts, authority {sha[:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
