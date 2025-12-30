# Topic 17: Interfacing with C

## Overview

Assembly code rarely exists in isolation. Most real-world assembly programming involves interfacing with C code - either calling C functions from assembly or calling assembly routines from C. This topic covers how to bridge these two worlds.

```c
// C calling assembly:
extern long my_asm_function(long a, long b);
int main() {
    long result = my_asm_function(10, 20);
    return 0;
}
```

```nasm
; Assembly implementing function for C:
global my_asm_function
my_asm_function:
    mov rax, rdi        ; First argument
    add rax, rsi        ; Add second argument
    ret                 ; Return RAX to C
```

---

## Why Interface with C?

### Advantages
1. **Access to C standard library**: printf, malloc, FILE I/O, etc.
2. **Portability**: C handles platform differences
3. **Development speed**: Use C for most code, assembly for hot paths
4. **Maintainability**: Mix high-level C with performance-critical assembly
5. **Ecosystem**: Link with existing C libraries

### Common Use Cases
- Optimize performance-critical functions
- Access CPU-specific instructions (SIMD, crypto)
- Low-level hardware control
- Inline assembly in C for small snippets
- Creating reusable assembly libraries

---

## Calling Conventions (Review)

### System V AMD64 ABI (Linux, macOS, Unix)

**Function Parameters:**

| Argument | Register | Type |
|----------|----------|------|
| 1st | RDI | Integer/Pointer |
| 2nd | RSI | Integer/Pointer |
| 3rd | RDX | Integer/Pointer |
| 4th | RCX | Integer/Pointer |
| 5th | R8 | Integer/Pointer |
| 6th | R9 | Integer/Pointer |
| 7th+ | Stack | Pushed right-to-left |

**Floating-Point Parameters:**

| Argument | Register |
|----------|----------|
| 1st-8th | XMM0-XMM7 |
| 9th+ | Stack |

**Return Values:**
- Integer/Pointer: **RAX** (64-bit), **RDX:RAX** (128-bit)
- Floating-point: **XMM0** (float/double), **XMM1:XMM0** (long double)

**Caller-Saved (Volatile):** RAX, RCX, RDX, RSI, RDI, R8-R11, XMM0-XMM15  
**Callee-Saved (Non-Volatile):** RBX, RBP, R12-R15

**Stack Alignment:** **16-byte aligned** before `call` instruction

---

## Assembly Function Called from C

### Example 1: Simple Addition

```nasm
; add.asm - Simple function to add two numbers

section .text
global add_numbers          ; Make function visible to C

; C prototype:
; long add_numbers(long a, long b);

add_numbers:
    ; RDI = a (first parameter)
    ; RSI = b (second parameter)
    
    mov rax, rdi            ; RAX = a
    add rax, rsi            ; RAX = a + b
    ret                     ; Return RAX to caller
```

```c
// main.c - C code calling assembly function

#include <stdio.h>

// Declare external assembly function
extern long add_numbers(long a, long b);

int main() {
    long result = add_numbers(10, 20);
    printf("Result: %ld\n", result);  // Output: Result: 30
    return 0;
}
```

**Compile and Link:**

```bash
nasm -f elf64 add.asm -o add.o
gcc main.c add.o -o program
./program
```

### Example 2: Function with Multiple Parameters

```nasm
; compute.asm - More complex calculation

section .text
global compute

; C prototype:
; long compute(long a, long b, long c, long d, long e, long f);
; Returns: (a + b) * (c - d) + e / f

compute:
    ; RDI = a, RSI = b, RDX = c, RCX = d, R8 = e, R9 = f
    
    push rbx                ; Save callee-saved register
    
    ; Compute a + b
    mov rax, rdi
    add rax, rsi            ; RAX = a + b
    
    ; Compute c - d
    mov rbx, rdx
    sub rbx, rcx            ; RBX = c - d
    
    ; Multiply (a + b) * (c - d)
    imul rax, rbx           ; RAX = (a + b) * (c - d)
    
    ; Save intermediate result
    mov rbx, rax
    
    ; Compute e / f
    mov rax, r8             ; RAX = e
    cqo                     ; Sign-extend for division
    idiv r9                 ; RAX = e / f
    
    ; Add to intermediate result
    add rax, rbx            ; RAX = (a+b)*(c-d) + e/f
    
    pop rbx                 ; Restore callee-saved register
    ret
```

