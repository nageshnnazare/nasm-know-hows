# Topic 18: SIMD Instructions (SSE/AVX)

## Overview

SIMD (Single Instruction, Multiple Data) allows processing multiple data elements simultaneously with a single instruction. Modern x86-64 processors support several SIMD instruction sets: SSE, SSE2, SSE3, SSSE3, SSE4, AVX, AVX2, and AVX-512.

```c
// C equivalent - scalar processing:
for (int i = 0; i < 4; ++i) {
    result[i] = a[i] + b[i];  // 4 separate additions
}

// SIMD - vectorized processing:
// One instruction processes 4 floats at once!
// result_vector = a_vector + b_vector;
```

**Performance Gain:** Up to **4x-16x** speedup for compatible workloads!

---

## SIMD Registers

### XMM Registers (SSE): 128-bit

16 registers: **XMM0-XMM15**

```
XMM0: [127 -------- 64][63 -------- 0]
      |    64-bit     ||    64-bit    |
      | 4x float      || 2x double    |
      | 4x int32      || 2x int64     |
```

**Data Layouts:**

| Type | Count | Each Element |
|------|-------|--------------|
| float | 4 | 32-bit single-precision |
| double | 2 | 64-bit double-precision |
| int8 | 16 | 8-bit integer |
| int16 | 8 | 16-bit integer |
| int32 | 4 | 32-bit integer |
| int64 | 2 | 64-bit integer |

### YMM Registers (AVX): 256-bit

16 registers: **YMM0-YMM15** (extend XMM0-XMM15)

```
YMM0: [255----192][191----128][127----64][63-----0]
      |  64-bit  ||  64-bit  ||  64-bit ||  64-bit|
      |       8x float        ||   4x double      |
```

### ZMM Registers (AVX-512): 512-bit

32 registers: **ZMM0-ZMM31** (extend YMM0-YMM31)

**Note:** We'll focus on SSE and AVX, as they're most widely supported.

---

## SSE Instructions

### Moving Data

```nasm
; C equivalent:
; float a[4] = {1.0, 2.0, 3.0, 4.0};
; float b[4];
; memcpy(b, a, sizeof(a));

section .data
    align 16
    floats dd 1.0, 2.0, 3.0, 4.0

section .bss
    align 16
    result resd 4

section .text
    ; Load 4 floats at once
    movaps xmm0, [floats]   ; Aligned load (faster)
    
    ; Store 4 floats at once
    movaps [result], xmm0   ; Aligned store
    
    ; Unaligned variants (slower but flexible)
    movups xmm1, [floats]   ; Unaligned load
    movups [result], xmm1   ; Unaligned store
```

**Alignment:** SSE requires **16-byte alignment** for best performance. Use `align 16` directive.

### Arithmetic Operations

#### Packed Single-Precision (PS): 4x float

```nasm
; C equivalent:
; for (int i = 0; i < 4; ++i) {
;     c[i] = a[i] + b[i];
;     d[i] = a[i] - b[i];
;     e[i] = a[i] * b[i];
;     f[i] = a[i] / b[i];
; }

section .data
    align 16
    a dd 1.0, 2.0, 3.0, 4.0
    b dd 5.0, 6.0, 7.0, 8.0

section .bss
    align 16
    c resd 4
    d resd 4
    e resd 4
    f resd 4

section .text
    movaps xmm0, [a]        ; Load a
    movaps xmm1, [b]        ; Load b
    
    movaps xmm2, xmm0
    addps xmm2, xmm1        ; xmm2 = a + b (4 additions)
    movaps [c], xmm2
    
    movaps xmm2, xmm0
    subps xmm2, xmm1        ; xmm2 = a - b (4 subtractions)
    movaps [d], xmm2
    
    movaps xmm2, xmm0
    mulps xmm2, xmm1        ; xmm2 = a * b (4 multiplications)
    movaps [e], xmm2
    
    movaps xmm2, xmm0
    divps xmm2, xmm1        ; xmm2 = a / b (4 divisions)
    movaps [f], xmm2
```

#### Packed Double-Precision (PD): 2x double

```nasm
; C equivalent:
; for (int i = 0; i < 2; ++i) {
;     c[i] = a[i] + b[i];
; }

section .data
    align 16
    a dq 1.5, 2.5
    b dq 3.5, 4.5

section .text
    movapd xmm0, [a]        ; Load 2 doubles
    movapd xmm1, [b]
    addpd xmm0, xmm1        ; Add 2 doubles at once
```

