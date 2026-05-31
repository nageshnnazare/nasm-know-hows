# Topic 25: ELF Binary Format

## Overview

Every executable you create with NASM is an **ELF** (Executable and Linkable Format) file. This topic dissects the ELF format completely — showing how your assembly source becomes bytes on disk, how the linker combines object files, and how the kernel's ELF loader maps your program into memory and starts execution.

```
Your workflow:
  hello.asm  →(nasm)→  hello.o  →(ld)→  hello
  
  Source         Object file       Executable
  (text)         (ELF relocatable) (ELF executable)
                 
What's inside each:
  hello.o:  ELF header + section headers + .text + .data + .symtab + .rela.text
  hello:    ELF header + program headers + segments (.text+.rodata, .data+.bss)
```

---

## Part 1: ELF File Structure

### High-Level Layout

```
ELF Executable:
┌────────────────────────────┐ Offset 0
│     ELF Header (64 bytes)  │ Magic number, type, entry point, etc.
├────────────────────────────┤
│  Program Header Table      │ Describes segments for loading
│  (array of Phdr entries)   │ (used by kernel/loader at runtime)
├────────────────────────────┤
│                            │
│  Segment 1: .text + .rodata│ (LOAD, R-X)
│                            │
├────────────────────────────┤
│                            │
│  Segment 2: .data + .bss   │ (LOAD, RW-)
│                            │
├────────────────────────────┤
│  Section Header Table      │ Describes sections for linking/debugging
│  (array of Shdr entries)   │ (used by linker, debugger, objdump)
├────────────────────────────┤
│  .symtab (symbol table)    │ Function/variable names and addresses
├────────────────────────────┤
│  .strtab (string table)    │ Null-terminated name strings
├────────────────────────────┤
│  .shstrtab                 │ Section name strings
└────────────────────────────┘

Key distinction:
  Sections: logical units (.text, .data, .bss) — for linking/debugging
  Segments: loadable chunks — for execution (kernel only reads these)
  One segment typically contains multiple sections
```

### The ELF Header

```nasm
; The ELF header is the first 64 bytes of any ELF file (x86-64)
; You can craft one manually to make a minimal executable:

; ELF header structure (Elf64_Ehdr):
;   e_ident[16]    Magic + class + endian + version + OS/ABI
;   e_type         ET_EXEC=2, ET_DYN=3, ET_REL=1
;   e_machine      EM_X86_64 = 0x3E
;   e_version      EV_CURRENT = 1
;   e_entry        Virtual address of entry point (_start)
;   e_phoff        Offset to program header table
;   e_shoff        Offset to section header table
;   e_flags        Processor-specific flags (0 for x86-64)
;   e_ehsize       Size of ELF header (64 bytes)
;   e_phentsize    Size of one program header entry (56 bytes)
;   e_phnum        Number of program headers
;   e_shentsize    Size of one section header entry (64 bytes)
;   e_shnum        Number of section headers
;   e_shstrndx     Index of .shstrtab section header

; Minimal ELF executable (no linker, no sections — just raw bytes!)
; This is a valid Linux x86-64 executable:

BITS 64
ORG 0x400000               ; Load address

; === ELF Header (64 bytes) ===
elf_header:
    db 0x7F, "ELF"         ; e_ident[0..3]: magic number
    db 2                    ; e_ident[4]: ELFCLASS64
    db 1                    ; e_ident[5]: ELFDATA2LSB (little-endian)
    db 1                    ; e_ident[6]: EV_CURRENT
    db 0                    ; e_ident[7]: ELFOSABI_NONE
    dq 0                    ; e_ident[8..15]: padding
    dw 2                    ; e_type: ET_EXEC (executable)
    dw 0x3E                 ; e_machine: EM_X86_64
    dd 1                    ; e_version: EV_CURRENT
    dq _start              ; e_entry: entry point address
    dq phdr - $$           ; e_phoff: program header offset
    dq 0                    ; e_shoff: no section headers
    dd 0                    ; e_flags
    dw 64                   ; e_ehsize: ELF header size
    dw 56                   ; e_phentsize: program header entry size
    dw 1                    ; e_phnum: one program header
    dw 64                   ; e_shentsize
    dw 0                    ; e_shnum: no section headers
    dw 0                    ; e_shstrndx

; === Program Header (56 bytes) ===
phdr:
    dd 1                    ; p_type: PT_LOAD
    dd 5                    ; p_flags: PF_R | PF_X (read + execute)
    dq 0                    ; p_offset: start of file
    dq 0x400000             ; p_vaddr: virtual address
    dq 0x400000             ; p_paddr: physical address (ignored)
    dq file_size            ; p_filesz: size in file
    dq file_size            ; p_memsz: size in memory
    dq 0x200000             ; p_align: alignment

; === Code starts here ===
_start:
    ; Write "Hi\n"
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    lea rsi, [rel message]
    mov rdx, 3              ; length
    syscall

    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall

message:
    db "Hi", 10

file_size equ $ - $$
; Total file size: ~170 bytes! (smallest valid ELF executable)
```

