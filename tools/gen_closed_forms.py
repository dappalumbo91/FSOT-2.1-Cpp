#!/usr/bin/env python3
"""Generate include/fsot/closed_forms.gen.inc from the FSOT authority.

Reads vendor/fsot_compute.py (FSOT-2.1-Lean), verifies its SHA-256 against
AUTHORITY_PIN.json, and translates every closed-form section (wave1..wave10,
validation, lepton, dynamical, neural, consciousness, homeostasis, soliton,
cross_species, trinary, predictions, chemistry_*) from Python AST to C++.

Translation is mechanical: no number is typed by hand. Python-only constructs
(f-string loops) are covered by hand snippets keyed on a hash of the exact AST
statement, so if the authority edits one of those lines generation fails loudly
instead of silently drifting.

Usage: python tools/gen_closed_forms.py --authority /path/to/fsot_compute.py
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "include" / "fsot" / "closed_forms.gen.inc"

SECTIONS = [
    "wave1", "validation_suite", "wave2", "wave3", "wave4", "wave5", "wave6", "wave7",
    "wave8", "wave9", "wave10", "lepton_ratios", "dynamical_systems", "neural_architecture",
    "consciousness_model", "homeostasis", "soliton_stdp", "cross_species", "trinary",
    "predictions", "chemistry_ionization", "chemistry_electronegativity",
    "chemistry_bond_lengths", "chemistry_bond_energies", "chemistry_molecular", "chemistry_radii",
]

MATH = {"sqrt": "m::sqrt", "ln": "m::ln", "exp": "m::exp", "sin": "m::sin", "cos": "m::cos",
        "acos": "m::acos", "floor": "m::floor", "fabs": "m::fabs"}

# Hand snippets for Python-only loop constructs, keyed by sha256(ast.dump(stmt))[:16].
SPECIAL: dict[str, str] = {}
SPECIAL_SRC = {
    # validation_suite: Richardson loop
    "richardson": (
        "for (auto [D_val, tgt] : std::array<std::pair<int, const char*>, 3>{{{4, \"1.4427\"}, {13, \"1.1397\"}, {25, \"1.0000\"}}}) {\n"
        "      const R v = m::pow(R(25) / R(D_val), lit<R>(\"0.2\"));\n"
        "      r.push_back(mk(\"Richardson_D=\" + std::to_string(D_val), \"(25/D)^0.2\", v, lit<R>(tgt)));\n"
        "    }"
    ),
    "w1_assign": "const Results w1 = wave1();",
    "w1_loop": (
        "{ int i = 24; for (const auto& w : w1) { Res x = w; x.name = \"V\" + std::to_string(i++) + \"_\" + w.name; x.sigma.reset(); r.push_back(x); } }"
    ),
    "neural_total": "R total(0); for (int i = 1; i < 7; ++i) total += R(1) / m::ipow(PHI, i);",
    "neural_layers": (
        "for (int i = 1; i < 7; ++i) {\n"
        "      const R t = (R(1) / m::ipow(PHI, i)) / total;\n"
        "      r.push_back(mk(\"Layer_\" + std::to_string(i) + \"_thickness\", \"(1/\\u03c6^\" + std::to_string(i) + \")/\\u03a3\", t));\n"
        "    }"
    ),
}


class Untranslatable(Exception):
    pass


_SRC = ""


def h(node: ast.AST) -> str:
    """Fingerprint of the exact source text of a node (independent of the Python version's AST layout)."""
    seg = ast.get_source_segment(_SRC, node)
    if seg is None:
        raise Untranslatable("no source segment")
    return hashlib.sha256(seg.encode("utf-8")).hexdigest()[:16]


def is_int_const(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) and type(n.value) is int


def int_exponent(n: ast.AST) -> int | None:
    if is_int_const(n):
        return n.value
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub) and is_int_const(n.operand):
        return -n.operand.value
    return None


