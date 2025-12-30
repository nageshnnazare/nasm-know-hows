# 📘 Topic 6: Loops

Master loop patterns and iteration in assembly language.

---

## **Overview**

**Loops** are fundamental programming constructs that let you repeat code. In assembly, you build loops using:
- 🔄 Conditional jumps (from Topic 5)
- 🎯 Counter registers (usually RCX)
- 🔍 Comparison instructions
- ⚡ Special loop instructions

**Common loop types:**
- Counted loops (repeat N times)
- Condition-tested loops (while/until)
- Infinite loops with breaks
- Nested loops
- Loop unrolling for performance

---

## **Part 1: Loop Fundamentals**

### **Basic Loop Structure**

Every loop needs three components:

```
1. Initialization (setup counter/condition)
2. Loop body (code to repeat)
3. Update and test (modify counter, check condition)
```

### **Generic Loop Pattern**

```nasm
    ; 1. Initialization
    mov rcx, 10             ; Set counter

loop_start:                 ; Loop label
    ; 2. Loop body
    ; ... do something ...
    
    ; 3. Update and test
    dec rcx                 ; Modify counter
    jnz loop_start          ; Jump if not zero
    
    ; Continue after loop
```

---

## **Part 2: Counted Loops (For Loop)**

### **Count Up (For i = 0 to N)**

**C Equivalent:**
```c
for (int i = 0; i < 10; i++) {
    // body
}
```

**Assembly:**
```nasm
    xor rcx, rcx            ; i = 0

loop_start:
    cmp rcx, 10
    jge loop_end            ; Exit if i >= 10
    
    ; Loop body here
    ; ... use RCX as index ...
    
    inc rcx                 ; i++
    jmp loop_start

loop_end:
```

### **Count Down (For i = N to 0)**

**C Equivalent:**
```c
for (int i = 10; i > 0; i--) {
    // body
}
```

**Assembly:**
```nasm
    mov rcx, 10             ; i = 10

loop_start:
    ; Loop body here
    ; ... use RCX ...
    
    dec rcx                 ; i--
    jnz loop_start          ; Loop if i != 0
    
    ; RCX is now 0
```

**Why count down is popular:**
- Shorter: `dec rcx; jnz` is 2 instructions
- vs count up: `inc rcx; cmp rcx, N; jl` is 3 instructions
- Automatically tests for zero

### **Example: Sum 1 to 10**

```nasm
section .text
    global _start

_start:
    xor rax, rax            ; sum = 0
    mov rcx, 10             ; counter = 10

sum_loop:
    add rax, rcx            ; sum += counter
    dec rcx                 ; counter--
    jnz sum_loop            ; Loop if counter != 0
    
    ; RAX = 55 (1+2+3+...+10)
    
    ; Exit
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 3: Condition-Tested Loops**

### **While Loop**

**C Equivalent:**
```c
while (condition) {
    // body
}
```

**Assembly:**
```nasm
while_start:
    ; Test condition FIRST
    test rax, rax
    jz while_end            ; Exit if condition false
    
    ; Loop body
    ; ... modify variables ...
    
    jmp while_start         ; Loop back

while_end:
```

**Example: While Not Empty**

```nasm
; Process array elements while not zero
section .data
    array dd 5, 10, 0, 15, 20  ; Terminates at first zero

section .text
    mov rsi, array          ; Pointer to array
    xor rax, rax            ; Sum = 0

while_loop:
    cmp dword [rsi], 0      ; Check for zero terminator
    je while_done
    
    add eax, [rsi]          ; sum += *ptr
    add rsi, 4              ; ptr++
    jmp while_loop

while_done:
    ; RAX = 15 (5 + 10)
```

### **Do-While Loop**

**C Equivalent:**
```c
do {
    // body
} while (condition);
```

**Assembly:**
```nasm
do_start:
    ; Loop body FIRST
    ; ... code ...
    
    ; Test condition LAST
    test rax, rax
    jnz do_start            ; Continue if condition true
    
    ; Exit loop
```

**Example: Input Validation**

```nasm
; Keep reading until valid input (non-zero)
do_loop:
    ; Read input (simplified)
    mov rax, 0              ; sys_read
    mov rdi, 0              ; stdin
    mov rsi, buffer
    mov rdx, 1
    syscall
    
    ; Check if valid
    cmp byte [buffer], '0'
    je do_loop              ; Repeat if zero
    
    ; Valid input received
