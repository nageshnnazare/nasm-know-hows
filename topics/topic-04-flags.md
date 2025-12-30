# 📘 Topic 4: Flags & Comparisons

Understanding the CPU's status flags - the foundation of conditional logic.

---

## **Overview**

The **FLAGS register** (RFLAGS in 64-bit) is a special register that contains individual bit flags indicating the results of operations. These flags are how the CPU remembers what happened in the last operation, enabling conditional execution.

**Why flags matter:**
- 🎯 Enable conditional jumps (if/else logic)
- 🔍 Detect overflow, carry, and errors
- 🔄 Control loops and comparisons
- ⚡ Essential for all control flow

---

## **Part 1: The RFLAGS Register**

### **RFLAGS Structure (64-bit)**

```
Bit:   63-21  20  19  18-12  11  10   9   8   7   6   5   4   3   2   1   0
       ─────  ──  ──  ─────  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──  ──
         │    │   │     │    │   │   │   │   │   │   │   │   │   │   │   │
         │    │   │     │    │   │   │   │   │   │   │   │   │   │   │   └─ CF  Carry
         │    │   │     │    │   │   │   │   │   │   │   │   │   │   └───── (1 - Reserved)
         │    │   │     │    │   │   │   │   │   │   │   │   │   └───────── PF  Parity
         │    │   │     │    │   │   │   │   │   │   │   │   └───────────── (3 - Reserved)
         │    │   │     │    │   │   │   │   │   │   │   └───────────────── AF  Adjust
         │    │   │     │    │   │   │   │   │   │   └───────────────────── (5 - Reserved)
         │    │   │     │    │   │   │   │   │   └───────────────────────── ZF  Zero
         │    │   │     │    │   │   │   │   └───────────────────────────── SF  Sign
         │    │   │     │    │   │   │   └───────────────────────────────── TF  Trap
         │    │   │     │    │   │   └───────────────────────────────────── IF  Interrupt Enable
         │    │   │     │    │   └───────────────────────────────────────── DF  Direction
         │    │   │     │    └───────────────────────────────────────────── OF  Overflow
         │    │   │     └────────────────────────────────────────────────── (12-18 - Reserved)
         │    │   └──────────────────────────────────────────────────────── RF  Resume
         │    └──────────────────────────────────────────────────────────── VM  Virtual 8086
         └───────────────────────────────────────────────────────────────── (21-63 - Reserved/System)
```

### **The Six Arithmetic Flags (Most Important)**

```
┌──────┬──────────────┬─────────────────────────────────────┐
│ Flag │ Name         │ Purpose                             │
├──────┼──────────────┼─────────────────────────────────────┤
│  CF  │ Carry        │ Unsigned overflow/borrow            │
│  ZF  │ Zero         │ Result is zero                      │
│  SF  │ Sign         │ Result is negative (bit 7/15/31/63) │
│  OF  │ Overflow     │ Signed overflow                     │
│  PF  │ Parity       │ Even number of 1-bits in low byte   │
│  AF  │ Auxiliary    │ BCD arithmetic carry (bit 3->4)     │
└──────┴──────────────┴─────────────────────────────────────┘
```

---

## **Part 2: Individual Flags Explained**

### **CF - Carry Flag (Bit 0)**

**Set when:** Unsigned arithmetic overflow/borrow occurs

**Use cases:**
- Unsigned comparison (above/below)
- Detecting overflow in addition
- Detecting borrow in subtraction
- Multi-precision arithmetic

**Examples:**

```nasm
; Addition overflow
mov al, 255
add al, 1               ; AL = 0, CF = 1 (carried out)

; No overflow
mov al, 100
add al, 50              ; AL = 150, CF = 0

; Subtraction borrow
mov al, 5
sub al, 10              ; AL = 251 (wraps), CF = 1 (borrowed)

; Checking if unsigned number is bigger
mov rax, 100
sub rax, 200            ; CF = 1 (100 < 200, borrow occurred)
jc less_than            ; Jump if carry (below)
```

**Affected by:** ADD, SUB, ADC, SBB, shifts, rotates  
**Not affected by:** INC, DEC

---

### **ZF - Zero Flag (Bit 6)**

**Set when:** Result of operation is zero

**Use cases:**
- Equality testing
- Loop termination
- Null checks

