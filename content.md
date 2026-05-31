# 📑 Complete File Index

A comprehensive index of all files in this NASM tutorial collection.

---

## 📁 Root Directory

### **README.md** (Main Overview)
**Purpose:** Course overview, complete curriculum (20 topics), progress tracking  
**Content:** Full learning path from beginner to advanced, organized by weeks and levels  
**Start Here:** ✅ This is your main navigation file

### **QUICK_REFERENCE.md** (Cheat Sheet)
**Purpose:** Fast lookup reference for common operations and syntax  
**Content:** Commands, templates, syscalls, addressing modes, debugging tips  
**Use When:** You need to quickly look up syntax or common patterns

### **INDEX.md** (This File)
**Purpose:** Complete file listing with descriptions  
**Content:** Overview of every file in the tutorial

---

## 📚 `/topics` - Core Curriculum

Sequential lessons that form the main course content. Work through these in order.

### **topic-01-setup.md** ✅ Completed
**Level:** Foundation (Week 1)  
**What You'll Learn:**
- Installing NASM and build tools
- Understanding the assembly workflow (.asm → .o → executable)
- Program structure (.data, .bss, .text sections)
- Your first "Hello World" program
- Debugging with GDB

**Key Concepts:**
- `nasm -f elf64` command
- `syscall` instruction
- Linux syscalls (sys_write, sys_exit)
- `$ - label` for calculating lengths

**Exercises:** 5 practice problems included

---

### **topic-02-registers.md** ✅ Completed
**Level:** Foundation (Week 1)  
**What You'll Learn:**
- The 16 general-purpose registers (RAX-R15)
- Register sizes: 64, 32, 16, 8-bit access
- Critical 32-bit zeroing behavior
- Register naming conventions and purposes
- Data types: DB, DW, DD, DQ
- Reserved vs defined data (RESB vs DB)

**Key Concepts:**
- RAX → EAX → AX → AH/AL hierarchy
- Writing to 32-bit register zeros upper 32 bits
- Register roles (accumulator, counter, stack pointer)
- System V calling convention (RDI, RSI, RDX...)

**Exercises:** 5 practice problems included

---

### **instruction-encoding.md** ✅ Completed (Supplementary)
**Level:** Advanced/Supplementary  
**What You'll Learn:**
- How assembly instructions become machine code
- Instruction format: Prefixes, Opcode, ModR/M, SIB, Displacement, Immediate
- REX prefix for 64-bit mode
- Why `xor eax, eax` is 2 bytes but `mov eax, 0` is 5 bytes
- ModR/M byte structure and addressing modes
- SIB byte for complex addressing
- Optimization techniques based on encoding

**Key Concepts:**
- Variable-length instructions (1-15 bytes)
- REX.W for 64-bit operations
- ModR/M byte for operand specification
- Special encodings (PUSH is 1 byte!)
- Instruction cache implications
- Decoding practice exercises

**Tools Covered:**
- objdump for disassembly
- NASM listing files
- Online assemblers

**When to Read:** After Topic 2, or when curious about why certain instructions are "better"

---

### **topic-03-basic-instructions.md** ✅ Completed
**Level:** Foundation (Week 2)  
**What You'll Learn:**
- MOV instruction and all its forms
- Arithmetic operations: ADD, SUB, INC, DEC, NEG
- Multiplication and division: MUL, IMUL, DIV, IDIV
- Bitwise operations: AND, OR, XOR, NOT, TEST
- Shift and rotate: SHL, SHR, SAL, SAR, ROL, ROR
- LEA for efficient arithmetic
- CMP instruction for comparisons
- Practical patterns and optimization tips

**Key Concepts:**
- MOV restrictions (no mem-to-mem)
- Setting up RDX:RAX for division
- Flags affected by each instruction
- LEA as a powerful arithmetic tool
- Choosing the most efficient instruction
- Common coding patterns

**Practical Examples:**
- Sum array elements
- Find maximum value
- Calculate factorial
- Bit manipulation
- Using LEA for complex math

**Exercises:** 5 practice problems with solutions

---

### **topic-04-flags.md** ✅ Completed
**Level:** Control Flow (Week 3)  
**What You'll Learn:**
- The RFLAGS register and its structure
- Six arithmetic flags: CF, ZF, SF, OF, PF, AF
- When each flag is set
- How instructions affect different flags
- CMP instruction in detail
- TEST instruction for bit testing
- Reading flag combinations
- Signed vs unsigned comparisons
- Flag manipulation instructions
- Common patterns and debugging