```

### **Until Loop (Repeat Until)**

Same as do-while but inverted condition:

```nasm
repeat_start:
    ; Loop body
    ; ...
    
    ; Continue until condition becomes true
    test rax, rax
    jz repeat_start         ; Loop while false
    
    ; Condition is now true, exit
```

---

## **Part 4: The LOOP Instruction**

### **LOOP - Hardware Loop Support**

```nasm
loop label              ; Equivalent to: dec rcx; jnz label
```

**Automatic behavior:**
- Decrements RCX
- Jumps if RCX != 0
- Very compact encoding

**Example:**

```nasm
    mov rcx, 10             ; Loop 10 times

loop_start:
    ; Loop body
    ; ...
    loop loop_start         ; Decrement RCX, jump if != 0
    
    ; RCX is now 0
```

### **LOOP Variants**

```nasm
loope/loopz label       ; Loop while equal/zero AND rcx != 0
loopne/loopnz label     ; Loop while not equal/zero AND rcx != 0
```

**LOOPE Example:**

```nasm
; Find first non-match in strings
    mov rcx, string_len
    mov rsi, string1
    mov rdi, string2

compare_loop:
    mov al, [rsi]
    cmp al, [rdi]
    loopne compare_loop     ; Continue if not equal AND rcx != 0
    
    ; Either found match or reached end
```

### **When to Use LOOP**

**✅ Use LOOP when:**
- Simple counted loop
- RCX is your counter
- No complex exit conditions
- Code clarity matters

**❌ Avoid LOOP when:**
- Need other exit conditions
- RCX needed for other purposes
- Performance critical (modern CPUs: manual loop may be faster)
- Complex loop logic

**Performance Note:**
On modern CPUs (Intel/AMD), `dec rcx; jnz` is often faster than `loop` due to macro-op fusion.

---

## **Part 5: Loop Patterns**

### **Pattern 1: Array Iteration**

```nasm
section .data
    array dd 10, 20, 30, 40, 50
    count equ 5

section .text
    mov rsi, array          ; Pointer to array
    xor rcx, rcx            ; Index = 0

array_loop:
    cmp rcx, count
    jge array_done
    
    ; Access array[rcx]
    mov eax, [rsi + rcx*4]
    
    ; Process element in EAX
    ; ...
    
    inc rcx
    jmp array_loop

array_done:
```

### **Pattern 2: String Traversal**

```nasm
section .data
    string db "Hello", 0

section .text
    mov rsi, string
    xor rcx, rcx            ; Length = 0

strlen_loop:
    cmp byte [rsi + rcx], 0 ; Check for null terminator
    je strlen_done
    
    inc rcx                 ; length++
    jmp strlen_loop

strlen_done:
    ; RCX contains string length
```

### **Pattern 3: Search/Find**

```nasm
; Find value in array
section .data
    array dd 5, 10, 15, 20, 25
    count equ 5
    target dd 15

section .text
    mov edi, [target]
    xor rcx, rcx            ; Index = 0

search_loop:
    cmp rcx, count
    jge not_found           ; Searched entire array
    
    cmp edi, [array + rcx*4]
    je found                ; Match!
    
    inc rcx
    jmp search_loop

found:
    ; Found at index RCX
    mov rax, rcx
    jmp done

not_found:
    mov rax, -1             ; Not found

done:
```

### **Pattern 4: Accumulation**

```nasm
; Sum array elements
section .data
    numbers dd 1, 2, 3, 4, 5
    count equ 5

section .text
    xor rax, rax            ; sum = 0
    xor rcx, rcx            ; index = 0

sum_loop:
    cmp rcx, count
    jge sum_done
    
    add eax, [numbers + rcx*4]  ; sum += numbers[index]
    inc rcx
    jmp sum_loop

sum_done:
    ; RAX contains sum (15)
```

### **Pattern 5: Filter/Count**

```nasm
; Count even numbers in array
section .data
    array dd 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
    count equ 10

section .text
    xor rax, rax            ; even_count = 0
    xor rcx, rcx            ; index = 0

