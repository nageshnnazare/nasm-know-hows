# 🎓 NASM Assembly Programming - Complete Tutorial

Welcome to your comprehensive NASM assembly programming course! This tutorial will take you from beginner to advanced assembly programmer through structured, hands-on lessons.

## 📚 Course Structure

This course is organized into progressive levels with 20 core topics plus advanced projects.

### 📁 Directory Structure

```
nasm-tutorial/
├── README.md                    # This file - course overview
├── topics/                      # Individual topic lessons
│   ├── topic-01-setup.md
│   ├── topic-02-registers.md
│   └── ...
└── qna/                        # Common questions and deep dives
    ├── push-pop-explained.md
    ├── int-vs-syscall.md
    ├── memory-addressing.md
    └── sections-and-optimization.md
```

---

## 🎯 Complete Curriculum

### **LEVEL 1: Foundation** (Weeks 1-2)

#### ✅ [Topic 1: Setup & First Program](topics/topic-01-setup.md)
- Install NASM and linker
- Understand assembly workflow
- Write "Hello World" using syscalls
- Learn basic program structure

#### ✅ [Topic 2: Registers & Data Types](topics/topic-02-registers.md)
- General purpose registers
- Register sizes (64, 32, 16, 8-bit)
- Data types: DB, DW, DD, DQ
- Register conventions

#### 📚 [Supplementary: Instruction Encoding](qna/instruction-encoding.md)
- How assembly becomes machine code
- REX prefix and 64-bit mode
- Opcode, ModR/M, SIB bytes
- Why some instructions are shorter
- Optimization techniques

#### ✅ [Topic 3: Basic Instructions](topics/topic-03-basic-instructions.md)
- MOV and data movement
- Arithmetic: ADD, SUB, INC, DEC, NEG, MUL, DIV
- Bitwise: AND, OR, XOR, NOT, TEST
- Shifts and rotates: SHL, SHR, SAL, SAR, ROL, ROR
- LEA for address calculation and arithmetic
- CMP for comparisons

---

### **LEVEL 2: Control Flow** (Weeks 3-4)

#### ✅ [Topic 4: Flags & Comparisons](topics/topic-04-flags.md)
- The RFLAGS register structure
- Six arithmetic flags: CF, ZF, SF, OF, PF, AF
- How instructions affect flags
- CMP instruction (compare)
- TEST instruction (test bits)
- Signed vs unsigned flag interpretation
- Flag manipulation and common patterns

#### ✅ [Topic 5: Conditional Jumps](topics/topic-05-jumps.md)
- How jumps work (RIP register)
- Unconditional jumps: JMP
- Conditional jumps based on flags
- Signed comparisons: JG, JGE, JL, JLE, JE, JNE
- Unsigned comparisons: JA, JAE, JB, JBE
- If/else statement implementation
- Loop construction
- LOOP instruction and variants
- Practical examples and patterns

#### ✅ [Topic 6: Loops](topics/topic-06-loops.md)
- Loop fundamentals and structure
- Counted loops (for equivalent)
- Condition-tested loops (while/do-while)
- LOOP instruction and variants
- Loop patterns (array iteration, search, accumulation)
- Loop control (break/continue)
- Nested loops
- Loop optimization techniques
- Practical examples (bubble sort, Fibonacci, matrix multiplication)

---

### **LEVEL 3: The Stack** (Week 5)

#### ✅ [Topic 7: Stack Operations](topics/topic-07-stack.md)
- `push` and `pop` mechanics
- Stack pointer (ESP/RSP)
- Stack alignment
- Complete with C code equivalents

#### ✅ [Topic 8: Stack Frames](topics/topic-08-functions.md)
- Base pointer (EBP/RBP)
- Function prologue/epilogue
- Local variables on stack
- Complete with C code equivalents

---

### **LEVEL 4: Functions & Procedures** (Weeks 6-7)

#### ✅ [Topic 9: Calling Conventions](topics/topic-09-calling-conventions.md)
- cdecl, stdcall, fastcall
- System V AMD64 ABI (Linux)
- Microsoft x64 (Windows)
- Complete with C code equivalents

