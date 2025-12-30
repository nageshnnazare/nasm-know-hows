# Topic 13: Multiplication and Division

## Overview

Multiplication and division are more complex operations in assembly than addition and subtraction. They involve multiple registers, can produce results larger than the input operands, and have special handling for signed vs unsigned operations.

```c
// C equivalent concepts we'll explore:
int product = a * b;
int quotient = a / b;
int remainder = a % b;
unsigned long long wide = (unsigned long long)a * b;  // 64-bit * 64-bit = 128-bit
```

---

## Multiplication Instructions

### `MUL` - Unsigned Multiplication

```nasm
; C equivalent:
; unsigned long long result = rax * operand;
; // Upper 64 bits go to RDX, lower 64 bits go to RAX

mul operand     ; RDX:RAX = RAX * operand (unsigned)
```

**Key Points:**
- **Operand sizes**: byte (8-bit), word (16-bit), dword (32-bit), qword (64-bit)
- **Implicit operands**: Always uses `AL/AX/EAX/RAX` as one input
- **Result**: Double-width result (upper half in `DX/EDX/RDX`, lower in `AX/EAX/RAX`)

**Size Variants:**

| Instruction | Operation | Result Location |
|-------------|-----------|-----------------|
| `mul r/m8` | `AX = AL * r/m8` | AH:AL (upper:lower) |
| `mul r/m16` | `DX:AX = AX * r/m16` | DX:AX |
| `mul r/m32` | `EDX:EAX = EAX * r/m32` | EDX:EAX |
| `mul r/m64` | `RDX:RAX = RAX * r/m64` | RDX:RAX |

**Flags Affected:**
- **CF/OF**: Set if upper half of result is non-zero (overflow occurred)
- **SF, ZF, AF, PF**: Undefined

**Example: 64-bit × 64-bit = 128-bit**

```nasm
section .data
    a dq 0x123456789ABCDEF0
    b dq 0x0FEDCBA987654321
    result_low dq 0
    result_high dq 0

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned __int128 result = (unsigned __int128)a * (unsigned __int128)b;
    ; unsigned long long result_high = result >> 64;
    ; unsigned long long result_low = result & 0xFFFFFFFFFFFFFFFF;
    
    mov rax, [a]            ; RAX = first operand
    mul qword [b]           ; RDX:RAX = RAX * [b]
    mov [result_low], rax   ; Store lower 64 bits
    mov [result_high], rdx  ; Store upper 64 bits
    
    ; Result = 0x0121FA00AD77D9B0:2B00A5AAF1C5DF10
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### `IMUL` - Signed Multiplication

`IMUL` has three forms with different capabilities:

#### Form 1: Single Operand (like MUL)

```nasm
; C equivalent:
; long long result = (long long)rax * (long long)operand;

imul operand    ; RDX:RAX = RAX * operand (signed)
```

Same behavior as `MUL` but treats operands as signed:

| Instruction | Operation |
|-------------|-----------|
| `imul r/m8` | `AX = AL * r/m8` |
| `imul r/m16` | `DX:AX = AX * r/m16` |
| `imul r/m32` | `EDX:EAX = EAX * r/m32` |
| `imul r/m64` | `RDX:RAX = RAX * r/m64` |

#### Form 2: Two Operands

```nasm
; C equivalent:
; dest = dest * src;

imul dest, src      ; dest = dest * src (signed, truncated to dest size)
```

- Result only in destination register (no double-width)
- **CF/OF** set if result doesn't fit in destination
- Most commonly used form for normal arithmetic

**Example:**

```nasm
section .data
    x dd -15
    y dd 7

section .text
    ; C equivalent:
    ; int result = x * y;  // -15 * 7 = -105
    
    mov eax, [x]        ; EAX = -15
    imul eax, [y]       ; EAX = -15 * 7 = -105
    ; Result: EAX = -105 (0xFFFFFF97)
```

#### Form 3: Three Operands

```nasm
; C equivalent:
; dest = src1 * immediate;

imul dest, src, immediate   ; dest = src * immediate
```

**Example:**

```nasm
; C equivalent:
; int result = x * 10;