**Key Concepts:**
- CF for unsigned overflow/borrow
- ZF for zero results and equality
- SF for sign (negative numbers)
- OF for signed overflow
- CMP performs subtraction without storing
- TEST performs AND without storing
- Flag combinations for conditionals
- Which instructions affect which flags

**Practical Examples:**
- Zero checking
- Range validation
- Sign detection
- Overflow handling
- Multi-precision arithmetic
- Parity checks

**Exercises:** 5 practice problems with solutions

---

### **topic-05-jumps.md** ✅ Completed
**Level:** Control Flow (Week 3)  
**What You'll Learn:**
- Unconditional and conditional jumps
- All conditional jump variants (signed/unsigned)
- If/else and switch statement implementation
- Practical examples with complete C equivalents

---

### **topic-06-loops.md** ✅ Completed
**Level:** Control Flow (Week 4)  
**What You'll Learn:**
- Loop patterns (for, while, do-while)
- LOOP instruction and optimization
- Nested loops with examples (bubble sort, matrix ops)
- Complete with C code equivalents

---

### **topic-07-stack.md** ✅ Completed
**Level:** The Stack (Week 5)  
**What You'll Learn:**
- PUSH/POP mechanics and stack pointer
- Stack alignment (16-byte requirement)
- Practical examples with C equivalents

---

### **topic-08-functions.md** ✅ Completed
**Level:** The Stack (Week 5)  
**What You'll Learn:**
- Stack frames and base pointer
- Function prologue/epilogue patterns
- Local variables on stack
- Complete with C code equivalents

---

### **topic-09-calling-conventions.md** ✅ Completed
**Level:** Functions & Procedures (Week 6)  
**What You'll Learn:**
- cdecl, stdcall, fastcall conventions
- System V AMD64 ABI (Linux) detailed
- Microsoft x64 (Windows) differences
- Parameter passing in registers vs stack
- Complete with C code equivalents

---

### **topic-10-procedures.md** ✅ Completed
**Level:** Functions & Procedures (Week 7)  
**What You'll Learn:**
- CALL and RET instructions
- Return values and register preservation
- Recursive functions (factorial, Fibonacci)
- Complete with C code equivalents

---

### **topic-11-memory-addressing.md** ✅ Completed
**Level:** Memory & Addressing (Week 8)  
**What You'll Learn:**
- All 7 addressing modes explained
- Direct, indirect, indexed, scaled indexed
- RIP-relative addressing (x64)
- Complete with C code equivalents

---

### **topic-12-arrays-strings.md** ✅ Completed
**Level:** Memory & Addressing (Week 8)  
**What You'll Learn:**
- String instructions (MOVS, LODS, STOS, SCAS, CMPS)
- Direction flag and REP prefix
- Array manipulation patterns
- Complete with C code equivalents

---

### **topic-13-multiplication-division.md** ✅ Completed
**Level:** Advanced Operations (Week 9)  
**What You'll Learn:**
- MUL (unsigned) and IMUL (signed) multiplication
- DIV (unsigned) and IDIV (signed) division
- 128-bit results (RDX:RAX)
- Sign extension (CDQ, CQO)
- Practical examples: factorial, GCD, integer sqrt, decimal to ASCII
- Performance characteristics and optimization
- Complete with C code equivalents

**Key Topics:**
- Single, double, and triple operand IMUL forms
- Proper sign extension before IDIV
- Common pitfalls (division by zero, forgetting to clear EDX)
- When to use shifts instead of multiply/divide

---

### **topic-14-shifts-rotates.md** ✅ Completed
**Level:** Advanced Operations (Week 9)  
**What You'll Learn:**
- Logical shifts (SHL, SHR) for unsigned
- Arithmetic shift (SAR) for signed division
- Rotates (ROL, ROR, RCL, RCR)
- Double-precision shifts (SHLD, SHRD)
- Bit manipulation patterns
- Complete with C code equivalents

**Practical Applications:**
- Bit extraction and field packing
- Fast multiply/divide by powers of 2
- Byte swapping (endianness)
- Count leading zeros
- Alignment checks
- Barrel shifter emulation

---

