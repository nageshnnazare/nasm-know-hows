# Instruction Size (Bytes) vs Execution Time (Cycles)

## The Question

**"Why is every instruction written with 2 bytes, 5 bytes, etc.? Aren't we supposed to see the cycles and not bytes?"**

**Short Answer:** Both matter! **Bytes** measure how much memory/space an instruction occupies, while **cycles** measure how long it takes to execute. They're different measurements for different purposes.

---

## Understanding the Difference

### Instruction Size (Bytes) - Space in Memory

```c
// C equivalent concept:
sizeof(instruction)  // How much memory does it occupy?
```

**What it measures:** The physical size of the machine code instruction in memory.

**Why it matters:**
1. **Code size** - smaller programs fit in cache better
2. **Instruction fetch** - CPU must fetch these bytes from memory
3. **Cache efficiency** - more instructions fit in I-cache
4. **Jump distances** - affects whether you can use short jumps

**Example:**

```nasm
; These do the same thing but have different sizes:

mov rax, 0          ; 7 bytes: REX.W + opcode + immediate (8 bytes)
xor rax, rax        ; 3 bytes: REX.W + opcode + ModRM

; Both set RAX to zero, but XOR is 4 bytes smaller!
```

**Hexdump showing actual bytes:**

```
48 c7 c0 00 00 00 00    ; mov rax, 0 (7 bytes)
48 31 c0                ; xor rax, rax (3 bytes)
```

---

### Execution Time (Cycles) - How Long It Takes

```c
// C equivalent concept:
time_to_execute(instruction)  // How many CPU cycles?
```

**What it measures:** The number of CPU clock cycles required to execute the instruction.

**Why it matters:**
1. **Performance** - faster code = fewer cycles
2. **Latency** - when is the result available?
3. **Throughput** - how many per second can execute?
4. **Optimization** - choosing faster instructions

**Example:**

```nasm
; Same result, but different execution times:

mov rax, 0          ; ~1 cycle latency
xor rax, rax        ; ~0 cycles latency (dependency breaking!)

div rbx             ; ~40-90 cycles (very slow!)
shr rax, 1          ; ~1 cycle (fast alternative for divide by 2)
```

---

## Both Measurements Are Important!

### Real-World Example: Jump Instructions

Let's look at why we care about BOTH for jumps:

```nasm
section .text
loop_start:
    ; Loop body (10 bytes of instructions)
    inc rax
    cmp rax, 100
    
    ; Which jump should we use?
```

#### Option 1: Short Jump (2 bytes)

```nasm
jl loop_start       ; 2 bytes: EB F6
```

**Bytes:** 2 bytes (opcode + 8-bit signed offset)
**Cycles:** 1-2 cycles if predicted correctly, ~15-20 if mispredicted
**Range:** -128 to +127 bytes

#### Option 2: Near Jump (5-6 bytes)

```nasm
jl loop_start       ; 5-6 bytes: 0F 8C [4-byte offset]
```

**Bytes:** 5-6 bytes (prefix + opcode + 32-bit offset)
**Cycles:** Same 1-2 cycles if predicted, ~15-20 if mispredicted
**Range:** ±2GB

### Why BOTH Matter:

```nasm
; If loop_start is nearby (< 128 bytes away):
jl loop_start       ; NASM generates: 2 bytes
                    ; Faster to fetch from memory
                    ; More code fits in cache
                    ; Same execution time

; If loop_start is far away (> 127 bytes):
jl loop_start       ; NASM generates: 5-6 bytes
                    ; Required for large distance
                    ; Same execution time
                    ; Takes more space
```

---

## Complete Comparison Table

| Aspect | Instruction Size (Bytes) | Execution Time (Cycles) |
|--------|-------------------------|------------------------|
| **Measures** | Memory/space occupied | Time to execute |
| **Unit** | Bytes | CPU clock cycles |
| **Affects** | Code size, cache efficiency | Performance, speed |
| **Visible in** | Disassembly, hexdump | Profiler, benchmarks |
| **Matters for** | Memory, I-cache | Execution speed |
| **Fixed?** | Yes (per encoding) | No (varies by CPU) |

---

## Why Bytes Matter: Code Density

### Example: Loop with Different Jump Sizes

```nasm
; Short jumps (2 bytes each) - GOOD
section .text
    xor rax, rax
.loop:
    inc rax
    cmp rax, 10
    jl .loop        ; 2 bytes (loop is nearby)
    ret

; Total: ~15 bytes
; Fits entirely in ONE cache line (64 bytes)
; Fast instruction fetch!
```

```nasm
; Long jumps (5-6 bytes each) - WORSE
section .text
    xor rax, rax
    jmp start       ; Force long jumps
    times 200 nop   ; Padding to force distance
start:
.loop:
    inc rax
    cmp rax, 10
    jl .loop        ; 5-6 bytes (forced long jump)
    ret

; Total: ~220 bytes
; Spans MULTIPLE cache lines
; Slower instruction fetch
; Same execution time for the jump itself!
```