```c
// main.c

#include <stdio.h>

extern long compute(long a, long b, long c, long d, long e, long f);

int main() {
    // (10 + 20) * (50 - 30) + 100 / 10
    // = 30 * 20 + 10
    // = 600 + 10 = 610
    long result = compute(10, 20, 50, 30, 100, 10);
    printf("Result: %ld\n", result);  // Output: Result: 610
    return 0;
}
```

### Example 3: String Length (Working with Pointers)

```nasm
; strlen.asm - Calculate string length

section .text
global asm_strlen

; C prototype:
; size_t asm_strlen(const char *str);

asm_strlen:
    ; RDI = str (pointer to null-terminated string)
    
    xor rax, rax            ; length = 0
    
.loop:
    cmp byte [rdi + rax], 0 ; Check for null terminator
    je .done
    inc rax                 ; length++
    jmp .loop
    
.done:
    ret                     ; Return length in RAX
```

```c
// main.c

#include <stdio.h>
#include <string.h>

extern size_t asm_strlen(const char *str);

int main() {
    const char *str = "Hello, Assembly!";
    
    size_t len1 = strlen(str);      // C standard library
    size_t len2 = asm_strlen(str);  // Our assembly version
    
    printf("strlen:     %zu\n", len1);
    printf("asm_strlen: %zu\n", len2);
    
    return 0;
}
```

---

## C Function Called from Assembly

### Example 1: Calling printf

```nasm
; hello.asm - Call printf from assembly

section .data
    format db "Hello, %s! The answer is %d", 10, 0
    name db "World", 0
    answer dd 42

section .text
extern printf               ; Declare external C function
global main                 ; Entry point for C runtime

main:
    ; C equivalent:
    ; printf("Hello, %s! The answer is %d\n", "World", 42);
    
    push rbp                ; Set up stack frame
    mov rbp, rsp
    
    ; Prepare arguments for printf
    ; RDI = format string
    ; RSI = first %s argument
    ; RDX = first %d argument
    
    lea rdi, [format]       ; 1st arg: format string
    lea rsi, [name]         ; 2nd arg: "World"
    mov edx, [answer]       ; 3rd arg: 42
    
    xor rax, rax            ; RAX = 0 (no FP args in XMM registers)
    call printf
    
    ; Return 0 from main
    xor eax, eax
    
    leave                   ; Restore stack frame
    ret
```

**Compile:**

```bash
nasm -f elf64 hello.asm -o hello.o
gcc hello.o -o hello -no-pie  # -no-pie for simpler addressing
./hello
```

**Important:** Set `RAX` to the number of floating-point arguments passed in XMM registers (0 if none).

### Example 2: Calling malloc and free

```nasm
; memory.asm - Dynamic memory allocation

section .data
    format db "Allocated at: %p", 10, 0

section .text
extern malloc
extern free
extern printf
global main

main:
    push rbp
    mov rbp, rsp
    push rbx                ; Save callee-saved register
    
    ; C equivalent:
    ; void *ptr = malloc(1024);
    ; printf("Allocated at: %p\n", ptr);
    ; free(ptr);
    
    ; Allocate 1024 bytes
    mov rdi, 1024           ; Size argument
    call malloc
    mov rbx, rax            ; Save pointer in callee-saved RBX
    
    ; Print the address
    lea rdi, [format]
    mov rsi, rbx            ; Pointer as argument
    xor rax, rax
    call printf
    
    ; Free memory
    mov rdi, rbx
    call free
    
    ; Return 0
    xor eax, eax
    
    pop rbx
    leave
    ret
```

### Example 3: Reading User Input