count_loop:
    cmp rcx, count
    jge count_done
    
    mov edx, [array + rcx*4]
    test edx, 1             ; Check if odd (bit 0 set)
    jnz skip_count          ; Skip if odd
    
    inc rax                 ; even_count++

skip_count:
    inc rcx
    jmp count_loop

count_done:
    ; RAX contains count of even numbers (5)
```

---

## **Part 6: Loop Control**

### **Break (Early Exit)**

**C Code:**
```c
for (i = 0; i < 10; i++) {
    if (condition) break;
    // body
}
```

**Assembly:**
```nasm
    xor rcx, rcx

loop_start:
    cmp rcx, 10
    jge loop_end
    
    ; Check break condition
    test rax, rax
    jz break_loop           ; Break if condition met
    
    ; Loop body
    ; ...
    
    inc rcx
    jmp loop_start

break_loop:
    ; Exited early
    
loop_end:
    ; Normal or early exit
```

### **Continue (Skip to Next Iteration)**

**C Code:**
```c
for (i = 0; i < 10; i++) {
    if (condition) continue;
    // body
}
```

**Assembly:**
```nasm
    xor rcx, rcx

loop_start:
    cmp rcx, 10
    jge loop_end
    
    ; Check continue condition
    test rax, rax
    jnz continue_loop       ; Skip body if condition met
    
    ; Loop body (skipped if continue)
    ; ...

continue_loop:
    inc rcx
    jmp loop_start

loop_end:
```

### **Multiple Exit Conditions**

```nasm
; Loop with multiple ways to exit
    xor rcx, rcx

multi_exit_loop:
    ; Exit condition 1: counter limit
    cmp rcx, 100
    jge exit_limit_reached
    
    ; Exit condition 2: found zero
    cmp dword [array + rcx*4], 0
    je exit_zero_found
    
    ; Exit condition 3: error flag
    test byte [error_flag], 1
    jnz exit_error
    
    ; Loop body
    ; ...
    
    inc rcx
    jmp multi_exit_loop

exit_limit_reached:
    mov rax, 1
    jmp done

exit_zero_found:
    mov rax, 2
    jmp done

exit_error:
    mov rax, -1

done:
    ; RAX indicates exit reason
```

---

## **Part 7: Nested Loops**

### **Two-Level Nesting**

**C Code:**
```c
for (i = 0; i < rows; i++) {
    for (j = 0; j < cols; j++) {
        // body
    }
}
```

**Assembly:**
```nasm
    mov rbx, 3              ; rows (outer loop)

outer_loop:
    test rbx, rbx
    jz outer_done
    
    mov rcx, 4              ; cols (inner loop)

inner_loop:
    test rcx, rcx
    jz inner_done
    
    ; Loop body - access [rbx][rcx]
    ; ...
    
    dec rcx
    jmp inner_loop

inner_done:
    dec rbx
    jmp outer_loop

outer_done:
```

### **Matrix Traversal**

```nasm
; Process 3x3 matrix
section .data
    matrix dd 1, 2, 3
           dd 4, 5, 6
           dd 7, 8, 9
    rows equ 3
    cols equ 3

section .text
    xor rbx, rbx            ; row = 0

row_loop:
    cmp rbx, rows
    jge matrix_done
    
    xor rcx, rcx            ; col = 0

col_loop:
    cmp rcx, cols
    jge col_done
    
    ; Calculate offset: (row * cols + col) * 4
    mov rax, rbx
    imul rax, cols
    add rax, rcx
    
    ; Access matrix[row][col]
    mov edx, [matrix + rax*4]
    
    ; Process element in EDX
    ; ...
    
    inc rcx
    jmp col_loop

col_done:
    inc rbx
    jmp row_loop

matrix_done:
```

### **Nested Loop with Break**

```nasm
; Search 2D array, break on first match
    xor rbx, rbx            ; i = 0

outer:
    cmp rbx, rows
    jge not_found_2d
    
    xor rcx, rcx            ; j = 0

inner:
    cmp rcx, cols
    jge inner_done
    
    ; Check for match
    mov rax, rbx
    imul rax, cols
    add rax, rcx
    cmp dword [array + rax*4], target
    je found_2d             ; Break both loops
    
    inc rcx
    jmp inner

