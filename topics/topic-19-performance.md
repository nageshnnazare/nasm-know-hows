# Topic 19: Performance and Optimization

## Overview

Writing correct assembly is one thing; writing *fast* assembly is another. This topic covers techniques to maximize performance by understanding CPU architecture, instruction timing, memory hierarchy, and compiler-level optimizations.

```c
// Correct but slow:
for (int i = 0; i < n; ++i) {
    result += array[i];  // Memory access every iteration
}

// Fast:
int temp = 0;
for (int i = 0; i < n; ++i) {
    temp += array[i];    // Register accumulation
}
result = temp;
```

---

## CPU Architecture Fundamentals

### Pipeline Stages

Modern CPUs use instruction pipelining to execute multiple instructions simultaneously:

```
Cycle: 1    2    3    4    5    6    7    8
Inst1: F    D    E    M    W
Inst2:      F    D    E    M    W
Inst3:           F    D    E    M    W
Inst4:                F    D    E    M    W

F = Fetch, D = Decode, E = Execute, M = Memory, W = Write-back
```

**Throughput:** Up to 1 instruction per cycle (ideal)  
**Latency:** Individual instruction takes multiple cycles

### Superscalar Execution

Modern CPUs can execute multiple instructions per cycle:

```
Port 0: ALU, FPU
Port 1: ALU, FPU
Port 2: Load (Memory Read)
Port 3: Load (Memory Read)
Port 4: Store (Memory Write)
Port 5: ALU, Branch

Example: These can execute in parallel:
mov rax, [data]     ; Port 2 (load)
add rbx, rcx        ; Port 0 or 1 (ALU)
imul rdx, rsi       ; Port 1 (multiply)
```

**Instruction-Level Parallelism (ILP):** CPU finds independent instructions and executes them simultaneously.

---

## Instruction Timing

### Latency vs Throughput

**Latency:** Cycles until result is available  
**Throughput:** How often instruction can be issued

Example (typical Intel/AMD):

| Instruction | Latency | Throughput | Ports |
|-------------|---------|------------|-------|
| `mov r, r` | 0-1 | 0.25/cycle | 0,1,5,6 |
| `add r, r` | 1 | 0.25/cycle | 0,1,5,6 |
| `imul r, r` | 3 | 1/cycle | 1 |
| `div r64` | 36-95 | 21-74/cycle | 0 |
| `movaps xmm, m` | 5-7 | 0.5/cycle | 2,3 |
| `addps xmm, xmm` | 3-4 | 0.5/cycle | 0,1 |

**Key Insight:** Focus on **throughput** for loops, **latency** for dependency chains.

### Dependency Chains

```nasm
; C equivalent:
; int a = 1;
; a = a + 1;  // Depends on previous
; a = a + 1;  // Depends on previous
; a = a + 1;  // Depends on previous

; BAD: Serial dependency chain (latency = 3 cycles)
mov eax, 1
add eax, 1          ; Waits for previous
add eax, 1          ; Waits for previous
add eax, 1          ; Waits for previous
; Total: ~3 cycles

; GOOD: Independent operations (throughput = 1 cycle)
mov eax, 1
mov ebx, 1
mov ecx, 1
add eax, 1          ; All execute in parallel
add ebx, 1
add ecx, 1
; Total: ~1 cycle
```

---

## Memory Hierarchy

### Cache Levels

```
CPU Registers:  < 1 cycle      ~1 KB
L1 Cache:       4-5 cycles     32-64 KB per core
L2 Cache:       12-15 cycles   256-512 KB per core
L3 Cache:       40-75 cycles   4-32 MB shared
RAM:            200+ cycles    Gigabytes
```

**Performance Impact:** Cache miss can be **50-200x slower** than cache hit!

### Cache Lines

- **Size:** 64 bytes (typical)
- **Prefetching:** CPU loads entire cache line, not just requested byte
- **Alignment:** Misaligned access may span two cache lines

```nasm
; C equivalent:
; struct Data { int value; char padding[60]; };  // 64 bytes
; Data array[100];  // Each element = one cache line

section .bss
    align 64
    data resb 6400      ; 100 x 64-byte structures

; Access aligned to cache line - FAST
mov eax, [data]
mov eax, [data + 64]
mov eax, [data + 128]

; Misaligned - may span cache lines - SLOWER
mov eax, [data + 1]
```

### False Sharing