def pure_int(n: ast.AST) -> bool:
    if is_int_const(n):
        return True
    if isinstance(n, ast.UnaryOp):
        return pure_int(n.operand)
    if isinstance(n, ast.BinOp):
        return pure_int(n.left) and pure_int(n.right)
    return False


def cstr(s: str) -> str:
    return json.dumps(s, ensure_ascii=True)  # \uXXXX escapes are valid C++ too


def expr(n: ast.AST) -> str:
    if isinstance(n, ast.BinOp):
        if isinstance(n.op, ast.Div) and pure_int(n):
            raise Untranslatable("pure-int true division (Python float semantics): " + ast.unparse(n))
        if isinstance(n.op, ast.Pow):
            k = int_exponent(n.right)
            if k is not None:
                return f"m::ipow({expr(n.left)}, {k})"
            return f"m::pow({expr(n.left)}, {expr(n.right)})"
        op = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}.get(type(n.op))
        if op is None:
            raise Untranslatable(ast.unparse(n))
        return f"({expr(n.left)} {op} {expr(n.right)})"
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        return f"(-{expr(n.operand)})"
    if isinstance(n, ast.Constant):
        if type(n.value) is int:
            return f"R({n.value})"
        raise Untranslatable("bare non-int constant " + repr(n.value))
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
        f = n.func.id
        if f == "mpf":
            (a,) = n.args
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                return f"lit<R>({cstr(a.value)})"
            if int_exponent(a) is not None:
                return f"R({int_exponent(a)})"
            raise Untranslatable(ast.unparse(n))
        if f in MATH:
            (a,) = n.args
            return f"{MATH[f]}({expr(a)})"
        if f == "domain_scalar":
            (a,) = n.args
            return f"domain_scalar({cstr(a.value)})"
    raise Untranslatable(ast.unparse(n))


def result_call(call: ast.Call) -> str:
    a = call.args
    if len(a) < 3 or call.keywords:
        raise Untranslatable(ast.unparse(call))
    if not (isinstance(a[0], ast.Constant) and isinstance(a[1], ast.Constant)):
        raise Untranslatable("non-literal Result name: " + ast.unparse(call))
    parts = [cstr(a[0].value), cstr(a[1].value), expr(a[2])]
    if len(a) >= 4:
        parts.append(expr(a[3]))
    if len(a) >= 5:
        sig = a[4]
        if not isinstance(sig, ast.Constant):
            raise Untranslatable(ast.unparse(sig))
        parts.append(repr(float(sig.value)))
    return f"r.push_back(mk({', '.join(parts)}));"


def stmt(s: ast.stmt, special_hashes: dict[str, str], declared: set[str]) -> str:
    key = h(s)
    if key in special_hashes:
        return SPECIAL_SRC[special_hashes[key]]
    if isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name):
        name = s.targets[0].id
        if isinstance(s.value, ast.List) and not s.value.elts:
            return "Results r;"
        if name in declared:
            return f"{name} = {expr(s.value)};"
        declared.add(name)
        return f"R {name} = {expr(s.value)};"
    if isinstance(s, ast.Expr) and isinstance(s.value, ast.Call):
        c = s.value
        if (isinstance(c.func, ast.Attribute) and c.func.attr == "append"
                and isinstance(c.args[0], ast.Call) and getattr(c.args[0].func, "id", "") == "Result"):
            return result_call(c.args[0])
    if isinstance(s, ast.Return):
        return "return r;"
    if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
        return ""  # docstring
    raise Untranslatable(f"[{key}] " + ast.unparse(s).splitlines()[0])


