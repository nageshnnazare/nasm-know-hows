# 📘 Topic 3: Basic Instructions

Master the fundamental assembly instructions you'll use every day.

---

## **Overview**

Assembly instructions are the building blocks of your programs. In this topic, you'll learn the most essential instructions for:
- Moving data around
- Performing arithmetic
- Manipulating bits
- Working with memory addresses

---

## **Part 1: The MOV Instruction**

**MOV** is the most fundamental instruction - it copies data from source to destination.

### **Basic Syntax**

```nasm
mov destination, source     ; destination = source
```

### **Important Rules**

```nasm
; ✅ ALLOWED combinations:
mov reg, reg        ; Register to register
mov reg, mem        ; Memory to register
mov mem, reg        ; Register to memory
mov reg, imm        ; Immediate to register
mov mem, imm        ; Immediate to memory

; ❌ NOT ALLOWED:
mov mem, mem        ; Cannot move memory to memory directly!
mov seg, seg        ; Cannot move segment to segment
```

### **MOV Examples**

```nasm
section .data
    value dq 42
    buffer resb 64

section .text
    ; Register to register
    mov rax, rbx            ; RAX = RBX
    mov ecx, edx            ; ECX = EDX (32-bit)
    mov al, bl              ; AL = BL (8-bit)
    
    ; Immediate to register
    mov rax, 100            ; RAX = 100
    mov eax, 0x12345678     ; EAX = 0x12345678
    mov cl, 'A'             ; CL = 65 (ASCII 'A')
    
    ; Memory to register
    mov rax, [value]        ; RAX = contents of value
    mov al, [buffer]        ; AL = first byte of buffer
    mov ecx, [value + 4]    ; ECX = dword at value+4
    
    ; Register to memory
    mov [buffer], rax       ; Store RAX at buffer
    mov [value], rbx        ; Store RBX at value
    
    ; Immediate to memory (must specify size!)
    mov qword [buffer], 42  ; Store 42 as quadword
    mov dword [buffer], 42  ; Store 42 as dword
    mov byte [buffer], 42   ; Store 42 as byte
```

### **MOV Gotchas**

```nasm
; ❌ Size ambiguity
mov [buffer], 42            ; ERROR: What size?

; ✅ Fix: Specify size
mov byte [buffer], 42       ; Clear: 1 byte
mov qword [buffer], 42      ; Clear: 8 bytes

; ❌ Cannot move memory to memory
mov [dest], [source]        ; ERROR!

; ✅ Fix: Use intermediate register
mov rax, [source]
mov [dest], rax

; ⚠️ Watch 32-bit zeroing!
mov rax, 0xFFFFFFFFFFFFFFFF ; RAX = all F's
mov eax, 0x11111111         ; RAX = 0x0000000011111111
                            ;       ^^^^^^^^ zeroed!
```

---

## **Part 2: Arithmetic Instructions**

### **ADD - Addition**

```nasm
add destination, source     ; destination = destination + source
```

**Examples:**

```nasm
; Register arithmetic
mov rax, 10
add rax, 5              ; RAX = 15
add rax, rbx            ; RAX = RAX + RBX

; Memory arithmetic
add qword [counter], 1  ; Increment counter in memory
add rax, [value]        ; RAX = RAX + [value]

; Sets flags!
mov al, 255
add al, 1               ; AL = 0, Carry Flag (CF) = 1
```

**Flags affected:** CF, ZF, SF, OF, AF, PF

---

### **SUB - Subtraction**

```nasm
sub destination, source     ; destination = destination - source
```

**Examples:**

```nasm
; Basic subtraction
mov rax, 100
sub rax, 30             ; RAX = 70
sub rax, rbx            ; RAX = RAX - RBX

; Detect underflow
mov al, 5
sub al, 10              ; AL = 251 (wraps around), CF = 1

; Compare without storing (common pattern)
mov rax, 10
sub rax, rax            ; RAX = 0, ZF = 1 (zero result)
```

**Flags affected:** CF, ZF, SF, OF, AF, PF

