# 📘 Topic 5: Conditional Jumps

Master conditional execution - the foundation of if/else logic in assembly.

---

## **Overview**

**Jumps** are how you control program flow in assembly. They let you:
- Implement if/else statements
- Create loops
- Handle different cases
- Skip code sections
- Build complex logic

**Types of jumps:**
- 🔀 Unconditional jumps (always jump)
- 🎯 Conditional jumps (jump based on flags)

---

## **Part 1: How Jumps Work**

### **The Instruction Pointer**

The **RIP** (Instruction Pointer) register always points to the next instruction to execute.

```
Normal execution (no jumps):
┌─────────────────┐
│ mov rax, 10     │ ← RIP here
│ add rax, 5      │ ← RIP moves here next
│ mov rbx, rax    │ ← Then here
│ ret             │ ← Finally here
└─────────────────┘

With a jump:
┌─────────────────┐
│ mov rax, 10     │ ← RIP here
│ jmp skip        │ ← Jump changes RIP
│ add rax, 5      │   (skipped!)
│ skip:           │ ← RIP jumps here
│ mov rbx, rax    │
└─────────────────┘
```

### **Labels**

Labels are markers in your code that jumps can target:

```nasm
section .text
    global _start

_start:                 ; Label marking program start
    mov rax, 10
    jmp continue        ; Jump to 'continue' label
    
    ; This code is skipped
    mov rax, 99
    
continue:               ; Label marking jump target
    mov rbx, rax        ; RBX = 10 (not 99)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

**Label rules:**
- Can contain letters, numbers, underscore, dot
- Must start with letter, underscore, or dot
- Case-sensitive
- Followed by colon `:` when defined
- No colon when referenced in jumps

---

## **Part 2: Unconditional Jumps**

### **JMP - Jump Always**

```nasm
jmp label               ; Always jump to label
```

**Examples:**

```nasm
; Simple jump
jmp end_program
mov rax, 100            ; Skipped!
end_program:
    ; Continues here

; Jump forward
mov rax, 10
jmp skip_error
    mov rax, -1         ; Error code (skipped)
skip_error:
    ; Normal flow

; Jump backward (loop)
start_loop:
    dec rcx
    cmp rcx, 0
    jne start_loop      ; Jump back to start_loop
```

### **Short vs Near vs Far Jumps**

```nasm
; Short jump (2 bytes, offset -128 to +127 bytes)
jmp short nearby_label

; Near jump (5 bytes, offset ±2GB)
jmp near far_label
jmp far_label           ; Default is near

; Far jump (different code segment, rarely used)
jmp far segment:offset
```

**Usually:** Let NASM choose automatically. It picks the shortest encoding.

---

## **Part 3: Conditional Jumps**

Conditional jumps check CPU flags and jump only if conditions are met.

### **Jump Mnemonic Format**

```
J + condition