```c
// BAD: Two threads writing to same cache line
struct {
    int counter1;  // Thread 1 writes here
    int counter2;  // Thread 2 writes here (same cache line!)
} shared;

// GOOD: Separate cache lines
struct {
    int counter1;
    char padding[60];
    int counter2;
} shared;
```

---

## Optimization Techniques

### 1. Loop Unrolling

Process multiple iterations in one loop iteration to reduce overhead.

```nasm
; C equivalent:
; int sum = 0;
; for (int i = 0; i < n; ++i) {
;     sum += array[i];
; }

; Original loop
xor eax, eax            ; sum = 0
xor ecx, ecx            ; i = 0
loop_original:
    add eax, [array + rcx*4]
    inc ecx
    cmp ecx, [n]
    jl loop_original
; Overhead: cmp, jl every iteration

; Unrolled by 4
xor eax, eax
xor ecx, ecx
mov edx, [n]
shr edx, 2              ; n / 4
loop_unrolled:
    add eax, [array + rcx*4]
    add eax, [array + rcx*4 + 4]
    add eax, [array + rcx*4 + 8]
    add eax, [array + rcx*4 + 12]
    add ecx, 4
    dec edx
    jnz loop_unrolled
; Overhead: dec, jnz every 4 iterations (4x less!)
```

**Benefits:**
- Reduced branch overhead
- More instruction-level parallelism
- Better CPU utilization

**Drawback:** Increased code size

### 2. Multiple Accumulators

Break dependency chains by using multiple independent accumulators.

```nasm
; C equivalent:
; int sum = 0;
; for (int i = 0; i < n; ++i) {
;     sum += array[i];
; }

; Single accumulator (dependency chain)
xor eax, eax
xor ecx, ecx
loop_single:
    add eax, [array + rcx*4]    ; Each add depends on previous
    inc ecx
    cmp ecx, [n]
    jl loop_single
; Latency-bound!

; Four accumulators (parallel)
xor eax, eax        ; sum0
xor ebx, ebx        ; sum1
xor edx, edx        ; sum2
xor esi, esi        ; sum3
xor ecx, ecx
loop_parallel:
    add eax, [array + rcx*4]
    add ebx, [array + rcx*4 + 4]
    add edx, [array + rcx*4 + 8]
    add esi, [array + rcx*4 + 12]
    add ecx, 4
    cmp ecx, [n]
    jl loop_parallel

; Combine accumulators
add eax, ebx
add edx, esi
add eax, edx
; Much faster! Throughput-bound instead of latency-bound
```

### 3. Software Pipelining

Overlap operations from different iterations.

```nasm
; C equivalent:
; for (int i = 0; i < n; ++i) {
;     int temp = expensive_operation(array[i]);
;     result[i] = process(temp);
; }

; Original (serial)
loop_original:
    mov eax, [array + rcx*4]
    ; expensive_operation (10 cycles latency)
    imul eax, eax
    imul eax, eax
    ; process
    add eax, 1
    mov [result + rcx*4], eax
    inc rcx
    cmp ecx, [n]
    jl loop_original

; Pipelined (overlap operations)
mov eax, [array]            ; Preload first
imul eax, eax
loop_pipelined:
    imul eax, eax           ; Finish expensive op for i
    mov ebx, [array + rcx*4 + 4]  ; Start load for i+1
    add eax, 1              ; Process for i
    imul ebx, ebx           ; Start expensive op for i+1
    mov [result + rcx*4], eax
    mov eax, ebx            ; Move i+1 result to working register
    inc rcx
    cmp ecx, [n]
    jl loop_pipelined
```

### 4. Strength Reduction

Replace expensive operations with cheaper equivalents.

```nasm
; C equivalent:
; for (int i = 0; i < n; ++i) {
;     result[i] = array[i] * 10;
; }

; SLOW: Multiplication every iteration
loop_mul:
    mov eax, [array + rcx*4]
    imul eax, 10                ; 3 cycles latency
    mov [result + rcx*4], eax
    inc rcx
    cmp ecx, [n]
    jl loop_mul

; FAST: LEA trick
loop_lea:
    mov eax, [array + rcx*4]
    lea eax, [rax + rax*4]      ; eax = rax + rax*4 = rax*5
    add eax, eax                ; eax = eax*2 = rax*10 (1 cycle!)
    mov [result + rcx*4], eax
    inc rcx
    cmp ecx, [n]
    jl loop_lea
```

