// fsot/fsotb_vm.hpp — port of the FSOTB / Metatron trinary ISA interpreter
// (FSOT-Reality-OS kernel/crates/reality_os_trinary/src/lib.rs, v0.3 kernel encoding).
// 27 opcodes (3^3), 25 registers (= D_eff ceiling), 27-trit word ABI.
// Difference from the Rust kernel: EVAL_PANEL reads the live 35-domain nest
// table (pin AEB2AD) supplied by the caller, not the stale 530-row D1D38A table.
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <span>
#include <vector>

#include "fsot/trit.hpp"

namespace fsot::fsotb {

inline constexpr std::uint32_t WORD_WIDTH_TRITS = 27;
inline constexpr std::size_t REGISTER_COUNT = 25;
inline constexpr std::size_t NUM_TASK_SLOTS = 8;
inline constexpr std::size_t STACK_DEPTH = 32;

enum class Op : std::uint8_t {
  Halt, Imm, Movt, Loadt, Storet, Addt, Subt, Mult, Negt, Min3, Max3, Collapse, EvalPanel,
  Consensus, PhaseRot, Brancht, Emit, LoadRule, ApplyOvr, Measure, Call, Ret, PushT, PopT,
  Syscall, Spawn, Join
};
inline constexpr std::uint8_t OP_COUNT = 27;

struct Instr { std::uint8_t op, a, b, c; std::int32_t imm; };
enum class Status { Ok, Halted, Error };

struct Vm {
  std::array<std::int32_t, REGISTER_COUNT> regs{};
  std::size_t pc = 0;
  Status status = Status::Ok;
  std::uint32_t steps = 0;
  std::int32_t last_emit_tag = 0;
  std::uint64_t last_emit_s_bits = 0;
  std::array<std::int32_t, STACK_DEPTH> stack{};
  std::size_t sp = 0;
  std::array<std::size_t, STACK_DEPTH> call_stack{};
  std::size_t csp = 0;
  std::uint32_t spawn_count = 0, join_count = 0, eval_count = 0;
  std::span<const double> panel_S;  // live domain scalars (nest order)

  std::int32_t reg(std::uint8_t i) const { return regs[i % REGISTER_COUNT]; }
  void set(std::uint8_t i, std::int32_t v) { regs[i % REGISTER_COUNT] = v; }
  static std::int32_t wrap(std::int64_t v) { return static_cast<std::int32_t>(static_cast<std::uint32_t>(v)); }

  Status step(std::span<const Instr> prog) {
    if (status != Status::Ok) return status;
    if (pc >= prog.size()) return status = Status::Halted;
    const Instr ins = prog[pc++];
    ++steps;
    if (ins.op >= OP_COUNT) return status = Status::Error;
    switch (static_cast<Op>(ins.op)) {
      case Op::Halt: status = Status::Halted; break;
      case Op::Imm: set(ins.a, ins.imm); break;
      case Op::Movt: case Op::Loadt: case Op::Storet: set(ins.a, reg(ins.b)); break;
      case Op::Addt: set(ins.a, wrap(std::int64_t(reg(ins.b)) + reg(ins.c))); break;
      case Op::Subt: set(ins.a, wrap(std::int64_t(reg(ins.b)) - reg(ins.c))); break;
      case Op::Mult: set(ins.a, wrap(std::int64_t(reg(ins.b)) * reg(ins.c))); break;
      case Op::Negt: set(ins.a, wrap(-std::int64_t(reg(ins.b)))); break;
      case Op::Min3: set(ins.a, std::min(reg(ins.b), reg(ins.c))); break;
      case Op::Max3: set(ins.a, std::max(reg(ins.b), reg(ins.c))); break;
      case Op::Collapse: set(ins.a, trit::sign_trit(double(reg(ins.b)))); break;
      case Op::EvalPanel: {
        if (panel_S.empty()) return status = Status::Error;
        const double s = panel_S[ins.b % panel_S.size()];
        set(ins.a, static_cast<std::int32_t>(s * 1'000'000.0));
        std::memcpy(&last_emit_s_bits, &s, sizeof s);
        last_emit_tag = ins.imm;
        ++eval_count;
        break;
      }
      case Op::Consensus: { auto x = reg(ins.b), y = reg(ins.c); set(ins.a, x == y ? x : 0); break; }
      case Op::PhaseRot: { auto v = reg(ins.b); set(ins.a, v < 0 ? 0 : (v == 0 ? 1 : -1)); break; }
      case Op::Brancht: if (reg(ins.a) != 0) pc = static_cast<std::size_t>(std::int64_t(pc) + ins.imm); break;
      case Op::Emit: last_emit_tag = ins.imm; break;
      case Op::LoadRule: case Op::ApplyOvr: case Op::Measure: case Op::Syscall: break;  // reserved
      case Op::Call:
        if (csp >= STACK_DEPTH) status = Status::Error;
        else { call_stack[csp++] = pc; pc = static_cast<std::size_t>(ins.imm); }
        break;
      case Op::Ret: if (csp == 0) status = Status::Halted; else pc = call_stack[--csp]; break;
      case Op::PushT: if (sp >= STACK_DEPTH) status = Status::Error; else stack[sp++] = reg(ins.a); break;
      case Op::PopT: if (sp == 0) status = Status::Error; else set(ins.a, stack[--sp]); break;
      case Op::Spawn: ++spawn_count; break;
      case Op::Join: ++join_count; break;
    }
    return status;
  }
  Status run(std::span<const Instr> prog, std::uint32_t max_steps) {
    for (std::uint32_t n = 0; status == Status::Ok && n < max_steps; ++n) step(prog);
    return status;
  }
};

// Boot self-test: IMM r1,3; IMM r2,4; ADDT r0,r1,r2; EVAL_PANEL r3,0; EMIT 42; HALT
inline std::array<Instr, 6> boot_selftest_program() {
  return {{{1, 1, 0, 0, 3}, {1, 2, 0, 0, 4}, {5, 0, 1, 2, 0}, {12, 3, 0, 0, 0}, {16, 0, 0, 0, 42}, {0, 0, 0, 0, 0}}};
}

}  // namespace fsot::fsotb