### **topic-15-macros.md** ✅ Completed
**Level:** Advanced Operations (Week 10)  
**What You'll Learn:**
- Text substitution with %define
- Multi-line macros with %macro
- Conditional assembly (%if, %ifdef)
- File inclusion and code organization
- Complete with C code equivalents

---

### **topic-16-system-calls.md** ✅ Completed
**Level:** System Programming (Week 11)  
**What You'll Learn:**
- SYSCALL instruction and mechanism (user → kernel)
- Register mapping (RAX, RDI, RSI, RDX, R10, R8, R9)
- File I/O: open, read, write, close with flags and modes
- Process management: fork, execve, wait4
- Memory management: brk, mmap, munmap
- Time functions: time, clock_gettime, nanosleep
- Error handling (-errno in RAX)
- Complete echo server skeleton example
- Complete with C code equivalents

**Key Concepts:**
- Syscall vs int 0x80 (64-bit vs 32-bit)
- Why R10 instead of RCX (RCX saves return address)
- Syscall overhead and batching optimization

---

### **topic-17-interfacing-c.md** ✅ Completed
**Level:** System Programming (Week 12)  
**What You'll Learn:**
- System V AMD64 ABI in depth
- Calling C functions from assembly (printf, malloc, fgets)
- Calling assembly from C
- Stack alignment (16-byte requirement critical)
- Passing structures by value vs pointer
- Inline assembly in C with GCC extended asm
- Creating reusable assembly libraries
- Complete with C code equivalents

**Practical Examples:**
- String length function callable from C
- Using printf for debugging
- Dynamic memory allocation
- Math library (factorial, power, GCD)
- Debugging mixed C/Assembly with GDB

---

### **topic-18-simd.md** ✅ Completed
**Level:** Optimization & Advanced (Week 13)  
**What You'll Learn:**
- SIMD fundamentals (Single Instruction Multiple Data)
- XMM registers (128-bit) and YMM registers (256-bit)
- Packed operations: 4x float, 2x double at once
- SSE instructions: MOVAPS, ADDPS, MULPS, etc.
- AVX non-destructive operations
- Complete with C code equivalents

**Real-World Examples:**
- Array addition (4x speedup)
- Array sum with horizontal reduction
- Dot product with benchmarking
- Shuffle and broadcast operations
- Integer SIMD operations

**Performance:**
- Typical 3-8x speedup for vectorizable code
- Alignment requirements (16/32 bytes)
- When SIMD helps vs hurts

---

### **topic-19-performance.md** ✅ Completed
**Level:** Optimization & Advanced (Week 13)  
**What You'll Learn:**
- CPU architecture: pipeline, superscalar execution
- Instruction latency vs throughput
- Memory hierarchy (L1/L2/L3 cache, RAM)
- Cache lines and false sharing
- Complete with C code equivalents

**Optimization Techniques:**
- Loop unrolling (reduce branch overhead)
- Multiple accumulators (break dependency chains)
- Software pipelining (overlap operations)
- Strength reduction (LEA tricks, shifts)
- Induction variable elimination
- Branch prediction and branchless code
- Data alignment optimization

**Complete Example:**
- Optimized array average: 10-15x speedup
- Before/after comparison with explanation

---

### **topic-20-debugging.md** ✅ Completed
**Level:** Optimization & Advanced (Week 14)  
**What You'll Learn:**
- GDB comprehensive guide (50+ commands)
- TUI mode for visual debugging
- Breakpoints, watchpoints, conditional breaks
- Examining registers and memory
- Disassembly with objdump
- System call tracing with strace
- Memory debugging with valgrind
- ELF analysis with readelf
- Binary viewing with hexdump

**Debugging Scenarios:**
- Fixing segmentation faults
- Detecting infinite loops
- Correcting wrong results
- Using core dumps
- Remote debugging with gdbserver

**Best Practices:**
- Defensive programming patterns
- Debug vs release builds
- Common bug locations checklist
- Tool selection guide

---

## ❓ `/qna` - Deep Dive Explanations

Detailed answers to specific questions that arose during learning. Read these when you encounter the topic or have similar questions.

### **push-pop-explained.md**
**Question:** "What does push and pop do in assembly?"  
**Topics Covered:**
- Stack mechanics (LIFO data structure)
- How PUSH decrements RSP and writes data
- How POP reads data and increments RSP
- Common uses: saving registers, function calls, local variables
- Bonus: Swapping registers with push/pop