#### ✅ [Topic 10: Procedures](topics/topic-10-procedures.md)
- `call` and `ret` instructions
- Return values
- Recursive functions
- Complete with C code equivalents

---

### **LEVEL 5: Memory & Addressing** (Week 8)

#### ✅ [Topic 11: Memory Addressing Modes](topics/topic-11-memory-addressing.md)
- Direct, indirect, indexed
- Scaled indexed addressing
- RIP-relative (x64)
- SIB addressing with scale factors
- Complete with C code equivalents

#### ✅ [Topic 12: Arrays & Strings](topics/topic-12-arrays-strings.md)
- String instructions (MOVS, LODS, STOS, SCAS, CMPS)
- Direction flag
- `rep` prefix
- Complete with C code equivalents

---

### **LEVEL 6: Advanced Operations** (Weeks 9-10)

#### ✅ [Topic 13: Multiplication & Division](topics/topic-13-multiplication-division.md)
- `mul`/`imul` - unsigned and signed multiplication
- `div`/`idiv` - unsigned and signed division
- 64-bit results and RDX:RAX usage
- Complete with C code equivalents

#### ✅ [Topic 14: Shifts & Rotates (Advanced)](topics/topic-14-shifts-rotates.md)
- Logical shifts: `shl, shr`
- Arithmetic shift: `sar`
- Rotates: `rol, ror, rcl, rcr`
- Complete with C code equivalents

#### ✅ [Topic 15: Macros & Directives](topics/topic-15-macros.md)
- `%define`, `%macro`
- Conditional assembly (%if, %ifdef)
- `%include` and file organization
- Complete with practical examples

---

### **LEVEL 7: System Programming** (Weeks 11-12)

#### ✅ [Topic 16: Linux System Calls](topics/topic-16-system-calls.md)
- `syscall` instruction and mechanism
- Syscall numbers and register usage (RAX, RDI, RSI, RDX, R10, R8, R9)
- File I/O: read, write, open, close
- Process management: fork, exec, wait
- Memory management: brk, mmap, munmap
- Error handling and return values
- Complete with C code equivalents

#### ✅ [Topic 17: Interfacing with C](topics/topic-17-interfacing-c.md)
- Calling conventions (System V AMD64 ABI)
- Calling C from assembly
- Calling assembly from C
- Stack alignment requirements
- Using `printf`, `malloc`, and libc functions
- Creating reusable assembly libraries
- Inline assembly in C
- Complete with C code equivalents

---

### **LEVEL 8: Optimization & Advanced** (Weeks 13-14)

#### ✅ [Topic 18: SIMD Instructions](topics/topic-18-simd.md)
- SSE/AVX fundamentals
- XMM/YMM registers (128-bit/256-bit)
- Packed operations on multiple data elements
- Vector arithmetic, comparisons, shuffling
- Practical examples (array sum, dot product)
- Performance gains from vectorization
- Complete with C code equivalents

#### ✅ [Topic 19: Performance & Optimization](topics/topic-19-performance.md)
- CPU architecture and pipeline fundamentals
- Instruction latency vs throughput
- Memory hierarchy and cache optimization
- Loop unrolling and multiple accumulators
- Branch prediction and branchless code
- Strength reduction and induction variables
- Data alignment and SIMD optimization
- Profiling with perf and RDTSC
- Complete optimization checklist

#### ✅ [Topic 20: Debugging & Tools](topics/topic-20-debugging.md)
- GDB comprehensive guide (breakpoints, watchpoints, TUI mode)
- Objdump for disassembly
- Strace for syscall tracing
- Valgrind for memory debugging
- Readelf for ELF analysis
- Common debugging scenarios (segfault, infinite loop, wrong results)
- Core dumps and remote debugging
- Reverse engineering basics

---

### **LEVEL 9: OS Internals at Assembly Level** (Weeks 15-18)

#### ✅ [Topic 21: Memory Allocation Internals](topics/topic-21-memory-internals.md)
- How malloc/free actually work at the assembly level
- brk() and mmap() syscalls for obtaining memory from the kernel
- Free list management, chunk headers, bins
- Chunk coalescing and fragmentation
- Demand paging and page faults
- Thread-local arenas
- Implementing a custom allocator in assembly