**Examples:**

```nasm
; Zero result
mov rax, 10
sub rax, 10             ; RAX = 0, ZF = 1

; Non-zero result
mov rax, 10
sub rax, 5              ; RAX = 5, ZF = 0

; Testing for zero
test rax, rax           ; ZF = 1 if RAX = 0
jz is_zero              ; Jump if zero

; Equality check
cmp rax, rbx            ; Compare by subtraction
je equal                ; Jump if equal (ZF = 1)

; Loop until zero
mov rcx, 10
loop_start:
    ; ... do work ...
    dec rcx             ; Decrement
    jnz loop_start      ; Jump if not zero
```

**Affected by:** Most arithmetic and logical operations  
**Set by:** Any operation producing zero result

---

### **SF - Sign Flag (Bit 7)**

**Set when:** Most significant bit (MSB) of result is 1

**Use cases:**
- Checking if signed number is negative
- Signed comparisons

**Examples:**

```nasm
; Positive result
mov al, 50
add al, 20              ; AL = 70 (0x46), SF = 0 (bit 7 = 0)

; Negative result (two's complement)
mov al, 10
sub al, 20              ; AL = -10 (0xF6), SF = 1 (bit 7 = 1)

; Check if negative
test rax, rax           ; Sets SF based on MSB
js is_negative          ; Jump if sign (negative)

; Signed comparison
mov rax, -5
cmp rax, 10             ; RAX - 10 = negative
jl less_than            ; Jump if less (SF != OF)
```

**Affected by:** Most arithmetic and logical operations  
**Simply:** SF = bit 7 (8-bit), bit 15 (16-bit), bit 31 (32-bit), bit 63 (64-bit)

---

### **OF - Overflow Flag (Bit 11)**

**Set when:** Signed arithmetic overflow occurs

**Use cases:**
- Detecting signed overflow
- Signed comparisons

**Examples:**

```nasm
; Signed overflow (positive + positive = negative)
mov al, 127             ; Maximum signed 8-bit value
add al, 1               ; AL = -128 (0x80), OF = 1, SF = 1

; No overflow
mov al, 100
add al, 20              ; AL = 120, OF = 0

; Signed overflow (negative + negative = positive)
mov al, -128            ; Minimum signed 8-bit value
sub al, 1               ; AL = 127 (0x7F), OF = 1, SF = 0

; Detect overflow
mov ax, 32767           ; Max signed 16-bit
add ax, 1               ; AX = -32768, OF = 1
jo overflow_occurred    ; Jump if overflow
```

**Key insight:** OF tells you if the sign bit is wrong for signed arithmetic

**Affected by:** ADD, SUB, NEG, arithmetic shifts  
**Not affected by:** Logical operations (AND, OR, XOR)

---

### **PF - Parity Flag (Bit 2)**

**Set when:** Low byte of result has even number of 1-bits

**Use cases:**
- Error detection (rarely used in modern code)
- Serial communication parity checks

**Examples:**

```nasm
; Even parity (even number of 1-bits)
mov al, 0b00000011      ; Two 1-bits (even)
test al, al             ; PF = 1

; Odd parity
mov al, 0b00000111      ; Three 1-bits (odd)
test al, al             ; PF = 0

; Only low byte matters!
mov ax, 0xFF00
test ax, ax             ; PF = 1 (low byte = 0x00, zero 1-bits = even)
```

**Rarely used** in typical assembly programming.

---

### **AF - Auxiliary Carry Flag (Bit 4)**

**Set when:** Carry/borrow from bit 3 to bit 4 (low nibble to high nibble)

**Use cases:**
- BCD (Binary Coded Decimal) arithmetic
- Rarely used in modern programming

**Examples:**

```nasm
; Auxiliary carry
mov al, 0x0F            ; 0000 1111
add al, 0x01            ; 0001 0000, AF = 1 (carry from bit 3->4)

; No auxiliary carry
mov al, 0x07            ; 0000 0111
add al, 0x01            ; 0000 1000, AF = 0
```

**Rarely used** except in BCD operations.

---

## **Part 3: Flags and Instructions**

### **Which Instructions Affect Which Flags?**