Examples:
JE  = Jump if Equal
JNE = Jump if Not Equal
JG  = Jump if Greater
JL  = Jump if Less
```

### **All Conditional Jumps**

```
┌────────────┬─────────────────────┬────────────────────┐
│ Mnemonic   │ Meaning             │ Condition          │
├────────────┼─────────────────────┼────────────────────┤
│ JE / JZ    │ Jump if Equal/Zero  │ ZF = 1             │
│ JNE / JNZ  │ Jump if Not Equal   │ ZF = 0             │
├────────────┼─────────────────────┼────────────────────┤
│ JS         │ Jump if Sign        │ SF = 1             │
│ JNS        │ Jump if Not Sign    │ SF = 0             │
├────────────┼─────────────────────┼────────────────────┤
│ JC         │ Jump if Carry       │ CF = 1             │
│ JNC        │ Jump if Not Carry   │ CF = 0             │
├────────────┼─────────────────────┼────────────────────┤
│ JO         │ Jump if Overflow    │ OF = 1             │
│ JNO        │ Jump if Not Overflow│ OF = 0             │
├────────────┼─────────────────────┼────────────────────┤
│ JP / JPE   │ Jump if Parity Even │ PF = 1             │
│ JNP / JPO  │ Jump if Parity Odd  │ PF = 0             │
└────────────┴─────────────────────┴────────────────────┘
```

### **Signed Comparison Jumps (After CMP)**

```
┌────────┬─────────────────────┬───────────────────────┐
│ Jump   │ Meaning             │ Condition             │
├────────┼─────────────────────┼───────────────────────┤
│ JE     │ Jump if Equal       │ ZF = 1                │
│ JNE    │ Jump if Not Equal   │ ZF = 0                │
│ JG     │ Jump if Greater     │ ZF = 0 AND SF = OF    │
│ JGE    │ Jump if ≥           │ SF = OF               │
│ JL     │ Jump if Less        │ SF ≠ OF               │
│ JLE    │ Jump if ≤           │ ZF = 1 OR SF ≠ OF     │
└────────┴─────────────────────┴───────────────────────┘
```

### **Unsigned Comparison Jumps (After CMP)**

```
┌────────┬─────────────────────┬───────────────────────┐
│ Jump   │ Meaning             │ Condition             │
├────────┼─────────────────────┼───────────────────────┤
│ JE     │ Jump if Equal       │ ZF = 1                │
│ JNE    │ Jump if Not Equal   │ ZF = 0                │
│ JA     │ Jump if Above       │ CF = 0 AND ZF = 0     │
│ JAE    │ Jump if ≥           │ CF = 0                │
│ JB     │ Jump if Below       │ CF = 1                │
│ JBE    │ Jump if ≤           │ CF = 1 OR ZF = 1      │
└────────┴─────────────────────┴───────────────────────┘
```

### **Aliases (Same Instruction, Different Name)**

```
JE  = JZ     (Equal = Zero)
JNE = JNZ    (Not Equal = Not Zero)
JA  = JNBE   (Above = Not Below or Equal)
JAE = JNB    (Above or Equal = Not Below)
JB  = JNAE   (Below = Not Above or Equal)
JBE = JNA    (Below or Equal = Not Above)
JG  = JNLE   (Greater = Not Less or Equal)
JGE = JNL    (Greater or Equal = Not Less)
JL  = JNGE   (Less = Not Greater or Equal)
JLE = JNG    (Less or Equal = Not Greater)
```

---

## **Part 4: Using Conditional Jumps**

### **Basic Pattern**

```nasm
1. Perform comparison (CMP, TEST, or arithmetic)
2. Check flags with conditional jump
3. Execute code based on result
```

### **Equality Check**

```nasm
; if (rax == 42) goto equal_handler

cmp rax, 42
je equal_handler        ; Jump if equal
; Not equal path
mov rbx, 0
jmp done

equal_handler:
; Equal path
mov rbx, 1

done:
```

### **Inequality Check**

```nasm
; if (rax != 42) goto not_equal

cmp rax, 42
jne not_equal           ; Jump if not equal
; Equal path
mov rbx, 1
jmp done

not_equal:
; Not equal path
mov rbx, 0

done:
```

### **Greater Than (Signed)**

```nasm
; if (rax > 10) goto greater

cmp rax, 10
jg greater              ; Jump if rax > 10 (signed)
; Less than or equal path
mov rbx, 0
jmp done

greater:
; Greater path
mov rbx, 1

done:
```

### **Less Than (Signed)**

```nasm
; if (rax < 0) goto negative

cmp rax, 0
jl negative             ; Jump if rax < 0 (signed)
; Positive or zero path
mov rbx, 0
jmp done

negative:
; Negative path
mov rbx, 1

done:
```

### **Above (Unsigned)**

```nasm
; if (rax > 100) goto above  [unsigned comparison]

cmp rax, 100
ja above                ; Jump if rax > 100 (unsigned)
; Below or equal path
mov rbx, 0
jmp done

above:
; Above path
mov rbx, 1

done:
```

---

## **Part 5: If/Else in Assembly**

### **Simple If Statement**

**C Code:**
```c
if (x == 10) {
    y = 100;
}
```

**Assembly:**
```nasm
; if (rax == 10) rbx = 100

cmp rax, 10
jne skip_if             ; Jump if not equal (skip the if body)
    mov rbx, 100        ; If body