---

### **INC - Increment**

```nasm
inc destination         ; destination = destination + 1
```

**Examples:**

```nasm
; Increment registers
mov rax, 10
inc rax                 ; RAX = 11
inc ecx                 ; ECX = ECX + 1

; Increment memory
inc qword [counter]     ; counter = counter + 1
inc byte [buffer]       ; First byte of buffer + 1

; Loop counter pattern
mov rcx, 0
loop_start:
    ; ... do work ...
    inc rcx
    cmp rcx, 10
    jl loop_start
```

**Note:** INC is shorter than `add reg, 1` but doesn't affect CF!

**Flags affected:** ZF, SF, OF, AF, PF (but NOT CF)

---

### **DEC - Decrement**

```nasm
dec destination         ; destination = destination - 1
```

**Examples:**

```nasm
; Decrement registers
mov rax, 10
dec rax                 ; RAX = 9

; Countdown loop
mov rcx, 10
countdown:
    ; ... do work ...
    dec rcx
    jnz countdown       ; Jump if not zero
```

**Flags affected:** ZF, SF, OF, AF, PF (but NOT CF)

---

### **NEG - Negate (Two's Complement)**

```nasm
neg destination         ; destination = -destination
```

**Examples:**

```nasm
mov rax, 10
neg rax                 ; RAX = -10 (0xFFFFFFFFFFFFFFF6)

mov al, 5
neg al                  ; AL = -5 (0xFB = 251 unsigned)

; Absolute value pattern
; if (rax < 0) rax = -rax;
test rax, rax           ; Check sign
jns skip_neg            ; Jump if not negative
neg rax
skip_neg:
```

**Flags affected:** CF, ZF, SF, OF, AF, PF

---

### **MUL/IMUL - Multiplication**

**MUL** - Unsigned multiply  
**IMUL** - Signed multiply

#### **Single Operand Form (MUL/IMUL)**

```nasm
mul source              ; RDX:RAX = RAX * source (unsigned)
imul source             ; RDX:RAX = RAX * source (signed)
```

**Examples:**

```nasm
; Unsigned multiply
mov rax, 10
mov rbx, 20
mul rbx                 ; RDX:RAX = 200 (result in RAX, RDX = 0)

; 64-bit result
mov rax, 0xFFFFFFFFFFFFFFFF
mov rbx, 2
mul rbx                 ; RDX:RAX = 0x1FFFFFFFFFFFFFFFE
                        ; RDX = 0x1, RAX = 0xFFFFFFFFFFFFFFFE

; Signed multiply
mov rax, -5
mov rbx, 3
imul rbx                ; RAX = -15
```

#### **Two Operand Form (IMUL only)**

```nasm
imul dest, source       ; dest = dest * source (truncated)
```

**Examples:**

```nasm
mov rax, 10
imul rax, 5             ; RAX = 50

mov ecx, 100
imul ecx, edx           ; ECX = ECX * EDX
```

#### **Three Operand Form (IMUL only)**

```nasm
imul dest, source, imm  ; dest = source * immediate
```

**Examples:**

```nasm
imul rax, rbx, 10       ; RAX = RBX * 10
imul ecx, edx, 100      ; ECX = EDX * 100

; Quick scaling
imul rax, rsi, 4        ; RAX = RSI * 4 (array index)
```

---

### **DIV/IDIV - Division**

**DIV** - Unsigned division  
**IDIV** - Signed division

```nasm
div divisor             ; RAX = RDX:RAX / divisor (quotient)
                        ; RDX = RDX:RAX % divisor (remainder)

idiv divisor            ; Same but signed
```

**Important:** Must set up RDX:RAX correctly before dividing!

**Examples:**

