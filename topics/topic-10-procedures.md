# 📘 Topic 10: Procedures

Master the `call` and `ret` instructions, and learn to write reusable procedures including recursive functions.

---

## **Overview**

A **procedure** (also called a **subroutine** or **function**) is a reusable block of code that can be called from different places in your program.

**Key Concepts:**
- 📞 `call` instruction - jumps to procedure and saves return address
- ↩️  `ret` instruction - returns to caller
- 🔄 Recursion - procedures that call themselves
- 📦 Modularity - breaking programs into manageable pieces

---

## **Part 1: The CALL Instruction**

### **What `call` Does**

```nasm
call procedure_name
```

**Internally, `call` performs two operations:**

```nasm
; call is equivalent to:
push return_address         ; Save where to return to
jmp procedure_name          ; Jump to procedure
```

**Step-by-step:**
1. Push the address of the **next instruction** onto the stack
2. Jump to the procedure's address

---

### **Example: Simple Call**

**C Equivalent:**
```c
void greet() {
    // Print greeting (conceptual)
}

int main() {
    greet();
    // Execution continues here after greet() returns
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global _start

_start:
    call greet              ; Call the procedure
    ; Execution continues here after greet returns
    
    mov rax, 60
    xor rdi, rdi
    syscall

greet:
    ; Do something here
    ret                     ; Return to caller
```

**What happens:**
```
Before call:
RSP → [some_value]
RIP = address of "call greet"

During call:
RSP → [return_address]    ← RSP decremented by 8
RIP = address of greet

After ret:
RSP → [some_value]        ← RSP incremented by 8
RIP = return_address (instruction after call)
```

---

## **Part 2: The RET Instruction**

### **What `ret` Does**

```nasm
ret
```

**Internally, `ret` performs:**

```nasm
; ret is equivalent to:
pop rip                     ; Pop return address into RIP
```

**Step-by-step:**
1. Pop the return address from the stack
2. Jump to that address (continue execution after `call`)

---

### **RET Variants**

```nasm
; Standard return
ret

; Return and pop N bytes from stack (32-bit stdcall)
ret 16                      ; Pop return address, then add 16 to ESP

; Far return (rarely used, different code segment)
retf
```

---

## **Part 3: Simple Procedures**

### **Example 1: Procedure with No Arguments**

**C Equivalent:**
```c
void print_newline() {
    write(1, "\n", 1);
}

int main() {
    print_newline();
    print_newline();
    return 0;
}
```

**Assembly:**
```nasm
section .data
    newline db 10

section .text
    global _start

print_newline:
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    mov rsi, newline        ; "\n"
    mov rdx, 1              ; length
    syscall
    ret

_start:
    call print_newline
    call print_newline
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

### **Example 2: Procedure with Arguments (System V)**

**C Equivalent:**
```c
int square(int x) {
    return x * x;
}

int main() {
    int result = square(5);
    return result;
}
```

**Assembly:**
```nasm
section .text
    global _start

; int square(int x)
; Argument: x in EDI
; Return: result in EAX
square:
    mov eax, edi            ; EAX = x
    imul eax, edi           ; EAX = x * x
    ret

_start:
    mov edi, 5              ; arg: x = 5
    call square
    ; EAX now contains 25
    
    mov rdi, rax            ; exit code = result
    mov rax, 60
    syscall
```

---

### **Example 3: Procedure with Return Value**

**C Equivalent:**
```c
int add_three(int a, int b, int c) {
    return a + b + c;
}

int main() {
    int sum = add_three(10, 20, 30);
    return sum;
}
```

**Assembly:**
```nasm
section .text
    global _start

; int add_three(int a, int b, int c)
; Args: a=EDI, b=ESI, c=EDX
; Return: EAX
add_three:
    lea eax, [rdi + rsi]    ; sum = a + b
    add eax, edx            ; sum += c
    ret

_start:
    mov edi, 10             ; a = 10
    mov esi, 20             ; b = 20
    mov edx, 30             ; c = 30
    call add_three
    ; EAX = 60
    
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 4: Preserving Registers**

### **Callee-Saved Registers**

When a procedure uses callee-saved registers (RBX, RBP, R12-R15), it **must** preserve them.

**C Equivalent:**
```c
int complex_calc(int x) {
    int temp1 = x * 2;      // Might use RBX
    int temp2 = x + 10;     // Might use R12
    return temp1 + temp2;
}
```

