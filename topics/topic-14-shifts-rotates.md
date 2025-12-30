# Topic 14: Shifts and Rotates (Advanced)

## Overview

Shift and rotate instructions are fundamental bit manipulation operations. They're used for multiplication/division by powers of 2, bit extraction, packing/unpacking data, and many low-level optimizations.

```c
// C equivalent concepts:
x << 2;     // Shift left (multiply by 4)
x >> 2;     // Shift right (divide by 4)
x >>> 2;    // Logical right shift (unsigned)
// Rotates have no direct C equivalent
```

---

## Logical Shifts

### `SHL` / `SAL` - Shift Left

Shifts bits to the left, filling with zeros from the right. Both `SHL` and `SAL` are identical.

```nasm
; C equivalent:
; x = x << count;

shl dest, count     ; dest <<= count
sal dest, count     ; Same as SHL
```

**What happens:**
1. Bits shift left by `count` positions
2. Leftmost bits fall into the **Carry Flag (CF)**
3. Rightmost bits filled with **0**
4. Effectively multiplies by 2^count (if no overflow)

```
Before: 01011010 (0x5A = 90)
SHL 1:  10110100 (0xB4 = 180)  CF=0
SHL 1:  01101000 (0x68 = 104)  CF=1  (bit fell off)
```

**Syntax variants:**

```nasm
; C equivalent:
; x = x << 1;
; y = y << 3;
; z = z << cl;

shl rax, 1          ; Shift by 1 (most efficient)
shl rbx, 3          ; Shift by immediate (0-63)
shl rcx, cl         ; Shift by CL register (variable)
```

**Flags:**
- **CF**: Last bit shifted out
- **OF**: Set if sign bit changed (only for count=1)
- **SF, ZF, PF**: Set according to result

**Example: Multiply by 8**

```nasm
section .data
    x dd 15
    result dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int result = x * 8;  // 15 * 8 = 120
    
    mov eax, [x]
    shl eax, 3              ; Multiply by 2^3 = 8
    mov [result], eax       ; result = 120
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### `SHR` - Logical Shift Right

Shifts bits to the right, filling with zeros from the left. Used for **unsigned** division by powers of 2.

```nasm
; C equivalent (unsigned):
; x = x >> count;

shr dest, count     ; dest >>= count (unsigned)
```

**What happens:**
1. Bits shift right by `count` positions
2. Rightmost bits fall into the **Carry Flag (CF)**
3. Leftmost bits filled with **0**
4. Effectively divides by 2^count (unsigned)

```
Before: 10110100 (0xB4 = 180)
SHR 1:  01011010 (0x5A = 90)   CF=0
SHR 1:  00101101 (0x2D = 45)   CF=0
```

**Example: Divide by 4 (Unsigned)**

```nasm
section .data
    x dd 100
    result dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned int result = x / 4;  // 100 / 4 = 25
    
    mov eax, [x]
    shr eax, 2              ; Divide by 2^2 = 4
    mov [result], eax       ; result = 25
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Arithmetic Shift

### `SAR` - Arithmetic Shift Right

Like `SHR`, but preserves the **sign bit** (leftmost bit). Used for **signed** division by powers of 2.

```nasm
; C equivalent (signed):
; x = x >> count;  // For signed integers

sar dest, count     ; dest >>= count (signed)
```

**What happens:**
1. Bits shift right by `count` positions
2. Rightmost bits fall into the **Carry Flag (CF)**
3. Leftmost bits filled with **original sign bit**
4. Effectively divides by 2^count (signed, rounds toward -∞)

```
Positive: 01011010 (0x5A = 90)
SAR 1:    00101101 (0x2D = 45)   CF=0  (sign bit = 0)

Negative: 10110100 (0xB4 = -76 in signed)
SAR 1:    11011010 (0xDA = -38)  CF=0  (sign bit = 1, preserved)
```

**Example: Signed Division**