```nasm
; Unsigned division
mov rax, 100
xor rdx, rdx            ; Clear RDX (upper 64 bits)
mov rbx, 10
div rbx                 ; RAX = 10 (quotient), RDX = 0 (remainder)

; Division with remainder
mov rax, 23
xor rdx, rdx
mov rbx, 5
div rbx                 ; RAX = 4, RDX = 3 (23 = 5*4 + 3)

; Signed division
mov rax, -20
cqo                     ; Sign-extend RAX into RDX
mov rbx, 3
idiv rbx                ; RAX = -6, RDX = -2

; 32-bit division
mov eax, 100
xor edx, edx            ; Clear EDX
mov ecx, 10
div ecx                 ; EAX = 10, EDX = 0
```

**Critical:** Always clear/set RDX before DIV/IDIV!

```nasm
; ❌ WRONG - RDX has garbage
mov rax, 100
div rbx                 ; Divides RDX:RAX (huge number!)

; ✅ CORRECT - Clear RDX for unsigned
mov rax, 100
xor rdx, rdx
div rbx

; ✅ CORRECT - Sign-extend for signed
mov rax, -100
cqo                     ; RDX = 0xFFFFFFFFFFFFFFFF if RAX < 0
idiv rbx
```

---

## **Part 3: Bitwise Instructions**

### **AND - Bitwise AND**

```nasm
and destination, source ; destination = destination & source
```

**Truth Table:**
```
0 & 0 = 0
0 & 1 = 0
1 & 0 = 0
1 & 1 = 1
```

**Examples:**

```nasm
; Masking bits
mov rax, 0b11111111
and rax, 0b00001111     ; RAX = 0b00001111 (keep lower 4 bits)

; Check if even (bit 0 = 0)
mov rax, 42
and rax, 1              ; RAX = 0 (even), ZF = 1

; Clear specific bits
mov rax, 0xFF
and rax, 0xF0           ; RAX = 0xF0 (clear lower 4 bits)

; Alignment check (is address 16-byte aligned?)
mov rax, address
and rax, 0xF            ; If RAX = 0, address is aligned
```

**Flags affected:** ZF, SF, PF (CF and OF cleared)

---

### **OR - Bitwise OR**

```nasm
or destination, source  ; destination = destination | source
```

**Truth Table:**
```
0 | 0 = 0
0 | 1 = 1
1 | 0 = 1
1 | 1 = 1
```

**Examples:**

```nasm
; Set specific bits
mov rax, 0b00000000
or rax, 0b00001111      ; RAX = 0b00001111 (set lower 4 bits)

; Combine flags
mov rax, 0x01           ; Flag bit 0
mov rbx, 0x04           ; Flag bit 2
or rax, rbx             ; RAX = 0x05 (both flags set)

; Test for zero (common idiom)
or rax, rax             ; Sets ZF if RAX = 0 (doesn't change RAX)
jz is_zero
```

**Flags affected:** ZF, SF, PF (CF and OF cleared)

---

### **XOR - Bitwise XOR (Exclusive OR)**

```nasm
xor destination, source ; destination = destination ^ source
```

**Truth Table:**
```
0 ^ 0 = 0
0 ^ 1 = 1
1 ^ 0 = 1
1 ^ 1 = 0  ← Same bits = 0
```

**Examples:**

```nasm
; Toggle bits
mov rax, 0b11110000
xor rax, 0b11111111     ; RAX = 0b00001111 (all bits toggled)

; Zero a register (most efficient!)
xor rax, rax            ; RAX = 0 (any value XOR itself = 0)
xor eax, eax            ; EAX = 0 (also zeros upper 32 bits)

; Swap without temp variable!
mov rax, 5
mov rbx, 10
xor rax, rbx            ; RAX = 5 ^ 10
xor rbx, rax            ; RBX = 10 ^ (5 ^ 10) = 5
xor rax, rbx            ; RAX = (5 ^ 10) ^ 5 = 10
; Now: RAX = 10, RBX = 5

; Simple encryption (XOR cipher)
mov al, 'A'             ; AL = 65
xor al, 0x42            ; Encrypt: AL = 39
xor al, 0x42            ; Decrypt: AL = 65 ('A' again!)
```

**Flags affected:** ZF, SF, PF (CF and OF cleared)