inner_done:
    inc rbx
    jmp outer

found_2d:
    ; Found at [rbx][rcx]
    ; ...
    jmp search_done

not_found_2d:
    ; Not found
    
search_done:
```

---

## **Part 8: Loop Optimization**

### **Technique 1: Count Down Instead of Up**

```nasm
; ❌ Count up (longer)
xor rcx, rcx
loop_up:
    cmp rcx, 100
    jge loop_up_done
    ; body
    inc rcx
    jmp loop_up
loop_up_done:

; ✅ Count down (shorter)
mov rcx, 100
loop_down:
    ; body
    dec rcx
    jnz loop_down
```

### **Technique 2: Strength Reduction**

Replace expensive operations with cheaper ones:

```nasm
; ❌ Multiplication in loop
mov rcx, 100
loop_mul:
    mov rax, rcx
    imul rax, 4             ; Expensive!
    ; use RAX
    dec rcx
    jnz loop_mul

; ✅ Addition instead
mov rcx, 100
mov rax, 400                ; Start at end
loop_add:
    sub rax, 4              ; Cheaper!
    ; use RAX
    dec rcx
    jnz loop_add
```

### **Technique 3: Loop Unrolling**

Process multiple iterations at once:

```nasm
; ❌ Normal loop (1 element per iteration)
mov rcx, 100
loop_normal:
    mov eax, [array + rcx*4]
    add [sum], eax
    dec rcx
    jnz loop_normal

; ✅ Unrolled (4 elements per iteration)
mov rcx, 25                 ; 100/4 iterations
loop_unrolled:
    mov eax, [array + rcx*16]       ; element 0
    add eax, [array + rcx*16 + 4]   ; element 1
    add eax, [array + rcx*16 + 8]   ; element 2
    add eax, [array + rcx*16 + 12]  ; element 3
    add [sum], eax
    dec rcx
    jnz loop_unrolled
```

**Benefits:**
- Fewer jumps
- Better instruction pipeline utilization
- Less loop overhead

**Drawbacks:**
- More code size
- Need to handle remainder

### **Technique 4: Pointer Arithmetic**

```nasm
; ❌ Index-based (calculates address each time)
xor rcx, rcx
loop_index:
    cmp rcx, count
    jge done
    mov eax, [array + rcx*4]  ; Calculate address
    inc rcx
    jmp loop_index

; ✅ Pointer-based (increment pointer)
mov rsi, array
mov rcx, count
loop_pointer:
    mov eax, [rsi]          ; Use pointer directly
    add rsi, 4              ; Advance pointer
    dec rcx
    jnz loop_pointer
```

### **Technique 5: Eliminate Invariant Code**

Move code that doesn't change out of loop:

```nasm
; ❌ Calculation inside loop
mov rcx, 100
loop_invariant:
    mov rax, base_address   ; Doesn't change!
    add rax, offset         ; Doesn't change!
    mov edx, [rax + rcx*4]
    dec rcx
    jnz loop_invariant

; ✅ Calculate once before loop
mov rax, base_address
add rax, offset             ; Calculate once
mov rcx, 100
loop_optimized:
    mov edx, [rax + rcx*4]
    dec rcx
    jnz loop_optimized
```

---

## **Part 9: Advanced Loop Techniques**

### **Technique 1: Duff's Device (Partial Unrolling)**

```nasm
; Process array with partial unrolling
    mov rcx, count
    mov rsi, array
    
    ; Calculate remainder
    mov rax, rcx
    and rax, 3              ; remainder = count % 4
    shr rcx, 2              ; iterations = count / 4
    
    ; Handle remainder first
    jmp [remainder_table + rax*8]

remainder_3:
    mov eax, [rsi]
    add rsi, 4
    ; process

remainder_2:
    mov eax, [rsi]
    add rsi, 4
    ; process

remainder_1:
    mov eax, [rsi]
    add rsi, 4
    ; process

remainder_0:
    ; Main unrolled loop
    test rcx, rcx
    jz done

main_loop:
    mov eax, [rsi]          ; 1st
    add rsi, 4
    mov eax, [rsi]          ; 2nd
    add rsi, 4
    mov eax, [rsi]          ; 3rd
    add rsi, 4
    mov eax, [rsi]          ; 4th
    add rsi, 4
    
    dec rcx
    jnz main_loop

