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

**Supplementary:**
- ✅ Instruction Encoding (Advanced)
- ✅ All Q&A articles with C equivalents
- ✅ Comprehensive syscall reference

**🎉 ALL 20 TOPICS COMPLETED!** Over 30,000 lines of comprehensive content!

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

**Current Status**: 🎉 **ALL 20 TOPICS COMPLETED!** Over 30,000 lines of comprehensive NASM assembly programming content with C equivalents throughout!

---

*Happy Assembly Programming! 🚀*