```nasm
; input.asm - Read and echo user input

section .data
    prompt db "Enter your name: ", 0
    format db "Hello, %s!", 10, 0

section .bss
    buffer resb 100

section .text
extern printf
extern fgets
extern stdin
global main

main:
    push rbp
    mov rbp, rsp
    
    ; C equivalent:
    ; printf("Enter your name: ");
    ; fgets(buffer, sizeof(buffer), stdin);
    ; printf("Hello, %s!", buffer);
    
    ; Print prompt
    lea rdi, [prompt]
    xor rax, rax
    call printf
    
    ; Read input: char *fgets(char *s, int size, FILE *stream)
    lea rdi, [buffer]       ; Buffer
    mov rsi, 100            ; Size
    mov rdx, [stdin]        ; FILE *stdin (from libc)
    call fgets
    
    ; Print greeting
    lea rdi, [format]
    lea rsi, [buffer]
    xor rax, rax
    call printf
    
    xor eax, eax
    leave
    ret
```

**Note:** `stdin` is a global variable from libc, accessed via `[stdin]` (not `stdin` directly).

---

## Stack Alignment

The System V ABI requires the stack to be **16-byte aligned** before a `call` instruction. Misalignment can cause crashes (especially with SSE instructions).

### Problem Example

```nasm
main:
    push rbp            ; RSP now misaligned (8-byte offset)
    mov rbp, rsp
    
    call printf         ; CRASH! Stack not 16-byte aligned
```

### Solution 1: Dummy Push

```nasm
main:
    push rbp            ; RSP -= 8 (misaligned)
    mov rbp, rsp
    push rax            ; Dummy push to realign RSP
    
    call printf         ; OK: stack 16-byte aligned
    
    leave
    ret
```

### Solution 2: Sub RSP

```nasm
main:
    push rbp
    mov rbp, rsp
    sub rsp, 8          ; Align stack
    
    call printf
    
    leave
    ret
```

### Solution 3: Calculate Alignment

```nasm
main:
    push rbp
    mov rbp, rsp
    
    ; Save registers we need
    push rbx
    push r12
    ; ... more pushes
    
    ; Align stack
    and rsp, -16        ; Round down to 16-byte boundary
    
    ; ... function calls ...
    
    leave
    ret
```

---

## Passing Structures

### Example: Returning Small Struct

```c
// C code
typedef struct {
    long x;
    long y;
} Point;

Point create_point(long x, long y);
```

```nasm
; point.asm

section .text
global create_point

; Small structs (≤16 bytes) returned in RAX, RDX

create_point:
    ; RDI = x, RSI = y
    mov rax, rdi        ; Return x in RAX
    mov rdx, rsi        ; Return y in RDX
    ret
```

```c
// main.c

#include <stdio.h>

typedef struct {
    long x;
    long y;
} Point;

extern Point create_point(long x, long y);

int main() {
    Point p = create_point(10, 20);
    printf("Point: (%ld, %ld)\n", p.x, p.y);
    return 0;
}
```

### Example: Passing Large Struct

```c
// Large structs (>16 bytes) passed by pointer

typedef struct {
    long a, b, c, d;
} BigStruct;

long sum_struct(const BigStruct *s);
```

```nasm
; struct.asm

section .text
global sum_struct

sum_struct:
    ; RDI = pointer to BigStruct
    
    mov rax, [rdi]          ; s->a
    add rax, [rdi + 8]      ; s->b
    add rax, [rdi + 16]     ; s->c
    add rax, [rdi + 24]     ; s->d
    ret
```

---

## Inline Assembly in C

For small snippets, you can embed assembly directly in C using GCC's extended asm syntax.

### Basic Syntax

```c
asm("assembly code");
```

### Extended Syntax

```c
asm("assembly code"
    : output operands
    : input operands
    : clobbered registers);
```

### Example 1: Read CPU Timestamp Counter

```c
#include <stdio.h>
#include <stdint.h>

uint64_t rdtsc() {
    uint32_t low, high;
    asm volatile("rdtsc" : "=a"(low), "=d"(high));
    return ((uint64_t)high << 32) | low;
}

int main() {
    uint64_t start = rdtsc();
    
    // Do some work
    for (int i = 0; i < 1000000; ++i);
    
    uint64_t end = rdtsc();
    printf("Cycles: %lu\n", end - start);
    return 0;
}
```