#### ✅ [Topic 22: Process Internals](topics/topic-22-process-internals.md)
- How fork() duplicates a process (Copy-on-Write)
- clone() — the real syscall behind fork and threads
- execve() — replacing process image, ELF loading
- The initial stack layout after execve (argc, argv, envp, auxv)
- Signals — installation, delivery mechanism, signal handlers
- Pipes and inter-process communication
- Implementing shell pipelines in assembly

#### ✅ [Topic 23: Virtual Memory & Paging](topics/topic-23-virtual-memory.md)
- 4-level page table structure (PML4 → PDPT → PD → PT)
- Page Table Entry format (Present, R/W, U/S, NX bits)
- TLB (Translation Lookaside Buffer) and performance
- Page sizes: 4KB, 2MB huge pages, 1GB gigantic pages
- Page faults: demand paging, COW, stack growth
- mprotect() and memory protection
- Guard pages, ASLR, shared memory
- Memory-mapped files

#### ✅ [Topic 24: I/O Internals](topics/topic-24-io-internals.md)
- Complete path of write() from syscall to screen pixels
- File descriptor table internals
- Terminal I/O: TTY layer, line discipline, PTY
- Buffered I/O (why printf doesn't write immediately)
- Implementing printf-like formatting in assembly
- read() path: keyboard → IRQ → driver → TTY → your buffer
- Blocking vs non-blocking I/O, poll/select
- ANSI escape sequences, direct framebuffer access
- writev() scatter/gather I/O

#### ✅ [Topic 25: ELF Binary Format](topics/topic-25-elf-format.md)
- Complete ELF file structure (header, program headers, sections)
- Creating a minimal ELF executable by hand (~170 bytes)
- Object files (.o): relocations and symbol resolution
- The linker: symbol resolution, section merging, address assignment
- Segments vs sections (runtime vs link-time view)
- Dynamic linking: GOT, PLT, lazy binding
- Position-Independent Code (PIC/PIE) and ASLR
- How the kernel loads an ELF (execve internals)
- DWARF debug information

#### ✅ [Topic 26: Interrupts & Exceptions](topics/topic-26-interrupts.md)
- Interrupt types: exceptions, hardware IRQs, software interrupts
- Interrupt Descriptor Table (IDT) structure and entries
- CPU exception handling: page fault, GPF, divide error
- What the CPU pushes on the stack during an exception
- Hardware interrupt delivery (APIC, IRQ routing)
- Timer interrupt and preemptive multitasking
- Debugger breakpoints (INT 3) and hardware watchpoints
- SYSCALL vs INT 0x80 — why syscall is faster
- vDSO: syscalls without entering the kernel

#### ✅ [Topic 27: Context Switching & Scheduling](topics/topic-27-context-switching.md)
- What constitutes process context (all saved state)
- The switch_to mechanism in assembly
- Voluntary vs involuntary context switches
- FPU/SSE/AVX state saving (XSAVE/XRSTOR)
- Thread switching vs process switching
- Thread Local Storage (TLS) and the FS register
- CFS scheduler: vruntime, red-black tree, time slices
- Measuring context switch cost
- CPU affinity and NUMA
- User-space context switching (coroutines)

#### ✅ [Topic 28: Synchronization Primitives](topics/topic-28-synchronization.md)
- x86-64 memory ordering model (TSO)
- Memory barriers (MFENCE, SFENCE, LFENCE)
- Atomic instructions: LOCK prefix, XCHG, CMPXCHG
- Compare-and-Swap (CAS) patterns and retry loops
- Spinlocks: test-and-set, ticket locks
- Futex: fast userspace mutex (hybrid kernel/user approach)
- Implementing a full mutex with futex in assembly
- Lock-free data structures (Treiber stack)
- Read-write locks, semaphores, condition variables
- Producer-consumer with lock-free ring buffer

---

## ❓ Q&A Section - Deep Dives

These files contain detailed explanations of specific questions that came up during learning:

1. **[Push and Pop Explained](qna/push-pop-explained.md)**
   - Stack mechanics
   - LIFO behavior
   - Swapping values with push/pop

2. **[int 0x80 vs syscall](qna/int-vs-syscall.md)**
   - When to use each
   - Register differences
   - Syscall number differences
   - Performance implications

3. **[Memory Addressing with [ ] Brackets](qna/memory-addressing.md)**
   - Dereferencing explained
   - All addressing modes
   - Practical examples
   - Common mistakes

4. **[Sections (.text, .data, .bss) and XOR Optimization](qna/sections-and-optimization.md)**
   - Memory layout
   - Section purposes
   - Relation to C code
   - Why `xor reg, reg` is better than `mov reg, 0`

5. **[CMP vs TEST - What's the Difference?](qna/cmp-vs-test.md)**
   - CMP does subtraction, TEST does AND
   - When to use each instruction
   - Performance comparison
   - Common mistakes and decision tree

6. **[Linux x86-64 Syscall Reference](syscall-reference.md)**
   - Complete syscall register usage (RAX, RDI, RSI, RDX, R10, R8, R9)
   - Common syscalls with examples (read, write, open, close, exit)
   - File I/O, process control, memory management
   - Complete syscall number tables
   - Error handling and return values
   - Practical examples for each syscall

7. **[All Types of Jumps - Complete Reference](qna/all-jump-types.md)**
   - Unconditional jumps (JMP)
   - Conditional jumps: signed (JG, JL, etc.) and unsigned (JA, JB, etc.)
   - Flag-specific jumps (JZ, JS, JC, JO, JP)
   - Loop instructions (LOOP, LOOPE, LOOPNE)
   - Function calls (CALL/RET)
   - Indirect jumps and jump tables (switch statements)
   - Conditional move (CMOVcc) as branchless alternative
   - Complete reference table with all 40+ jump variants
   - Performance optimization patterns

8. **[Instruction Size (Bytes) vs Execution Time (Cycles)](qna/bytes-vs-cycles.md)**
   - Why we measure BOTH bytes and cycles
   - Bytes = space in memory (code size, cache efficiency)
   - Cycles = execution time (performance, speed)
   - How instruction size affects I-cache performance
   - Real-world examples showing both measurements matter
   - When to optimize for bytes vs cycles
   - Measuring techniques for each (objdump, RDTSC, perf)
   - Complete comparison with benchmarks

9. **[How malloc() Actually Works](qna/how-malloc-works.md)**
   - The hidden chunk header (why free knows the size)
   - Free list bins (fast bins, small bins, large bins)
   - malloc decision tree: tcache → fastbin → brk → mmap
   - Why free() doesn't return memory to the OS
   - Assembly-level implementation
   - Common bugs: use-after-free, double-free, heap overflow

10. **[How fork() Actually Works](qna/how-fork-works.md)**
    - Copy-on-Write explained (no actual memory copy!)
    - Page table manipulation during fork
    - COW page fault sequence
    - Why fork() returns different values in parent/child
    - fork+exec efficiency with COW
    - vfork for ultra-fast fork+exec

11. **[Virtual Memory Explained](qna/virtual-memory-explained.md)**
    - Virtual addresses are an illusion
    - The 4-level page table walk visualized
    - TLB: why translation isn't slow (99%+ hit rate)
    - What page faults really are (5 cases)
    - /proc/self/maps: observing your own mappings
    - Key insights: free until touched, isolation, shared libraries

12. **[Signals, Traps, and Exception Handling](qna/signals-and-traps.md)**
    - Signal vs exception vs interrupt
    - How the kernel delivers signals (stack modification)
    - Catching SIGSEGV and resuming execution
    - Signal lifecycle: generated → pending → delivered
    - Common signals reference table
    - Async-signal-safety: what you can/can't do in handlers

---

## 🎓 Progress Tracking

**✅ Foundation (Weeks 1-2):**
- ✅ Topic 1: Setup & First Program
- ✅ Topic 2: Registers & Data Types
- ✅ Topic 3: Basic Instructions

**✅ Control Flow (Weeks 3-4):**
- ✅ Topic 4: Flags & Comparisons
- ✅ Topic 5: Conditional Jumps
- ✅ Topic 6: Loops

**✅ The Stack (Week 5):**
- ✅ Topic 7: Stack Operations
- ✅ Topic 8: Stack Frames

**✅ Functions & Procedures (Weeks 6-7):**
- ✅ Topic 9: Calling Conventions
- ✅ Topic 10: Procedures

**✅ Memory & Addressing (Week 8):**
- ✅ Topic 11: Memory Addressing Modes
- ✅ Topic 12: Arrays & Strings

**✅ Advanced Operations (Weeks 9-10):**
- ✅ Topic 13: Multiplication & Division
- ✅ Topic 14: Shifts & Rotates (Advanced)
- ✅ Topic 15: Macros & Directives

**✅ System Programming (Weeks 11-12):**
- ✅ Topic 16: Linux System Calls
- ✅ Topic 17: Interfacing with C

**✅ Optimization & Advanced (Weeks 13-14):**
- ✅ Topic 18: SIMD Instructions
- ✅ Topic 19: Performance & Optimization
- ✅ Topic 20: Debugging & Tools

**✅ OS Internals (Weeks 15-18):**
- ✅ Topic 21: Memory Allocation Internals
- ✅ Topic 22: Process Internals
- ✅ Topic 23: Virtual Memory & Paging
- ✅ Topic 24: I/O Internals
- ✅ Topic 25: ELF Binary Format
- ✅ Topic 26: Interrupts & Exceptions
- ✅ Topic 27: Context Switching & Scheduling
- ✅ Topic 28: Synchronization Primitives

**Supplementary:**
- ✅ Instruction Encoding (Advanced)
- ✅ All 12 Q&A deep-dive articles
- ✅ Comprehensive syscall reference

**🎉 ALL 28 TOPICS COMPLETED!** Over 50,000 lines of comprehensive content!

---

## 📖 How to Use This Tutorial

1. **Sequential Learning**: Follow topics in order - each builds on previous knowledge
2. **Hands-On Practice**: Type and run every code example
3. **Complete Exercises**: Practice problems reinforce concepts
4. **Check Understanding**: Review knowledge checks before moving on
5. **Reference Q&A**: Deep dive into specific questions as needed

---

## 🛠️ Prerequisites

- Linux system (64-bit recommended)
- NASM installed: `sudo yum install nasm`
- GCC for linking: `sudo yum install gcc`
- Text editor (vim, nano, VSCode, etc.)
- Terminal access

---

## 📝 Quick Command Reference

```bash
# Assemble 64-bit
nasm -f elf64 program.asm -o program.o

# Link
ld -o program program.o

# Run
./program

# Check exit code
echo $?

# Assemble with debug info
nasm -f elf64 -g -F dwarf program.asm

# Debug with GDB
gdb ./program
```

---

## 🎯 Learning Goals

By completing this course, you will be able to:

✅ Write complete assembly programs from scratch
✅ Understand x86-64 architecture deeply
✅ Read and understand compiler output
✅ Optimize code at the lowest level
✅ Debug assembly with confidence
✅ Interface assembly with high-level languages
✅ Work with system calls and OS interfaces
✅ Apply assembly knowledge to reverse engineering and security
✅ Understand how malloc/free manage memory (brk, mmap, free lists)
✅ Know exactly what fork/exec do at the page table level
✅ Explain virtual memory translation (4-level page tables, TLB)
✅ Trace the path of a write() from syscall to screen pixels
✅ Parse and understand ELF binaries (headers, segments, relocations)
✅ Implement synchronization primitives (spinlocks, mutexes, lock-free structures)
✅ Understand how the OS context-switches between processes

---

## 📚 Additional Resources

- **Official NASM Documentation**: https://www.nasm.us/docs.php
- **Intel Manuals**: Intel® 64 and IA-32 Architectures Software Developer Manuals
- **Linux Syscall Table**: https://filippo.io/linux-syscall-table/
- **Practice**: [pwn.college](https://pwn.college), [crackmes.one](https://crackmes.one)

---

## 🤝 Contributing

Found an error? Have a question? Want to add content?
Feel free to modify and extend these materials!

---

**Current Status**: 🎉 **ALL 28 TOPICS COMPLETED!** Over 50,000 lines of comprehensive NASM assembly programming content covering everything from Hello World to OS internals, with working assembly implementations of malloc, fork, page tables, ELF loading, context switching, and lock-free data structures!

---

*Happy Assembly Programming! 🚀*