**Result:**
- Short version: Fetches 1 cache line → faster overall
- Long version: Fetches 4 cache lines → slower overall
- Individual jump cycle count: SAME
- Total program performance: DIFFERENT (due to I-cache)

---

## Why Cycles Matter: Execution Speed

### Example: Division vs Shift

```nasm
; C equivalent:
; unsigned int result = x / 4;

; Option 1: Division instruction
mov eax, [x]
xor edx, edx
mov ecx, 4
div ecx             ; SIZE: 2 bytes, TIME: ~40-90 cycles (SLOW!)
mov [result], eax

; Option 2: Shift instruction  
mov eax, [x]
shr eax, 2          ; SIZE: 3 bytes, TIME: ~1 cycle (FAST!)
mov [result], eax
```

**Comparison:**

| Instruction | Size (Bytes) | Cycles | Speed Difference |
|-------------|-------------|--------|------------------|
| `div ecx` | 2 | ~40-90 | Baseline |
| `shr eax, 2` | 3 | ~1 | **40-90x faster!** |

**Key Point:** The shift is **1 byte larger** but **40-90x faster**! Here, cycles matter WAY more than bytes.

---

## When Each Measurement Matters Most

### Bytes Matter Most When:

1. **Embedded systems** - limited ROM/Flash
2. **Cache optimization** - fitting hot loops in I-cache
3. **Code golf** - making smallest possible program
4. **Firmware** - space-constrained environments

```nasm
; Embedded: Every byte counts!
xor rax, rax        ; 3 bytes (GOOD)
; vs
mov rax, 0          ; 7 bytes (WASTEFUL)
```

### Cycles Matter Most When:

1. **Performance optimization** - hot loops
2. **Real-time systems** - predictable timing
3. **High-throughput** - processing large data
4. **Latency-sensitive** - fast response time

```nasm
; Performance: Speed is critical!
shr eax, 2          ; 1 cycle (GOOD)
; vs
div ecx             ; 90 cycles (TERRIBLE)
```

---

## Both Matter Together: The I-Cache Effect

Modern CPUs have separate caches for instructions (I-cache) and data (D-cache).

### Instruction Cache (I-Cache)

**Typical sizes:**
- L1 I-Cache: 32-64 KB
- Cache line: 64 bytes

**How instruction size affects performance:**

```nasm
; Example: Hot loop (executed millions of times)

; Version 1: Compact (short jumps, small instructions)
section .text
hot_loop:
    mov eax, [rsi]
    add eax, [rdi]
    mov [rdx], eax
    add rsi, 4
    add rdi, 4
    add rdx, 4
    dec rcx
    jnz hot_loop        ; 2 bytes (short jump)
    ret
; Total: ~30 bytes - fits in ONE cache line!
```

```nasm
; Version 2: Bloated (long jumps, inefficient encoding)
section .text
    jmp start
    times 100 nop       ; Force long jumps
start:
hot_loop:
    mov eax, [rsi]
    add eax, [rdi]  
    mov [rdx], eax
    add rsi, 4
    add rdi, 4
    add rdx, 4
    dec rcx
    jnz hot_loop        ; 6 bytes (long jump, forced)
    ret
; Total: ~130 bytes - spans THREE cache lines!
```

**Performance Impact:**

```
Version 1 (30 bytes):
- Cache line fetches per iteration: 0 (already in I-cache)
- I-cache misses: 0
- Execution time: ~10 cycles per iteration

Version 2 (130 bytes):
- Cache line fetches per iteration: 0-3 (depending on alignment)
- I-cache misses: More frequent
- Execution time: ~10-80 cycles per iteration (with cache misses)
```

**Conclusion:** Even though the instructions execute in the same number of cycles, Version 1 is **much faster overall** because it fits in I-cache!

---

## Practical Guidelines

### Optimize for Bytes When:

```nasm
; Hot loop that fits in I-cache
tight_loop:
    ; Use shortest instructions
    xor eax, eax        ; 2-3 bytes
    lea rbx, [rsi+8]    ; 4 bytes (vs mov+add = 7 bytes)
    inc rcx             ; 3 bytes (vs add rcx, 1 = 4 bytes)
    loop tight_loop     ; 2 bytes
```

### Optimize for Cycles When:

```nasm
; One-time initialization (not in hot path)
initialization:
    ; Use fastest instructions, size doesn't matter
    xor rax, rax        ; Fast (zero latency)
    xorps xmm0, xmm0    ; Fast (zero latency)
    
    ; Avoid slow instructions
    ; BAD: div rbx (90 cycles)
    ; GOOD: shr rax, cl (1 cycle)
```

### Optimize for Both:

```nasm
; Best: Short AND fast
ideal:
    xor eax, eax        ; 2-3 bytes, 0 cycle latency ✅
    inc ecx             ; 2-3 bytes, 1 cycle latency ✅
    shl rax, 3          ; 3-4 bytes, 1 cycle latency ✅
```

---

## How to Measure Each

### Measuring Instruction Size (Bytes)

#### Method 1: Disassembly with objdump

