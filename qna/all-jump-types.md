# All Types of Jumps in Assembly

## Overview

Jumps are the fundamental control flow instructions in assembly. They change the instruction pointer (RIP/EIP) to alter program execution flow. This guide covers **every type of jump** available in x86-64 assembly.

```c
// C equivalent concepts:
if (x > 5) { }      // Conditional jump
goto label;         // Unconditional jump
for (;;) { }        // Loop with jump
switch (x) { }      // Jump table
function();         // Function call (special jump)
```

---

## 1. Unconditional Jumps

### `JMP` - Jump Always

Transfers control unconditionally to the target address.

```nasm
; C equivalent:
; goto target;

jmp target              ; Always jump to target

target:
    ; execution continues here
```

**Forms:**

```nasm
; Direct jump (relative)
jmp label               ; Most common - PC-relative

; Indirect jump (register)
jmp rax                 ; Jump to address in RAX

; Indirect jump (memory)
jmp [table + rbx*8]     ; Jump to address stored in memory

; Far jump (segment:offset)
jmp 0x08:offset         ; Change code segment (rarely used in 64-bit)
```

**Example: Skip code section**

```nasm
section .text
    ; C equivalent:
    ; if (condition) {
    ;     goto skip_dangerous;
    ; }
    ; dangerous_code();
    ; skip_dangerous:
    ; safe_code();
    
    cmp rax, 0
    je skip_dangerous       ; Conditional jump
    
    ; Dangerous code here
    call dangerous_function
    
skip_dangerous:
    ; Safe code continues
    mov rbx, 42
```

---

## 2. Conditional Jumps (Signed Comparisons)

Based on **signed** integer comparison results.

### After `CMP a, b` (signed):

| Instruction | Condition | Flags | Meaning | C Equivalent |
|-------------|-----------|-------|---------|--------------|
| `JE` / `JZ` | Equal / Zero | ZF=1 | a == b | `if (a == b)` |
| `JNE` / `JNZ` | Not Equal / Not Zero | ZF=0 | a != b | `if (a != b)` |
| `JG` / `JNLE` | Greater / Not Less or Equal | ZF=0 AND SF=OF | a > b | `if (a > b)` |
| `JGE` / `JNL` | Greater or Equal / Not Less | SF=OF | a >= b | `if (a >= b)` |
| `JL` / `JNGE` | Less / Not Greater or Equal | SF≠OF | a < b | `if (a < b)` |
| `JLE` / `JNG` | Less or Equal / Not Greater | ZF=1 OR SF≠OF | a <= b | `if (a <= b)` |

**Example:**

```nasm
section .data
    x dd -10
    y dd 5

section .text
    ; C equivalent:
    ; int x = -10, y = 5;
    ; if (x < y) {
    ;     // x is less than y (signed)
    ; }
    
    mov eax, [x]        ; EAX = -10 (signed)
    cmp eax, [y]        ; Compare -10 vs 5
    jl x_is_less        ; Jump if less (signed)
    
    ; x >= y path
    jmp done
    
x_is_less:
    ; x < y path (this executes)
    
done:
```

---

## 3. Conditional Jumps (Unsigned Comparisons)

Based on **unsigned** integer comparison results.

### After `CMP a, b` (unsigned):

| Instruction | Condition | Flags | Meaning | C Equivalent |
|-------------|-----------|-------|---------|--------------|
| `JE` / `JZ` | Equal / Zero | ZF=1 | a == b | `if (a == b)` |
| `JNE` / `JNZ` | Not Equal / Not Zero | ZF=0 | a != b | `if (a != b)` |
| `JA` / `JNBE` | Above / Not Below or Equal | CF=0 AND ZF=0 | a > b | `if ((unsigned)a > b)` |
| `JAE` / `JNB` / `JNC` | Above or Equal / Not Below / No Carry | CF=0 | a >= b | `if ((unsigned)a >= b)` |
| `JB` / `JNAE` / `JC` | Below / Not Above or Equal / Carry | CF=1 | a < b | `if ((unsigned)a < b)` |
| `JBE` / `JNA` | Below or Equal / Not Above | CF=1 OR ZF=1 | a <= b | `if ((unsigned)a <= b)` |

**Example:**

```nasm
section .data
    x dd 0xFFFFFFF0      ; Large unsigned value
    y dd 5

section .text
    ; C equivalent:
    ; unsigned int x = 0xFFFFFFF0;  // 4,294,967,280
    ; unsigned int y = 5;
    ; if (x > y) {
    ;     // x is greater (unsigned)
    ; }
    
    mov eax, [x]        ; EAX = 0xFFFFFFF0 (unsigned: 4,294,967,280)
    cmp eax, [y]        ; Compare unsigned
    ja x_is_greater     ; Jump if above (unsigned)
    
    jmp done
    
x_is_greater:
    ; x > y path (this executes for unsigned)
    
done:
```