skip_if:
    ; Continue...
```

### **If-Else Statement**

**C Code:**
```c
if (x > 5) {
    y = 1;
} else {
    y = 0;
}
```

**Assembly:**
```nasm
; if (rax > 5) rbx = 1, else rbx = 0

cmp rax, 5
jle else_branch         ; Jump if less or equal
    ; If true branch
    mov rbx, 1
    jmp end_if
else_branch:
    ; Else branch
    mov rbx, 0
end_if:
    ; Continue...
```

### **If-Else If-Else**

**C Code:**
```c
if (x < 0) {
    result = -1;
} else if (x > 0) {
    result = 1;
} else {
    result = 0;
}
```

**Assembly:**
```nasm
; Sign function: sign(rax) -> rbx

cmp rax, 0
jl negative             ; If x < 0
jg positive             ; Else if x > 0
    ; Else (x == 0)
    mov rbx, 0
    jmp done

negative:
    mov rbx, -1
    jmp done

positive:
    mov rbx, 1

done:
    ; Continue...
```

### **Nested If Statements**

**C Code:**
```c
if (x > 0) {
    if (x < 10) {
        result = 1;
    }
}
```

**Assembly:**
```nasm
; if (rax > 0 && rax < 10) rbx = 1

cmp rax, 0
jle skip_outer          ; Skip if not > 0
    cmp rax, 10
    jge skip_inner      ; Skip if not < 10
        mov rbx, 1      ; Both conditions true
    skip_inner:
skip_outer:
    ; Continue...
```

---

## **Part 6: Loops with Jumps**

### **While Loop**

**C Code:**
```c
while (count > 0) {
    sum += count;
    count--;
}
```

**Assembly:**
```nasm
; while (rcx > 0) { rax += rcx; rcx--; }

while_start:
    cmp rcx, 0
    jle while_end       ; Exit if rcx <= 0
    
    add rax, rcx        ; sum += count
    dec rcx             ; count--
    jmp while_start     ; Loop back
    
while_end:
    ; Continue...
```

### **Do-While Loop**

**C Code:**
```c
do {
    sum += count;
    count--;
} while (count > 0);
```

**Assembly:**
```nasm
; do { rax += rcx; rcx--; } while (rcx > 0)

do_start:
    add rax, rcx        ; sum += count
    dec rcx             ; count--
    
    cmp rcx, 0
    jg do_start         ; Loop if rcx > 0
    
; Continue...
```

### **For Loop**

**C Code:**
```c
for (i = 0; i < 10; i++) {
    sum += i;
}
```

**Assembly:**
```nasm
; for (rcx = 0; rcx < 10; rcx++) { rax += rcx; }

xor rcx, rcx            ; i = 0

for_start:
    cmp rcx, 10
    jge for_end         ; Exit if i >= 10
    
    add rax, rcx        ; sum += i
    inc rcx             ; i++
    jmp for_start
    
for_end:
    ; Continue...
```

### **Loop with Break**

**C Code:**
```c
while (1) {
    if (count == 0) break;
    sum += count;
    count--;
}
```

**Assembly:**
```nasm
; while (1) { if (rcx == 0) break; rax += rcx; rcx--; }

infinite_loop:
    cmp rcx, 0
    je loop_break       ; Break if count == 0
    
    add rax, rcx
    dec rcx
    jmp infinite_loop
    
loop_break:
    ; Continue after loop...
```

### **Loop with Continue**

**C Code:**
```c
for (i = 0; i < 10; i++) {
    if (i == 5) continue;
    sum += i;
}
```

**Assembly:**
```nasm
; for (rcx = 0; rcx < 10; rcx++) { if (rcx == 5) continue; rax += rcx; }

xor rcx, rcx

loop_start:
    cmp rcx, 10
    jge loop_end
    
    cmp rcx, 5
    je continue_point   ; Skip to next iteration
    
    add rax, rcx        ; sum += i
    
continue_point:
    inc rcx
    jmp loop_start
    
loop_end:
    ; Continue...