---

### **NOT - Bitwise NOT (One's Complement)**

```nasm
not destination         ; destination = ~destination
```

**Examples:**

```nasm
; Invert all bits
mov rax, 0b00001111
not rax                 ; RAX = 0b...11110000 (all bits flipped)

mov al, 0x0F
not al                  ; AL = 0xF0

; Create mask
mov rax, 0x00FF         ; Mask for lower byte
not rax                 ; RAX = 0x...FF00 (inverted mask)
```

**Flags affected:** None!

---

### **TEST - Logical Compare (AND without storing)**

```nasm
test operand1, operand2 ; Performs AND, sets flags, doesn't store result
```

**Examples:**

```nasm
; Check if zero
test rax, rax           ; ZF = 1 if RAX = 0
jz is_zero

; Check specific bit
test rax, 0x01          ; Check bit 0
jnz bit_is_set

; Check if negative (sign bit)
test rax, rax           ; SF = 1 if RAX < 0 (signed)
js is_negative

; Check multiple bits
test al, 0b11110000     ; Check if any of upper 4 bits are set
jnz has_upper_bits
```

**Flags affected:** ZF, SF, PF (CF and OF cleared)

**Why use TEST instead of AND?**
- Doesn't modify the operand
- Shorter encoding in some cases
- More readable intent (testing, not modifying)

---

## **Part 4: Shift and Rotate Instructions**

### **SHL/SHR - Logical Shifts**

```nasm
shl destination, count  ; Shift left (multiply by 2^count)
shr destination, count  ; Shift right (divide by 2^count, unsigned)
```

**Visual:**

```
SHL (Shift Left):
Before: 0000 1010 (10)
SHL 1:  0001 0100 (20)  ← bit shifted out to CF
SHL 2:  0010 1000 (40)

SHR (Shift Right):
Before: 0000 1010 (10)
SHR 1:  0000 0101 (5)   ← bit shifted out to CF
SHR 2:  0000 0010 (2)
```

**Examples:**

```nasm
; Multiply by powers of 2
mov rax, 10
shl rax, 1              ; RAX = 20 (10 * 2)
shl rax, 2              ; RAX = 80 (20 * 4)

; Divide by powers of 2 (unsigned)
mov rax, 100
shr rax, 1              ; RAX = 50 (100 / 2)
shr rax, 2              ; RAX = 12 (50 / 4)

; Extract high bits
mov al, 0b11010110
shr al, 4               ; AL = 0b00001101 (upper 4 bits moved down)

; Shift by CL register
mov cl, 3
mov rax, 1
shl rax, cl             ; RAX = 8 (1 << 3)

; Array indexing (multiply by element size)
mov rax, index
shl rax, 3              ; RAX = index * 8 (for 8-byte elements)
```

---

### **SAL/SAR - Arithmetic Shifts**

```nasm
sal destination, count  ; Shift Arithmetic Left (same as SHL)
sar destination, count  ; Shift Arithmetic Right (preserves sign bit)
```

**SAR preserves the sign bit:**

```
SAR on positive number:
Before: 0000 1010 (10)
SAR 1:  0000 0101 (5)

SAR on negative number:
Before: 1111 0110 (-10 in two's complement)
SAR 1:  1111 1011 (-5) ← sign bit duplicated
```

**Examples:**

```nasm
; Signed division by powers of 2
mov rax, -16
sar rax, 2              ; RAX = -4 (preserves sign)

; Compare with SHR (unsigned shift)
mov rax, -16            ; RAX = 0xFFFFFFFFFFFFFFF0
shr rax, 2              ; RAX = 0x3FFFFFFFFFFFFFFC (huge positive!)

mov rax, -16
sar rax, 2              ; RAX = 0xFFFFFFFFFFFFFFFC (correct: -4)
```

---

### **ROL/ROR - Rotate (No Bits Lost)**

```nasm
rol destination, count  ; Rotate left (bits wrap around)
ror destination, count  ; Rotate right
```

**Visual:**