#### Scalar Operations (SS/SD): Single element

```nasm
; C equivalent:
; float result = a + b;

section .data
    a dd 1.5
    b dd 2.5

section .text
    movss xmm0, [a]         ; Load single float
    addss xmm0, [b]         ; Add single float
    ; xmm0[31:0] = result, xmm0[127:32] unchanged
```

### Comparison Operations

```nasm
; C equivalent:
; for (int i = 0; i < 4; ++i) {
;     mask[i] = (a[i] < b[i]) ? 0xFFFFFFFF : 0x00000000;
; }

movaps xmm0, [a]
movaps xmm1, [b]
cmpltps xmm0, xmm1          ; Compare less-than
; xmm0[i] = 0xFFFFFFFF if a[i] < b[i], else 0x00000000
```

**Comparison Predicates:**

| Instruction | Condition | Description |
|-------------|-----------|-------------|
| `cmpeqps` | == | Equal |
| `cmpltps` | < | Less than |
| `cmpleps` | <= | Less or equal |
| `cmpneqps` | != | Not equal |
| `cmpnltps` | >= | Not less than |
| `cmpnleps` | > | Not less or equal |

### Logical Operations

```nasm
; C equivalent (bitwise):
; for (int i = 0; i < 4; ++i) {
;     result[i] = a[i] & b[i];  // Bitwise AND
; }

movaps xmm0, [a]
andps xmm0, [b]             ; Bitwise AND
orps xmm1, [c]              ; Bitwise OR
xorps xmm2, [d]             ; Bitwise XOR
andnps xmm3, [e]            ; Bitwise AND NOT
```

---

## Practical Example: Array Addition

```nasm
; add_arrays.asm - Add two float arrays using SSE

section .text
global add_arrays_simd

; C prototype:
; void add_arrays_simd(float *result, const float *a, const float *b, size_t count);
; Assumes count is multiple of 4, arrays are 16-byte aligned

add_arrays_simd:
    ; RDI = result, RSI = a, RDX = b, RCX = count
    
    xor rax, rax            ; i = 0
    
.loop:
    cmp rax, rcx
    jge .done
    
    ; Load 4 floats from a
    movaps xmm0, [rsi + rax*4]
    
    ; Add 4 floats from b
    addps xmm0, [rdx + rax*4]
    
    ; Store 4 results
    movaps [rdi + rax*4], xmm0
    
    add rax, 4              ; i += 4 (processed 4 elements)
    jmp .loop
    
.done:
    ret
```

```c
// test.c

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern void add_arrays_simd(float *result, const float *a, const float *b, size_t count);

// Scalar version for comparison
void add_arrays_scalar(float *result, const float *a, const float *b, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        result[i] = a[i] + b[i];
    }
}

int main() {
    const size_t count = 8;
    
    // Allocate aligned memory
    float *a = aligned_alloc(16, count * sizeof(float));
    float *b = aligned_alloc(16, count * sizeof(float));
    float *result = aligned_alloc(16, count * sizeof(float));
    
    // Initialize
    for (size_t i = 0; i < count; ++i) {
        a[i] = i + 1.0f;
        b[i] = (i + 1.0f) * 10.0f;
    }
    
    // SIMD version
    add_arrays_simd(result, a, b, count);
    
    printf("SIMD results:\n");
    for (size_t i = 0; i < count; ++i) {
        printf("%.1f ", result[i]);
    }
    printf("\n");
    
    free(a);
    free(b);
    free(result);
    return 0;
}
```

---

## Advanced SIMD Techniques

### Horizontal Operations

```nasm
; C equivalent:
; float sum = a[0] + a[1] + a[2] + a[3];

section .data
    align 16
    values dd 1.0, 2.0, 3.0, 4.0

section .text
    movaps xmm0, [values]   ; [1, 2, 3, 4]
    
    ; Method 1: Hadd (SSE3)
    haddps xmm0, xmm0       ; [1+2, 3+4, 1+2, 3+4] = [3, 7, 3, 7]
    haddps xmm0, xmm0       ; [3+7, 3+7, 3+7, 3+7] = [10, 10, 10, 10]
    ; xmm0[0] now contains sum
    
    ; Method 2: Manual shuffling (faster)
    movaps xmm1, xmm0       ; Copy
    shufps xmm1, xmm1, 0xB1 ; Swap adjacent pairs
    addps xmm0, xmm1        ; Add pairs
    movaps xmm1, xmm0
    shufps xmm1, xmm1, 0x4E ; Swap high/low halves
    addps xmm0, xmm1        ; Final sum in all elements
```