```
┌─────────────────┬────┬────┬────┬────┬────┬────┐
│ Instruction     │ CF │ ZF │ SF │ OF │ PF │ AF │
├─────────────────┼────┼────┼────┼────┼────┼────┤
│ ADD, SUB        │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
│ INC, DEC        │ -  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
│ NEG             │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
│ MUL, IMUL (1op) │ ✓* │ -  │ ?  │ ✓* │ ?  │ ?  │
│ DIV, IDIV       │ ?  │ ?  │ ?  │ ?  │ ?  │ ?  │
│ AND, OR, XOR    │ 0  │ ✓  │ ✓  │ 0  │ ✓  │ ?  │
│ NOT             │ -  │ -  │ -  │ -  │ -  │ -  │
│ TEST            │ 0  │ ✓  │ ✓  │ 0  │ ✓  │ ?  │
│ CMP             │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │ ✓  │
│ SHL, SHR        │ ✓  │ ✓  │ ✓  │ ✓* │ ✓  │ ?  │
│ SAL, SAR        │ ✓  │ ✓  │ ✓  │ ✓* │ ✓  │ ?  │
│ ROL, ROR        │ ✓  │ -  │ -  │ ✓* │ -  │ -  │
│ MOV             │ -  │ -  │ -  │ -  │ -  │ -  │
│ LEA             │ -  │ -  │ -  │ -  │ -  │ -  │
│ PUSH, POP       │ -  │ -  │ -  │ -  │ -  │ -  │
└─────────────────┴────┴────┴────┴────┴────┴────┘

Legend:
✓ = Modified       - = Not affected
0 = Cleared        ? = Undefined
✓* = Special behavior
```

### **Important Notes**

```nasm
; INC/DEC don't affect CF!
mov al, 255
inc al                  ; AL = 0, but CF unchanged!
; This is different from ADD:
mov al, 255
add al, 1               ; AL = 0, CF = 1

; AND/OR/XOR clear CF and OF
mov al, 0xFF
and al, 0x01            ; CF = 0, OF = 0, ZF = 0, SF = 0

; MOV and LEA don't affect any flags
mov rax, rbx            ; Flags unchanged
lea rax, [rbx + 10]     ; Flags unchanged
```

---

## **Part 4: The CMP Instruction**

**CMP** is specifically designed for comparisons. It performs subtraction but doesn't store the result.

```nasm
cmp operand1, operand2  ; Performs: operand1 - operand2
                        ; Sets flags, doesn't store result
```

### **How CMP Works**

```nasm
; Example: cmp rax, rbx
; Internally does: temp = rax - rbx
; Sets flags based on temp
; Throws away temp (doesn't modify rax or rbx)

cmp rax, 10             ; Compare RAX with 10
; If RAX = 10: ZF = 1 (equal)
; If RAX > 10: SF = 0, ZF = 0 (greater)
; If RAX < 10: SF = 1, ZF = 0 (less)
```

### **CMP Examples**

```nasm
; Equality check
mov rax, 42
cmp rax, 42             ; RAX - 42 = 0, ZF = 1
je equal                ; Jump if equal (ZF = 1)

; Not equal
cmp rax, 100            ; RAX - 100 = -58, ZF = 0
jne not_equal           ; Jump if not equal (ZF = 0)

; Greater than (signed)
mov rax, 50
cmp rax, 10             ; RAX - 10 = 40 (positive)
jg greater              ; Jump if greater (SF = OF and ZF = 0)

; Less than (signed)
mov rax, -5
cmp rax, 10             ; RAX - 10 = -15 (negative)
jl less                 ; Jump if less (SF != OF)

; Unsigned comparisons
mov rax, 100
cmp rax, 200            ; RAX - 200, CF = 1 (borrow)
jb below                ; Jump if below (CF = 1)
```

---

## **Part 5: The TEST Instruction**

**TEST** performs AND but doesn't store the result - only sets flags.

```nasm
test operand1, operand2 ; Performs: operand1 & operand2
                        ; Sets flags, doesn't store result
```

### **How TEST Works**

```nasm
; Example: test rax, rax
; Internally does: temp = rax & rax
; Result is always rax (X & X = X)
; Sets ZF = 1 if rax = 0, ZF = 0 otherwise
```

### **Common TEST Patterns**