```nasm
section .data
    x dd -100
    result dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int result = x / 4;  // -100 / 4 = -25
    
    mov eax, [x]
    sar eax, 2              ; Signed divide by 4
    mov [result], eax       ; result = -25
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Comparison: SHR vs SAR

```nasm
section .data
    unsigned_val dd 0x80000000  ; 2,147,483,648 (unsigned)
    signed_val   dd 0x80000000  ; -2,147,483,648 (signed)

section .text
    ; Unsigned division by 2
    ; C equivalent:
    ; unsigned int result = 0x80000000U >> 1;  // 1,073,741,824
    mov eax, [unsigned_val]
    shr eax, 1              ; EAX = 0x40000000 (1,073,741,824)
    
    ; Signed division by 2
    ; C equivalent:
    ; int result = ((int)0x80000000) >> 1;  // -1,073,741,824
    mov eax, [signed_val]
    sar eax, 1              ; EAX = 0xC0000000 (-1,073,741,824)
```

---

## Rotate Instructions

Rotate instructions shift bits in a circular manner - bits that fall off one end reappear at the other.

### `ROL` - Rotate Left

```nasm
; No direct C equivalent
; Conceptually: (x << count) | (x >> (SIZE - count))

rol dest, count     ; Rotate left
```

**What happens:**
1. Bits rotate left by `count` positions
2. Bits that fall off the left reappear on the right
3. Last bit rotated out copied to **CF**

```
Before: 10110100
ROL 1:  01101001  CF=1  (leftmost bit wraps to right)
ROL 1:  11010010  CF=0
```

**Example: Rotate for Bit Inspection**

```nasm
section .data
    x dd 0xABCD1234

section .text
global _start

_start:
    ; C equivalent (conceptual):
    ; // Inspect each nibble (4 bits) by rotating
    ; for (int i = 0; i < 8; ++i) {
    ;     int nibble = x & 0xF;
    ;     x = (x >> 4) | (x << 28);  // Rotate right by 4
    ; }
    
    mov eax, [x]
    mov ecx, 8              ; 8 nibbles in 32 bits
    
inspect_loop:
    rol eax, 4              ; Rotate left by 4 (next nibble to bottom)
    ; Bottom 4 bits now contain next nibble
    loop inspect_loop
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### `ROR` - Rotate Right

```nasm
; No direct C equivalent
; Conceptually: (x >> count) | (x << (SIZE - count))

ror dest, count     ; Rotate right
```

**What happens:**
1. Bits rotate right by `count` positions
2. Bits that fall off the right reappear on the left
3. Last bit rotated out copied to **CF**

```
Before: 10110100
ROR 1:  01011010  CF=0  (rightmost bit wraps to left)
ROR 1:  00101101  CF=0
```

### `RCL` - Rotate Through Carry Left

Like `ROL`, but **includes the Carry Flag** in the rotation.

```nasm
rcl dest, count     ; Rotate through carry left
```

**What happens:**
1. Bits rotate left through CF
2. CF becomes the rightmost bit
3. Leftmost bit becomes new CF

```
CF=1, Value: 10110100
RCL 1:  CF=1, Value: 01101001  (CF -> bit 0, bit 7 -> CF)
```

**Use case:** Multi-precision arithmetic (shifting 128-bit, 256-bit values)

### `RCR` - Rotate Through Carry Right

Like `ROR`, but **includes the Carry Flag** in the rotation.

```nasm
rcr dest, count     ; Rotate through carry right
```

**Example: 128-bit Right Shift**

```nasm
section .data
    ; 128-bit value: high:low
    value_high dq 0x0123456789ABCDEF
    value_low  dq 0xFEDCBA9876543210

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned __int128 value = ((__int128)value_high << 64) | value_low;
    ; value >>= 1;  // Shift entire 128-bit value right by 1
    
    ; Shift high qword right, bit 0 goes to CF
    mov rax, [value_high]
    shr rax, 1              ; Shift high part, bit 0 -> CF
    mov [value_high], rax
    
    ; Rotate low qword right through carry
    mov rax, [value_low]
    rcr rax, 1              ; CF -> bit 63, bit 0 -> CF
    mov [value_low], rax
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Double-Precision Shifts

### `SHLD` - Shift Left Double

Shifts the destination left, filling from the source register.

```nasm
; C equivalent (conceptual):
; dest = (dest << count) | (src >> (SIZE - count));