```

---

## **Part 7: Special Loop Instructions**

### **LOOP - Loop with RCX Counter**

```nasm
loop label              ; Decrement RCX, jump if RCX != 0
```

**Equivalent to:**
```nasm
dec rcx
jnz label
```

**Example:**

```nasm
; Loop 10 times
mov rcx, 10

loop_start:
    ; ... do something ...
    loop loop_start     ; Decrements RCX, loops if RCX != 0

; RCX is now 0
```

**Limitations:**
- Only works with RCX
- Can't check other conditions
- No way to break early without jumping

**When to use:**
- Simple counted loops
- When RCX counter is convenient
- Short, simple loop bodies

**When not to use:**
- Complex loop conditions
- Need to preserve RCX
- Need early exit/break

### **LOOPcc Variants**

```nasm
loope label             ; Loop if equal (ZF = 1) and RCX != 0
loopne label            ; Loop if not equal (ZF = 0) and RCX != 0
loopz label             ; Same as loope
loopnz label            ; Same as loopne
```

**Example:**

```nasm
; Search for zero in array
mov rcx, array_size
mov rsi, array

search_loop:
    cmp byte [rsi], 0
    loopne search_loop  ; Continue if not zero and RCX != 0
    
; Either found zero or reached end
```

**Rarely used** in modern code - explicit comparisons are clearer.

---

## **Part 8: Practical Examples**

### **Example 1: Find Maximum**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int32_t numbers[] = {15, 42, 7, 89, 23, 56};
    int32_t count = 6;
    int32_t max = numbers[0];
    
    for (int32_t i = 1; i < count; i++) {
        if (numbers[i] > max) {
            max = numbers[i];
        }
    }
    
    // max = 89
    return 0;
}
```

**Assembly:**
```nasm
section .data
    numbers dd 15, 42, 7, 89, 23, 56
    count equ 6

section .bss
    max resd 1

section .text
    global _start

_start:
    ; Find maximum value in array
    mov eax, [numbers]      ; max = numbers[0]
    mov ecx, 1              ; i = 1
    
find_max_loop:
    cmp ecx, count
    jge found_max           ; Exit if i >= count
    
    mov edx, [numbers + rcx*4]
    cmp eax, edx
    jge skip_update         ; Skip if max >= numbers[i]
    
    mov eax, edx            ; max = numbers[i]
    
skip_update:
    inc ecx
    jmp find_max_loop
    
found_max:
    mov [max], eax          ; Store result (89)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 2: String Length**

**C Equivalent:**
```c
#include <stdint.h>

size_t my_strlen(const char *str) {
    size_t length = 0;
    
    while (str[length] != '\0') {
        length++;
    }
    
    return length;
}

int main() {
    const char *string = "Hello, World!";
    size_t length = my_strlen(string);
    // length = 13
    
    return length;
}
```

**Assembly:**
```nasm
section .data
    string db "Hello, World!", 0

section .text
    global _start

_start:
    ; Calculate string length
    mov rsi, string         ; Pointer to string
    xor rcx, rcx            ; Length = 0
    
strlen_loop:
    cmp byte [rsi + rcx], 0 ; Check for null terminator
    je strlen_done          ; Exit if found null
    
    inc rcx                 ; Length++
    jmp strlen_loop
    
strlen_done:
    ; RCX contains length (13)
    
    ; Exit
    mov rax, 60
    mov rdi, rcx            ; Exit with length as code
    syscall
```

### **Example 3: Count Set Bits (Population Count)**

**C Equivalent:**
```c
#include <stdint.h>

int popcount(uint64_t value) {
    int count = 0;
    
    while (value != 0) {
        if (value & 1) {
            count++;
        }
        value >>= 1;  // Shift right by 1
    }
    
    return count;
}

int main() {
    uint64_t value = 0b10110101;
    int count = popcount(value);
    // count = 5 (five 1-bits)
    
    return count;
}
```

**Assembly:**
```nasm
section .text
    global _start

_start:
    ; Count set bits in RAX
    mov rax, 0b10110101     ; Test value
    xor rcx, rcx            ; count = 0
    