**Related Lessons:** Topic 7 (Stack Operations)  
**Read When:** Before learning about functions and stack frames

---

### **int-vs-syscall.md**
**Question:** "When to use int 0x80, and when to use syscall?"  
**Topics Covered:**
- Architecture differences (32-bit vs 64-bit)
- Register conventions (EAX/EBX vs RAX/RDI)
- Different syscall numbers between 32/64-bit
- Performance comparison (~300 vs ~100 cycles)
- Decision tree for choosing the right method
- Complete working examples of both

**Related Lessons:** Topic 1 (Setup & First Program)  
**Read When:** Confused about which system call method to use

---

### **memory-addressing.md**
**Question:** "What does the [ ] syntax mean?"  
**Topics Covered:**
- Memory dereferencing concept
- Bracket syntax = "go to this address"
- All 6 addressing modes with examples
- Practical array and string access patterns
- Size specifiers (byte, word, dword, qword)
- Common mistakes and memory safety warnings

**Related Lessons:** Topic 2 (Registers), Topic 11 (Memory Addressing Modes)  
**Read When:** Learning about pointers and memory access

---

### **sections-and-optimization.md**
**Questions:** 
1. "What is .text .bss .data sections with respect to C code?"
2. "Why xor rax, rax is used instead of mov rax, 0?"

**Topics Covered:**

**Part 1 - Sections:**
- Complete memory layout diagram
- .text section: executable code (read-only)
- .data section: initialized variables (in file)
- .bss section: uninitialized variables (NOT in file!)
- Relation to C global/static variables
- File size optimization techniques

**Part 2 - XOR Optimization:**
- Why `xor rax, rax` is 2-5 bytes smaller
- CPU zero-latency optimization
- Performance benefits (dependency breaking)
- Compiler output examples
- All zeroing methods compared

**Related Lessons:** Topic 1 (Program Structure), Topic 3 (Basic Instructions)  
**Read When:** Learning about program structure and optimization

---

### **cmp-vs-test.md**
**Question:** "What is the difference between CMP and TEST?"  
**Topics Covered:**
- CMP performs subtraction (for magnitude comparison)
- TEST performs AND (for bit testing and zero checks)
- When to use each instruction
- Flag behavior differences
- Encoding size comparison
- Common use cases and patterns
- Decision tree for choosing
- Common mistakes to avoid

**Related Lessons:** Topic 3 (Basic Instructions), Topic 4 (Flags & Comparisons)  
**Read When:** Confused about when to use CMP vs TEST

---

### **all-jump-types.md**
**Question:** "What all types of jumps exist in assembly?"  
**Topics Covered:**
- **Unconditional jumps**: JMP (direct, indirect, register, memory)
- **Conditional jumps (signed)**: JG, JGE, JL, JLE, JE, JNE
- **Conditional jumps (unsigned)**: JA, JAE, JB, JBE, JE, JNE
- **Flag-specific jumps**: JZ/JNZ, JS/JNS, JC/JNC, JO/JNO, JP/JNP
- **Loop instructions**: LOOP, LOOPE/LOOPZ, LOOPNE/LOOPNZ
- **Function calls**: CALL, RET (direct and indirect)
- **Indirect jumps**: Through registers and memory
- **Jump tables**: Efficient switch statement implementation
- **Conditional move**: CMOVcc as branchless alternative
- **Short vs Near vs Far jumps**
- Complete reference table with all 40+ jump variants
- Performance optimization patterns
- Decision tree for choosing the right jump

**Related Lessons:** Topic 5 (Conditional Jumps), Topic 4 (Flags), Topic 6 (Loops)  
**Read When:** Need comprehensive reference for all jump types

---

## 📊 File Statistics