**Key Difference:**

```nasm
; Same values, different interpretation:
mov eax, 0xFFFFFFF0

; Signed: -16
cmp eax, 5
jg is_greater_signed    ; Does NOT jump (-16 < 5)

; Unsigned: 4,294,967,280
cmp eax, 5
ja is_greater_unsigned  ; DOES jump (4,294,967,280 > 5)
```

---

## 4. Conditional Jumps (Single Flag Tests)

Test individual flags directly.

### Flag-Specific Jumps:

| Instruction | Condition | Flag | Meaning | C Equivalent |
|-------------|-----------|------|---------|--------------|
| `JZ` | Zero | ZF=1 | Result is zero | `if (x == 0)` |
| `JNZ` | Not Zero | ZF=0 | Result is not zero | `if (x != 0)` |
| `JS` | Sign | SF=1 | Result is negative | `if (x < 0)` |
| `JNS` | Not Sign | SF=0 | Result is non-negative | `if (x >= 0)` |
| `JO` | Overflow | OF=1 | Overflow occurred | (detect overflow) |
| `JNO` | Not Overflow | OF=0 | No overflow | (no overflow) |
| `JP` / `JPE` | Parity / Parity Even | PF=1 | Even parity | (even bits set) |
| `JNP` / `JPO` | Not Parity / Parity Odd | PF=0 | Odd parity | (odd bits set) |
| `JC` | Carry | CF=1 | Carry flag set | (unsigned overflow) |
| `JNC` | Not Carry | CF=0 | Carry flag clear | (no carry) |

**Example: Zero Check**

```nasm
; C equivalent:
; if (x == 0) {
;     // handle zero
; }

test eax, eax       ; Set flags based on EAX
jz is_zero          ; Jump if zero flag set

; Non-zero path
jmp done

is_zero:
    ; Zero path
    
done:
```

**Example: Negative Check**

```nasm
; C equivalent:
; if (x < 0) {
;     // handle negative
; }

test eax, eax       ; Set flags based on EAX
js is_negative      ; Jump if sign flag set

; Non-negative path
jmp done

is_negative:
    ; Negative path
    
done:
```

**Example: Overflow Detection**

```nasm
; C equivalent:
; int result = a + b;
; if (/* overflow occurred */) {
;     // handle overflow
; }

mov eax, [a]
add eax, [b]        ; Addition sets OF if overflow
jo overflow_handler ; Jump if overflow

; Normal path
jmp done

overflow_handler:
    ; Handle overflow
    
done:
```

---

## 5. Loop Jumps

Special jump instructions for loop control.

### Loop Instructions:

| Instruction | Operation | C Equivalent |
|-------------|-----------|--------------|
| `LOOP` | `--RCX; if (RCX != 0) jump` | `for (int i = n; i > 0; --i)` |
| `LOOPE` / `LOOPZ` | `--RCX; if (RCX != 0 && ZF=1) jump` | Loop while equal/zero |
| `LOOPNE` / `LOOPNZ` | `--RCX; if (RCX != 0 && ZF=0) jump` | Loop while not equal/zero |

**Example: Simple Loop**

```nasm
; C equivalent:
; for (int i = 10; i > 0; --i) {
;     // loop body
; }

mov rcx, 10         ; Loop counter

loop_start:
    ; Loop body here
    
    loop loop_start ; Decrement RCX, jump if RCX != 0
    
; Continue after loop
```

**Example: LOOPE (Loop While Equal)**

```nasm
; C equivalent:
; int i = 10;
; while (i > 0 && condition_is_true) {
;     --i;
; }

mov rcx, 10

loop_start:
    ; Check some condition
    cmp byte [flag], 1  ; Sets ZF if flag == 1
    loope loop_start    ; Continue if ZF=1 and RCX != 0
    
; Exit when RCX=0 or condition becomes false
```

---

## 6. Function Call/Return (Special Jumps)

### `CALL` - Call Subroutine

Jumps to a function and saves return address on stack.

```nasm
; C equivalent:
; function();

call function       ; Push return address, jump to function

function:
    ; Function body
    ret             ; Pop return address, jump back
```

**How CALL Works:**

```nasm
; call target is equivalent to:
push rip + 5        ; Save address of next instruction (size of call = 5 bytes)
jmp target          ; Jump to function
```

### `RET` - Return from Subroutine

