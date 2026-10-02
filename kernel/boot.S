/* Multiboot v1 entry (QEMU -kernel loads ELF32), 32-bit -> 64-bit long-mode trampoline.
   Identity-maps the first 1 GiB with 2 MiB pages, enables PAE + LME + paging, far-jumps to 64-bit code. */
    .set MB_MAGIC, 0x1BADB002
    .set MB_FLAGS, 0x00000003            /* align modules, provide memory map */
    .section .multiboot, "a"
    .align 4
    .long MB_MAGIC
    .long MB_FLAGS
    .long -(MB_MAGIC + MB_FLAGS)

    .section .bss
    .align 4096
pml4:   .skip 4096
pdpt:   .skip 4096
pd:     .skip 4096
    .align 16
stack_bottom: .skip 262144
stack_top:

    .section .rodata
    .align 8
gdt64:
    .quad 0
    .quad 0x00AF9A000000FFFF                /* 64-bit code segment */
    .quad 0x00CF92000000FFFF                /* data segment */
gdt64_ptr:
    .word gdt64_ptr - gdt64 - 1
    .long gdt64

    .section .text
    .code32
    .global _start
_start:
    cli
    mov $stack_top, %esp
    /* PML4[0] -> PDPT, PDPT[0] -> PD, PD[i] = i*2MiB | present|writable|huge */
    mov $pdpt, %eax
    or $3, %eax
    mov %eax, pml4
    mov $pd, %eax
    or $3, %eax
    mov %eax, pdpt
    xor %ecx, %ecx
1:  mov %ecx, %eax
    shl $21, %eax
    or $0x83, %eax
    mov %eax, pd(,%ecx,8)
    inc %ecx
    cmp $512, %ecx
    jne 1b
    mov $pml4, %eax
    mov %eax, %cr3
    mov %cr4, %eax
    or $0x20, %eax                          /* PAE */
    mov %eax, %cr4
    mov $0xC0000080, %ecx                   /* EFER */
    rdmsr
    or $0x100, %eax                         /* LME */
    wrmsr
    mov %cr0, %eax
    or $0x80000001, %eax                    /* PG | PE */
    mov %eax, %cr0
    lgdt gdt64_ptr
    ljmp $0x08, $long_mode

    .code64
long_mode:
    mov $0x10, %ax
    mov %ax, %ds
    mov %ax, %es
    mov %ax, %ss
    mov %ax, %fs
    mov %ax, %gs
    mov $stack_top, %rsp
    call kmain
2:  hlt
    jmp 2b