```
Total Files: 27 markdown files
Total Lines: ~31,000+ lines
Total Size: ~875 KB

Breakdown:
- README.md: 12 KB (curriculum overview - UPDATED)
- INDEX.md: 27 KB (this file - UPDATED)
- QUICK_REFERENCE.md: 12 KB (cheat sheet)
- syscall-reference.md: 35 KB (complete syscall reference)
- Topics: 17,651 lines / ~550 KB (20 complete topics!)
  • topic-01 through topic-12: 12 files (existing)
  • topic-13: Multiplication & Division (20KB)
  • topic-14: Shifts & Rotates (21KB)
  • topic-15: Macros (10KB)
  • topic-16: System Calls (19KB)
  • topic-17: Interfacing with C (18KB)
  • topic-18: SIMD (18KB)
  • topic-19: Performance (18KB)
  • topic-20: Debugging (17KB)
- Q&A: ~210 KB (7 detailed explanations with C equivalents)
  • push-pop-explained.md
  • int-vs-syscall.md
  • memory-addressing.md
  • sections-and-optimization.md
  • cmp-vs-test.md
  • instruction-encoding.md
  • all-jump-types.md (25KB) ⭐ NEW

🎉 ALL 20 TOPICS + 7 Q&A ARTICLES COMPLETED! 🎉
```

---

## 🎯 Recommended Reading Order

### **For Complete Beginners:**
1. ✅ README.md - Understand the learning path
2. ✅ topic-01-setup.md - Get environment set up
3. ✅ int-vs-syscall.md - Understand system calls
4. ✅ topic-02-registers.md - Learn about registers
5. ✅ memory-addressing.md - Understand [ ] syntax
6. ✅ sections-and-optimization.md - Program structure
7. ✅ topic-03-basic-instructions.md - Core instructions
8. ✅ topic-04-flags.md - Flags and comparisons
9. ✅ topic-05-jumps.md - Control flow
10. ✅ topic-06-loops.md - Loops and iteration
11. ✅ topic-07-stack.md - Stack operations
12. ✅ push-pop-explained.md - Stack deep dive
13. ✅ topic-08-functions.md - Stack frames
14. ✅ topic-09-calling-conventions.md - ABI details
15. ✅ topic-10-procedures.md - Functions and recursion
16. ✅ topic-11-memory-addressing.md - All addressing modes
17. ✅ topic-12-arrays-strings.md - Data structures
18. ✅ topic-13-multiplication-division.md - Math operations
19. ✅ topic-14-shifts-rotates.md - Bit manipulation
20. ✅ topic-15-macros.md - Macros and directives
21. ✅ topic-16-system-calls.md - OS interface
22. ✅ topic-17-interfacing-c.md - C integration
23. ✅ topic-18-simd.md - Vectorization
24. ✅ topic-19-performance.md - Optimization
25. ✅ topic-20-debugging.md - Debugging tools
26. 📖 QUICK_REFERENCE.md - Keep open for reference
27. 📖 syscall-reference.md - Syscall lookup table

### **For Quick Reference:**
1. 📖 QUICK_REFERENCE.md - Common operations and syntax
2. 📖 syscall-reference.md - Complete syscall tables
3. 📖 Topic files - Specific concepts
4. 📖 Q&A files - Deep explanations

## 📈 Completion Status

```
✅ LEVEL 1 - Foundation (3/3 topics complete)
✅ LEVEL 2 - Control Flow (3/3 topics complete)
✅ LEVEL 3 - The Stack (2/2 topics complete)
✅ LEVEL 4 - Functions & Procedures (2/2 topics complete)
✅ LEVEL 5 - Memory & Addressing (2/2 topics complete)
✅ LEVEL 6 - Advanced Operations (3/3 topics complete)
✅ LEVEL 7 - System Programming (2/2 topics complete)
✅ LEVEL 8 - Optimization & Advanced (3/3 topics complete)

🎉 ALL 20 CORE TOPICS: 100% COMPLETE! 🎉
📚 SUPPLEMENTARY: 7/7 Q&A articles complete
📖 REFERENCES: 3/3 reference documents complete

Total: 30 comprehensive files covering all aspects of NASM assembly!
```

---

## 🔍 Finding What You Need

### **I want to learn...**

- **"How to set up NASM"** → topic-01-setup.md
- **"About registers"** → topic-02-registers.md
- **"How push/pop work"** → push-pop-explained.md
- **"When to use int 0x80 vs syscall"** → int-vs-syscall.md
- **"What [ ] brackets mean"** → memory-addressing.md
- **"About .text .data .bss sections"** → sections-and-optimization.md
- **"Why use xor instead of mov"** → sections-and-optimization.md
- **"How instructions are encoded"** → instruction-encoding.md
- **"Why some instructions are shorter"** → instruction-encoding.md
- **"Quick syntax reference"** → QUICK_REFERENCE.md