```nasm
; Check if zero (most common!)
test rax, rax           ; ZF = 1 if RAX = 0
jz is_zero              ; Jump if zero

; Check specific bit
test al, 0x01           ; Check bit 0
jnz bit0_is_set

test al, 0x80           ; Check bit 7 (sign bit for byte)
jnz bit7_is_set

; Check if negative (for signed numbers)
test rax, rax           ; Sets SF based on MSB
js is_negative          ; Jump if sign flag set

; Check multiple bits
test al, 0b11110000     ; Check if any upper 4 bits are set
jnz has_upper_bits

; Even/odd check
test rax, 1             ; Check bit 0
jz is_even              ; Jump if zero (bit 0 = 0)
jnz is_odd              ; Jump if not zero (bit 0 = 1)
```

### **TEST vs AND**

```nasm
; Using AND (modifies operand)
mov al, 0xFF
and al, 0x0F            ; AL = 0x0F (destroyed original value!)

; Using TEST (doesn't modify)
mov al, 0xFF
test al, 0x0F           ; AL still = 0xFF, flags set
; Now you can use AL again without reloading
```

**When to use TEST:**
- ✅ Checking conditions without modifying data
- ✅ More readable intent (testing, not masking)
- ✅ Shorter encoding in some cases

**When to use AND:**
- ✅ When you need the result of the AND operation
- ✅ Masking/clearing bits

---

## **Part 6: Reading Flag Combinations**

Conditional jumps test flag combinations. Understanding these is crucial!

### **Equality (ZF only)**

```nasm
cmp rax, rbx
je equal                ; Jump if ZF = 1
jne not_equal           ; Jump if ZF = 0

; Works for both signed and unsigned!
```

### **Signed Comparisons (SF and OF matter)**

```nasm
cmp rax, rbx            ; Compare signed numbers

jg greater              ; Jump if (ZF = 0) AND (SF = OF)
jge greater_equal       ; Jump if (SF = OF)
jl less                 ; Jump if (SF != OF)
jle less_equal          ; Jump if (ZF = 1) OR (SF != OF)
```

**Why SF and OF?**
```
If no overflow (OF = 0):
  SF = 0 means result positive (A > B)
  SF = 1 means result negative (A < B)

If overflow (OF = 1):
  Signs are flipped!
  SF = 0 means result was supposed to be negative (A < B)
  SF = 1 means result was supposed to be positive (A > B)

So: SF != OF means A < B
    SF = OF means A >= B
```

### **Unsigned Comparisons (CF matters)**

```nasm
cmp rax, rbx            ; Compare unsigned numbers

ja above                ; Jump if (CF = 0) AND (ZF = 0)
jae above_equal         ; Jump if (CF = 0)
jb below                ; Jump if (CF = 1)
jbe below_equal         ; Jump if (CF = 1) OR (ZF = 1)
```

**Why CF?**
```
If borrow occurred (CF = 1): A < B (had to borrow)
If no borrow (CF = 0): A >= B
```

---

## **Part 7: Practical Flag Examples**

### **Example 1: Zero Check**

```nasm
; Method 1: CMP
cmp rax, 0
je is_zero

; Method 2: TEST (better!)
test rax, rax
jz is_zero

; Method 3: OR (also works)
or rax, rax             ; Doesn't change RAX, sets ZF
jz is_zero
```

### **Example 2: Range Check (10 <= x <= 20)**

**C Equivalent:**
```c
#include <stdint.h>
#include <stdbool.h>

bool in_range_method1(int64_t x) {
    // Method 1: Two comparisons
    if (x < 10) return false;
    if (x > 20) return false;
    return true;  // In range!
}

bool in_range_method2(uint64_t x) {
    // Method 2: Subtract lower bound (unsigned trick)
    uint64_t adjusted = x - 10;
    if (adjusted > 10) return false;  // Unsigned comparison
    return true;
}

int main() {
    int64_t value = 15;
    if (in_range_method1(value)) {
        // In range
    }
    return 0;
}
```

**Assembly:**
```nasm
; Check if RAX is in range [10, 20]

; Method 1: Two comparisons
cmp rax, 10
jl out_of_range         ; RAX < 10
cmp rax, 20
jg out_of_range         ; RAX > 20
; In range!

; Method 2: Subtract lower bound
sub rax, 10             ; Adjust range to [0, 10]
cmp rax, 10
ja out_of_range         ; Unsigned: above 10 means out of range
add rax, 10             ; Restore original value
```