### Example 2: Fast Multiply

```c
#include <stdio.h>

long fast_multiply(long a, long b) {
    long result;
    asm("imul %1, %2"
        : "=r"(result)      // Output: result = any register
        : "r"(a), "r"(b)    // Inputs: a and b in registers
    );
    return result;
}

int main() {
    printf("%ld\n", fast_multiply(10, 20));  // 200
    return 0;
}
```

### Example 3: Atomic Operations

```c
#include <stdio.h>

int atomic_increment(int *ptr) {
    int result;
    asm volatile(
        "lock xadd %0, %1"
        : "=r"(result), "+m"(*ptr)
        : "0"(1)
        : "memory"
    );
    return result;
}

int main() {
    int counter = 0;
    printf("Old: %d\n", atomic_increment(&counter));  // 0
    printf("New: %d\n", counter);  // 1
    return 0;
}
```

**Constraints:**
- `"r"` - Any register
- `"a"`, `"b"`, `"c"`, `"d"` - RAX, RBX, RCX, RDX
- `"m"` - Memory operand
- `"i"` - Immediate constant
- `"=r"` - Output register (write-only)
- `"+r"` - Input/output register (read/write)
- `"0"`, `"1"` - Same as operand 0, 1

**Clobbers:**
- `"memory"` - Memory was modified (prevents reordering)
- `"cc"` - Condition codes (flags) were modified

---

## Creating a Reusable Library

### Example: Math Library

**mathlib.asm:**

```nasm
section .text

; long factorial(long n);
global factorial
factorial:
    cmp rdi, 1
    jle .base_case
    
    push rbx
    mov rbx, rdi        ; Save n
    dec rdi
    call factorial      ; factorial(n-1)
    imul rax, rbx       ; n * factorial(n-1)
    pop rbx
    ret
    
.base_case:
    mov rax, 1
    ret

; long power(long base, long exp);
global power
power:
    mov rax, 1          ; result = 1
    test rsi, rsi
    jz .done            ; exp == 0
    
.loop:
    imul rax, rdi       ; result *= base
    dec rsi
    jnz .loop
    
.done:
    ret

; long gcd(long a, long b);
global gcd
gcd:
    test rsi, rsi
    jz .done            ; b == 0, return a
    
    mov rax, rdi        ; rax = a
    xor rdx, rdx
    div rsi             ; rdx = a % b
    
    mov rdi, rsi        ; a = b
    mov rsi, rdx        ; b = remainder
    jmp gcd             ; tail recursion
    
.done:
    mov rax, rdi
    ret
```

**mathlib.h:**

```c
#ifndef MATHLIB_H
#define MATHLIB_H

long factorial(long n);
long power(long base, long exp);
long gcd(long a, long b);

#endif
```

**test.c:**

```c
#include <stdio.h>
#include "mathlib.h"

int main() {
    printf("factorial(5) = %ld\n", factorial(5));      // 120
    printf("power(2, 10) = %ld\n", power(2, 10));      // 1024
    printf("gcd(48, 18) = %ld\n", gcd(48, 18));        // 6
    return 0;
}
```

**Build:**

```bash
nasm -f elf64 mathlib.asm -o mathlib.o
gcc -c test.c -o test.o
gcc test.o mathlib.o -o test
./test
```

**Create Static Library:**

```bash
nasm -f elf64 mathlib.asm -o mathlib.o
ar rcs libmathlib.a mathlib.o
gcc test.c -L. -lmathlib -o test
```

---

## Debugging Mixed C/Assembly

### Using GDB

```bash
# Compile with debug symbols
nasm -f elf64 -g -F dwarf mathlib.asm -o mathlib.o
gcc -g test.c mathlib.o -o test

# Debug
gdb ./test
```

**GDB Commands:**