### **I need help with...**

- **Building programs** → QUICK_REFERENCE.md (Build Commands)
- **System calls** → QUICK_REFERENCE.md (Linux Syscalls)
- **Memory addressing** → memory-addressing.md + QUICK_REFERENCE.md
- **Debugging** → topic-01-setup.md + QUICK_REFERENCE.md (Debugging)
- **Register names** → topic-02-registers.md + QUICK_REFERENCE.md

---

## 📝 Document Conventions

### **Status Indicators:**
- ✅ Completed - Content finished and ready
- ⏳ In Progress - Content being developed
- ☐ Planned - Content planned but not started

### **File Naming:**
- `topic-##-name.md` - Sequential curriculum topics
- `descriptive-name.md` - Q&A and reference files
- All lowercase, hyphens for spaces

### **Content Structure:**
- Each file starts with clear title and purpose
- Progressive complexity within each file
- Code examples for every concept
- Practice exercises where applicable
- Cross-references to related content

---

## 🔄 Updates & Maintenance

**Last Updated:** December 17, 2025

**What's New:**
- ✅ Created complete directory structure
- ✅ Completed Topics 1-3 (Foundation complete!)
- ✅ Added comprehensive Instruction Encoding guide
- ✅ Added 4 comprehensive Q&A documents
- ✅ Created quick reference guide
- ⏳ Topics 4-20 planned

---

## 📚 `/topics` - OS Internals (Level 9)

Advanced topics covering how operating system primitives work at the assembly level.

### **topic-21-memory-internals.md** ✅ Completed
**Level:** OS Internals (Week 15)
**What You'll Learn:**
- How brk() extends the heap (program break)
- How mmap() allocates independent memory regions
- Implementing sbrk() in assembly
- malloc chunk structure (headers, flags, size encoding)
- Free list strategies (fast bins, small bins, large bins)
- Chunk coalescing to fight fragmentation
- Demand paging and page faults on first access
- Thread-local arenas for multi-threaded allocation
- Memory alignment guarantees
- Debugging: use-after-free detection, double-free detection

**Key Concepts:** brk, mmap, munmap, mprotect, page faults, free lists, chunk headers, COW

---

### **topic-22-process-internals.md** ✅ Completed
**Level:** OS Internals (Week 15-16)
**What You'll Learn:**
- Process virtual address space layout
- fork() syscall and what the kernel duplicates
- Copy-on-Write (COW) mechanism in detail
- clone() — the real syscall behind fork() and threads
- execve() — how it destroys and rebuilds address space
- Initial stack after execve (argc, argv, envp, auxiliary vector)
- Signal installation and delivery mechanism
- Process groups, sessions, and daemons
- Pipes for inter-process communication
- Implementing shell pipelines (ls | wc -l) in assembly

**Key Concepts:** fork, clone, execve, COW, signals, pipes, dup2, wait4, process groups

---

### **topic-23-virtual-memory.md** ✅ Completed
**Level:** OS Internals (Week 16)
**What You'll Learn:**
- Why virtual memory exists (isolation, overcommit, sharing)
- 4-level page table structure (PML4/PDPT/PD/PT)
- Page Table Entry (PTE) bit fields (Present, R/W, U/S, NX, Dirty, Accessed)
- Complete virtual address translation walkthrough
- TLB: sizes, hit rates, flush events, PCID optimization
- Page sizes: 4KB standard, 2MB huge pages, 1GB gigantic pages
- Using huge pages via mmap (MAP_HUGETLB)
- Page fault types and kernel handler logic
- Memory protection with mprotect()
- Guard pages for overflow detection
- ASLR (Address Space Layout Randomization)
- Shared memory between processes
- Memory-mapped files (file as an array)

**Key Concepts:** page tables, TLB, page faults, huge pages, mprotect, ASLR, shared memory

---