Pops return address from stack and jumps to it.

```nasm
; ret is equivalent to:
pop rip             ; Pop return address into instruction pointer
```

**Forms:**

```nasm
; Direct call
call function_name

; Indirect call (register)
call rax            ; Jump to address in RAX

; Indirect call (memory)
call [function_ptr] ; Jump to address stored in memory

; Return
ret                 ; Simple return

; Return and pop N bytes
ret 16              ; Pop return address, then remove 16 bytes from stack
```

**Example: Function with Arguments**

```nasm
; C equivalent:
; int add(int a, int b) {
;     return a + b;
; }
; int result = add(10, 20);

section .text
global _start

_start:
    ; Call function
    mov rdi, 10         ; First argument
    mov rsi, 20         ; Second argument
    call add            ; CALL pushes return address, jumps to 'add'
    
    ; RAX now contains result (30)
    mov [result], rax
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall

add:
    ; Function prologue
    push rbp
    mov rbp, rsp
    
    ; Function body
    mov rax, rdi        ; RAX = first arg
    add rax, rsi        ; RAX += second arg
    
    ; Function epilogue
    pop rbp
    ret                 ; RET pops return address, jumps back
```

---

## 7. Indirect Jumps

Jump to an address stored in a register or memory.

### Register Indirect:

```nasm
; C equivalent:
; void (*func_ptr)(void) = some_function;
; func_ptr();  // Call through pointer

lea rax, [target]   ; Get address of target
jmp rax             ; Jump to address in RAX

target:
    ; Code here
```

### Memory Indirect:

```nasm
; C equivalent:
; void (*func_ptr)(void) = function_array[index];
; func_ptr();

section .data
    function_ptr dq target

section .text
    jmp [function_ptr]  ; Jump to address stored at function_ptr

target:
    ; Code here
```

---

## 8. Jump Tables (Switch Statement)

Efficient implementation of multi-way branches.

```nasm
; C equivalent:
; switch (x) {
;     case 0: action0(); break;
;     case 1: action1(); break;
;     case 2: action2(); break;
;     case 3: action3(); break;
;     default: default_action(); break;
; }

section .data
    jump_table dq case0, case1, case2, case3

section .text
    ; Bounds check
    mov rax, [x]
    cmp rax, 4
    jae default_case    ; Jump if x >= 4 (out of range)
    
    ; Jump through table
    jmp [jump_table + rax*8]    ; Each pointer is 8 bytes

case0:
    ; Handle case 0
    jmp done

case1:
    ; Handle case 1
    jmp done

case2:
    ; Handle case 2
    jmp done

case3:
    ; Handle case 3
    jmp done

default_case:
    ; Handle default
    
done:
```

**Complete Example:**

```nasm
section .data
    msg0 db "Zero", 10, 0
    msg1 db "One", 10, 0
    msg2 db "Two", 10, 0
    msg3 db "Three", 10, 0
    msg_default db "Other", 10, 0
    
    jump_table dq case0, case1, case2, case3

section .text
extern printf
global main

main:
    push rbp
    mov rbp, rsp
    
    ; Get input value
    mov rax, 2          ; Test with value 2
    
    ; Bounds check
    cmp rax, 4
    jae default_case
    
    ; Indirect jump through table
    lea rbx, [jump_table]
    jmp [rbx + rax*8]

case0:
    lea rdi, [msg0]
    jmp print_and_exit

case1:
    lea rdi, [msg1]
    jmp print_and_exit

case2:
    lea rdi, [msg2]
    jmp print_and_exit

case3:
    lea rdi, [msg3]
    jmp print_and_exit

default_case:
    lea rdi, [msg_default]

print_and_exit:
    xor rax, rax
    call printf
    
    xor eax, eax
    leave
    ret
```

---

## 9. Conditional Move (Alternative to Jumps)

`CMOVcc` instructions provide branchless conditional execution.

### Common CMOV Instructions:

| Instruction | Condition | When to Use |
|-------------|-----------|-------------|
| `CMOVE` | Equal (ZF=1) | `result = (a == b) ? x : result;` |
| `CMOVNE` | Not Equal (ZF=0) | `result = (a != b) ? x : result;` |
| `CMOVG` | Greater (signed) | `result = (a > b) ? x : result;` |
| `CMOVL` | Less (signed) | `result = (a < b) ? x : result;` |
| `CMOVA` | Above (unsigned) | `result = (a > b) ? x : result;` |
| `CMOVB` | Below (unsigned) | `result = (a < b) ? x : result;` |

**Example: Branchless Max**