### **Example 3: Sign Check**

**C Equivalent:**
```c
#include <stdint.h>

void check_sign(int64_t value) {
    if (value < 0) {
        // Handle negative
    } else if (value == 0) {
        // Handle zero
    } else {
        // Handle positive (value > 0)
    }
}

int main() {
    int64_t x = -5;
    check_sign(x);
    return 0;
}
```

**Assembly:**
```nasm
; Check if RAX is negative, zero, or positive

test rax, rax
js negative             ; SF = 1, RAX < 0
jz zero                 ; ZF = 1, RAX = 0
; Otherwise RAX > 0

negative:
    ; Handle negative
    jmp done
zero:
    ; Handle zero
    jmp done
; Positive case
done:
```

### **Example 4: Overflow Detection**

**C Equivalent:**
```c
#include <stdint.h>
#include <stdbool.h>
#include <limits.h>

bool add_with_overflow_check(int16_t a, int16_t b, int16_t *result) {
    int32_t temp = (int32_t)a + (int32_t)b;
    *result = (int16_t)temp;
    
    // Check if overflow occurred
    if (temp > INT16_MAX || temp < INT16_MIN) {
        return true;  // Overflow detected
    }
    return false;  // No overflow
}

int main() {
    int16_t result;
    
    // No overflow
    bool overflow1 = add_with_overflow_check(32000, 1000, &result);
    // overflow1 = true (33000 > 32767)
    
    // Overflow
    bool overflow2 = add_with_overflow_check(32767, 1, &result);
    // overflow2 = true, result = -32768
    
    return 0;
}
```

**Assembly:**
```nasm
; Detect signed overflow in addition
mov ax, 32000
add ax, 1000            ; Result = 33000 (in range)
jo overflow             ; OF = 0, no jump

mov ax, 32767           ; Max signed 16-bit
add ax, 1               ; Result = -32768 (overflow!)
jo overflow             ; OF = 1, jump taken

overflow:
    ; Handle overflow
```

### **Example 5: Carry Chain (Multi-Precision)**

**C Equivalent:**
```c
#include <stdint.h>

typedef struct {
    uint64_t low;
    uint64_t high;
} uint128_t;

uint128_t add128(uint128_t a, uint128_t b) {
    uint128_t result;
    
    // Add low 64 bits
    result.low = a.low + b.low;
    
    // Check if carry occurred (overflow from low addition)
    uint64_t carry = (result.low < a.low) ? 1 : 0;
    
    // Add high 64 bits + carry
    result.high = a.high + b.high + carry;
    
    return result;
}

int main() {
    uint128_t num1 = {0xFFFFFFFFFFFFFFFFULL, 0x1234567890ABCDEFULL};
    uint128_t num2 = {0x0000000000000001ULL, 0x0000000000000001ULL};
    uint128_t result = add128(num1, num2);
    // result.low = 0, result.high = 0x1234567890ABCDF1
    return 0;
}
```

**Assembly:**
```nasm
; Add two 128-bit numbers
; Number1 = RDX:RAX (high:low)
; Number2 = RBX:RCX (high:low)

add rax, rcx            ; Add low 64 bits, may set CF
adc rdx, rbx            ; Add high 64 bits + carry

; Result in RDX:RAX
```

### **Example 6: Parity Check**

```nasm
; Check if byte has even parity
mov al, 0b10110101      ; 5 ones (odd parity)
test al, al             ; Set PF
jp even_parity          ; Jump if PF = 1 (even number of 1s)
; Odd parity

even_parity:
    ; Even parity handling
```

---

## **Part 8: Flag Manipulation Instructions**

### **Direct Flag Control**

```nasm
; Clear carry flag
clc                     ; CF = 0

; Set carry flag
stc                     ; CF = 1

; Complement carry flag
cmc                     ; CF = !CF

; Clear direction flag (for string operations)
cld                     ; DF = 0 (forward)

; Set direction flag
std                     ; DF = 1 (backward)
```

### **Save/Restore Flags**