### Complete Array Sum Example

```nasm
; sum_array.asm - Sum array of floats using SSE

section .text
global sum_array_simd

; C prototype:
; float sum_array_simd(const float *array, size_t count);

sum_array_simd:
    ; RDI = array, RSI = count
    
    xorps xmm0, xmm0        ; accumulator = 0
    xor rax, rax            ; i = 0
    
    ; Process 4 elements at a time
    mov rcx, rsi
    shr rcx, 2              ; count / 4
    jz .remainder
    
.loop:
    addps xmm0, [rdi + rax*4]   ; Add 4 floats to accumulator
    add rax, 4
    dec rcx
    jnz .loop
    
.remainder:
    ; Handle leftover elements (count % 4)
    mov rcx, rsi
    and rcx, 3
    jz .horizontal_sum
    
.remainder_loop:
    addss xmm0, [rdi + rax*4]
    inc rax
    dec rcx
    jnz .remainder_loop
    
.horizontal_sum:
    ; Sum the 4 values in xmm0 into xmm0[0]
    movaps xmm1, xmm0
    shufps xmm1, xmm1, 0xB1     ; Swap adjacent
    addps xmm0, xmm1
    movaps xmm1, xmm0
    shufps xmm1, xmm1, 0x4E     ; Swap high/low
    addps xmm0, xmm1
    
    ; Result in xmm0[0] (XMM0 is return register for float)
    ret
```

### Shuffling and Permutation

```nasm
; C equivalent:
; float result[4] = {a[2], a[0], a[3], a[1]};

movaps xmm0, [a]            ; [a0, a1, a2, a3]
shufps xmm0, xmm0, 0x9C     ; Shuffle: [a2, a0, a3, a1]
; Immediate 0x9C = 10 01 11 00 (binary)
;                  a2 a0 a3 a1 (indices)
```

**Shuffle Control Byte:**
- Bits [1:0]: Select from source for element 0
- Bits [3:2]: Select from source for element 1
- Bits [5:4]: Select from source for element 2
- Bits [7:6]: Select from source for element 3

### Broadcast (Splat)

```nasm
; C equivalent:
; float result[4] = {x, x, x, x};

section .data
    x dd 5.0

section .text
    movss xmm0, [x]         ; Load single value
    shufps xmm0, xmm0, 0    ; Broadcast to all elements
    ; xmm0 = [5.0, 5.0, 5.0, 5.0]
```

---

## AVX Instructions

AVX extends SSE with 256-bit operations and non-destructive operations.

### Non-Destructive Operations

```nasm
; SSE (destructive):
movaps xmm0, [a]
addps xmm0, [b]             ; xmm0 = xmm0 + [b] (xmm0 overwritten)

; AVX (non-destructive):
vmovaps ymm0, [a]
vaddps ymm2, ymm0, [b]      ; ymm2 = ymm0 + [b] (ymm0 preserved!)
```

### 256-bit Operations

```nasm
; C equivalent:
; for (int i = 0; i < 8; ++i) {
;     result[i] = a[i] + b[i];  // 8 floats at once!
; }

section .data
    align 32                        ; AVX requires 32-byte alignment
    a dd 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0
    b dd 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0

section .bss
    align 32
    result resd 8

section .text
    vmovaps ymm0, [a]           ; Load 8 floats
    vaddps ymm0, ymm0, [b]      ; Add 8 floats
    vmovaps [result], ymm0      ; Store 8 floats
    
    ; IMPORTANT: Clean up AVX state
    vzeroupper                  ; Clear upper 128 bits of YMM registers
    ret
```

**Note:** Always use `vzeroupper` or `vzeroall` before transitioning back to non-AVX code to avoid performance penalties.

---

## Complete Real-World Example: Dot Product