mov eax, [x]
imul ebx, eax, 10       ; EBX = EAX * 10
```

### Complete Multiplication Example: Computing Area

```nasm
section .data
    width dd 1920
    height dd 1080
    area dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int area = width * height;  // 1920 * 1080 = 2,073,600
    
    mov eax, [width]        ; EAX = 1920
    imul eax, [height]      ; EAX = 1920 * 1080 = 2,073,600
    mov [area], eax         ; Store result
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Division Instructions

### `DIV` - Unsigned Division

```nasm
; C equivalent:
; unsigned long long dividend = (rdx << 64) | rax;
; rax = dividend / divisor;  // quotient
; rdx = dividend % divisor;  // remainder

div divisor
```

**Key Points:**
- **Dividend**: Double-width in `DX:AX/EDX:EAX/RDX:RAX`
- **Divisor**: Single operand (register or memory)
- **Quotient**: Stored in `AL/AX/EAX/RAX`
- **Remainder**: Stored in `AH/DX/EDX/RDX`

**Size Variants:**

| Instruction | Dividend | Divisor | Quotient | Remainder |
|-------------|----------|---------|----------|-----------|
| `div r/m8` | AX | r/m8 | AL | AH |
| `div r/m16` | DX:AX | r/m16 | AX | DX |
| `div r/m32` | EDX:EAX | r/m32 | EAX | EDX |
| `div r/m64` | RDX:RAX | r/m64 | RAX | RDX |

**Flags Affected:**
- All arithmetic flags are **undefined** after division

**Important: Zero the Upper Half!**

```nasm
; C equivalent:
; unsigned int quotient = dividend / divisor;

; WRONG - upper half contains garbage!
mov eax, [dividend]
div dword [divisor]     ; May cause #DE (divide error exception)!

; CORRECT - zero the upper half first
mov eax, [dividend]
xor edx, edx            ; Clear EDX (upper half)
div dword [divisor]     ; Now safe
```

**Example: Simple Division**

```nasm
section .data
    dividend dd 100
    divisor dd 7
    quotient dd 0
    remainder dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned int quotient = dividend / divisor;    // 100 / 7 = 14
    ; unsigned int remainder = dividend % divisor;   // 100 % 7 = 2
    
    mov eax, [dividend]     ; EAX = 100
    xor edx, edx            ; Clear EDX (no upper 32 bits)
    div dword [divisor]     ; EAX = quotient (14), EDX = remainder (2)
    
    mov [quotient], eax     ; Store quotient
    mov [remainder], edx    ; Store remainder
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### `IDIV` - Signed Division

```nasm
; C equivalent:
; long long dividend = (rdx << 64) | rax;  // Sign-extended!
; rax = dividend / divisor;  // quotient
; rdx = dividend % divisor;  // remainder

idiv divisor
```

Same operand structure as `DIV`, but treats operands as **signed** integers.

**Key Difference: Sign Extension!**

For signed division, you must **sign-extend** the dividend:

```nasm
; C equivalent:
; int quotient = dividend / divisor;

; 32-bit division
mov eax, [dividend]     ; EAX = dividend (32-bit signed)
cdq                     ; Sign-extend EAX into EDX:EAX
idiv dword [divisor]    ; Signed division

; 64-bit division
mov rax, [dividend]     ; RAX = dividend (64-bit signed)
cqo                     ; Sign-extend RAX into RDX:RAX
idiv qword [divisor]    ; Signed division
```

**Sign Extension Instructions:**

| Instruction | Operation | C Equivalent |
|-------------|-----------|--------------|
| `cbw` | AX = sign_extend(AL) | `short x = (char)al;` |
| `cwd` | DX:AX = sign_extend(AX) | `int x = (short)ax;` |
| `cdq` | EDX:EAX = sign_extend(EAX) | `long long x = (int)eax;` |
| `cqo` | RDX:RAX = sign_extend(RAX) | `__int128 x = (long)rax;` |

**Example: Signed Division**

```nasm
section .data
    dividend dd -100
    divisor dd 7
    quotient dd 0
    remainder dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int quotient = dividend / divisor;    // -100 / 7 = -14
    ; int remainder = dividend % divisor;   // -100 % 7 = -2
    
    mov eax, [dividend]     ; EAX = -100
    cdq                     ; EDX:EAX = sign-extend(-100)
    idiv dword [divisor]    ; EAX = -14, EDX = -2
    
    mov [quotient], eax     ; Store quotient
    mov [remainder], edx    ; Store remainder
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Practical Applications