done:
```

### **Technique 2: Sentinel Values**

```nasm
; Search without bounds checking
section .data
    array dd 5, 10, 15, 20, 9999  ; Sentinel at end

section .text
    mov edi, 15             ; Search for 15
    mov rsi, array

search_sentinel:
    cmp dword [rsi], edi
    je found_sentinel       ; No bounds check needed!
    add rsi, 4
    jmp search_sentinel

found_sentinel:
    ; Check if we found sentinel or actual value
    cmp dword [rsi], 9999
    je not_found_sentinel
    ; Found the value
```

### **Technique 3: Loop Reversal**

```nasm
; Sometimes reversing loop order improves cache performance
; Forward (may cause cache misses in some scenarios)
loop_forward:
    ; Access array[i]
    ; Access other_array[i]

; Backward (better cache locality in some cases)
mov rcx, count
loop_backward:
    dec rcx
    ; Access array[rcx]
    ; Access other_array[rcx]
    test rcx, rcx
    jnz loop_backward
```

---

## **Part 10: Practical Examples**

### **Example 1: Bubble Sort**

**C Equivalent:**
```c
#include <stdint.h>

void bubble_sort(int32_t *array, int32_t count) {
    for (int32_t i = count - 1; i > 0; i--) {
        for (int32_t j = 0; j < i; j++) {
            if (array[j] > array[j + 1]) {
                // Swap
                int32_t temp = array[j];
                array[j] = array[j + 1];
                array[j + 1] = temp;
            }
        }
    }
}

int main() {
    int32_t array[] = {64, 34, 25, 12, 22, 11, 90};
    int32_t count = 7;
    
    bubble_sort(array, count);
    // array is now: {11, 12, 22, 25, 34, 64, 90}
    
    return 0;
}
```

**Assembly:**
```nasm
section .data
    array dd 64, 34, 25, 12, 22, 11, 90
    count equ 7

section .text
    global _start

_start:
    ; Bubble sort
    mov rbx, count
    dec rbx                 ; outer loop: n-1 passes

outer_sort:
    test rbx, rbx
    jz sort_done
    
    xor rcx, rcx            ; inner loop: compare adjacent

inner_sort:
    cmp rcx, rbx
    jge inner_done
    
    ; Compare array[rcx] with array[rcx+1]
    mov eax, [array + rcx*4]
    mov edx, [array + rcx*4 + 4]
    cmp eax, edx
    jle no_swap
    
    ; Swap
    mov [array + rcx*4], edx
    mov [array + rcx*4 + 4], eax

no_swap:
    inc rcx
    jmp inner_sort

inner_done:
    dec rbx
    jmp outer_sort

sort_done:
    ; Array is now sorted
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 2: String Copy**

**C Equivalent:**
```c
#include <stdint.h>

void my_strcpy(char *dest, const char *source) {
    while (*source != '\0') {
        *dest = *source;
        dest++;
        source++;
    }
    *dest = '\0';  // Copy null terminator
}

int main() {
    const char *source = "Hello, World!";
    char dest[50];
    
    my_strcpy(dest, source);
    // dest now contains "Hello, World!"
    
    return 0;
}
```

**Assembly:**
```nasm
section .data
    source db "Hello, World!", 0

section .bss
    dest resb 50

section .text
    global _start

_start:
    ; strcpy
    mov rsi, source
    mov rdi, dest

strcpy_loop:
    mov al, [rsi]
    mov [rdi], al
    
    test al, al             ; Check for null terminator
    jz strcpy_done
    
    inc rsi
    inc rdi
    jmp strcpy_loop

strcpy_done:
    ; String copied
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 3: Fibonacci Sequence**

**C Equivalent:**
```c
#include <stdint.h>

void calculate_fibonacci(int32_t *fib, int32_t count) {
    fib[0] = 0;
    fib[1] = 1;
    
    for (int32_t i = 2; i < count; i++) {
        fib[i] = fib[i - 1] + fib[i - 2];
    }
}

int main() {
    int32_t fibonacci[10];
    
    calculate_fibonacci(fibonacci, 10);
    // fibonacci array contains: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
    
    return 0;
}
```

**Assembly:**
```nasm
; Calculate first 10 Fibonacci numbers
section .bss
    fibonacci resd 10