---

## Part 2: Object Files (.o) — Relocatable ELF

### What NASM Produces

```
$ nasm -f elf64 hello.asm -o hello.o
$ readelf -h hello.o

ELF Header:
  Type:          REL (Relocatable file)   ← Not executable yet!
  Entry:         0x0                       ← No entry point
  
$ readelf -S hello.o

Section Headers:
  [0]             NULL
  [1] .text       PROGBITS   ALLOC EXEC    ← Your code
  [2] .data       PROGBITS   ALLOC WRITE   ← Initialized data
  [3] .bss        NOBITS     ALLOC WRITE   ← Uninitialized data
  [4] .symtab     SYMTAB                    ← Symbol table
  [5] .strtab     STRTAB                    ← String table
  [6] .rela.text  RELA                      ← Relocation entries
  [7] .shstrtab   STRTAB                    ← Section name strings
```

### Relocations — Why Object Files Need the Linker

```nasm
; In hello.o, addresses are NOT final:
; 
; section .data
;     msg db "Hello", 10
;
; section .text
;     global _start
; _start:
;     mov rax, 1
;     mov rdi, 1
;     mov rsi, msg        ← Address of msg is UNKNOWN at assembly time!
;     mov rdx, 6
;     syscall
;
; NASM emits a relocation entry:
;   "At offset X in .text, patch in the address of symbol 'msg'"
;
; Relocation entry (Elf64_Rela):
;   r_offset:  offset in section where fix is needed
;   r_info:    symbol index + relocation type
;   r_addend:  adjustment value
;
; When the linker assigns final addresses, it:
;   1. Places .text at 0x401000, .data at 0x402000
;   2. Finds msg is at 0x402000
;   3. Patches the mov instruction with the correct address

; Common relocation types for x86-64:
;   R_X86_64_64      — absolute 64-bit address
;   R_X86_64_PC32    — PC-relative 32-bit (for RIP-relative addressing)
;   R_X86_64_PLT32   — PLT entry for function calls
;   R_X86_64_GOTPCREL — GOT entry for global data access
```

### Examining Relocations

```nasm
; Example: calling an external function from assembly

; In mylib.asm:
section .text
    global add_numbers
add_numbers:
    mov rax, rdi
    add rax, rsi
    ret

; In main.asm:
section .text
    extern add_numbers      ; Defined elsewhere
    global _start
_start:
    mov rdi, 10
    mov rsi, 20
    call add_numbers        ; ← Generates R_X86_64_PLT32 relocation
    ; Linker patches the call target with actual address

    mov rdi, rax
    mov rax, 60
    syscall

; Build:
; nasm -f elf64 mylib.asm -o mylib.o
; nasm -f elf64 main.asm -o main.o
; ld main.o mylib.o -o program
;
; readelf -r main.o shows:
;   Offset    Type              Symbol
;   0x000010  R_X86_64_PLT32    add_numbers - 4
;
; The linker resolves this to the actual address of add_numbers
```