CROSS_SPECIES = r'''  // cross_species: hand-ported (dataclass loop). Same Neuroscience nest; species carry counts only.
  Results cross_species() const {
    struct Sp { const char* name; double neurons; double volume_cm3; };
    static constexpr Sp SPECIES[] = {{"Human", 86e9, 1200}, {"Octopus", 500e6, 10}, {"Corvid", 2e9, 10},
                                     {"Honeybee", 960e3, 1}, {"C_elegans", 302, 0.001}};
    const R s = domain_scalar("Neuroscience");
    const int d = derived_D_eff("Neuroscience");
    Results r;
    for (const auto& sp : SPECIES) {
      // mpf(float) is the exact binary value of the double, as in Python.
      const R density = R(sp.neurons) / (m::fabs(s) * R(sp.volume_cm3));
      r.push_back(mk(std::string("S(") + sp.name + ")", "S_neuro D=" + std::to_string(d), s));
      r.push_back(mk(std::string("Density(") + sp.name + ")", "N/(|S_neuro|\u00b7V)", density));
    }
    return r;
  }
'''

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--authority", required=True)
    args = ap.parse_args()
    src_bytes = Path(args.authority).read_bytes()
    sha = hashlib.sha256(src_bytes).hexdigest().upper()
    pin = json.loads((ROOT / "AUTHORITY_PIN.json").read_text())
    if sha != pin["authority_sha256"]:
        print(f"PIN MISMATCH: authority sha {sha[:6]} != expected {pin['pin_prefix']}", file=sys.stderr)
        return 2
    global _SRC
    _SRC = src_bytes.decode("utf-8")
    tree = ast.parse(_SRC)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    # Bind hand snippets to exact AST statements.
    special_hashes: dict[str, str] = {}
    vs = funcs["validation_suite"].body
    for s in vs:
        if isinstance(s, ast.For) and "Richardson" in ast.unparse(s):
            special_hashes[h(s)] = "richardson"
        if isinstance(s, ast.Assign) and ast.unparse(s) == "w1 = wave1()":
            special_hashes[h(s)] = "w1_assign"
        if isinstance(s, ast.For) and "enumerate(w1, 24)" in ast.unparse(s):
            special_hashes[h(s)] = "w1_loop"
    for s in funcs["neural_architecture"].body:
        if isinstance(s, ast.Assign) and ast.unparse(s) == "total = sum((1 / PHI ** i for i in range(1, 7)))":
            special_hashes[h(s)] = "neural_total"
        if isinstance(s, ast.For) and "thickness" in ast.unparse(s):
            special_hashes[h(s)] = "neural_layers"
    expected_specials = {"richardson", "w1_assign", "w1_loop", "neural_total", "neural_layers"}
    if set(special_hashes.values()) != expected_specials:
        print("special statements changed in authority:", expected_specials - set(special_hashes.values()), file=sys.stderr)
        return 3
    # Recorded fingerprint of the exact special statements (fail loudly if edited).
    fp = hashlib.sha256("".join(sorted(special_hashes)).encode()).hexdigest()[:16]
    cs_fp = h(funcs["cross_species"]) + h(next(n for n in tree.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "SPECIES"))

    out = [
        "// AUTO-GENERATED by tools/gen_closed_forms.py — do not edit.",
        f"// Authority: vendor/fsot_compute.py sha256 {sha} (pin {sha[:6]})",
        f"// Special-statement fingerprint {fp}; cross_species fingerprint {cs_fp}",
        "",
    ]
    errors = []
    counts = {}
    for name in SECTIONS:
        if name == "cross_species":
            out.append(CROSS_SPECIES)
            continue
        fn = funcs[name]
        body = []
        declared: set[str] = set()
        for s in fn.body:
            try:
                line = stmt(s, special_hashes, declared)
            except Untranslatable as exc:
                errors.append(f"{name}: {exc}")
                continue
            if line:
                body.append("    " + line)
        counts[name] = sum(1 for b in body if "push_back(mk(" in b)
        out.append(f"  Results {name}() const {{")
        out.extend(body)
        out.append("  }")
        out.append("")
    out.append("  // Ordered list of every section, matching full_report() in the authority.")
    out.append("  std::vector<std::pair<const char*, Results (Engine::*)() const>> sections() const {")
    out.append("    return {" + ", ".join(f'{{"{n}", &Engine::{n}}}' for n in SECTIONS) + "};")
    out.append("  }")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(SECTIONS)} sections, pin {sha[:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