**Assembly:**
```nasm
; int complex_calc(int x)
complex_calc:
    ; Save callee-saved registers we'll use
    push rbx
    push r12
    
    ; x is in EDI
    mov ebx, edi
    shl ebx, 1              ; temp1 = x * 2 (in RBX)
    
    lea r12d, [rdi + 10]    ; temp2 = x + 10 (in R12)
    
    lea eax, [rbx + r12]    ; result = temp1 + temp2
    
    ; Restore callee-saved registers (reverse order!)
    pop r12
    pop rbx
    ret
```

**Why it matters:**

```nasm
main:
    mov rbx, 100            ; RBX has important value
    call complex_calc
    ; RBX still contains 100 (procedure preserved it)
```

---

## **Part 5: Local Variables**

### **Allocating Space on Stack**

**C Equivalent:**
```c
int calculate() {
    int local1 = 10;
    int local2 = 20;
    int result = local1 + local2;
    return result;
}
```

**Assembly:**
```nasm
; int calculate()
calculate:
    push rbp
    mov rbp, rsp
    sub rsp, 16             ; Allocate 16 bytes for locals
    
    ; local1 at [rbp-4], local2 at [rbp-8]
    mov dword [rbp - 4], 10     ; local1 = 10
    mov dword [rbp - 8], 20     ; local2 = 20
    
    ; result = local1 + local2
    mov eax, [rbp - 4]
    add eax, [rbp - 8]
    
    mov rsp, rbp            ; Deallocate locals
    pop rbp
    ret
```

---

## **Part 6: Recursion**

### **What is Recursion?**

A procedure that **calls itself** to solve a problem by breaking it into smaller instances.

---

### **Example 1: Factorial**

**C Equivalent:**
```c
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int result = factorial(5);  // result = 120
    return result;
}
```

**Assembly:**
```nasm
section .text
    global _start

; int factorial(int n)
; Arg: n in EDI
; Return: EAX
factorial:
    ; Base case: if n <= 1, return 1
    cmp edi, 1
    jg recursive_case
    
    mov eax, 1              ; return 1
    ret
    
recursive_case:
    ; Save n on stack (RDI is caller-saved, might be clobbered)
    push rdi
    
    ; Recursive call: factorial(n-1)
    dec edi                 ; n-1
    call factorial          ; EAX = factorial(n-1)
    
    ; Restore n
    pop rdi
    
    ; return n * factorial(n-1)
    imul eax, edi           ; EAX = n * factorial(n-1)
    ret

_start:
    mov edi, 5              ; factorial(5)
    call factorial
    ; EAX = 120
    
    mov rdi, rax
    mov rax, 60
    syscall
```

**How it works:**

```
factorial(5)
├─ 5 * factorial(4)
│  ├─ 4 * factorial(3)
│  │  ├─ 3 * factorial(2)
│  │  │  ├─ 2 * factorial(1)
│  │  │  │  └─ returns 1
│  │  │  └─ returns 2 * 1 = 2
│  │  └─ returns 3 * 2 = 6
│  └─ returns 4 * 6 = 24
└─ returns 5 * 24 = 120
```

---

### **Example 2: Fibonacci**

**C Equivalent:**
```c
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    int result = fibonacci(6);  // result = 8
    return result;
}
```

**Assembly:**
```nasm
section .text
    global _start

; int fibonacci(int n)
; Arg: n in EDI
; Return: EAX
fibonacci:
    ; Base case: if n <= 1, return n
    cmp edi, 1
    jg recursive_case
    
    mov eax, edi            ; return n (0 or 1)
    ret
    
recursive_case:
    push rbx                ; Save RBX (callee-saved)
    push rdi                ; Save n
    
    ; fib(n-1)
    dec edi
    call fibonacci
    mov ebx, eax            ; RBX = fib(n-1)
    
    ; fib(n-2)
    pop rdi                 ; Restore n
    sub edi, 2
    call fibonacci          ; EAX = fib(n-2)
    
    ; return fib(n-1) + fib(n-2)
    add eax, ebx
    
    pop rbx                 ; Restore RBX
    ret

_start:
    mov edi, 6              ; fibonacci(6)
    call fibonacci
    ; EAX = 8 (sequence: 0,1,1,2,3,5,8)
    
    mov rdi, rax
    mov rax, 60
    syscall
```