```gdb
(gdb) break main
(gdb) run
(gdb) stepi              # Step one instruction
(gdb) info registers     # Show all registers
(gdb) x/10i $rip         # Disassemble next 10 instructions
(gdb) layout asm         # Show assembly in TUI mode
(gdb) layout regs        # Show registers in TUI mode
```

### Printing from Assembly (Debug)

```nasm
section .data
    debug_fmt db "Debug: RAX=%ld, RBX=%ld", 10, 0

section .text
extern printf

; ... in your function ...
    push rax
    push rbx
    
    ; Save registers that printf uses
    push rdi
    push rsi
    push rdx
    
    lea rdi, [debug_fmt]
    mov rsi, rax
    mov rdx, rbx
    xor rax, rax
    call printf
    
    pop rdx
    pop rsi
    pop rdi
    pop rbx
    pop rax
```

---

## Common Pitfalls

### 1. Stack Misalignment

```c
// WRONG: Misaligned stack
void asm_func() {
    asm("call printf");  // May crash!
}

// CORRECT: Ensure alignment
void asm_func() {
    asm("sub $8, %%rsp");  // Align
    asm("call printf");
    asm("add $8, %%rsp");  // Restore
}
```

### 2. Not Saving Callee-Saved Registers

```nasm
; WRONG: Corrupting RBX
my_func:
    mov rbx, rdi        ; Use RBX
    ; ... use rbx ...
    ret                 ; BUG: didn't restore RBX!

; CORRECT:
my_func:
    push rbx
    mov rbx, rdi
    ; ... use rbx ...
    pop rbx
    ret
```

### 3. Forgetting RAX for varargs

```nasm
; WRONG: Calling printf with float
mov rdi, format
movsd xmm0, [value]
call printf             ; BUG: RAX not set!

; CORRECT:
mov rdi, format
movsd xmm0, [value]
mov rax, 1              ; 1 floating-point arg in XMM
call printf
```

### 4. Wrong Parameter Order

```c
// C: long subtract(long a, long b) { return a - b; }
```

```nasm
; WRONG: Swapped parameters
subtract:
    mov rax, rsi        ; rsi is b, not a!
    sub rax, rdi
    ret

; CORRECT:
subtract:
    mov rax, rdi        ; First param (a) in RDI
    sub rax, rsi        ; Subtract second param (b)
    ret
```

---

## Summary

### Key Concepts
1. **System V ABI**: Parameters in RDI, RSI, RDX, RCX, R8, R9; return in RAX
2. **Stack alignment**: Must be 16-byte aligned before `call`
3. **Callee-saved**: Must preserve RBX, RBP, R12-R15
4. **Caller-saved**: RAX, RCX, RDX, RSI, RDI, R8-R11 can be clobbered
5. **Small structs**: Returned in RAX:RDX
6. **Large structs**: Passed/returned by pointer

### Workflow
1. Write assembly with `global` for exported functions
2. Declare `extern` for C functions you call
3. Use proper calling convention
4. Compile: `nasm -f elf64 file.asm -o file.o`
5. Link: `gcc main.c file.o -o program`

### Best Practices
1. Always preserve callee-saved registers
2. Align stack before calling C functions
3. Set RAX for varargs functions
4. Use inline asm for small snippets
5. Create libraries for reusable assembly code
6. Test thoroughly - calling convention bugs are subtle

---

## Practice Exercises

### Exercise 1: Implement memcpy

Write an assembly function with C prototype:
```c
void *memcpy(void *dest, const void *src, size_t n);
```

### Exercise 2: Binary Search

Implement binary search in assembly, callable from C:
```c
int binary_search(const int *array, int size, int target);
```

### Exercise 3: SIMD Sum

Use SSE to sum an array of floats:
```c
float sum_array(const float *array, int count);
```

---

## Next Topic

In **Topic 18: SIMD Instructions**, we'll explore Single Instruction Multiple Data operations using SSE and AVX, enabling massive parallelism for data processing.

**Preview:**
- SSE/AVX registers (XMM, YMM, ZMM)
- Packed operations on multiple data elements
- Vectorized array processing
- Common SIMD patterns
- Performance gains from SIMD