### Example 1: Computing Average

```nasm
section .data
    numbers dd 15, 23, 42, 8, 31
    count dd 5
    average dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int sum = 0;
    ; for (int i = 0; i < count; ++i) {
    ;     sum += numbers[i];
    ; }
    ; int average = sum / count;
    
    ; Sum the array
    xor eax, eax            ; sum = 0
    xor ecx, ecx            ; i = 0
sum_loop:
    cmp ecx, [count]
    jge sum_done
    add eax, [numbers + ecx*4]
    inc ecx
    jmp sum_loop

sum_done:
    ; EAX now contains sum (119)
    
    ; Divide by count
    xor edx, edx            ; Clear upper half
    div dword [count]       ; EAX = 119 / 5 = 23
    mov [average], eax
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Example 2: Integer Square Root (Newton's Method)

```nasm
section .data
    n dd 144            ; Find sqrt(144)
    result dd 0

section .text
global _start

_start:
    ; C equivalent:
    ; int isqrt(int n) {
    ;     if (n == 0) return 0;
    ;     int x = n;
    ;     while (1) {
    ;         int x_new = (x + n / x) / 2;
    ;         if (x_new >= x) return x;
    ;         x = x_new;
    ;     }
    ; }
    
    mov ebx, [n]            ; n
    test ebx, ebx
    jz done                 ; if n == 0, result = 0
    
    mov eax, ebx            ; x = n (initial guess)
    
sqrt_loop:
    ; x_new = (x + n/x) / 2
    mov ecx, eax            ; Save x
    
    mov eax, ebx            ; EAX = n
    xor edx, edx
    div ecx                 ; EAX = n / x
    
    add eax, ecx            ; EAX = x + n/x
    shr eax, 1              ; EAX = (x + n/x) / 2 = x_new
    
    cmp eax, ecx            ; if x_new >= x
    jge sqrt_done
    
    jmp sqrt_loop
    
sqrt_done:
    mov eax, ecx            ; result = x
    
done:
    mov [result], eax       ; Store result (12)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Example 3: Convert Decimal to ASCII

```nasm
section .data
    number dd 12345
    buffer times 12 db 0    ; Room for digits + newline + null
    
section .text
global _start

_start:
    ; C equivalent:
    ; char buffer[12];
    ; int n = number;
    ; int i = 0;
    ; do {
    ;     buffer[i++] = '0' + (n % 10);
    ;     n /= 10;
    ; } while (n > 0);
    ; // Reverse buffer
    
    mov eax, [number]       ; EAX = number to convert
    lea rsi, [buffer + 11]  ; RSI = end of buffer
    mov byte [rsi], 10      ; Newline
    dec rsi
    
convert_loop:
    xor edx, edx            ; Clear remainder
    mov ecx, 10
    div ecx                 ; EAX = quotient, EDX = remainder
    
    add dl, '0'             ; Convert digit to ASCII
    mov [rsi], dl           ; Store digit
    dec rsi
    
    test eax, eax           ; More digits?
    jnz convert_loop
    
    ; Now print the string
    inc rsi                 ; Move back to first digit
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    lea rdx, [buffer + 12]
    sub rdx, rsi            ; Length = end - start
    syscall
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### Example 4: 64-bit × 64-bit = 128-bit Multiplication

```nasm
section .data
    ; Multiply two 64-bit numbers to get 128-bit result
    a dq 0xFFFFFFFFFFFFFFFF     ; Max 64-bit value
    b dq 0xFFFFFFFFFFFFFFFF     ; Max 64-bit value
    result_low dq 0
    result_high dq 0

section .text
global _start

_start:
    ; C equivalent:
    ; unsigned __int128 result = (unsigned __int128)a * (unsigned __int128)b;
    ; result_low = (unsigned long long)result;
    ; result_high = (unsigned long long)(result >> 64);
    
    mov rax, [a]            ; RAX = first operand
    mul qword [b]           ; RDX:RAX = RAX * [b]
    ; Result: RDX = 0xFFFFFFFFFFFFFFFE, RAX = 0x0000000000000001
    ; Because: 0xFFFF...FFFF * 0xFFFF...FFFF = 0xFFFE...0001
    
    mov [result_low], rax
    mov [result_high], rdx
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Common Pitfalls and Best Practices