shld dest, src, count   ; Shift dest left, fill from src
```

**Example: Extract Middle Bits**

```nasm
section .data
    high dd 0xABCD0000
    low  dd 0x00001234

section .text
global _start

_start:
    ; C equivalent:
    ; // Extract bits 16-47 from a 64-bit value (high:low)
    ; unsigned long long combined = ((unsigned long long)high << 32) | low;
    ; unsigned int middle = (combined >> 16) & 0xFFFFFFFF;
    
    mov eax, [high]
    mov edx, [low]
    shld eax, edx, 16   ; EAX = (high << 16) | (low >> 16)
    ; EAX now contains 0x0000ABCD
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### `SHRD` - Shift Right Double

Shifts the destination right, filling from the source register.

```nasm
; C equivalent (conceptual):
; dest = (dest >> count) | (src << (SIZE - count));

shrd dest, src, count   ; Shift dest right, fill from src
```

**Example: 64-bit Rotate Right**

```nasm
; C equivalent:
; // Rotate a 64-bit value right by 8 bits
; unsigned long long rotate_right_64(unsigned long long x, int count) {
;     return (x >> count) | (x << (64 - count));
; }

mov rax, [value]        ; RAX = 64-bit value
mov rdx, rax            ; Copy to RDX
shrd rax, rdx, 8        ; RAX = (RAX >> 8) | (RDX << 56)
; RAX now rotated right by 8
```

---

## Practical Applications

### Application 1: Bit Extraction

```nasm
section .data
    ; Extract bits 12-19 from a 32-bit value
    value dd 0x12345678

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned int extract = (value >> 12) & 0xFF;
    
    mov eax, [value]    ; EAX = 0x12345678
    shr eax, 12         ; EAX = 0x00012345
    and eax, 0xFF       ; EAX = 0x00000045
    ; Extracted bits 12-19 (value = 0x45 = 69)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Application 2: Bit Field Packing

```nasm
section .data
    ; Pack three values: A (5 bits), B (11 bits), C (16 bits)
    a dd 0x1F           ; 5 bits: 11111
    b dd 0x7FF          ; 11 bits: 11111111111
    c dd 0xFFFF         ; 16 bits: 1111111111111111
    packed dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; struct Packed {
    ;     unsigned a : 5;   // bits 0-4
    ;     unsigned b : 11;  // bits 5-15
    ;     unsigned c : 16;  // bits 16-31
    ; };
    ; unsigned int packed = (a & 0x1F) | ((b & 0x7FF) << 5) | ((c & 0xFFFF) << 16);
    
    ; Pack A (bits 0-4)
    mov eax, [a]
    and eax, 0x1F       ; Mask to 5 bits
    
    ; Pack B (bits 5-15)
    mov ebx, [b]
    and ebx, 0x7FF      ; Mask to 11 bits
    shl ebx, 5          ; Shift to position
    or eax, ebx
    
    ; Pack C (bits 16-31)
    mov ebx, [c]
    and ebx, 0xFFFF     ; Mask to 16 bits
    shl ebx, 16         ; Shift to position
    or eax, ebx
    
    mov [packed], eax   ; Result: 0xFFFFFFFF
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Application 3: Fast Power of 2 Check