```nasm
; Save flags on stack
pushf                   ; Push FLAGS (16-bit)
pushfq                  ; Push RFLAGS (64-bit)

; Restore flags from stack
popf                    ; Pop FLAGS (16-bit)
popfq                   ; Pop RFLAGS (64-bit)

; Example: Preserve flags across operation
pushfq
; ... operations that modify flags ...
popfq                   ; Restore original flags
```

### **Load Flags**

```nasm
; Load AH from FLAGS (legacy, rarely used)
lahf                    ; AH = SF:ZF:0:AF:0:PF:1:CF

; Store AH to FLAGS (legacy, rarely used)
sahf                    ; FLAGS = AH (some bits)
```

---

## **Part 9: Common Patterns and Idioms**

### **Pattern 1: Boolean to Integer**

```nasm
; Convert boolean condition to 0/1

; Method 1: Using SETcc
cmp rax, rbx
setg al                 ; AL = 1 if RAX > RBX, else AL = 0

; Method 2: Using jumps
xor ecx, ecx            ; ECX = 0
cmp rax, rbx
jle skip
mov ecx, 1
skip:
```

### **Pattern 2: Max/Min**

```nasm
; max(rax, rbx) -> rax
cmp rax, rbx
jge already_max         ; RAX >= RBX, already maximum
mov rax, rbx            ; RBX is bigger
already_max:

; min(rax, rbx) -> rax
cmp rax, rbx
jle already_min         ; RAX <= RBX, already minimum
mov rax, rbx            ; RBX is smaller
already_min:

; Or use CMOVcc (conditional move)
cmp rax, rbx
cmovl rax, rbx          ; If RAX < RBX, RAX = RBX (min)
cmovg rax, rbx          ; If RAX > RBX, RAX = RBX (max)
```

### **Pattern 3: Abs (Absolute Value)**

```nasm
; abs(rax) using flags
test rax, rax
jns already_positive    ; Jump if not sign (positive)
neg rax
already_positive:

; Branchless absolute value (for EAX)
mov edx, eax
sar edx, 31             ; EDX = all 1s if negative, 0 if positive
xor eax, edx
sub eax, edx            ; EAX = abs(EAX)
```

### **Pattern 4: Conditional Assignment**

```nasm
; if (rax > 10) rax = 100; else rax = 0;

cmp rax, 10
jle else_branch
    mov rax, 100
    jmp end_if
else_branch:
    xor rax, rax
end_if:

; Or with conditional move
mov rcx, 100
xor rdx, rdx
cmp rax, 10
cmovg rax, rcx          ; If RAX > 10, RAX = 100
cmovle rax, rdx         ; If RAX <= 10, RAX = 0
```

---

## **Part 10: Debugging with Flags**

### **Viewing Flags in GDB**

```bash
# Run program in GDB
gdb ./program

# View all registers including flags
(gdb) info registers

# View just RFLAGS
(gdb) print $eflags

# View flags in binary
(gdb) print/t $eflags

# Common flag abbreviations in GDB output:
# CF PF AF ZF SF TF IF DF OF
```

### **GDB Flag Display**

```
RFLAGS: 0x246 [ PF ZF IF ]

Flags shown if set:
CF - carry
PF - parity
AF - auxiliary
ZF - zero
SF - sign
TF - trap
IF - interrupt enable
DF - direction
OF - overflow
```

### **Manual Flag Testing**

```nasm
section .text
    global _start

_start:
    ; Test various flag conditions
    
    ; Set CF
    mov al, 255
    add al, 1               ; CF = 1
    ; Now run in debugger and check
    
    ; Set ZF
    xor rax, rax            ; ZF = 1
    
    ; Set SF
    mov al, 200
    add al, 100             ; SF = 1 (result = -56 in signed)
    
    ; Set OF
    mov al, 127
    add al, 1               ; OF = 1 (signed overflow)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## **✅ Practice Exercises**

### **Exercise 1: Predict Flags**

```nasm
mov al, 150
add al, 150
```

What are CF, ZF, SF, OF?

<details>
<summary>Solution</summary>

```
150 + 150 = 300 (0x12C)
AL stores only 8 bits: 0x2C = 44

CF = 1 (unsigned overflow, 300 > 255)
ZF = 0 (result is 44, not zero)
SF = 0 (bit 7 of 0x2C = 0)
OF = 1 (signed: 150+150 should be positive but looks negative in 8-bit)