```
ROL (Rotate Left):
Before: 1010 0001
ROL 1:  0100 0011  ← MSB wraps to LSB

ROR (Rotate Right):
Before: 1010 0001
ROR 1:  1101 0000  ← LSB wraps to MSB
```

**Examples:**

```nasm
; Circular rotation
mov al, 0b10000001
rol al, 1               ; AL = 0b00000011
rol al, 1               ; AL = 0b00000110

; Endianness conversion (byte swap)
mov eax, 0x12345678
rol eax, 8              ; EAX = 0x34567812
rol eax, 8              ; EAX = 0x56781234
```

---

## **Part 5: LEA - Load Effective Address**

**LEA** is a special instruction that computes an address but doesn't access memory.

```nasm
lea destination, [address]  ; destination = address (not contents!)
```

### **LEA vs MOV**

```nasm
section .data
    array dq 10, 20, 30, 40

section .text
    ; MOV loads the VALUE
    mov rax, [array]        ; RAX = 10 (value at array)
    
    ; LEA loads the ADDRESS
    lea rax, [array]        ; RAX = address of array
    
    ; Equivalent to:
    mov rax, array          ; Same as LEA for simple labels
```

### **LEA for Arithmetic (No Memory Access!)**

This is where LEA shines - it uses the addressing mode calculator for math:

```nasm
; Traditional arithmetic
mov rax, rbx
add rax, rcx
add rax, 8
; Total: 3 instructions

; With LEA - one instruction!
lea rax, [rbx + rcx + 8]    ; RAX = RBX + RCX + 8

; Multiply by 2, 3, 4, 5, 8, 9
lea rax, [rbx * 2]          ; RAX = RBX * 2
lea rax, [rbx + rbx*2]      ; RAX = RBX * 3
lea rax, [rbx * 4]          ; RAX = RBX * 4
lea rax, [rbx + rbx*4]      ; RAX = RBX * 5
lea rax, [rbx * 8]          ; RAX = RBX * 8
lea rax, [rbx + rbx*8]      ; RAX = RBX * 9

; Complex calculation
lea rax, [rbx + rcx*4 + 100]; RAX = RBX + (RCX * 4) + 100
```

### **LEA Advantages**

```nasm
; 1. No memory access (faster)
lea rax, [rbx + 8]          ; Just arithmetic, no memory read

; 2. Doesn't affect flags (unlike ADD)
add rax, rbx                ; Affects CF, ZF, SF, OF, AF, PF
lea rax, [rax + rbx]        ; Affects NO flags!

; 3. Three-operand arithmetic
add rax, rbx                ; RAX = RAX + RBX (destroys old RAX)
lea rax, [rbx + rcx]        ; RAX = RBX + RCX (preserves RBX and RCX)

; 4. Combined operations
; Traditional:
mov rax, index
shl rax, 3
add rax, base
add rax, 16

; With LEA:
lea rax, [base + index*8 + 16]  ; One instruction!
```

### **Practical LEA Examples**

```nasm
; Array element address
; address = base + index * sizeof(element)
lea rax, [array + rcx*8]    ; 8-byte elements

; String offset
lea rsi, [string + 5]       ; Point to 6th character

; Struct member
; struct.field at offset 16
lea rax, [rbx + 16]

; Scale and offset
; result = x * 5 + 10
lea rax, [rdi + rdi*4 + 10] ; x + x*4 + 10 = x*5 + 10
```

---

## **Part 6: Comparison Instructions**

### **CMP - Compare (SUB without storing)**

```nasm
cmp operand1, operand2      ; Performs SUB, sets flags, doesn't store
```

**Examples:**

```nasm
; Basic comparison
cmp rax, 10                 ; Compare RAX with 10
je equal                    ; Jump if RAX == 10
jne not_equal               ; Jump if RAX != 10
jg greater                  ; Jump if RAX > 10 (signed)
jl less                     ; Jump if RAX < 10 (signed)

; Compare registers
cmp rax, rbx
jge rax_greater_or_equal    ; Jump if RAX >= RBX

; Compare with memory
cmp rax, [value]
je values_match

; Zero check
cmp rax, 0                  ; Check if zero
jz is_zero
; Better: test rax, rax    ; More efficient!
```