```nasm
section .data
    x dd 64             ; Is 64 a power of 2? (Yes)

section .text
global _start

_start:
    ; C equivalent:
    ; bool is_power_of_2(unsigned int x) {
    ;     return x != 0 && (x & (x - 1)) == 0;
    ; }
    ; // Power of 2 has exactly one bit set
    
    mov eax, [x]
    test eax, eax       ; Check if zero
    jz not_power_of_2
    
    mov ebx, eax
    dec ebx             ; EBX = x - 1
    and ebx, eax        ; EBX = x & (x - 1)
    jnz not_power_of_2
    
    ; Is power of 2
    mov edi, 1
    jmp done
    
not_power_of_2:
    xor edi, edi
    
done:
    ; EDI = 1 (true, 64 is power of 2)
    
    ; Exit
    mov rax, 60
    syscall
```

### Application 4: Byte Swapping (Endianness Conversion)

```nasm
section .data
    value dd 0x12345678     ; Little-endian
    swapped dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned int swap32(unsigned int x) {
    ;     return ((x & 0xFF000000) >> 24) |
    ;            ((x & 0x00FF0000) >> 8)  |
    ;            ((x & 0x0000FF00) << 8)  |
    ;            ((x & 0x000000FF) << 24);
    ; }
    
    mov eax, [value]    ; EAX = 0x12345678
    
    ; Modern CPUs have BSWAP instruction:
    bswap eax           ; EAX = 0x78563412
    
    ; Manual method:
    ; mov eax, [value]
    ; rol eax, 8          ; 0x34567812
    ; mov ebx, eax
    ; and eax, 0x00FF00FF ; 0x00560012
    ; and ebx, 0xFF00FF00 ; 0x34007800
    ; shr ebx, 8          ; 0x00340078
    ; shl eax, 8          ; 0x56001200
    ; or eax, ebx         ; 0x56341278 (wrong!)
    
    mov [swapped], eax  ; Result: 0x78563412 (big-endian)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Application 5: Count Leading Zeros (CLZ)

```nasm
section .data
    x dd 0x00001234     ; 16 leading zeros
    clz dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int count_leading_zeros(unsigned int x) {
    ;     if (x == 0) return 32;
    ;     int count = 0;
    ;     while ((x & 0x80000000) == 0) {
    ;         count++;
    ;         x <<= 1;
    ;     }
    ;     return count;
    ; }
    
    mov eax, [x]
    test eax, eax
    jz all_zeros
    
    xor ecx, ecx        ; count = 0
    
clz_loop:
    test eax, 0x80000000
    jnz clz_done
    shl eax, 1
    inc ecx
    jmp clz_loop
    
all_zeros:
    mov ecx, 32
    
clz_done:
    mov [clz], ecx      ; Result: 16
    
    ; Modern alternative: BSR (Bit Scan Reverse)
    mov eax, [x]
    bsr ecx, eax        ; ECX = position of highest bit set
    xor ecx, 31         ; Convert to leading zeros
    ; ECX = 16
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Application 6: Alignment Check

```nasm
section .data
    address dq 0x1000       ; 4KB-aligned
    align_mask dq 0xFFF     ; 4KB - 1

section .text
global _start

_start:
    ; C equivalent:
    ; bool is_aligned(void* addr, size_t alignment) {
    ;     return ((uintptr_t)addr & (alignment - 1)) == 0;
    ; }
    
    mov rax, [address]
    and rax, [align_mask]
    test rax, rax
    jz is_aligned
    
    ; Not aligned
    xor edi, edi
    jmp done
    
is_aligned:
    mov edi, 1
    
done:
    ; EDI = 1 (aligned)
    
    ; Exit
    mov rax, 60
    syscall
```

---

## Advanced: Barrel Shifter Emulation

Some processors have hardware barrel shifters that can shift by any amount in one cycle. Here's how to emulate efficient shifting:

```nasm
section .data
    value dq 0x123456789ABCDEF0
    shift_count db 17

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned long long result = value << shift_count;
    
    movzx ecx, byte [shift_count]   ; CL = shift count
    mov rax, [value]
    shl rax, cl                      ; Variable shift
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Optimization Techniques

### 1. Multiply/Divide by Powers of 2

```nasm
; C equivalent:
; int x = 100;
; int a = x * 16;
; int b = x / 8;