count_bits_loop:
    test rax, rax
    jz count_done           ; Exit if no bits left
    
    test rax, 1             ; Check lowest bit
    jz skip_count
    inc rcx                 ; Count if set
    
skip_count:
    shr rax, 1              ; Shift to next bit
    jmp count_bits_loop
    
count_done:
    ; RCX contains count (5 bits set)
    
    ; Exit
    mov rax, 60
    mov rdi, rcx
    syscall
```

### **Example 4: Binary Search**

**C Equivalent:**
```c
#include <stdint.h>

int binary_search(int32_t *array, int32_t size, int32_t target) {
    int32_t left = 0;
    int32_t right = size;
    
    while (left < right) {
        int32_t mid = (left + right) / 2;
        
        if (array[mid] == target) {
            return mid;  // Found at index mid
        } else if (array[mid] < target) {
            left = mid + 1;  // Search right half
        } else {
            right = mid;  // Search left half
        }
    }
    
    return -1;  // Not found
}

int main() {
    int32_t array[] = {1, 3, 5, 7, 9, 11, 13, 15};
    int32_t size = 8;
    int32_t target = 7;
    
    int32_t index = binary_search(array, size, target);
    // index = 3 (found at position 3)
    
    return index;
}
```

**Assembly:**
```nasm
section .data
    ; Sorted array
    array dd 1, 3, 5, 7, 9, 11, 13, 15
    array_size equ 8
    target dd 7

section .text
    global _start

_start:
    ; Binary search for target
    xor rcx, rcx            ; left = 0
    mov rdx, array_size     ; right = size
    mov edi, [target]       ; value to find
    
binary_search:
    cmp rcx, rdx
    jge not_found           ; Exit if left >= right
    
    ; mid = (left + right) / 2
    mov rax, rcx
    add rax, rdx
    shr rax, 1              ; Divide by 2
    
    ; Compare array[mid] with target
    mov esi, [array + rax*4]
    cmp esi, edi
    je found                ; Found!
    jl search_right         ; array[mid] < target
    
    ; Search left half
    mov rdx, rax            ; right = mid
    jmp binary_search
    
search_right:
    ; Search right half
    lea rcx, [rax + 1]      ; left = mid + 1
    jmp binary_search
    
found:
    ; Found at index RAX
    mov rdi, rax
    jmp exit_program
    
not_found:
    ; Not found
    mov rdi, -1
    
exit_program:
    mov rax, 60
    syscall
```

### **Example 5: FizzBuzz**

```nasm
section .data
    fizz db "Fizz", 10
    fizz_len equ $ - fizz
    buzz db "Buzz", 10
    buzz_len equ $ - buzz
    fizzbuzz db "FizzBuzz", 10
    fizzbuzz_len equ $ - fizzbuzz

section .text
    global _start

_start:
    mov rcx, 1              ; counter = 1
    
fizzbuzz_loop:
    cmp rcx, 100
    jg fizzbuzz_end         ; Exit if counter > 100
    
    ; Check if divisible by 15
    mov rax, rcx
    xor rdx, rdx
    mov rbx, 15
    div rbx
    test rdx, rdx
    jz print_fizzbuzz       ; Divisible by 15
    
    ; Check if divisible by 3
    mov rax, rcx
    xor rdx, rdx
    mov rbx, 3
    div rbx
    test rdx, rdx
    jz print_fizz           ; Divisible by 3
    
    ; Check if divisible by 5
    mov rax, rcx
    xor rdx, rdx
    mov rbx, 5
    div rbx
    test rdx, rdx
    jz print_buzz           ; Divisible by 5
    
    ; Print number (simplified - just skip)
    jmp next_iteration
    
print_fizzbuzz:
    mov rax, 1
    mov rdi, 1
    mov rsi, fizzbuzz
    mov rdx, fizzbuzz_len
    syscall
    jmp next_iteration
    
print_fizz:
    mov rax, 1
    mov rdi, 1
    mov rsi, fizz
    mov rdx, fizz_len
    syscall
    jmp next_iteration
    
print_buzz:
    mov rax, 1
    mov rdi, 1
    mov rsi, buzz
    mov rdx, buzz_len
    syscall
    
