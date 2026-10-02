#!/bin/sh
# Build the bare-metal demo: ./kernel/build.sh [outdir]   (needs g++ and binutils; run from the repo root)
set -e
OUT=${1:-build-kernel}
mkdir -p "$OUT"
CXXFLAGS="-std=gnu++20 -O2 -ffreestanding -fno-exceptions -fno-rtti -fno-threadsafe-statics -fno-stack-protector
  -fno-pic -no-pie -mno-red-zone -mgeneral-regs-only -mcmodel=kernel -fno-asynchronous-unwind-tables -nostdlib -Iinclude"
# -mcmodel=kernel needs the image in the top 2 GiB; we link low (1 MiB) instead, so use the small model.
CXXFLAGS=$(echo $CXXFLAGS | sed 's/-mcmodel=kernel/-mcmodel=small/')
g++ $CXXFLAGS -c kernel/kmain.cpp -o "$OUT/kmain.o"
g++ -c kernel/boot.S -o "$OUT/boot.o"
ld -n -T kernel/linker.ld -o "$OUT/fsot_kernel64.elf" "$OUT/boot.o" "$OUT/kmain.o"
# QEMU's multiboot loader takes ELF32: re-wrap the (64-bit code) image without changing its bytes.
objcopy -O elf32-i386 "$OUT/fsot_kernel64.elf" "$OUT/fsot_kernel.elf"
if nm -u "$OUT/kmain.o" | grep -q .; then echo "undefined symbols:"; nm -u "$OUT/kmain.o"; exit 1; fi
echo "built $OUT/fsot_kernel.elf"
