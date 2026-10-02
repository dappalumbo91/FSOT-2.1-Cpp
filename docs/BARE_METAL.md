# Bare-metal demo: the 35 domain scalars and 368 closed-form rows in balanced ternary on x86_64

`kernel/` holds a freestanding x86_64 kernel with no OS and no libc. It boots under QEMU, evaluates the
FSOT 2.1 core in balanced ternary and prints over COM1 the 35 domain scalars S, then every closed-form row of the 26 sections (`CF i name value`, 368 rows, ending in `DONE CF 368`).

```sh
./kernel/build.sh build-kernel
qemu-system-x86_64 -m 64 -kernel build-kernel/fsot_kernel.elf -serial stdio -display none -no-reboot \
  -monitor none -device isa-debug-exit,iobase=0xf4,iosize=0x04      # exits with status 33 when done
python3 tools/check_kernel_serial.py serial.txt                      # compare with the 50-digit golden
```

## Pieces

- **`include/fsot/core.hpp`** contains the freestanding `CoreEngine<R>`:
  - seeds, layers 1–2, the 35-domain nest, D_eff, look/hits/observed, and S = K(T1+T2+T3);
  - a ternary-only decimal renderer;
  - all 26 closed-form sections (Milestone 3). They are generated into `include/fsot/closed_forms_core.gen.inc` by `tools/gen_closed_forms.py`, with no heap or strings, and include `bt::acos` and the cross-species exact decimals. `tests/test_core_closed_forms.cpp` (CTest `core_closed_forms_vs_golden`) checks all 368 rows, names and order against the golden; the worst relative error is 1.0e−46.
  - It needs no heap, exceptions, RTTI, `<string>`, `<vector>` or libm. With R = `BTFloat<110>`, every operation is ternary: two bit-planes per word, ternary carry, ternary range reduction.
  - Operation order matches `Engine`. `tests/test_core.cpp` (CTest `core_vs_engine`) checks that all 35 S are **bit-identical** to `Engine<BTFloat<P>>` for P = 40, 72 and 110, and that the D_eff rungs match `derived_D_eff`.
- **`kernel/boot.S`** is the multiboot v1 header and the 32 → 64-bit trampoline:
  - identity-maps 1 GiB with 2 MiB pages;
  - enables PAE, LME and paging, then far-jumps to long mode.
- **`kernel/kmain.cpp`** handles serial output, `mem*` and the isa-debug-exit device.
  - Build flags: `-ffreestanding -fno-exceptions -fno-rtti -mgeneral-regs-only -mno-red-zone`. No SSE/x87 is used anywhere, so the binary contains no binary floating point.
  - `build.sh` fails if the object has any undefined symbol.
  - QEMU's multiboot loader only accepts ELF32, so the 64-bit image is re-wrapped with `objcopy -O elf32-i386`. The bytes are unchanged.
- **CI job `bare-metal`** builds the kernel, boots it under QEMU (120 s timeout), requires exit status 33, and runs `tools/check_kernel_serial.py`.

## Result (pin AEB2AD; output in `docs/bare_metal_serial_AEB2AD.txt`)

- Under QEMU TCG on the box, boot to exit took about 1.6 s.
- All 35 S values plus ALPHA, then the 368 closed-form rows, were printed to 40 significant digits.
- Closed-form rows: worst relative error against the 50-digit golden is 4.7e−40 (local QEMU run, exit 33).
- The worst relative error against the 50-digit hub golden is **7.6e−41**. That is the limit of the 40-digit print; BTFloat<110> itself carries about 52 digits.
- The D_eff rungs and the domain order match the authority.