```nasm
; C equivalent:
; int max = (a > b) ? a : b;

; With conditional jump (slower if mispredicted):
mov eax, [a]
cmp eax, [b]
jg a_is_max
mov eax, [b]
a_is_max:
    ; EAX contains max

; With CMOV (faster, no branch):
mov eax, [a]
mov ebx, [b]
cmp eax, ebx
cmovl eax, ebx      ; If a < b, move b to a
; EAX now contains max
```

---

## 10. Short vs Near vs Far Jumps

### Jump Distances:

| Type | Range | Encoding | Use Case |
|------|-------|----------|----------|
| **Short** | -128 to +127 bytes | 2 bytes | Small loops, nearby labels |
| **Near** | ±2GB (32-bit offset) | 5-6 bytes | Same segment, most common |
| **Far** | Different segment | 7+ bytes | Rarely used in 64-bit |

**NASM Automatically Chooses:**

```nasm
jmp short target    ; Force short jump (2 bytes)
jmp near target     ; Force near jump (5 bytes)
jmp target          ; NASM chooses optimal size
```

**Example:**

```nasm
loop_start:
    ; Loop body (small)
    loop loop_start     ; Short jump (2 bytes)

very_far_label:
    ; Lots of code here (> 127 bytes)
    jmp very_far_label  ; Near jump required (5 bytes)
```

---

## 11. Jump Optimization Patterns

### Pattern 1: Remove Unnecessary Jumps

```nasm
; BAD: Unnecessary jump
cmp eax, 0
je case_zero
jmp case_nonzero

case_zero:
    ; handle zero

case_nonzero:
    ; handle non-zero

; GOOD: Fall through
cmp eax, 0
jne case_nonzero

; handle zero (fall through)
jmp done

case_nonzero:
    ; handle non-zero
    
done:
```

### Pattern 2: Invert Condition to Remove Jump

```nasm
; BAD:
cmp eax, 0
je skip
; common path
skip:
    ; rare path

; GOOD:
cmp eax, 0
jne common_path
; rare path (fall through)
jmp done

common_path:
    ; common path
    
done:
```

### Pattern 3: Use CMOV for Simple Conditionals

```nasm
; BAD: Branch for simple selection
cmp eax, ebx
jle use_eax
mov ecx, ebx
jmp done
use_eax:
    mov ecx, eax
done:

; GOOD: Branchless with CMOV
mov ecx, eax
cmp eax, ebx
cmovg ecx, ebx      ; If eax > ebx, use ebx
```

---

## 12. Complete Jump Reference Table

### All Jump Instructions Alphabetically:

| Instruction | Alternative Names | Condition | Flags | Type |
|-------------|------------------|-----------|-------|------|
| `JA` | `JNBE` | Above (unsigned) | CF=0 & ZF=0 | Conditional |
| `JAE` | `JNB`, `JNC` | Above or Equal | CF=0 | Conditional |
| `JB` | `JNAE`, `JC` | Below (unsigned) | CF=1 | Conditional |
| `JBE` | `JNA` | Below or Equal | CF=1 OR ZF=1 | Conditional |
| `JC` | | Carry | CF=1 | Flag test |
| `JCXZ` | | CX is zero | CX=0 | Special |
| `JECXZ` | | ECX is zero | ECX=0 | Special |
| `JRCXZ` | | RCX is zero | RCX=0 | Special |
| `JE` | `JZ` | Equal / Zero | ZF=1 | Conditional |
| `JG` | `JNLE` | Greater (signed) | ZF=0 & SF=OF | Conditional |
| `JGE` | `JNL` | Greater or Equal | SF=OF | Conditional |
| `JL` | `JNGE` | Less (signed) | SF≠OF | Conditional |
| `JLE` | `JNG` | Less or Equal | ZF=1 OR SF≠OF | Conditional |
| `JMP` | | Always | None | Unconditional |
| `JNA` | `JBE` | Not Above | CF=1 OR ZF=1 | Conditional |
| `JNAE` | `JB`, `JC` | Not Above or Equal | CF=1 | Conditional |
| `JNB` | `JAE`, `JNC` | Not Below | CF=0 | Conditional |
| `JNBE` | `JA` | Not Below or Equal | CF=0 & ZF=0 | Conditional |
| `JNC` | `JAE`, `JNB` | No Carry | CF=0 | Flag test |
| `JNE` | `JNZ` | Not Equal / Not Zero | ZF=0 | Conditional |
| `JNG` | `JLE` | Not Greater | ZF=1 OR SF≠OF | Conditional |
| `JNGE` | `JL` | Not Greater or Equal | SF≠OF | Conditional |
| `JNL` | `JGE` | Not Less | SF=OF | Conditional |
| `JNLE` | `JG` | Not Less or Equal | ZF=0 & SF=OF | Conditional |
| `JNO` | | No Overflow | OF=0 | Flag test |
| `JNP` | `JPO` | Not Parity / Parity Odd | PF=0 | Flag test |
| `JNS` | | Not Sign | SF=0 | Flag test |
| `JNZ` | `JNE` | Not Zero / Not Equal | ZF=0 | Conditional |
| `JO` | | Overflow | OF=1 | Flag test |
| `JP` | `JPE` | Parity / Parity Even | PF=1 | Flag test |
| `JPE` | `JP` | Parity Even | PF=1 | Flag test |
| `JPO` | `JNP` | Parity Odd | PF=0 | Flag test |
| `JS` | | Sign | SF=1 | Flag test |
| `JZ` | `JE` | Zero / Equal | ZF=1 | Conditional |
| `LOOP` | | Loop | RCX--, RCX≠0 | Loop |
| `LOOPE` | `LOOPZ` | Loop Equal | RCX--, RCX≠0 & ZF=1 | Loop |
| `LOOPNE` | `LOOPNZ` | Loop Not Equal | RCX--, RCX≠0 & ZF=0 | Loop |
| `LOOPNZ` | `LOOPNE` | Loop Not Zero | RCX--, RCX≠0 & ZF=0 | Loop |
| `LOOPZ` | `LOOPE` | Loop Zero | RCX--, RCX≠0 & ZF=1 | Loop |