```bash
$ objdump -d program | grep -A5 "loop_start"
00401000 <loop_start>:
  401000:   48 31 c0          xor    rax,rax         # 3 bytes
  401003:   48 ff c0          inc    rax             # 3 bytes
  401006:   48 83 f8 0a       cmp    rax,0xa         # 4 bytes
  40100a:   7c f7             jl     401003          # 2 bytes (short)
```

#### Method 2: Hexdump

```bash
$ hexdump -C program | head
00000000  48 31 c0 48 ff c0 48 83  f8 0a 7c f7 c3
```

#### Method 3: NASM listing

```bash
$ nasm -f elf64 -l listing.txt program.asm
$ cat listing.txt
     1 00000000 4831C0            xor rax, rax        ; 3 bytes
     2 00000003 48FFC0            inc rax             ; 3 bytes
     3 00000006 4883F80A          cmp rax, 10         ; 4 bytes
     4 0000000A 7CF7              jl loop_start       ; 2 bytes
```

### Measuring Execution Time (Cycles)

#### Method 1: RDTSC (CPU timestamp counter)

```nasm
section .text
global benchmark

benchmark:
    ; Start timing
    rdtsc                   ; Read timestamp
    shl rdx, 32
    or rax, rdx            ; RDX:RAX = 64-bit cycle count
    mov r12, rax           ; Save start time
    
    ; CODE TO BENCHMARK
    mov eax, 100
    xor edx, edx
    mov ecx, 4
    div ecx                ; Measure this
    
    ; End timing
    rdtsc
    shl rdx, 32
    or rax, rdx
    sub rax, r12           ; RAX = cycles elapsed
    ret
```

#### Method 2: perf (Linux)

```bash
$ perf stat -e cycles,instructions ./program

 Performance counter stats for './program':

     1,234,567      cycles
       456,789      instructions              #    0.37  insn per cycle
```

#### Method 3: Intel Architecture Code Analyzer (IACA)

```bash
$ iaca -arch SKL program.o
Throughput Analysis Report
Block Throughput: 2.50 Cycles
```

---

## Real-World Example: Optimizing a Loop

```c
// C code to optimize:
for (int i = 0; i < 1000000; ++i) {
    result += array[i];
}
```

### Version 1: Naive (Not optimized)

```nasm
    xor eax, eax            ; result = 0
    xor ecx, ecx            ; i = 0
loop_v1:
    add eax, [array + rcx*4]  ; 7 bytes
    inc ecx                   ; 3 bytes
    cmp ecx, 1000000          ; 6 bytes
    jl loop_v1                ; 6 bytes (near jump, forced by size)
    
; Size: ~22 bytes per iteration
; Cycles: ~5 per iteration (with I-cache misses)
; Total: 1M iterations × 5 cycles = 5M cycles
```

### Version 2: Optimized for Bytes AND Cycles

```nasm
    xor eax, eax            ; result = 0
    mov ecx, 1000000        ; i = 1000000 (count down)
    lea rsi, [array]        ; Pointer to array
loop_v2:
    add eax, [rsi]          ; 2 bytes (simpler addressing)
    add rsi, 4              ; 3 bytes
    dec ecx                 ; 2 bytes
    jnz loop_v2             ; 2 bytes (short jump!)
    
; Size: ~9 bytes per iteration (fits in I-cache!)
; Cycles: ~2 per iteration (no I-cache misses)
; Total: 1M iterations × 2 cycles = 2M cycles
```

**Improvement: 2.5x faster!** (Both from bytes AND better instruction choice)

---

## Summary

### Key Takeaways:

1. **Bytes = Space** (how big is the instruction in memory)
2. **Cycles = Time** (how long does it take to execute)
3. **Both matter** for different reasons
4. **Small code** → better I-cache efficiency → faster overall
5. **Fast instructions** → fewer cycles → faster execution

### When to Focus on Each:

| Situation | Focus | Why |
|-----------|-------|-----|
| Hot loops | Both | Small code fits in I-cache, fast instructions reduce cycles |
| Cold code | Cycles | Executed rarely, size doesn't matter |
| Embedded | Bytes | Limited memory, space critical |
| Performance | Cycles | Speed is critical |

### The Best Code:

```nasm
; Ideal: Short AND fast!
xor rax, rax        ; 3 bytes, 0 cycle latency ✅
shl rax, 3          ; 4 bytes, 1 cycle latency ✅
; vs
mov rax, 0          ; 7 bytes, 1 cycle latency ❌ (wasteful)
; vs  
div rbx             ; 2 bytes, 90 cycle latency ❌ (slow)
```

---

## Related Topics

- [Topic 19: Performance & Optimization](../topics/topic-19-performance.md) - Detailed cycle analysis
- [Instruction Encoding](instruction-encoding.md) - How bytes are structured
- [Sections & Optimization](sections-and-optimization.md) - Why XOR is smaller
- [All Jump Types](all-jump-types.md) - Jump sizes and distances

---

**Bottom Line:** We measure instructions in **bytes** for size/space and **cycles** for speed/time. Both measurements are critical for understanding and optimizing assembly code! 🚀