section .text
    global _start

_start:
    ; fib[0] = 0, fib[1] = 1
    mov dword [fibonacci], 0
    mov dword [fibonacci + 4], 1
    
    mov rcx, 2              ; Start from index 2

fib_loop:
    cmp rcx, 10
    jge fib_done
    
    ; fib[n] = fib[n-1] + fib[n-2]
    mov eax, [fibonacci + rcx*4 - 4]   ; fib[n-1]
    add eax, [fibonacci + rcx*4 - 8]   ; + fib[n-2]
    mov [fibonacci + rcx*4], eax
    
    inc rcx
    jmp fib_loop

fib_done:
    ; fibonacci array contains: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 4: Prime Sieve (Sieve of Eratosthenes)**

```nasm
section .bss
    sieve resb 101          ; Sieve for numbers 0-100

section .text
    global _start

_start:
    ; Initialize sieve (1 = prime, 0 = composite)
    mov rdi, sieve
    mov rcx, 101
    mov al, 1
    rep stosb               ; Fill with 1s
    
    ; 0 and 1 are not prime
    mov byte [sieve], 0
    mov byte [sieve + 1], 0
    
    ; Sieve algorithm
    mov rbx, 2              ; Start with 2

sieve_outer:
    cmp rbx, 10             ; Only need to check up to sqrt(100)
    jg sieve_done
    
    ; Skip if already marked composite
    cmp byte [sieve + rbx], 0
    je sieve_next_outer
    
    ; Mark multiples of rbx as composite
    mov rcx, rbx
    add rcx, rbx            ; Start at 2*rbx

sieve_inner:
    cmp rcx, 100
    jg sieve_inner_done
    
    mov byte [sieve + rcx], 0  ; Mark as composite
    add rcx, rbx               ; Next multiple
    jmp sieve_inner

sieve_inner_done:
sieve_next_outer:
    inc rbx
    jmp sieve_outer

sieve_done:
    ; sieve array now contains 1 for primes, 0 for composites
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 5: Matrix Multiplication**

```nasm
; Multiply two 2x2 matrices
section .data
    matrixA dd 1, 2
            dd 3, 4
    matrixB dd 5, 6
            dd 7, 8

section .bss
    result resd 4           ; 2x2 result matrix

section .text
    global _start

_start:
    xor rbx, rbx            ; row = 0

mat_row:
    cmp rbx, 2
    jge mat_done
    
    xor rcx, rcx            ; col = 0

mat_col:
    cmp rcx, 2
    jge mat_col_done
    
    ; Calculate result[row][col] = sum of A[row][k] * B[k][col]
    xor eax, eax            ; sum = 0
    xor rdx, rdx            ; k = 0

mat_inner:
    cmp rdx, 2
    jge mat_inner_done
    
    ; Get A[row][k]
    mov rsi, rbx
    shl rsi, 1              ; row * 2
    add rsi, rdx
    mov edi, [matrixA + rsi*4]
    
    ; Get B[k][col]
    mov rsi, rdx
    shl rsi, 1              ; k * 2
    add rsi, rcx
    imul edi, [matrixB + rsi*4]
    
    ; sum += A[row][k] * B[k][col]
    add eax, edi
    
    inc rdx
    jmp mat_inner

mat_inner_done:
    ; Store result[row][col]
    mov rsi, rbx
    shl rsi, 1
    add rsi, rcx
    mov [result + rsi*4], eax
    
    inc rcx
    jmp mat_col

mat_col_done:
    inc rbx
    jmp mat_row

mat_done:
    ; result now contains: 19 22
    ;                      43 50
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## **✅ Practice Exercises**

### **Exercise 1: Factorial**

Calculate factorial of 5 using a loop.

<details>
<summary>Solution</summary>

```nasm
mov rax, 1              ; result = 1
mov rcx, 5              ; n = 5

factorial_loop:
    imul rax, rcx       ; result *= n
    dec rcx             ; n--
    jnz factorial_loop
    
; RAX = 120 (5!)
```
</details>

### **Exercise 2: Reverse Array**

Reverse an array in place.

<details>
<summary>Solution</summary>