**Common Strength Reductions:**

| Original | Optimized | Savings |
|----------|-----------|---------|
| `x * 2` | `add x, x` or `shl x, 1` | 2 cycles |
| `x / 2` (unsigned) | `shr x, 1` | 20+ cycles |
| `x % powerof2` | `and x, (powerof2-1)` | 20+ cycles |
| `x * 10` | `lea rax, [rax+rax*4]` + `add rax, rax` | 2 cycles |

### 5. Induction Variable Elimination

Compute addresses directly instead of using index.

```nasm
; C equivalent:
; for (int i = 0; i < n; ++i) {
;     result[i] = array[i] + 1;
; }

; With index
xor ecx, ecx
loop_index:
    mov eax, [array + rcx*4]    ; Compute address every time
    add eax, 1
    mov [result + rcx*4], eax   ; Compute address every time
    inc ecx
    cmp ecx, [n]
    jl loop_index

; With pointer
lea rsi, [array]
lea rdi, [result]
mov ecx, [n]
loop_pointer:
    mov eax, [rsi]              ; Direct dereference
    add eax, 1
    mov [rdi], eax              ; Direct dereference
    add rsi, 4                  ; Increment pointer
    add rdi, 4
    dec ecx
    jnz loop_pointer
; Fewer address calculations!
```

---

## Branch Optimization

### Branch Prediction

Modern CPUs predict branch outcomes to avoid pipeline stalls.

**Branch Misprediction Penalty:** 15-20 cycles!

```nasm
; C equivalent:
; int count = 0;
; for (int i = 0; i < n; ++i) {
;     if (array[i] > threshold) {  // Hard to predict!
;         count++;
;     }
; }

; BAD: Unpredictable branch
xor eax, eax            ; count
xor ecx, ecx
loop_branch:
    mov edx, [array + rcx*4]
    cmp edx, [threshold]
    jle skip                ; 50% misprediction if data is random
    inc eax
skip:
    inc ecx
    cmp ecx, [n]
    jl loop_branch
```

### Branch-Free Code (Predication)

```nasm
; C equivalent (branchless):
; count += (array[i] > threshold);

; GOOD: Branchless with conditional move
xor eax, eax
xor ecx, ecx
loop_branchless:
    mov edx, [array + rcx*4]
    xor ebx, ebx            ; temp = 0
    cmp edx, [threshold]
    setg bl                 ; bl = 1 if edx > threshold, else 0
    add eax, ebx            ; No branch!
    inc ecx
    cmp ecx, [n]
    jl loop_branchless

; Alternative with CMOV
loop_cmov:
    mov edx, [array + rcx*4]
    mov ebx, eax
    inc ebx                 ; ebx = count + 1
    cmp edx, [threshold]
    cmovg eax, ebx          ; count = (edx > threshold) ? ebx : count
    inc ecx
    cmp ecx, [n]
    jl loop_cmov
```

### Loop-Invariant Code Motion

Move calculations that don't change out of the loop.

```nasm
; C equivalent:
; int factor = x * 2 + 5;
; for (int i = 0; i < n; ++i) {
;     result[i] = array[i] * factor;
; }

; BAD: Recomputing factor every iteration
loop_bad:
    mov eax, [x]
    shl eax, 1
    add eax, 5              ; Computed every iteration!
    imul eax, [array + rcx*4]
    mov [result + rcx*4], eax
    inc rcx
    cmp ecx, [n]
    jl loop_bad

; GOOD: Compute factor once
mov eax, [x]
shl eax, 1
add eax, 5
mov ebx, eax            ; Save factor

loop_good:
    mov eax, [array + rcx*4]
    imul eax, ebx       ; Use saved factor
    mov [result + rcx*4], eax
    inc rcx
    cmp ecx, [n]
    jl loop_good
```

---

## Data Alignment

### Alignment Requirements

```nasm
; SLOW: Misaligned data
section .data
    x db 0
    data dq 0x123456789ABCDEF0  ; Misaligned!

; FAST: Aligned data
section .data
    align 8
    data dq 0x123456789ABCDEF0  ; 8-byte aligned

; CRITICAL for SIMD
section .data
    align 16
    floats dd 1.0, 2.0, 3.0, 4.0  ; Must be 16-byte aligned for movaps
```