---

## Part 3: The Linker (ld) — Combining Object Files

### What the Linker Does

```
Input: main.o, lib.o, libc.a, libm.so
Output: executable (or shared library)

Steps:
1. Symbol Resolution
   - Collect all symbol definitions and references
   - Match each reference to exactly one definition
   - Error if: undefined symbol, multiple definitions
   
2. Section Merging
   - Combine all .text sections into one .text segment
   - Combine all .data sections into one .data segment
   - Apply linker script rules for ordering
   
3. Address Assignment
   - Assign virtual addresses to each section
   - Default text starts at 0x401000 (Linux x86-64)
   - Data follows text, aligned to page boundary
   
4. Relocation
   - For each relocation entry: compute final address
   - Patch the instruction bytes with resolved addresses
   
5. Output
   - Write ELF header with entry point
   - Write program headers for kernel loader
   - Write merged sections
   - Write section headers (for debugging)
```

### Linker Script (How Addresses Are Assigned)

```nasm
; Default linker script places sections at these addresses:
; (simplified view of `ld --verbose` output)
;
; SECTIONS {
;   . = 0x400000 + SIZEOF_HEADERS;
;   .text : { *(.text) }
;   .rodata : { *(.rodata) }
;   . = ALIGN(0x1000);        /* Page-align data segment */
;   .data : { *(.data) }
;   .bss : { *(.bss) }
; }
;
; Custom linker script for embedded/OS development:
; ld -T my_linker.ld main.o -o kernel.bin

; Example: placing code at a specific address (for a bootloader)
; linker.ld:
; ENTRY(_start)
; SECTIONS {
;   . = 0x7C00;              /* BIOS loads bootsector here */
;   .text : { *(.text) }
;   .data : { *(.data) }
;   . = 0x7C00 + 510;
;   .sig : { SHORT(0xAA55) } /* Boot signature */
; }
```

---

## Part 4: Program Headers — Runtime Loading

### Segments vs Sections

```
Linking (sections):                 Loading (segments):
┌──────────────┐                    ┌──────────────────────┐
│ .text        │──┐                 │ LOAD Segment 1 (R-X) │
│ .rodata      │──┤── merged ──→    │  (.text + .rodata)   │
├──────────────┤  │                 └──────────────────────┘
│ .data        │──┤── merged ──→    ┌──────────────────────┐
│ .bss         │──┘                 │ LOAD Segment 2 (RW-) │
├──────────────┤                    │  (.data + .bss)      │
│ .symtab      │                    └──────────────────────┘
│ .strtab      │── NOT loaded (only used by tools)
│ .debug_*     │
└──────────────┘

The kernel only reads PROGRAM HEADERS (segments).
Section headers are optional for execution!
(You can strip them: strip --strip-all ./program)
```

### Program Header Types

```nasm
; Common program header types:
;
; PT_LOAD (1):     Loadable segment — kernel mmaps this into memory
; PT_DYNAMIC (2):  Dynamic linking information (.dynamic section)
; PT_INTERP (3):   Path to dynamic linker ("/lib64/ld-linux-x86-64.so.2")
; PT_NOTE (4):     Auxiliary information (build ID, etc.)
; PT_GNU_STACK (0x6474e551): Stack executability flag
; PT_GNU_RELRO (0x6474e552): Read-only after relocation

; readelf -l output for a typical static executable:
;
; Program Headers:
;   Type    Offset   VirtAddr           PhysAddr           FileSiz  MemSiz   Flg Align
;   LOAD    0x000000 0x0000000000400000 0x0000000000400000 0x000200 0x000200 R   0x1000
;   LOAD    0x001000 0x0000000000401000 0x0000000000401000 0x000035 0x000035 R E 0x1000
;   LOAD    0x002000 0x0000000000402000 0x0000000000402000 0x000010 0x000018 RW  0x1000
;                                                                                    ↑
;                                                     MemSiz > FileSiz = BSS (zero-filled)
```

---

## Part 5: Dynamic Linking