; Slow:
imul eax, [x], 16
mov edx, [x]
mov ecx, 8
xor ebx, ebx
div ecx

; Fast:
mov eax, [x]
shl eax, 4              ; x * 16
mov edx, [x]
shr edx, 3              ; x / 8
```

### 2. Extracting Specific Bits

```nasm
; C equivalent:
; unsigned int extract_bits_10_15(unsigned int x) {
;     return (x >> 10) & 0x3F;  // Extract 6 bits
; }

; Method 1: Shift then mask
mov eax, [x]
shr eax, 10
and eax, 0x3F

; Method 2: Mask then shift (if other bits needed)
mov eax, [x]
and eax, 0xFC00         ; Mask bits 10-15
shr eax, 10
```

### 3. Clearing Lower Bits (Alignment)

```nasm
; C equivalent:
; void* align_down(void* ptr, size_t alignment) {
;     return (void*)((uintptr_t)ptr & ~(alignment - 1));
; }

; Align pointer to 16-byte boundary
and rax, ~0xF           ; Clear lower 4 bits

; Align to 4KB (0x1000)
and rax, ~0xFFF         ; Clear lower 12 bits
```

### 4. Fast Modulo Powers of 2

```nasm
; C equivalent:
; unsigned int mod = x % 16;

; Slow:
mov eax, [x]
xor edx, edx
mov ecx, 16
div ecx             ; EDX = remainder

; Fast:
mov eax, [x]
and eax, 0xF        ; x & (16-1) = x % 16
```

---

## Performance Characteristics

| Instruction | Latency | Throughput | Notes |
|-------------|---------|------------|-------|
| `shl/shr/sar r, 1` | 1 cycle | 0.5/cycle | Immediate count = 1 |
| `shl/shr/sar r, imm` | 1 cycle | 0.5/cycle | Immediate count |
| `shl/shr/sar r, cl` | 1-3 cycles | 2/cycle | Variable count |
| `rol/ror r, imm` | 1 cycle | 0.5/cycle | Fast on modern CPUs |
| `rcl/rcr r, 1` | 3 cycles | 1/cycle | Slower due to CF dependency |
| `shld/shrd` | 3 cycles | 0.5/cycle | Complex operation |
| `bswap` | 1 cycle | 0.5/cycle | Very fast byte swap |

---

## Common Patterns and Idioms

### Pattern 1: Test Specific Bit

```nasm
; C equivalent:
; bool is_bit_set(unsigned int x, int bit) {
;     return (x & (1 << bit)) != 0;
; }

mov eax, [x]
bt eax, 5           ; Test bit 5, result in CF
jc bit_is_set

; Alternative with shift:
mov eax, [x]
shr eax, 5          ; Shift bit 5 to bit 0
and eax, 1          ; Isolate bit
```

### Pattern 2: Set/Clear Specific Bit

```nasm
; C equivalent:
; x |= (1 << bit);   // Set bit
; x &= ~(1 << bit);  // Clear bit

; Set bit 7
bts dword [x], 7    ; Bit Test and Set

; Clear bit 7
btr dword [x], 7    ; Bit Test and Reset

; Alternative:
mov eax, [x]
or eax, 0x80        ; Set bit 7
and eax, ~0x80      ; Clear bit 7
```

### Pattern 3: Sign Extension

```nasm
; C equivalent:
; int extend = (char)byte_val;  // Sign-extend 8-bit to 32-bit

; 8-bit to 32-bit
movsx eax, byte [val]

; Manual with shifts:
movzx eax, byte [val]
shl eax, 24
sar eax, 24         ; Sign bit fills from left
```

---

## Practice Exercises

### Exercise 1: Rotate Bits

Write code to rotate a 32-bit value left by an arbitrary amount.

```nasm
section .data
    value dd 0x12345678
    count dd 12
    result dd 0

section .text
global _start