**How CMP works:**
- Computes `operand1 - operand2`
- Sets flags based on result
- Doesn't store the result
- Use conditional jumps after CMP

---

## **Part 7: Practical Examples**

### **Example 1: Sum Array Elements**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int32_t numbers[] = {10, 20, 30, 40, 50};
    int32_t count = 5;
    int32_t sum = 0;
    
    for (int32_t index = 0; index < count; index++) {
        sum += numbers[index];
    }
    
    // sum = 150
    return 0;
}
```

**Assembly:**
```nasm
section .data
    numbers dd 10, 20, 30, 40, 50
    count equ 5

section .bss
    sum resd 1

section .text
    global _start

_start:
    xor eax, eax            ; sum = 0
    xor ecx, ecx            ; index = 0
    
sum_loop:
    add eax, [numbers + rcx*4]  ; sum += numbers[index]
    inc ecx                     ; index++
    cmp ecx, count              ; index < count?
    jl sum_loop                 ; Loop if less
    
    mov [sum], eax          ; Store result (150)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 2: Find Maximum**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int32_t numbers[] = {15, 42, 7, 89, 23};
    int32_t count = 5;
    int32_t max = numbers[0];
    
    for (int32_t index = 1; index < count; index++) {
        if (numbers[index] > max) {
            max = numbers[index];
        }
    }
    
    // max = 89
    return 0;
}
```

**Assembly:**
```nasm
section .data
    numbers dd 15, 42, 7, 89, 23
    count equ 5

section .bss
    max resd 1

section .text
    global _start

_start:
    mov eax, [numbers]      ; max = numbers[0]
    mov ecx, 1              ; index = 1
    
find_max:
    cmp eax, [numbers + rcx*4]  ; max < numbers[index]?
    jge skip_update
    mov eax, [numbers + rcx*4]  ; max = numbers[index]
    
skip_update:
    inc ecx
    cmp ecx, count
    jl find_max
    
    mov [max], eax          ; Store result (89)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 3: Factorial**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int64_t n = 5;
    int64_t result = 1;
    
    while (n != 0) {
        result *= n;
        n--;
    }
    
    // result = 120 (5!)
    return result;
}
```

**Assembly:**
```nasm
; Calculate factorial of 5
section .text
    global _start

_start:
    mov rcx, 5              ; n = 5
    mov rax, 1              ; result = 1
    
factorial_loop:
    imul rax, rcx           ; result *= n
    dec rcx                 ; n--
    jnz factorial_loop      ; Loop if n != 0
    
    ; RAX now contains 120 (5!)
    
    ; Exit
    mov rdi, rax            ; Exit with factorial as code
    mov rax, 60
    syscall
```

### **Example 4: Bit Manipulation**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    uint64_t value = 0b10110101;
    
    // Set bit 3
    value |= 0b00001000;          // value = 0b10111101
    
    // Clear bit 5
    value &= ~0b00100000;         // value = 0b10011101
    
    // Toggle bit 0
    value ^= 0b00000001;          // value = 0b10011100
    
    // Test bit 4
    if (value & 0b00010000) {     // Check if bit 4 is set
        // bit4_is_set
    }
    
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global _start

_start:
    mov rax, 0b10110101
    
    ; Set bit 3
    or rax, 0b00001000      ; RAX = 0b10111101
    
    ; Clear bit 5
    and rax, ~0b00100000    ; RAX = 0b10011101
    
    ; Toggle bit 0
    xor rax, 0b00000001     ; RAX = 0b10011100
    
    ; Test bit 4
    test rax, 0b00010000    ; ZF = 0 (bit is set)
    jnz bit4_is_set
    
bit4_is_set:
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 5: Using LEA**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    // Calculate: result = x * 5 + y * 3 + 10
    int64_t x = 4;
    int64_t y = 7;
    
    int64_t result = x * 5 + y * 3 + 10;
    
    // result = 51
    return result;
}
```