---

### **Example 3: String Length (Recursive)**

**C Equivalent:**
```c
int strlen_recursive(const char *str) {
    if (*str == '\0') {
        return 0;
    }
    return 1 + strlen_recursive(str + 1);
}

int main() {
    const char *text = "Hello";
    int len = strlen_recursive(text);  // len = 5
    return len;
}
```

**Assembly:**
```nasm
section .data
    text db "Hello", 0

section .text
    global _start

; int strlen_recursive(const char *str)
; Arg: str in RDI
; Return: EAX
strlen_recursive:
    ; Base case: if (*str == 0), return 0
    cmp byte [rdi], 0
    jne recursive_case
    
    xor eax, eax            ; return 0
    ret
    
recursive_case:
    push rdi                ; Save str
    
    inc rdi                 ; str + 1
    call strlen_recursive   ; EAX = strlen(str+1)
    
    pop rdi                 ; Restore str (not actually needed)
    
    inc eax                 ; return 1 + strlen(str+1)
    ret

_start:
    mov rdi, text           ; arg = "Hello"
    call strlen_recursive
    ; EAX = 5
    
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 7: Nested Calls**

Procedures can call other procedures:

**C Equivalent:**
```c
int helper(int x) {
    return x * 2;
}

int calculate(int a, int b) {
    int temp = helper(a);
    return temp + b;
}

int main() {
    int result = calculate(5, 10);  // result = 20
    return result;
}
```

**Assembly:**
```nasm
section .text
    global _start

; int helper(int x)
helper:
    lea eax, [rdi + rdi]    ; return x * 2
    ret

; int calculate(int a, int b)
; Args: a=EDI, b=ESI
calculate:
    push rbx                ; Save RBX (we'll use it for b)
    mov ebx, esi            ; Save b in RBX
    
    ; temp = helper(a)
    ; EDI already has a
    call helper             ; EAX = helper(a)
    
    ; return temp + b
    add eax, ebx
    
    pop rbx
    ret

_start:
    mov edi, 5              ; a = 5
    mov esi, 10             ; b = 10
    call calculate
    ; EAX = 20
    
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 8: Leaf vs Non-Leaf Procedures**

### **Leaf Procedure**

A procedure that **doesn't call other procedures** (and doesn't need a stack frame).

```nasm
; Leaf procedure - simple and fast
add_numbers:
    lea eax, [rdi + rsi]
    ret                     ; No prologue/epilogue needed
```

### **Non-Leaf Procedure**

A procedure that **calls other procedures** (needs to save return address protection).

```nasm
; Non-leaf procedure
outer:
    push rbp
    mov rbp, rsp
    
    call inner              ; Calls another procedure
    
    mov rsp, rbp
    pop rbp
    ret
```

---

## **Part 9: Tail Call Optimization**

When the last thing a procedure does is call another procedure, you can optimize by replacing `call` + `ret` with just `jmp`.

**Without optimization:**
```nasm
wrapper:
    ; Setup...
    call actual_work
    ret                     ; Immediately return after call
```

**With tail call optimization:**
```nasm
wrapper:
    ; Setup...
    jmp actual_work         ; Jump instead of call
                            ; actual_work will return directly to our caller
```

**C Example:**
```c
int factorial_tail(int n, int accumulator) {
    if (n <= 1) {
        return accumulator;
    }
    return factorial_tail(n - 1, n * accumulator);  // Tail call
}
```

**Assembly (optimized):**
```nasm
; int factorial_tail(int n, int accumulator)
; Args: n=EDI, accumulator=ESI
factorial_tail:
    cmp edi, 1
    jle base_case
    
    ; Tail call: factorial_tail(n-1, n*accumulator)
    imul esi, edi           ; accumulator *= n
    dec edi                 ; n--
    jmp factorial_tail      ; Tail call (no call/ret overhead!)
    
base_case:
    mov eax, esi
    ret
```

---

## **Part 10: Common Patterns**

### **Pattern 1: Standard Prologue/Epilogue**

```nasm
procedure:
    ; Prologue
    push rbp
    mov rbp, rsp
    sub rsp, N              ; Allocate N bytes for locals
    
    ; Body
    ; ... procedure code ...
    
    ; Epilogue
    mov rsp, rbp            ; or: add rsp, N
    pop rbp
    ret
```