### 1. Division by Zero

```nasm
; C equivalent:
; int safe_divide(int dividend, int divisor) {
;     if (divisor == 0) return -1;  // Error
;     return dividend / divisor;
; }

mov eax, [dividend]
mov ebx, [divisor]

test ebx, ebx           ; Check if divisor is zero
jz division_error       ; Handle error

xor edx, edx
div ebx                 ; Safe to divide

division_error:
    ; Handle error (set result to -1, etc.)
    mov eax, -1
```

### 2. Forgetting to Clear/Extend Upper Half

```nasm
; WRONG (unsigned):
mov eax, [dividend]
div dword [divisor]     ; EDX contains garbage!

; CORRECT (unsigned):
mov eax, [dividend]
xor edx, edx            ; Clear EDX
div dword [divisor]

; WRONG (signed):
mov eax, [dividend]
idiv dword [divisor]    ; EDX contains garbage!

; CORRECT (signed):
mov eax, [dividend]
cdq                     ; Sign-extend EAX into EDX:EAX
idiv dword [divisor]
```

### 3. Overflow Detection

```nasm
; C equivalent:
; bool multiply_overflows(int a, int b) {
;     long long result = (long long)a * b;
;     return result > INT_MAX || result < INT_MIN;
; }

mov eax, [a]
imul eax, [b]           ; EAX = a * b
jo overflow_occurred    ; Jump if overflow flag set

overflow_occurred:
    ; Handle overflow
```

### 4. Using the Right Instruction

```c
// Unsigned multiplication → MUL
unsigned int a, b, product;
product = a * b;

// Signed multiplication → IMUL
int a, b, product;
product = a * b;

// Unsigned division → DIV
unsigned int quotient = a / b;

// Signed division → IDIV
int quotient = a / b;
```

---

## Optimization Tips

### 1. Multiply by Powers of 2: Use Shifts

```nasm
; C equivalent:
; int result = x * 8;

; Slow:
imul eax, [x], 8

; Fast:
mov eax, [x]
shl eax, 3              ; x * 8 = x << 3
```

### 2. Divide by Powers of 2: Use Shifts

```nasm
; C equivalent (unsigned):
; unsigned int result = x / 4;

; Slow:
mov eax, [x]
xor edx, edx
mov ecx, 4
div ecx

; Fast:
mov eax, [x]
shr eax, 2              ; x / 4 = x >> 2
```

**Note**: Signed division by power of 2 requires rounding toward zero:

```nasm
; C equivalent (signed):
; int result = x / 4;

mov eax, [x]
cdq                     ; Sign extend
and edx, 3              ; Add (divisor - 1) if negative
add eax, edx            ; Adjust for rounding
sar eax, 2              ; Arithmetic shift right
```

### 3. Multiply by Constants: LEA Trick

```nasm
; C equivalent:
; int result = x * 5;

; Using IMUL:
imul eax, [x], 5

; Using LEA (faster):
mov eax, [x]
lea eax, [rax + rax*4]  ; EAX = x + x*4 = x*5
```

### 4. Reciprocal Multiplication

For repeated division by the same constant, use reciprocal multiplication:

```nasm
; C equivalent:
; // Instead of: result = x / 10
; // Use: result = (x * 0xCCCCCCCD) >> 35

mov eax, [x]
mov edx, 0xCCCCCCCD     ; Reciprocal of 10
mul edx                 ; EDX:EAX = x * reciprocal
shr edx, 3              ; Shift by (35 - 32) = 3
; EDX now contains x / 10
```

---

## Performance Characteristics

| Operation | Latency | Throughput | Notes |
|-----------|---------|------------|-------|
| `imul r32, r32` | 3 cycles | 1/cycle | Two-operand form |
| `imul r64, r64` | 3 cycles | 1/cycle | Two-operand form |
| `mul r32` | 3 cycles | 1/cycle | One-operand form |
| `mul r64` | 3 cycles | 1/cycle | One-operand form |
| `div r32` | 14-23 cycles | 6 cycles | Very slow! |
| `div r64` | 32-95 cycles | 20-40 cycles | Extremely slow! |
| `idiv r32` | 17-26 cycles | 6 cycles | Very slow! |
| `idiv r64` | 39-103 cycles | 20-40 cycles | Extremely slow! |