_start:
    ; Your code here: rotate value left by count
    ; Store in result
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

<details>
<summary>Solution</summary>

```nasm
section .data
    value dd 0x12345678
    count dd 12
    result dd 0

section .text
global _start

_start:
    mov eax, [value]
    mov ecx, [count]
    rol eax, cl
    mov [result], eax       ; Result: 0x45678123
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```
</details>

### Exercise 2: Count Set Bits (Population Count)

Count the number of 1-bits in a 32-bit value.

```nasm
; C equivalent:
; int popcount(unsigned int x) {
;     int count = 0;
;     while (x) {
;         count += x & 1;
;         x >>= 1;
;     }
;     return count;
; }

section .data
    value dd 0x12345678
    count dd 0

section .text
global _start

_start:
    ; Your code here
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

<details>
<summary>Solution</summary>

```nasm
section .data
    value dd 0x12345678     ; Binary: 00010010001101000101011001111000
    count dd 0

section .text
global _start

_start:
    mov eax, [value]
    xor ecx, ecx            ; count = 0
    
popcount_loop:
    test eax, eax
    jz popcount_done
    
    mov edx, eax
    and edx, 1              ; Check lowest bit
    add ecx, edx            ; Add to count
    shr eax, 1              ; Shift right
    jmp popcount_loop
    
popcount_done:
    mov [count], ecx        ; Result: 13
    
    ; Modern alternative: POPCNT instruction
    ; popcnt ecx, [value]
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```
</details>

### Exercise 3: Reverse Bits

Reverse the order of bits in a 32-bit value.

```nasm
; C equivalent:
; unsigned int reverse_bits(unsigned int x) {
;     unsigned int result = 0;
;     for (int i = 0; i < 32; ++i) {
;         result = (result << 1) | (x & 1);
;         x >>= 1;
;     }
;     return result;
; }

section .data
    value dd 0x12345678
    reversed dd 0

section .text
global _start

_start:
    ; Your code here
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

<details>
<summary>Solution</summary>

```nasm
section .data
    value dd 0x12345678
    reversed dd 0

section .text
global _start

_start:
    mov eax, [value]        ; Source
    xor ebx, ebx            ; Result = 0
    mov ecx, 32             ; Bit count
    
reverse_loop:
    shl ebx, 1              ; Make room for next bit
    shr eax, 1              ; Get lowest bit in CF
    adc ebx, 0              ; Add CF to result
    loop reverse_loop
    
    mov [reversed], ebx     ; Result: 0x1E6A2C48
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```
</details>

---

## Summary

### Shift Instructions
- **`SHL/SAL`**: Shift left (multiply by 2^n), fill with 0
- **`SHR`**: Logical shift right (unsigned divide by 2^n), fill with 0
- **`SAR`**: Arithmetic shift right (signed divide by 2^n), fill with sign bit

### Rotate Instructions
- **`ROL/ROR`**: Rotate left/right (circular)
- **`RCL/RCR`**: Rotate through carry (9-bit, 17-bit, 33-bit, 65-bit rotation)

### Double Precision
- **`SHLD/SHRD`**: Shift from two registers

### Key Concepts
1. Shifts are fast alternatives to multiply/divide by powers of 2
2. Logical shifts treat values as unsigned
3. Arithmetic shifts preserve sign bit
4. Rotates have no C equivalent but useful for bit manipulation
5. Carry flag captures bits that "fall off"

### Common Uses
- Fast multiplication/division
- Bit field extraction/insertion
- Alignment checks and adjustments
- Endianness conversion
- Multi-precision arithmetic
- Bit manipulation algorithms

---

## Next Topic

In **Topic 15: Macros & Directives**, we'll learn about NASM's powerful macro system and assembler directives that help write cleaner, more maintainable assembly code.

**Preview:**
- Defining constants and symbols
- Text substitution macros
- Multi-line macros with parameters
- Conditional assembly
- File inclusion
- Repetition and loops at assembly time