---

## Summary

### Jump Categories:

1. **Unconditional**: `JMP` (always jumps)
2. **Signed Conditional**: `JG`, `JGE`, `JL`, `JLE`, `JE`, `JNE`
3. **Unsigned Conditional**: `JA`, `JAE`, `JB`, `JBE`, `JE`, `JNE`
4. **Flag Tests**: `JZ`, `JNZ`, `JS`, `JNS`, `JO`, `JNO`, `JP`, `JNP`, `JC`, `JNC`
5. **Loop**: `LOOP`, `LOOPE`, `LOOPNE`
6. **Function**: `CALL`, `RET`
7. **Indirect**: Through register or memory
8. **Conditional Move**: `CMOVcc` (branchless alternative)

### Quick Decision Tree:

```
Need to jump?
├─ Always? → JMP
├─ Based on comparison?
│  ├─ Signed integers? → JG, JGE, JL, JLE, JE, JNE
│  └─ Unsigned integers? → JA, JAE, JB, JBE, JE, JNE
├─ Based on single flag?
│  ├─ Zero? → JZ, JNZ
│  ├─ Sign? → JS, JNS
│  ├─ Carry? → JC, JNC
│  └─ Overflow? → JO, JNO
├─ Loop counter? → LOOP, LOOPE, LOOPNE
├─ Call function? → CALL (with RET to return)
├─ Computed target? → JMP [register/memory]
└─ Want branchless? → CMOV (conditional move)
```

### Performance Tips:

1. **Avoid unpredictable branches** - use CMOV when possible
2. **Put common case first** - less misprediction
3. **Minimize jump distance** - short jumps are faster
4. **Use jump tables** for multi-way branches (switch)
5. **Eliminate unnecessary jumps** - let code fall through

---

## Practice Exercises

### Exercise 1: Implement Absolute Value

```nasm
; int abs(int x) {
;     return (x < 0) ? -x : x;
; }

; Your code here using conditional jumps
```

<details>
<summary>Solution</summary>

```nasm
abs_value:
    ; Input: EDI = x
    ; Output: EAX = |x|
    
    mov eax, edi
    test eax, eax
    jns positive        ; Jump if not sign (x >= 0)
    neg eax             ; x = -x
positive:
    ret
```
</details>

### Exercise 2: Implement Clamp

```nasm
; int clamp(int x, int min, int max) {
;     if (x < min) return min;
;     if (x > max) return max;
;     return x;
; }

; Your code here
```

<details>
<summary>Solution</summary>

```nasm
clamp:
    ; RDI = x, RSI = min, RDX = max
    mov rax, rdi
    cmp rax, rsi
    cmovl rax, rsi      ; If x < min, x = min
    cmp rax, rdx
    cmovg rax, rdx      ; If x > max, x = max
    ret
```
</details>

---

**Related Topics:**
- [Topic 5: Conditional Jumps](../topics/topic-05-jumps.md)
- [Topic 4: Flags & Comparisons](../topics/topic-04-flags.md)
- [Topic 6: Loops](../topics/topic-06-loops.md)
- [CMP vs TEST](cmp-vs-test.md)