next_iteration:
    inc rcx
    jmp fizzbuzz_loop
    
fizzbuzz_end:
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## **Part 9: Optimization Tips**

### **Invert Conditions to Reduce Jumps**

```nasm
; ❌ Less efficient (2 jumps in common case)
cmp rax, 10
je equal
mov rbx, 0
jmp done
equal:
mov rbx, 1
done:

; ✅ More efficient (1 jump in common case)
cmp rax, 10
jne not_equal
mov rbx, 1
jmp done
not_equal:
mov rbx, 0
done:
```

### **Place Common Case First**

```nasm
; If rax is usually not zero:
test rax, rax
jnz common_case         ; Taken most often (predicted taken)
    ; Rare case
    jmp done
common_case:
    ; Common case
done:
```

### **Avoid Jumping Over Single Instructions**

```nasm
; ❌ Inefficient
test rax, rax
jz skip
inc rbx
skip:

; ✅ Use conditional move (if appropriate)
test rax, rax
cmovnz rbx, some_value  ; Only if rbx = some_value needed
```

### **Short Jumps When Possible**

NASM automatically chooses, but be aware:

```nasm
; Short jump: 2 bytes (offset -128 to +127)
jmp short nearby

; Near jump: 5 bytes (offset ±2GB)
jmp near far_away
```

Keep frequently executed loops small to fit in instruction cache.

---

## **Part 10: Common Patterns**

### **Pattern 1: Early Exit/Guard Clause**

```nasm
; Check precondition and exit early
test rax, rax
jz error_null_pointer   ; Exit early if invalid

; Normal processing continues...
```

### **Pattern 2: Switch/Case**

```nasm
; switch (rax) { case 0: ..., case 1: ..., default: ... }

cmp rax, 0
je case_0
cmp rax, 1
je case_1
cmp rax, 2
je case_2
jmp default_case

case_0:
    ; Handle case 0
    jmp end_switch
case_1:
    ; Handle case 1
    jmp end_switch
case_2:
    ; Handle case 2
    jmp end_switch
default_case:
    ; Handle default

end_switch:
```

### **Pattern 3: Jump Table (Efficient Switch)**

```nasm
section .data
    jump_table dq case_0, case_1, case_2

section .text
    ; switch (rax) using jump table
    cmp rax, 2
    ja default_case         ; Out of range
    
    jmp [jump_table + rax*8]
    
case_0:
    ; Handle case 0
    jmp done
case_1:
    ; Handle case 1
    jmp done
case_2:
    ; Handle case 2
    jmp done
default_case:
    ; Handle default
done:
```

### **Pattern 4: State Machine**

```nasm
; Simple state machine
state_loop:
    cmp byte [state], 0
    je state_0
    cmp byte [state], 1
    je state_1
    cmp byte [state], 2
    je state_2
    jmp error_invalid_state

state_0:
    ; Process state 0
    ; Update state
    jmp state_loop
    
state_1:
    ; Process state 1
    jmp state_loop
    
state_2:
    ; Final state
    jmp exit

error_invalid_state:
    ; Handle error
exit:
```

---

## **✅ Practice Exercises**

### **Exercise 1: Absolute Value**

Implement `abs(rax)` using conditional jumps.

<details>
<summary>Solution</summary>

```nasm
; abs(rax) -> rax
test rax, rax
jns already_positive    ; Jump if not sign (positive)
neg rax
already_positive:
; RAX now contains absolute value
```
</details>

### **Exercise 2: Clamp Function**

Clamp RAX to range [min, max]. If RAX < min, set to min. If RAX > max, set to max.
min = 10, max = 100

<details>
<summary>Solution</summary>

```nasm
; Clamp rax to [10, 100]
cmp rax, 10
jge check_max           ; RAX >= 10, check upper bound
mov rax, 10             ; RAX < 10, set to 10
jmp done

check_max:
cmp rax, 100
jle done                ; RAX <= 100, already in range
mov rax, 100            ; RAX > 100, set to 100

done:
; RAX is now clamped to [10, 100]
```
</details>

### **Exercise 3: Count Down Loop**