**Performance Impact:**
- Misaligned scalar access: 0-10% slower
- Misaligned SIMD access: Can be **2-3x slower** or **crash**!

### Structure Padding

```c
// BAD: Lots of padding, poor cache utilization
struct Data {
    char a;       // 1 byte
    // 7 bytes padding
    double b;     // 8 bytes (needs 8-byte alignment)
    char c;       // 1 byte
    // 7 bytes padding
};  // Total: 24 bytes (13 bytes wasted!)

// GOOD: Reordered to minimize padding
struct Data {
    double b;     // 8 bytes
    char a;       // 1 byte
    char c;       // 1 byte
    // 6 bytes padding (end)
};  // Total: 16 bytes (6 bytes wasted)
```

---

## Complete Optimization Example

### Problem: Compute average of large array

```nasm
; Original - unoptimized
; C equivalent:
; double average = 0;
; for (int i = 0; i < n; ++i) {
;     average += array[i];
; }
; average /= n;

average_slow:
    xorpd xmm0, xmm0        ; sum = 0.0
    xor ecx, ecx            ; i = 0
.loop:
    addsd xmm0, [rdi + rcx*8]   ; Scalar add (2 doubles per cycle max)
    inc ecx
    cmp ecx, esi
    jl .loop
    
    cvtsi2sd xmm1, esi      ; Convert n to double
    divsd xmm0, xmm1        ; Divide (very slow!)
    ret
```

```nasm
; Optimized version
; Uses: SIMD, unrolling, multiple accumulators

average_fast:
    ; Check if we have enough elements for SIMD
    cmp esi, 8
    jl .scalar_fallback
    
    ; Initialize 4 accumulators for parallel accumulation
    xorpd xmm0, xmm0        ; sum0
    xorpd xmm1, xmm1        ; sum1
    xorpd xmm2, xmm2        ; sum2
    xorpd xmm3, xmm3        ; sum3
    
    xor ecx, ecx
    mov edx, esi
    shr edx, 3              ; Process 8 doubles per iteration
    jz .remainder
    
.loop_simd:
    ; Process 8 doubles = 4 * 2 doubles
    addpd xmm0, [rdi + rcx*8]       ; Add 2 doubles
    addpd xmm1, [rdi + rcx*8 + 16]  ; Add 2 doubles
    addpd xmm2, [rdi + rcx*8 + 32]  ; Add 2 doubles
    addpd xmm3, [rdi + rcx*8 + 48]  ; Add 2 doubles
    add ecx, 8
    dec edx
    jnz .loop_simd
    
.remainder:
    ; Handle remaining elements (n % 8)
    mov edx, esi
    and edx, 7
    jz .horizontal_sum
    
.remainder_loop:
    addsd xmm0, [rdi + rcx*8]
    inc ecx
    dec edx
    jnz .remainder_loop
    
.horizontal_sum:
    ; Combine the 4 accumulators
    addpd xmm0, xmm1        ; xmm0 = sum0+sum1
    addpd xmm2, xmm3        ; xmm2 = sum2+sum3
    addpd xmm0, xmm2        ; xmm0 = all sums
    
    ; Horizontal add within xmm0
    movapd xmm1, xmm0
    unpckhpd xmm1, xmm0     ; Extract high double
    addsd xmm0, xmm1        ; Final sum
    
    ; Divide by n (use multiplication by reciprocal if n is constant!)
    cvtsi2sd xmm1, esi
    divsd xmm0, xmm1
    ret
    
.scalar_fallback:
    ; Handle small arrays
    xorpd xmm0, xmm0
    xor ecx, ecx
.scalar_loop:
    addsd xmm0, [rdi + rcx*8]
    inc ecx
    cmp ecx, esi
    jl .scalar_loop
    cvtsi2sd xmm1, esi
    divsd xmm0, xmm1
    ret
```

**Optimizations Applied:**
1. ✓ SIMD (4x parallelism with packed doubles)
2. ✓ Loop unrolling (8 elements per iteration)
3. ✓ Multiple accumulators (break dependency chains)
4. ✓ Separate remainder handling
5. ✓ Scalar fallback for small arrays

**Expected Speedup:** 10-15x over naive version!

---

## Profiling and Measurement

### CPU Cycle Counting