**Assembly:**
```nasm
section .text
    global _start

_start:
    ; Calculate: result = x * 5 + y * 3 + 10
    ; where x = 4, y = 7
    
    mov rdi, 4              ; x = 4
    mov rsi, 7              ; y = 7
    
    ; x * 5 using LEA
    lea rax, [rdi + rdi*4]  ; RAX = x * 5 = 20
    
    ; y * 3 using LEA
    lea rbx, [rsi + rsi*2]  ; RBX = y * 3 = 21
    
    ; Combine and add 10
    lea rax, [rax + rbx + 10]   ; RAX = 20 + 21 + 10 = 51
    
    ; Exit with result
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 8: Performance Tips**

### **Choose the Right Instruction**

```nasm
; Zeroing a register:
xor eax, eax            ; ✅ Best: 2 bytes, fast
mov eax, 0              ; ❌ Worse: 5 bytes, slower

; Incrementing:
inc rax                 ; ✅ Good: 3 bytes
add rax, 1              ; ❌ Longer: 4 bytes
lea rax, [rax + 1]      ; ⚠️ Doesn't affect flags, but longer

; Testing for zero:
test rax, rax           ; ✅ Best: clear intent
cmp rax, 0              ; ❌ Longer encoding
or rax, rax             ; ✅ Also good, but TEST is clearer

; Multiplying by constant power of 2:
shl rax, 3              ; ✅ Best: RAX * 8
imul rax, 8             ; ❌ Slower, longer latency

; Small multiplications:
lea rax, [rax + rax*2]  ; ✅ Best: RAX * 3
imul rax, 3             ; ❌ Slower
```

### **Avoid False Dependencies**

```nasm
; ❌ BAD: False dependency
mov eax, [mem1]
add eax, 10
mov eax, [mem2]         ; CPU must wait for previous MOV

; ✅ GOOD: Break dependency with XOR
mov eax, [mem1]
add eax, 10
xor eax, eax            ; Breaks dependency chain
mov eax, [mem2]         ; Can start immediately
```

---

## **Part 9: Common Patterns**

### **Clear a Register**

```nasm
xor rax, rax            ; Preferred
xor eax, eax            ; Even better (shorter, zeros full RAX)
```

### **Set Register to -1**

```nasm
mov rax, -1             ; Works but longer
or rax, -1              ; Same result
xor rax, rax            ; 2 bytes
dec rax                 ; 3 bytes total (0 - 1 = -1)
```

### **Conditional Move**

```nasm
; if (rax > rbx) rax = rbx;
cmp rax, rbx
jle skip
mov rax, rbx
skip:

; Better (on modern CPUs): CMOVcc
cmp rax, rbx
cmovg rax, rbx          ; Conditional move if greater
```

### **Absolute Value**

```nasm
; abs(rax)
test rax, rax
jns skip_neg
neg rax
skip_neg:

; Alternative using CDQ tricks (for EAX)
mov edx, eax
sar edx, 31             ; EDX = all 1's if negative, 0 if positive
xor eax, edx
sub eax, edx            ; EAX = abs(EAX)
```

### **Min/Max**

```nasm
; min(rax, rbx) -> rax
cmp rax, rbx
jle already_min
mov rax, rbx
already_min:

; max(rax, rbx) -> rax
cmp rax, rbx
jge already_max
mov rax, rbx
already_max:
```

---

## **✅ Practice Exercises**

### **Exercise 1: Basic Operations**

Write code to:
1. Set RAX to 100
2. Add 50 to RAX
3. Multiply RAX by 2
4. Subtract 75
5. What's the final value?

<details>
<summary>Solution</summary>

```nasm
mov rax, 100        ; RAX = 100
add rax, 50         ; RAX = 150
shl rax, 1          ; RAX = 300 (multiply by 2)
sub rax, 75         ; RAX = 225