Write a loop that counts from 10 down to 1, summing the values in RAX.

<details>
<summary>Solution</summary>

```nasm
xor rax, rax            ; sum = 0
mov rcx, 10             ; counter = 10

countdown_loop:
    add rax, rcx        ; sum += counter
    dec rcx             ; counter--
    jnz countdown_loop  ; Loop if counter != 0
    
; RAX = 55 (1+2+3+...+10)
```
</details>

### **Exercise 4: Linear Search**

Search for value 42 in an array of 10 numbers. Return index in RAX or -1 if not found.

<details>
<summary>Solution</summary>

```nasm
section .data
    array dd 10, 5, 42, 7, 3, 42, 9, 1, 8, 6
    count equ 10

section .text
    xor rcx, rcx            ; index = 0

search_loop:
    cmp rcx, count
    jge not_found           ; Reached end

    cmp dword [array + rcx*4], 42
    je found                ; Found it!
    
    inc rcx
    jmp search_loop
    
found:
    mov rax, rcx            ; Return index
    jmp done
    
not_found:
    mov rax, -1             ; Return -1
    
done:
```
</details>

### **Exercise 5: Is Prime?**

Check if RAX is a prime number. Set RBX = 1 if prime, 0 if not. (Assume RAX >= 2)

<details>
<summary>Solution</summary>

```nasm
; Check if rax is prime
cmp rax, 2
je is_prime             ; 2 is prime

; Check if even
test rax, 1
jz not_prime            ; Even numbers (except 2) not prime

; Check odd divisors from 3 to sqrt(rax)
mov rbx, 3

check_divisor:
    ; Check if rbx * rbx > rax
    mov rcx, rbx
    imul rcx, rcx
    cmp rcx, rax
    jg is_prime         ; No divisors found, is prime
    
    ; Check if rax % rbx == 0
    mov rdx, rax
    push rax
    mov rax, rdx
    xor rdx, rdx
    div rbx
    test rdx, rdx
    pop rax
    jz not_prime        ; Found divisor, not prime
    
    add rbx, 2          ; Next odd number
    jmp check_divisor

is_prime:
    mov rbx, 1
    jmp done

not_prime:
    mov rbx, 0

done:
```
</details>

---

## **📋 Quick Reference**

### **Unconditional Jump**
```
jmp label               ; Always jump
```

### **Equality Jumps**
```
je/jz label             ; Jump if equal/zero (ZF=1)
jne/jnz label           ; Jump if not equal/zero (ZF=0)
```

### **Signed Comparisons**
```
jg label                ; Jump if greater (signed)
jge label               ; Jump if greater or equal
jl label                ; Jump if less (signed)
jle label               ; Jump if less or equal
```

### **Unsigned Comparisons**
```
ja label                ; Jump if above (unsigned)
jae label               ; Jump if above or equal
jb label                ; Jump if below (unsigned)
jbe label               ; Jump if below or equal
```

### **Single Flag Tests**
```
js label                ; Jump if sign (negative)
jns label               ; Jump if not sign (positive/zero)
jc label                ; Jump if carry
jnc label               ; Jump if not carry
jo label                ; Jump if overflow
jno label               ; Jump if not overflow
```

### **Loop Instructions**
```
loop label              ; dec rcx; jnz label
loope/loopz label       ; Loop if equal and rcx!=0
loopne/loopnz label     ; Loop if not equal and rcx!=0
```

---

## **🎯 Knowledge Check**

Before moving to Topic 6, verify you understand:
- ✅ How RIP controls program flow
- ✅ Unconditional jumps (JMP)
- ✅ Conditional jumps based on flags
- ✅ Signed vs unsigned comparison jumps
- ✅ Implementing if/else statements
- ✅ Building loops with jumps
- ✅ When to use LOOP instruction
- ✅ Jump optimization techniques

---

**🎉 Excellent!** You now master conditional jumps and control flow!

**Next:** [Topic 6: Loops](topic-06-loops.md) (coming soon)

---

[← Previous Topic](topic-04-flags.md) | [Back to Main](../README.md) | Next Topic →