---

### **Pattern 2: Minimal (Leaf Procedure)**

```nasm
leaf_procedure:
    ; No prologue needed
    
    ; Body (doesn't call others, no locals)
    ; ... simple computation ...
    
    ; Return
    ret
```

---

### **Pattern 3: Save/Restore Callee-Saved**

```nasm
procedure:
    push rbx
    push r12
    push r13
    
    ; Use RBX, R12, R13
    
    pop r13
    pop r12
    pop rbx
    ret
```

---

## **Part 11: Debugging Procedures**

### **GDB Commands**

```bash
gdb ./program

# Set breakpoint at procedure
(gdb) break my_procedure

# Step into call
(gdb) step

# Step over call
(gdb) next

# View stack frames
(gdb) backtrace

# View current frame
(gdb) frame

# View arguments
(gdb) info args

# View locals
(gdb) info locals

# View return address
(gdb) x/xg $rsp
```

---

## **✅ Practice Exercises**

### **Exercise 1: Write a Procedure**

Write a procedure that returns the maximum of two integers.

```c
int max(int a, int b) {
    return (a > b) ? a : b;
}
```

<details>
<summary>Solution</summary>

```nasm
; int max(int a, int b)
; Args: a=EDI, b=ESI
; Return: EAX
max:
    cmp edi, esi
    jg return_a
    
    mov eax, esi            ; return b
    ret
    
return_a:
    mov eax, edi            ; return a
    ret
```
</details>

---

### **Exercise 2: Recursive Sum**

Write a recursive procedure that sums integers from 1 to n.

```c
int sum_to_n(int n) {
    if (n <= 0) return 0;
    return n + sum_to_n(n - 1);
}
```

<details>
<summary>Solution</summary>

```nasm
; int sum_to_n(int n)
; Arg: n in EDI
; Return: EAX
sum_to_n:
    test edi, edi
    jle base_case
    
    push rdi                ; Save n
    dec edi
    call sum_to_n           ; EAX = sum_to_n(n-1)
    pop rdi
    
    add eax, edi            ; return n + sum_to_n(n-1)
    ret
    
base_case:
    xor eax, eax
    ret
```
</details>

---

### **Exercise 3: Fix the Bug**

What's wrong with this recursive procedure?

```nasm
countdown:
    test edi, edi
    jz done
    
    dec edi
    call countdown          ; ❌ BUG!
    
done:
    ret
```

<details>
<summary>Solution</summary>

The procedure doesn't preserve RDI, which is caller-saved. After the recursive call, RDI might be modified.

```nasm
countdown:
    test edi, edi
    jz done
    
    push rdi                ; ✓ Save RDI
    dec edi
    call countdown
    pop rdi                 ; ✓ Restore (though not needed here)
    
done:
    ret
```
</details>

---

## **📋 Quick Reference**

### **Call/Ret Mechanics**
```nasm
call proc       ; push rip; jmp proc
ret             ; pop rip
ret N           ; pop rip; add rsp, N (32-bit)
```

### **Standard Pattern**
```nasm
procedure:
    push rbp
    mov rbp, rsp
    sub rsp, 16         ; locals
    push rbx            ; save regs
    
    ; ... body ...
    
    pop rbx             ; restore
    mov rsp, rbp
    pop rbp
    ret
```

### **Recursion Checklist**
- ✅ Base case (termination condition)
- ✅ Save arguments if needed
- ✅ Recursive call with modified argument
- ✅ Combine result properly
- ✅ Restore saved values

---

## **🎯 Knowledge Check**

Before moving to Topic 11, verify you understand:
- ✅ What `call` and `ret` do internally
- ✅ How the stack stores return addresses
- ✅ Writing procedures with arguments and return values
- ✅ Preserving callee-saved registers
- ✅ Allocating local variables on the stack
- ✅ Recursive procedures and base cases
- ✅ Tail call optimization
- ✅ Leaf vs non-leaf procedures

---

**🎉 Excellent!** You now understand procedures!

**Next:** Topic 11: Memory Addressing Modes

---

[← Previous Topic](topic-09-calling-conventions.md) | [Back to Main](../README.md) | [Next Topic →](topic-11-memory-addressing.md)