```nasm
; dot_product.asm - Compute dot product using SSE

section .text
global dot_product_simd

; C prototype:
; float dot_product_simd(const float *a, const float *b, size_t count);
; Assumes count is multiple of 4

dot_product_simd:
    ; RDI = a, RSI = b, RDX = count
    
    xorps xmm0, xmm0        ; sum = 0
    xor rax, rax            ; i = 0
    
.loop:
    cmp rax, rdx
    jge .horizontal_sum
    
    ; Load 4 elements from each array
    movaps xmm1, [rdi + rax*4]
    movaps xmm2, [rsi + rax*4]
    
    ; Multiply element-wise
    mulps xmm1, xmm2
    
    ; Add to accumulator
    addps xmm0, xmm1
    
    add rax, 4
    jmp .loop
    
.horizontal_sum:
    ; Sum the 4 partial sums in xmm0
    movaps xmm1, xmm0
    shufps xmm1, xmm1, 0xB1     ; [1, 0, 3, 2]
    addps xmm0, xmm1            ; [0+1, 1+0, 2+3, 3+2]
    
    movaps xmm1, xmm0
    shufps xmm1, xmm1, 0x4E     ; [2, 3, 0, 1]
    addps xmm0, xmm1            ; [sum, sum, sum, sum]
    
    ; Result in xmm0[0]
    ret
```

```c
// test_dot.c

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

extern float dot_product_simd(const float *a, const float *b, size_t count);

float dot_product_scalar(const float *a, const float *b, size_t count) {
    float sum = 0.0f;
    for (size_t i = 0; i < count; ++i) {
        sum += a[i] * b[i];
    }
    return sum;
}

int main() {
    const size_t count = 1024 * 1024;  // 1 million elements
    
    float *a = aligned_alloc(16, count * sizeof(float));
    float *b = aligned_alloc(16, count * sizeof(float));
    
    // Initialize
    for (size_t i = 0; i < count; ++i) {
        a[i] = 1.0f;
        b[i] = 2.0f;
    }
    
    // Benchmark scalar
    clock_t start = clock();
    float result_scalar = dot_product_scalar(a, b, count);
    clock_t end = clock();
    double time_scalar = (double)(end - start) / CLOCKS_PER_SEC;
    
    // Benchmark SIMD
    start = clock();
    float result_simd = dot_product_simd(a, b, count);
    end = clock();
    double time_simd = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Scalar: %.2f (%.6f seconds)\n", result_scalar, time_scalar);
    printf("SIMD:   %.2f (%.6f seconds)\n", result_simd, time_simd);
    printf("Speedup: %.2fx\n", time_scalar / time_simd);
    
    free(a);
    free(b);
    return 0;
}
```

---

## Integer SIMD Operations

```nasm
; C equivalent:
; for (int i = 0; i < 4; ++i) {
;     result[i] = a[i] + b[i];  // 32-bit integers
; }

section .data
    align 16
    a dd 1, 2, 3, 4
    b dd 5, 6, 7, 8

section .bss
    align 16
    result resd 4

section .text
    movdqa xmm0, [a]        ; Load 4 int32s (aligned)
    paddd xmm0, [b]         ; Add 4 int32s
    movdqa [result], xmm0   ; Store 4 int32s
```

**Integer Operations:**

| Instruction | Description |
|-------------|-------------|
| `paddb/w/d/q` | Add packed bytes/words/dwords/qwords |
| `psubb/w/d/q` | Subtract |
| `pmullw/d` | Multiply low (words/dwords) |
| `pmulhw/uw` | Multiply high (signed/unsigned words) |
| `pand/por/pxor` | Logical AND/OR/XOR |
| `psllw/d/q` | Shift left logical |
| `psrlw/d/q` | Shift right logical |
| `psraw/d` | Shift right arithmetic |
| `pcmpeqb/w/d` | Compare equal |
| `pcmpgtb/w/d` | Compare greater than |

---

## Performance Considerations

### When to Use SIMD

**Good candidates:**
- Array operations (add, multiply, etc.)
- Vector math (graphics, physics)
- Signal processing (audio, video)
- Matrix operations
- Image processing
- Data parallel algorithms

**Poor candidates:**
- Irregular control flow (many branches)
- Data dependencies between iterations
- Non-contiguous memory access
- Small datasets (overhead dominates)

### Alignment