### How Shared Libraries Work

```
Static linking:
  All code copied into executable at link time
  Large executable, no external dependencies
  
Dynamic linking:
  Only stubs included; actual code loaded at runtime
  Small executable, depends on .so files being present
  Allows library updates without recompiling
  
At runtime:
1. Kernel loads your program
2. Kernel sees PT_INTERP → loads dynamic linker (ld-linux-x86-64.so.2)
3. Dynamic linker reads PT_DYNAMIC segment
4. Loads required shared libraries (.so files)
5. Performs relocations (patches GOT/PLT entries)
6. Calls your _start (or __libc_start_main for C programs)
```

### The GOT and PLT

```
GOT (Global Offset Table):
  Array of pointers to external symbols
  Initially points to PLT resolver stub
  After first call: patched to point to actual function
  
PLT (Procedure Linkage Table):
  Stub code for each external function
  First call: jumps to resolver (slow path)
  Subsequent calls: jumps directly via GOT (fast path)

┌──────────────────┐
│ Your code:       │
│   call printf@PLT│──→┌──────────────────┐
└──────────────────┘   │ PLT[printf]:     │
                       │   jmp [GOT[n]]   │──→ First call: resolver
                       │   push n         │    Subsequent: actual printf()
                       │   jmp PLT[0]     │
                       └──────────────────┘
                              │ (first call only)
                              ▼
                       ┌──────────────────┐
                       │ PLT[0]:          │
                       │   push [GOT[1]]  │ (link_map)
                       │   jmp [GOT[2]]   │ (dl_runtime_resolve)
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Dynamic linker:  │
                       │   Find printf()  │
                       │   Patch GOT[n]   │
                       │   Jump to printf │
                       └──────────────────┘
```

### Calling Shared Library Functions from Assembly

```nasm
; Calling printf from assembly (dynamic linking)
; Build: nasm -f elf64 prog.asm && ld -dynamic-linker /lib64/ld-linux-x86-64.so.2 -lc prog.o -o prog

section .data
    fmt db "Value: %d", 10, 0

section .text
    extern printf
    extern exit
    global _start

_start:
    ; Align stack to 16 bytes before calling C functions
    and rsp, -16

    ; Call printf(fmt, 42)
    lea rdi, [rel fmt]     ; Format string
    mov rsi, 42            ; Value
    xor eax, eax           ; Number of vector args (0 for integer-only)
    call printf wrt ..plt  ; Call through PLT (NASM syntax for PLT call)

    ; Exit
    xor edi, edi
    call exit wrt ..plt
```

### Position-Independent Code (PIC/PIE)

```nasm
; Position-Independent Executables (PIE) are loaded at random addresses (ASLR)
; All memory references must be RIP-relative

; Build PIE: nasm -f elf64 prog.asm && ld -pie -dynamic-linker ... prog.o -o prog

; PIE requirements:
; 1. All data access via RIP-relative addressing (lea rdi, [rel msg])
; 2. All external calls through PLT (call func wrt ..plt)
; 3. Global data access through GOT (for shared libraries)

section .data
    msg db "Hello from PIE!", 10, 0

section .text
    global _start

_start:
    ; RIP-relative addressing works regardless of load address
    lea rsi, [rel msg]     ; This works at ANY load address
    ; NOT: mov rsi, msg    ; This would be an absolute address (wrong for PIE!)

    mov rax, 1
    mov rdi, 1
    mov rdx, 16
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Part 6: How the Kernel Loads an ELF

### The execve() Loading Sequence

```
When kernel processes execve() for an ELF file:

1. Read first 4 bytes: check magic (0x7F "ELF")

2. Parse ELF header:
   - Verify e_type (must be ET_EXEC or ET_DYN)
   - Verify e_machine (must be EM_X86_64)
   - Read e_entry (entry point)
   - Read e_phoff, e_phnum (program headers)