### **topic-24-io-internals.md** ✅ Completed
**Level:** OS Internals (Week 16-17)
**What You'll Learn:**
- Complete write() syscall path (user→kernel→VFS→driver→hardware)
- What happens inside the SYSCALL instruction (MSRs, ring transition)
- File descriptor table structure (fd → file struct → operations)
- Terminal I/O path: kernel TTY → line discipline → PTY → terminal emulator
- Canonical vs raw terminal mode (ioctl TCSETS)
- User-space buffering (why printf doesn't write immediately)
- Implementing buffered I/O in assembly
- Implementing printf-like formatting (%d, %s, %x, %c)
- The read() path: keyboard IRQ → input subsystem → TTY → process
- Blocking vs non-blocking I/O (O_NONBLOCK, fcntl)
- poll() for monitoring multiple file descriptors
- Shell redirection (dup2 mechanics)
- ANSI escape sequences for terminal graphics
- Direct framebuffer access (/dev/fb0)
- writev() scatter/gather I/O

**Key Concepts:** write, read, ioctl, file descriptors, buffering, TTY, poll, dup2, framebuffer

---

### **topic-25-elf-format.md** ✅ Completed
**Level:** OS Internals (Week 17)
**What You'll Learn:**
- ELF file structure overview (header, program headers, sections)
- ELF header fields (64 bytes): magic, type, machine, entry point
- Crafting a minimal ELF executable by hand (~170 bytes)
- Object files (.o): sections, symbol table, relocations
- Relocation types (R_X86_64_64, R_X86_64_PC32, R_X86_64_PLT32)
- What the linker does: symbol resolution, section merging, address assignment
- Linker scripts and custom memory layouts
- Segments vs sections (runtime loading vs link-time organization)
- Program header types (PT_LOAD, PT_DYNAMIC, PT_INTERP)
- Dynamic linking: GOT, PLT, lazy binding, dl_runtime_resolve
- Position-Independent Code (PIC/PIE) for ASLR
- How the kernel loads an ELF during execve()
- Symbol tables and visibility (global, local, weak)
- DWARF debug information
- ELF inspection tools (readelf, objdump, nm, strip)

**Key Concepts:** ELF, sections, segments, relocations, GOT, PLT, PIE, dynamic linking

---

### **topic-26-interrupts.md** ✅ Completed
**Level:** OS Internals (Week 17-18)
**What You'll Learn:**
- Interrupt classification: exceptions, hardware IRQs, software interrupts
- Exception subtypes: faults (retried), traps (next instr), aborts
- IDT structure: 256 entries × 16 bytes, gate descriptors
- Interrupt gate vs trap gate
- Complete exception table (vectors 0-31)
- Page fault (#PF) step-by-step: what CPU pushes, error code bits, CR2
- General Protection Fault (#GP) causes
- Hardware interrupt delivery: device → I/O APIC → Local APIC → CPU
- Timer interrupt and how preemptive scheduling works
- Debugger breakpoints: INT 3 (0xCC) and how GDB uses them
- Hardware debug registers (DR0-DR7) for watchpoints
- SYSCALL instruction vs INT 0x80: MSR-based fast path
- Why RCX and R11 are clobbered by syscall
- vDSO: kernel-mapped shared library for fast "syscalls" without ring transition
- Interrupt latency and real-time considerations
- Catching SIGSEGV and SIGFPE: recovery in signal handlers

**Key Concepts:** IDT, exceptions, IRQs, page fault, timer, INT 3, SYSCALL, vDSO

---

### **topic-27-context-switching.md** ✅ Completed
**Level:** OS Internals (Week 18)
**What You'll Learn:**
- Complete process context: all state that defines execution
- Voluntary switch (blocking on I/O) vs involuntary (timer preemption)
- The switch_to assembly: push callee-saved, swap RSP, pop, RET
- What's on each process's kernel stack when switched out
- FPU/SSE/AVX state: lazy vs eager switching, XSAVE/XRSTOR
- Thread switching vs process switching (no CR3 change = much faster)
- Thread Local Storage (TLS) via FS segment register
- CFS scheduler: vruntime, red-black tree, weight-based time slices
- Process states (RUNNING, SLEEPING, ZOMBIE, STOPPED)
- Measuring context switch cost (pipe ping-pong benchmark)
- CPU affinity: sched_setaffinity, pinning to cores
- NUMA awareness
- User-space context switching: implementing coroutines in assembly

**Key Concepts:** switch_to, kernel stack, CR3, XSAVE, CFS, coroutines, TLS, CPU affinity

---

### **topic-28-synchronization.md** ✅ Completed
**Level:** OS Internals (Week 18)
**What You'll Learn:**
- x86-64 memory model (Total Store Order)
- Memory barriers: MFENCE, SFENCE, LFENCE
- LOCK prefix: makes read-modify-write atomic + full barrier
- Atomic operations: LOCK INC, LOCK ADD, XCHG, LOCK XADD
- CMPXCHG (Compare-and-Swap): the fundamental CAS operation
- CMPXCHG16B for 128-bit atomic operations
- Spinlock implementations: test-and-set, ticket lock (fair)
- PAUSE instruction: why it matters in spin loops
- Futex syscall: FUTEX_WAIT, FUTEX_WAKE
- Implementing a full mutex using futex (3-state: unlocked/locked/contended)
- Lock-free Treiber stack with CAS
- ABA problem and solutions (version counter with CMPXCHG16B)
- Exponential backoff for contention
- Read-write locks
- Semaphores with futex
- Condition variables
- Single-producer single-consumer lock-free ring buffer
- Complete thread-safe counter example with clone()

**Key Concepts:** LOCK, CMPXCHG, spinlock, futex, lock-free, CAS, ring buffer, memory ordering

---

## 📚 `/qna` - Supplementary Deep Dives (OS Internals)

### **how-malloc-works.md** ✅ Completed
**Question:** How does malloc() actually work from application to physical memory?
**Topics:** chunk headers, free list bins, brk vs mmap decision, why free doesn't return memory, common bugs

### **how-fork-works.md** ✅ Completed
**Question:** How does fork() create a process copy without copying all memory?
**Topics:** Copy-on-Write mechanism, page table duplication, COW page fault, return value magic, vfork

### **virtual-memory-explained.md** ✅ Completed
**Question:** What is a virtual address and how is it translated to physical?
**Topics:** 4-level translation, TLB caching, page fault types, /proc/self/maps, isolation

### **signals-and-traps.md** ✅ Completed
**Question:** How do signals get delivered? Can I catch SIGSEGV?
**Topics:** signal vs exception vs interrupt, kernel stack modification, async-signal-safety, SIGSEGV recovery

---

## 🤝 How to Use This Collection

1. **Linear Learning:** Follow README.md curriculum sequentially
2. **Question-Driven:** Use INDEX.md to find specific answers
3. **Reference:** Keep QUICK_REFERENCE.md open while coding
4. **Deep Dives:** Read Q&A files for thorough explanations
5. **Practice:** Complete exercises in each topic file
6. **OS Internals:** Topics 21-28 explain how the OS works under the hood at assembly level

---

## 📖 Printable Checklist

```
Foundation (Weeks 1-2):
[✅] Topic 1: Setup & First Program
[✅] Topic 2: Registers & Data Types
[✅] Topic 3: Basic Instructions

Control Flow (Weeks 3-4):
[✅] Topic 4: Flags & Comparisons
[✅] Topic 5: Conditional Jumps
[✅] Topic 6: Loops

The Stack (Week 5):
[✅] Topic 7: Stack Operations
[✅] Topic 8: Stack Frames

Functions (Weeks 6-7):
[✅] Topic 9: Calling Conventions
[✅] Topic 10: Procedures

Memory (Week 8):
[✅] Topic 11: Memory Addressing Modes
[✅] Topic 12: Arrays & Strings

Advanced Ops (Weeks 9-10):
[✅] Topic 13: Multiplication & Division
[✅] Topic 14: Shifts & Rotates
[✅] Topic 15: Macros & Directives

System Programming (Weeks 11-12):
[✅] Topic 16: Linux System Calls
[✅] Topic 17: Interfacing with C

Optimization (Weeks 13-14):
[✅] Topic 18: SIMD Instructions
[✅] Topic 19: Performance & Optimization
[✅] Topic 20: Debugging & Tools

OS Internals (Weeks 15-18):
[✅] Topic 21: Memory Allocation Internals
[✅] Topic 22: Process Internals
[✅] Topic 23: Virtual Memory & Paging
[✅] Topic 24: I/O Internals
[✅] Topic 25: ELF Binary Format
[✅] Topic 26: Interrupts & Exceptions
[✅] Topic 27: Context Switching & Scheduling
[✅] Topic 28: Synchronization Primitives

Supplementary:
[✅] Instruction Encoding (Advanced)
[✅] 12 Q&A Deep-Dive Articles
[✅] Comprehensive Syscall Reference
```

---

**Ready to learn?** Start with [README.md](README.md)!

---

[← Back to Main](README.md)

