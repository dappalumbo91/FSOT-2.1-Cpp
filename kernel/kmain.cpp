// FSOT bare-metal demo (x86_64, no OS, no libc): evaluates the FSOT 2.1 core in balanced ternary
// (BTFloat<110>, about 52 decimal digits) and prints the 35 domain scalars S and the 368 closed-form rows
// over COM1, then exits QEMU
// through the isa-debug-exit device. Every arithmetic operation on S is ternary (two bit-planes per word).
#include "fsot/core.hpp"

using namespace fsot;
using F = bt::BTFloat<110>;

static inline void outb(unsigned short port, unsigned char v) { asm volatile("outb %0, %1" : : "a"(v), "Nd"(port)); }
static inline unsigned char inb(unsigned short port) { unsigned char v; asm volatile("inb %1, %0" : "=a"(v) : "Nd"(port)); return v; }
static void serial_init() {
  outb(0x3F9, 0x00); outb(0x3FB, 0x80); outb(0x3F8, 0x01); outb(0x3F9, 0x00); outb(0x3FB, 0x03); outb(0x3FA, 0xC7); outb(0x3FC, 0x0B);
}
static void putc(char c) { while (!(inb(0x3FD) & 0x20)) {} outb(0x3F8, (unsigned char)c); }
static void puts(const char* s) { while (*s) putc(*s++); }
static void putint(long long v) {
  char b[24]; int n = 0;
  if (v < 0) { putc('-'); v = -v; }
  do { b[n++] = char('0' + v % 10); v /= 10; } while (v);
  while (n) putc(b[--n]);
}

// Closed-form sink: "CF <index> <name> <value>" (40 significant digits, ternary-rendered).
struct SerialSink {
  int n = 0;
  void operator()(const core::CfRow<F>& r) {
    char nb[160], vb[160];
    core::cf_name(r, nb, sizeof nb);
    core::to_decimal(r.value, 40, vb, sizeof vb);
    puts("CF "); putint(n++); putc(' '); puts(nb); putc(' '); puts(vb); putc('\n');
  }
};

extern "C" {
// the compiler may emit these for struct copies
void* memcpy(void* d, const void* s, unsigned long n) { auto* a = (unsigned char*)d; auto* b = (const unsigned char*)s; while (n--) *a++ = *b++; return d; }
void* memset(void* d, int c, unsigned long n) { auto* a = (unsigned char*)d; while (n--) *a++ = (unsigned char)c; return d; }
void* memmove(void* d, const void* s, unsigned long n) {
  auto* a = (unsigned char*)d; auto* b = (const unsigned char*)s;
  if (a < b) while (n--) *a++ = *b++; else { a += n; b += n; while (n--) *--a = *--b; }
  return d;
}
int memcmp(const void* x, const void* y, unsigned long n) { auto* a = (const unsigned char*)x; auto* b = (const unsigned char*)y; for (; n; --n, ++a, ++b) if (*a != *b) return *a - *b; return 0; }

void kmain() {
  serial_init();
  puts("FSOT-2.1-Cpp bare-metal x86_64 | authority pin AEB2AD | balanced ternary BTFloat<110>\n");
  core::CoreEngine<F> eng;  // seeds, layer 1, layer 2: all ternary
  char buf[160];
  core::to_decimal(eng.ALPHA, 40, buf, sizeof buf);
  puts("ALPHA "); puts(buf); putc('\n');
  for (int i = 0; i < core::DOMAIN_COUNT; ++i) {
    const F s = eng.domain_scalar(i);
    core::to_decimal(s, 40, buf, sizeof buf);
    puts("S "); puts(core::NEST[i].name); puts(" D_eff="); putint(eng.derived_D_eff(i)); putc(' '); puts(buf); putc('\n');
  }
  puts("DONE 35\n");
  SerialSink sink;  // the 26 closed-form sections (closed_forms_core.gen.inc), also all ternary
  eng.all_sections(sink);
  puts("DONE CF "); putint(sink.n); putc('\n');
  outb(0xF4, 0x10);  // isa-debug-exit: QEMU exits with status (0x10 << 1) | 1 = 33
  for (;;) asm volatile("hlt");
}
}