```nasm
section .text
global benchmark_function

benchmark_function:
    ; Save registers
    push rbx
    
    ; Read timestamp counter (before)
    rdtsc                   ; EDX:EAX = cycle count
    shl rdx, 32
    or rax, rdx             ; RAX = 64-bit cycle count
    mov rbx, rax            ; Save start time
    
    ; *** Code to benchmark ***
    ; ...
    
    ; Read timestamp counter (after)
    rdtsc
    shl rdx, 32
    or rax, rdx
    
    ; Calculate elapsed cycles
    sub rax, rbx            ; RAX = elapsed cycles
    
    pop rbx
    ret
```

### Using `perf` (Linux)

```bash
# Count cycles, instructions, cache misses
perf stat -e cycles,instructions,cache-misses ./program

# Profile with sampling
perf record -g ./program
perf report

# Analyze specific events
perf stat -e L1-dcache-loads,L1-dcache-load-misses ./program
```

---

## Optimization Checklist

### Algorithm Level
- [ ] Use optimal algorithm (O(n log n) vs O(n²))
- [ ] Minimize memory allocations
- [ ] Cache reusable computations

### Data Structure Level
- [ ] Align data structures
- [ ] Use cache-friendly layouts (SoA vs AoS)
- [ ] Pack structures to minimize padding
- [ ] Consider false sharing in multithreaded code

### Loop Level
- [ ] Unroll loops (2x, 4x, 8x)
- [ ] Use multiple accumulators
- [ ] Move invariant code out of loop
- [ ] Eliminate induction variables
- [ ] Use SIMD when possible

### Instruction Level
- [ ] Use faster instructions (LEA, shifts vs multiply/divide)
- [ ] Minimize dependency chains
- [ ] Use conditional moves instead of branches
- [ ] Align loop targets
- [ ] Avoid partial register stalls

### Memory Level
- [ ] Prefetch data before use
- [ ] Access memory sequentially
- [ ] Minimize cache misses
- [ ] Use appropriate data alignment

---

## Common Pitfalls

### 1. Premature Optimization

```c
// DON'T optimize before profiling!
// 90% of time is often in 10% of code

// Profile first:
// - Find the hot spots
// - Optimize those
// - Measure improvement
```

### 2. Over-Optimization

```nasm
; Sometimes "optimized" code is slower!

; "Optimized" but slower (more instructions, worse for branch prediction)
xor eax, eax
cmp [value], 0
setg al
add [result], eax

; Simpler and faster (well-predicted branch)
cmp [value], 0
jle .skip
inc dword [result]
.skip:
```

### 3. Ignoring the Compiler

```c
// Modern compilers are VERY good
// Sometimes C is faster than hand-written assembly!

// Let the compiler optimize:
int sum = 0;
for (int i = 0; i < n; ++i) {
    sum += array[i];  // Compiler may auto-vectorize this!
}
```

---

## Summary

### Key Principles
1. **Profile first** - Optimize hot paths only
2. **Algorithm beats microoptimization** - O(n) vs O(n²) matters more
3. **Understand hardware** - Cache, pipeline, branch prediction
4. **Break dependencies** - Use multiple accumulators
5. **Use SIMD** - 4-16x speedup for parallel data

### Optimization Priorities
1. **Algorithm** (100x+ gains possible)
2. **Data structures** (10x+ gains)
3. **Loop optimizations** (2-5x gains)
4. **SIMD** (4-16x gains)
5. **Instruction selection** (1.5-2x gains)
6. **Micro-optimizations** (5-20% gains)

### Tools
- **perf** - CPU performance counters
- **valgrind/cachegrind** - Cache profiling
- **gprof** - Function-level profiling
- **RDTSC** - Cycle-accurate timing
- **VTune** - Intel's profiler (commercial)

---

## Practice Exercises

### Exercise 1: Matrix Multiplication
Optimize 4x4 matrix multiplication using SIMD and unrolling.

### Exercise 2: String Length
Write the fastest possible `strlen` implementation.

### Exercise 3: Sorting
Implement optimized quicksort with:
- Insertion sort for small arrays
- Three-way partitioning
- Tail recursion elimination

---

## Next Topic

In **Topic 20: Debugging & Tools**, we'll explore essential debugging techniques, disassembly analysis, and tools for working with assembly code.

**Preview:**
- GDB debugging
- Disassembly with objdump
- strace for syscall tracing
- Memory debugging with valgrind
- Reading crash dumps
- Reverse engineering basics