Wait, let's recalculate:
150 in 8-bit signed = -106
-106 + -106 = -212
In 8-bit: 44 (should be negative but isn't)
OF = 1 (signed overflow)

Actually 150 = 0x96 = 1001 0110 (negative in signed: -106)
300 = 0x12C, truncated to 8-bit = 0x2C = 44 (positive)
OF = 1 because two negatives gave positive
```
</details>

### **Exercise 2: Write Comparison**

Write code to check if RAX is in the range [-10, 10] (inclusive, signed).

<details>
<summary>Solution</summary>

```nasm
cmp rax, -10
jl out_of_range         ; RAX < -10
cmp rax, 10
jg out_of_range         ; RAX > 10
; In range [-10, 10]

out_of_range:
    ; Handle out of range
```
</details>

### **Exercise 3: Flag Logic**

After these instructions, which conditional jumps will be taken?

```nasm
mov al, 10
sub al, 10
je target1              ; ?
jg target2              ; ?
js target3              ; ?
```

<details>
<summary>Solution</summary>

```
sub al, 10: AL = 0

ZF = 1 (result is zero)
SF = 0 (result is positive/zero)
OF = 0 (no signed overflow)

je target1  → TAKEN (ZF = 1)
jg target2  → NOT TAKEN (ZF = 1, need ZF = 0 for greater)
js target3  → NOT TAKEN (SF = 0, need SF = 1 for negative)
```
</details>

### **Exercise 4: Implement Sign Function**

Implement sign(x): returns -1 if x < 0, 0 if x = 0, 1 if x > 0

<details>
<summary>Solution</summary>

```nasm
; Input: RAX
; Output: RAX = sign(RAX)

test rax, rax
js negative
jz zero
; Positive
mov rax, 1
jmp done

negative:
mov rax, -1
jmp done

zero:
xor rax, rax

done:
```
</details>

### **Exercise 5: Overflow Check**

Write code that adds two signed 64-bit numbers and detects overflow.

<details>
<summary>Solution</summary>

```nasm
; Add RAX and RBX, check overflow
add rax, rbx
jo overflow_occurred

; No overflow, continue normally
jmp no_overflow

overflow_occurred:
    ; Handle overflow
    ; Could saturate, return error, etc.

no_overflow:
    ; Result in RAX is valid
```
</details>

---

## **📋 Quick Reference**

### **The Six Main Flags**

```
CF (Carry)    - Unsigned overflow/borrow
ZF (Zero)     - Result is zero
SF (Sign)     - Result is negative (MSB = 1)
OF (Overflow) - Signed overflow
PF (Parity)   - Even number of 1-bits in low byte
AF (Aux)      - BCD carry (bit 3→4)
```

### **Flag Interpretation**

```nasm
; After: cmp rax, rbx (equivalent to rax - rbx)

ZF = 1           → rax == rbx
ZF = 0           → rax != rbx

SF = OF          → rax >= rbx (signed)
SF != OF         → rax < rbx (signed)

CF = 0           → rax >= rbx (unsigned)
CF = 1           → rax < rbx (unsigned)

ZF=0 && SF=OF    → rax > rbx (signed)
ZF=0 && CF=0     → rax > rbx (unsigned)
```

### **Common Checks**

```nasm
test rax, rax ; Zero check (best)
test rax, 1   ; Check bit 0 (even/odd)
test rax, rax ; Negative check (use js)
cmp rax, rbx  ; Comparison
```

---

## **🎯 Knowledge Check**

Before moving to Topic 5, verify you understand:
- ✅ Purpose of each flag (CF, ZF, SF, OF, PF, AF)
- ✅ Which instructions affect which flags
- ✅ How CMP works (subtraction without storing)
- ✅ How TEST works (AND without storing)
- ✅ Signed vs unsigned comparisons
- ✅ Reading flag combinations
- ✅ When to use TEST vs CMP vs AND

---

**🎉 Excellent!** You now understand CPU flags and comparisons!

**Next:** [Topic 5: Conditional Jumps](topic-05-jumps.md) (coming soon)

---

[← Previous Topic](topic-03-basic-instructions.md) | [Back to Main](../README.md) | Next Topic →