```nasm
; Aligned (fast):
section .data
    align 16
    data dd 1.0, 2.0, 3.0, 4.0
    
movaps xmm0, [data]     ; Fast aligned load

; Unaligned (slower):
movups xmm0, [data]     ; Slower unaligned load
```

**Best Practice:** Always align data to 16/32 bytes when possible.

### Typical Speedups

| Operation | SSE Speedup | AVX Speedup |
|-----------|-------------|-------------|
| Float add/sub | 3-4x | 6-8x |
| Float multiply | 3-4x | 6-8x |
| Float divide | 2-3x | 4-6x |
| Int32 add | 3-4x | 6-8x |
| Dot product | 3-4x | 6-8x |

**Actual speedup depends on:**
- Memory bandwidth
- Data alignment
- Loop overhead
- CPU architecture

---

## Common Patterns

### Pattern 1: Conditional Selection

```nasm
; C equivalent:
; for (int i = 0; i < 4; ++i) {
;     result[i] = (a[i] > b[i]) ? a[i] : b[i];  // Max
; }

movaps xmm0, [a]
maxps xmm0, [b]         ; Per-element maximum
movaps [result], xmm0

; Manual with blending:
movaps xmm0, [a]
movaps xmm1, [b]
cmpgtps xmm2, xmm0, xmm1    ; mask = (a > b)
andps xmm0, xmm2            ; a & mask
andnps xmm2, xmm1           ; b & ~mask
orps xmm0, xmm2             ; result = (a & mask) | (b & ~mask)
```

### Pattern 2: AoS to SoA Conversion

```c
// Array of Structures (AoS) - cache unfriendly for SIMD
struct Point { float x, y, z; };
Point points[1000];

// Structure of Arrays (SoA) - SIMD friendly
float x[1000], y[1000], z[1000];
```

```nasm
; Process SoA data with SIMD
movaps xmm0, [x]        ; Load 4 x values
movaps xmm1, [y]        ; Load 4 y values
movaps xmm2, [z]        ; Load 4 z values
; Process 4 points in parallel!
```

### Pattern 3: Fused Multiply-Add (FMA)

```nasm
; C equivalent:
; for (int i = 0; i < 4; ++i) {
;     result[i] = a[i] * b[i] + c[i];
; }

; Without FMA (SSE):
movaps xmm0, [a]
mulps xmm0, [b]
addps xmm0, [c]

; With FMA (AVX2+):
vmovaps ymm0, [a]
vfmadd231ps ymm0, [b], [c]  ; ymm0 = (b * c) + ymm0
```

---

## Summary

### Key Concepts
1. **SIMD**: Process multiple data elements with one instruction
2. **SSE**: 128-bit (4x float, 2x double, 4x int32)
3. **AVX**: 256-bit (8x float, 4x double, 8x int32)
4. **Alignment**: 16-byte for SSE, 32-byte for AVX
5. **Speedup**: Typically 3-8x for vectorizable code

### Common Instructions
- **Load/Store**: `movaps`, `movups`, `movdqa`, `movdqu`
- **Arithmetic**: `addps`, `subps`, `mulps`, `divps`
- **Comparison**: `cmpltps`, `cmpeqps`, etc.
- **Logical**: `andps`, `orps`, `xorps`
- **Shuffle**: `shufps`, `unpcklps`, `unpckhps`

### Best Practices
1. Align data to 16/32 bytes
2. Process 4/8 elements at a time
3. Handle remainder elements separately
4. Use non-destructive AVX when possible
5. Call `vzeroupper` after AVX code
6. Profile to verify actual speedup

### Limitations
1. Requires contiguous memory
2. Benefits diminish with branching
3. Data dependencies reduce parallelism
4. Alignment requirements
5. CPU feature detection needed

---

## Practice Exercises

### Exercise 1: Max Element

Implement a function to find the maximum element in a float array using SSE.

### Exercise 2: Vector Normalization

Normalize a 3D vector array (x, y, z) using SIMD.

### Exercise 3: Matrix Multiplication

Implement 4x4 matrix multiplication using SSE.

---

## Next Topic

In **Topic 19: Performance & Optimization**, we'll explore advanced optimization techniques, profiling, and how to write the fastest possible assembly code.

**Preview:**
- CPU pipeline and instruction-level parallelism
- Cache optimization
- Branch prediction
- Loop unrolling
- Register allocation strategies
- Profiling and benchmarking