; Final answer: 225
```
</details>

### **Exercise 2: Bit Manipulation**

Given AL = 0b10110100:
1. Set bit 0
2. Clear bit 6
3. Toggle bit 3
4. What's the final binary value?

<details>
<summary>Solution</summary>

```nasm
mov al, 0b10110100
or al, 0b00000001       ; Set bit 0: 0b10110101
and al, ~0b01000000     ; Clear bit 6: 0b00110101
xor al, 0b00001000      ; Toggle bit 3: 0b00111101

; Final answer: 0b00111101 (0x3D)
```
</details>

### **Exercise 3: Average of Two Numbers**

Calculate average of RAX and RBX (assume they won't overflow).

<details>
<summary>Solution</summary>

```nasm
; Method 1: Simple
mov rcx, rax
add rcx, rbx
shr rcx, 1              ; Divide by 2

; Method 2: Overflow-safe
mov rcx, rax
and rcx, rbx            ; Common bits
xor rax, rbx            ; Differing bits
shr rax, 1              ; Half the difference
add rax, rcx            ; Average
```
</details>

### **Exercise 4: Count Set Bits**

Count how many bits are set in AL (population count).

<details>
<summary>Solution (simple loop)</summary>

```nasm
xor rcx, rcx            ; count = 0
mov rbx, 8              ; bits to check

count_loop:
    test al, 1          ; Check lowest bit
    jz skip_count
    inc rcx             ; Count if set
skip_count:
    shr al, 1           ; Next bit
    dec rbx
    jnz count_loop
    
; RCX contains count
```
</details>

### **Exercise 5: Using LEA**

Calculate: result = (x * 9) + (y * 5) + 20
Where x = RDI, y = RSI
Use only LEA instructions for multiplication.

<details>
<summary>Solution</summary>

```nasm
lea rax, [rdi + rdi*8]      ; x * 9
lea rbx, [rsi + rsi*4]      ; y * 5
lea rax, [rax + rbx + 20]   ; Combine and add 20

; Final answer in RAX
```
</details>

---

## **📋 Quick Reference**

### **Data Movement**
```
mov dest, src       ; Copy data
lea dest, [addr]    ; Load address (no memory access)
xchg op1, op2       ; Swap
```

### **Arithmetic**
```
add dest, src       ; Addition
sub dest, src       ; Subtraction
inc dest            ; Increment
dec dest            ; Decrement
neg dest            ; Negate
mul src             ; Unsigned multiply
imul src/dest,src   ; Signed multiply
div src             ; Unsigned divide
idiv src            ; Signed divide
```

### **Bitwise**
```
and dest, src       ; Bitwise AND
or dest, src        ; Bitwise OR
xor dest, src       ; Bitwise XOR
not dest            ; Bitwise NOT
test op1, op2       ; AND without storing
```

### **Shifts**
```
shl dest, count     ; Shift left (unsigned)
shr dest, count     ; Shift right (unsigned)
sal dest, count     ; Shift arithmetic left
sar dest, count     ; Shift arithmetic right (preserves sign)
rol dest, count     ; Rotate left
ror dest, count     ; Rotate right
```

### **Comparison**
```
cmp op1, op2        ; Compare (SUB without storing)
```

---

## **🎯 Knowledge Check**

Before moving to Topic 4, verify you understand:
- ✅ MOV and its restrictions (no mem-to-mem)
- ✅ ADD, SUB, INC, DEC
- ✅ MUL/IMUL/DIV/IDIV and setting up RDX:RAX
- ✅ AND, OR, XOR, NOT, TEST
- ✅ Shifts (SHL, SHR, SAL, SAR, ROL, ROR)
- ✅ LEA for arithmetic without memory access
- ✅ CMP for comparisons
- ✅ When to use which instruction

---

**🎉 Excellent!** You now know the essential assembly instructions!

**Next:** Topic 4: Flags & Comparisons (coming soon)

---

[← Previous Topic](topic-02-registers.md) | [Back to Main](../README.md) | Next Topic →