3. For each PT_LOAD program header:
   - Calculate mapping parameters:
     file_offset = p_offset
     map_addr = p_vaddr (or random base for PIE)
     file_size = p_filesz
     mem_size = p_memsz
     permissions = p_flags (R/W/X)
   
   - mmap the segment:
     mmap(map_addr, file_size, prot, MAP_PRIVATE|MAP_FIXED, fd, file_offset)
   
   - Zero BSS portion (memsz > filesz):
     memset(map_addr + filesz, 0, memsz - filesz)

4. If PT_INTERP present (dynamically linked):
   - Read interpreter path ("/lib64/ld-linux-x86-64.so.2")
   - Load interpreter ELF into memory
   - Set entry point to interpreter's entry (not program's!)
   - Interpreter will eventually jump to program's entry

5. Set up initial stack:
   [See Topic 22 for stack layout details]
   - Push auxiliary vector, environment, arguments

6. Set registers and jump:
   - RSP = top of new stack
   - RIP = e_entry (or interpreter entry for dynamic)
   - All other registers = 0
```

---

## Part 7: Symbol Tables

```nasm
; Symbol table entries tell tools about functions and variables:
;
; Elf64_Sym:
;   st_name:  offset into .strtab (name string)
;   st_info:  type (FUNC/OBJECT/NOTYPE) + binding (LOCAL/GLOBAL/WEAK)
;   st_other: visibility (DEFAULT/HIDDEN/PROTECTED)
;   st_shndx: section index where symbol is defined
;   st_value: address (or offset in relocatable file)
;   st_size:  size of symbol (function size, variable size)

; Making symbols visible/hidden:
section .text
    global public_func         ; Visible to linker (GLOBAL binding)
    global _start

; Local label (not in symbol table by default):
.local_helper:
    ret

; Global function:
public_func:
    ; ... code ...
    ret

; Weak symbol (can be overridden by a strong definition):
; global weak_func:function weak
; weak_func:
;     ret

_start:
    call public_func
    mov rax, 60
    xor rdi, rdi
    syscall

; readelf -s program shows:
;   Num  Value           Size Type   Bind   Vis     Name
;   1    0x401000        0    FUNC   GLOBAL DEFAULT _start
;   2    0x401020        16   FUNC   GLOBAL DEFAULT public_func
```

---

## Part 8: Debugging Information (DWARF)

```nasm
; DWARF debug info maps machine code back to source:
; - Line number tables (.debug_line)
; - Variable locations (.debug_info)
; - Type information (.debug_abbrev, .debug_types)
;
; Build with debug info:
; nasm -f elf64 -g -F dwarf prog.asm -o prog.o
; ld -g prog.o -o prog
;
; Now GDB can show source lines and variable values!

; NASM debug directives:
section .text
    global _start

_start:
    ; GDB will show these source lines
    mov rdi, 42
    call do_work
    
    mov rdi, rax
    mov rax, 60
    syscall

do_work:
    mov rax, rdi
    imul rax, rax       ; Square the input
    ret

; With -g -F dwarf, NASM emits:
;   .debug_info    — compilation unit, types
;   .debug_line    — line number → address mapping
;   .debug_abbrev  — abbreviation tables
;
; GDB can then:
;   (gdb) list           → show source
;   (gdb) break _start   → set breakpoint by name
;   (gdb) next           → step by source line
```

---

## Part 9: ELF Inspection Tools

```nasm
; Essential tools for examining ELF files:

; readelf — comprehensive ELF analysis
; $ readelf -h prog         # ELF header
; $ readelf -S prog         # Section headers
; $ readelf -l prog         # Program headers (segments)
; $ readelf -s prog         # Symbol table
; $ readelf -r prog.o       # Relocations
; $ readelf -d prog         # Dynamic section
; $ readelf -n prog         # Notes (build ID)
; $ readelf -a prog         # Everything

; objdump — disassembly and headers
; $ objdump -d prog         # Disassemble .text
; $ objdump -D prog         # Disassemble all sections
; $ objdump -t prog         # Symbol table
; $ objdump -r prog.o       # Relocations
; $ objdump -x prog         # All headers