```nasm
section .data
    array dd 1, 2, 3, 4, 5
    count equ 5

section .text
    xor rcx, rcx            ; left = 0
    mov rdx, count
    dec rdx                 ; right = count - 1

reverse_loop:
    cmp rcx, rdx
    jge reverse_done
    
    ; Swap array[left] with array[right]
    mov eax, [array + rcx*4]
    mov ebx, [array + rdx*4]
    mov [array + rcx*4], ebx
    mov [array + rdx*4], eax
    
    inc rcx                 ; left++
    dec rdx                 ; right--
    jmp reverse_loop

reverse_done:
; array is now: 5, 4, 3, 2, 1
```
</details>

### **Exercise 3: Count Vowels**

Count vowels (a,e,i,o,u) in a string.

<details>
<summary>Solution</summary>

```nasm
section .data
    string db "Hello World", 0

section .text
    mov rsi, string
    xor rax, rax            ; count = 0

vowel_loop:
    mov cl, [rsi]
    test cl, cl
    jz vowel_done
    
    ; Check lowercase vowels
    cmp cl, 'a'
    je is_vowel
    cmp cl, 'e'
    je is_vowel
    cmp cl, 'i'
    je is_vowel
    cmp cl, 'o'
    je is_vowel
    cmp cl, 'u'
    je is_vowel
    jmp next_char

is_vowel:
    inc rax

next_char:
    inc rsi
    jmp vowel_loop

vowel_done:
; RAX = 3 (e, o, o)
```
</details>

### **Exercise 4: GCD (Greatest Common Divisor)**

Implement Euclid's algorithm with a loop.

<details>
<summary>Solution</summary>

```nasm
; GCD(48, 18) using Euclidean algorithm
mov rax, 48
mov rbx, 18

gcd_loop:
    test rbx, rbx
    jz gcd_done
    
    ; temp = a % b
    xor rdx, rdx
    div rbx
    
    ; a = b, b = temp
    mov rax, rbx
    mov rbx, rdx
    jmp gcd_loop

gcd_done:
; RAX = 6 (GCD of 48 and 18)
```
</details>

### **Exercise 5: Sum of Digits**

Calculate sum of digits of a number.

<details>
<summary>Solution</summary>

```nasm
; Sum digits of 12345
mov rax, 12345
xor rbx, rbx            ; sum = 0

digit_loop:
    test rax, rax
    jz digit_done
    
    ; Get last digit
    xor rdx, rdx
    mov rcx, 10
    div rcx             ; RAX = number / 10, RDX = digit
    
    add rbx, rdx        ; sum += digit
    jmp digit_loop

digit_done:
; RBX = 15 (1+2+3+4+5)
```
</details>

---

## **📋 Quick Reference**

### **Basic Loop Patterns**

```nasm
; Count down (most efficient)
mov rcx, N
loop_down:
    ; body
    dec rcx
    jnz loop_down

; Count up
xor rcx, rcx
loop_up:
    cmp rcx, N
    jge done
    ; body
    inc rcx
    jmp loop_up
done:

; While
while_start:
    test condition
    jz while_end
    ; body
    jmp while_start
while_end:

; Do-while
do_start:
    ; body
    test condition
    jnz do_start
```

### **Loop Instructions**

```nasm
loop label              ; dec rcx; jnz label
loope label             ; Loop if ZF=1 and RCX!=0
loopne label            ; Loop if ZF=0 and RCX!=0
```

### **Common Optimizations**

- Count down instead of up
- Use pointer arithmetic
- Unroll loops for performance
- Move invariant code outside loop
- Use strength reduction

---

## **🎯 Knowledge Check**

Before moving to Topic 7, verify you understand:
- ✅ Counted loops (for equivalent)
- ✅ Condition-tested loops (while/do-while)
- ✅ LOOP instruction and variants
- ✅ Loop control (break/continue)
- ✅ Nested loops
- ✅ Loop optimization techniques
- ✅ Common loop patterns

---

**🎉 Excellent!** You now master loops in assembly!

**Next:** [Topic 7: Stack Operations](topic-07-stack.md) (coming soon)

---

[← Previous Topic](topic-05-jumps.md) | [Back to Main](../README.md) | Next Topic →