**Key Takeaways:**
- Multiplication is relatively fast (3 cycles)
- Division is **very slow** (20-100 cycles)
- Avoid division in tight loops when possible
- Use shifts, LEA, and reciprocal multiplication as alternatives

---

## Practice Exercises

### Exercise 1: Factorial

Write a function to calculate `n!` (factorial of n).

```nasm
; C equivalent:
; unsigned long long factorial(int n) {
;     unsigned long long result = 1;
;     for (int i = 2; i <= n; ++i) {
;         result *= i;
;     }
;     return result;
; }

section .data
    n dd 10
    result dq 0

section .text
global _start

_start:
    ; Your code here
    ; Calculate factorial of n and store in result
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

<details>
<summary>Solution</summary>

```nasm
section .data
    n dd 10
    result dq 0

section .text
global _start

_start:
    mov rax, 1              ; result = 1
    mov ecx, 2              ; i = 2
    
factorial_loop:
    cmp ecx, [n]
    jg factorial_done
    
    imul rax, rcx           ; result *= i
    inc ecx
    jmp factorial_loop
    
factorial_done:
    mov [result], rax       ; result = 3,628,800
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```
</details>

### Exercise 2: GCD (Greatest Common Divisor)

Implement Euclid's algorithm to find GCD of two numbers.

```nasm
; C equivalent:
; int gcd(int a, int b) {
;     while (b != 0) {
;         int temp = b;
;         b = a % b;
;         a = temp;
;     }
;     return a;
; }

section .data
    a dd 48
    b dd 18
    result dd 0

section .text
global _start

_start:
    ; Your code here
    ; Calculate GCD and store in result
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

<details>
<summary>Solution</summary>

```nasm
section .data
    a dd 48
    b dd 18
    result dd 0

section .text
global _start

_start:
    mov eax, [a]            ; EAX = a
    mov ebx, [b]            ; EBX = b
    
gcd_loop:
    test ebx, ebx           ; while (b != 0)
    jz gcd_done
    
    xor edx, edx            ; Clear remainder
    div ebx                 ; EDX = a % b
    
    mov eax, ebx            ; a = b
    mov ebx, edx            ; b = remainder
    jmp gcd_loop
    
gcd_done:
    mov [result], eax       ; result = 6
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```
</details>

### Exercise 3: Check if Number is Prime

```nasm
; C equivalent:
; bool is_prime(int n) {
;     if (n <= 1) return false;
;     if (n <= 3) return true;
;     if (n % 2 == 0 || n % 3 == 0) return false;
;     for (int i = 5; i * i <= n; i += 6) {
;         if (n % i == 0 || n % (i + 2) == 0)
;             return false;
;     }
;     return true;
; }

section .data
    n dd 97
    is_prime db 0       ; 1 = prime, 0 = not prime

section .text
global _start

_start:
    ; Your code here
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Summary

### Multiplication
- **`MUL`**: Unsigned, double-width result in `DX:AX/EDX:EAX/RDX:RAX`
- **`IMUL`** (1-operand): Signed, double-width result
- **`IMUL`** (2-operand): Signed, single register result (most common)
- **`IMUL`** (3-operand): Signed with immediate value

### Division
- **`DIV`**: Unsigned, requires zeroing upper half (`xor edx, edx`)
- **`IDIV`**: Signed, requires sign-extending (`cdq` or `cqo`)
- **Quotient**: In `AL/AX/EAX/RAX`
- **Remainder**: In `AH/DX/EDX/RDX`

### Key Concepts
1. Always prepare upper register before division
2. Check for division by zero
3. Use appropriate signed/unsigned instruction
4. Division is slow - optimize when possible
5. CF/OF indicate multiplication overflow

### Optimization
- Use **shifts** for powers of 2
- Use **LEA** for simple multiplications (3x, 5x, 9x)
- Use **reciprocal multiplication** for repeated divisions
- Avoid division in hot loops

---

## Next Topic

In **Topic 14: Shifts & Rotates (Advanced)**, we'll dive deeper into bit manipulation with shifts, rotates, and their applications in optimization, bitfields, and low-level programming.

**Preview:**
- Logical vs arithmetic shifts
- Rotate operations
- Multi-precision arithmetic
- Bit extraction and manipulation
- Performance optimization techniques