; nm — symbol listing
; $ nm prog                 # List symbols (address, type, name)
; $ nm -D prog              # Dynamic symbols only

; hexdump — raw bytes
; $ hexdump -C prog | head  # View ELF magic and header bytes
; $ xxd prog | head

; file — identify file type
; $ file prog
; prog: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), 
;       statically linked, not stripped

; strip — remove symbols (smaller binary)
; $ strip --strip-all prog  # Remove all symbols
; $ strip --strip-debug prog # Remove only debug info

; size — section sizes
; $ size prog
;    text    data     bss     dec     hex filename
;      53      10       8      71      47 prog
```

---

## Part 10: Self-Modifying ELF Tricks

```nasm
; Writing a program that modifies its own ELF file on disk
; (Educational — demonstrates ELF structure understanding)

section .data
    self_path db "/proc/self/exe", 0
    ; Note: /proc/self/exe is a symlink to our own executable

section .bss
    elf_header_buf resb 64  ; Buffer for reading our own ELF header

section .text
    global _start

_start:
    ; Read our own ELF header from /proc/self/exe
    ; (Can't write to it — it's the running executable)
    ; But we can READ and understand our own structure

    ; Open ourselves
    mov rax, 2              ; sys_open
    lea rdi, [rel self_path]
    xor rsi, rsi            ; O_RDONLY
    xor rdx, rdx
    syscall
    mov r12, rax

    ; Read ELF header
    mov rax, 0              ; sys_read
    mov rdi, r12
    lea rsi, [rel elf_header_buf]
    mov rdx, 64             ; ELF header size
    syscall

    ; Parse: verify magic
    lea rdi, [rel elf_header_buf]
    cmp byte [rdi], 0x7F
    jne .not_elf
    cmp byte [rdi+1], 'E'
    jne .not_elf
    cmp byte [rdi+2], 'L'
    jne .not_elf
    cmp byte [rdi+3], 'F'
    jne .not_elf

    ; Read entry point (offset 24 in ELF64 header)
    mov rax, [rdi + 24]    ; e_entry
    ; RAX now contains our own entry point address!

    ; Read number of program headers (offset 56, 2 bytes)
    movzx ecx, word [rdi + 56]  ; e_phnum

    ; Close
    mov rax, 3
    mov rdi, r12
    syscall

    ; Exit with number of program headers as status
    mov rax, 60
    mov rdi, rcx
    syscall

.not_elf:
    mov rax, 60
    mov rdi, 1
    syscall
```

---

## Exercises

1. **Minimal ELF**: Create the smallest possible valid ELF executable (aim for under 200 bytes) that prints "Hi\n" and exits. Write the ELF header manually in NASM.

2. **ELF parser**: Write an assembly program that reads an ELF file, parses its header, and prints: type, architecture, entry point, and number of segments.

3. **Symbol resolver**: Given an object file, read its symbol table and print all global function symbols with their addresses.

4. **Two-file linking**: Create two .asm files that call each other's functions. Observe the relocation entries in the .o files and verify they're resolved in the final executable.

5. **Shared library**: Create a simple `.so` shared library in assembly, then write a program that calls it through PLT/GOT.

---

## Key Takeaways

| Concept | Reality |
|---------|---------|
| ELF Header | 64 bytes at offset 0; magic(7F ELF), type, entry point, table offsets |
| Sections | Logical divisions (.text/.data/.bss) for linker and debugger |
| Segments | Loadable chunks for kernel; each maps to a memory region |
| Relocations | "Patch address X with symbol Y's final address" |
| Linker | Resolves symbols, assigns addresses, patches relocations |
| GOT/PLT | Indirection for dynamic linking; lazy binding on first call |
| PIE/ASLR | RIP-relative addressing enables random load addresses |
| Program loading | Kernel mmaps segments, sets up stack, jumps to entry |

---

## Next Topic

[Topic 26: Interrupts & Exceptions →](topic-26-interrupts.md) — How the CPU handles hardware interrupts, software exceptions, and the interrupt descriptor table.
