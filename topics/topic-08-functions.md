# 📘 Topic 8: Functions & Procedures

Master function creation, calling conventions, and advanced procedural programming techniques.

---

## **Overview**

Functions (also called procedures or subroutines) are the building blocks of modular code. In this topic, you'll learn:
- 🔄 CALL and RET instructions
- 📋 System V AMD64 calling convention (Linux)
- 📦 Parameter passing and return values
- 🔗 Linking with external code
- 🎯 Advanced function techniques

---

## **Part 1: CALL and RET Instructions**

### **CALL Instruction**

```nasm
call label              ; Call function at label
call register           ; Call function at address in register
call [memory]           ; Call function at address in memory
```

**What CALL Does:**
```nasm
call my_function

; Equivalent to:
push rip + 5            ; Push return address (address of next instruction)
jmp my_function         ; Jump to function
```

### **RET Instruction**

```nasm
ret                     ; Return from function
ret N                   ; Return and pop N bytes from stack (rare in 64-bit)
```

**What RET Does:**
```nasm
ret

; Equivalent to:
pop rip                 ; Pop return address and jump to it
```

### **Simple Example**

**C Equivalent:**
```c
void greet() {
    // Function body
}

int main() {
    greet();  // Call function
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global _start

greet:
    ; Function body
    ; ... do something ...
    ret                     ; Return to caller

_start:
    call greet              ; Call function
    ; Execution continues here after greet() returns
    
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## **Part 2: System V AMD64 Calling Convention**

### **Register Usage**

```
┌──────────────────────────────────────────────────────────┐
│  FUNCTION ARGUMENTS (in order)                           │
│  1st: RDI    2nd: RSI    3rd: RDX                        │
│  4th: RCX    5th: R8     6th: R9                         │
│  7+:  Stack (right-to-left)                              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  RETURN VALUE                                            │
│  RAX (integer/pointer)                                   │
│  RDX:RAX (128-bit values)                                │
│  XMM0 (floating point)                                   │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  CALLER-SAVED (Volatile)                                 │
│  Function can modify without saving                      │
│  RAX, RCX, RDX, RSI, RDI, R8-R11                         │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  CALLEE-SAVED (Non-volatile)                             │
│  Function must preserve (save and restore)               │
│  RBX, RBP, R12-R15                                       │
│  RSP (always!)                                           │
└──────────────────────────────────────────────────────────┘
```

### **Complete Function Template**

**C Equivalent:**
```c
int my_function(int arg1, int arg2, int arg3) {
    // Compiler handles:
    // - Saving callee-saved registers
    // - Setting up stack frame
    // - Accessing arguments
    // - Returning value in RAX
    
    return arg1 + arg2 + arg3;
}
```

**Assembly:**
```nasm
my_function:
    ; === PROLOGUE ===
    push rbp                    ; Save frame pointer
    mov rbp, rsp                ; Set up new frame
    push rbx                    ; Save callee-saved registers
    push r12
    push r13
    sub rsp, 8                  ; Align stack to 16 bytes
    
    ; === FUNCTION BODY ===
    ; Arguments arrive in: RDI, RSI, RDX, RCX, R8, R9
    ; Use them or save them if needed
    
    mov rax, rdi                ; arg1
    add rax, rsi                ; + arg2
    add rax, rdx                ; + arg3
    
    ; === EPILOGUE ===
    add rsp, 8                  ; Deallocate locals
    pop r13                     ; Restore in reverse order
    pop r12
    pop rbx
    pop rbp
    ret                         ; Return (value in RAX)
```

---

## **Part 3: Parameter Passing**

### **Example 1: Six or Fewer Parameters**

**C Equivalent:**
```c
int add_six(int a, int b, int c, int d, int e, int f) {
    return a + b + c + d + e + f;
}

int main() {
    int result = add_six(1, 2, 3, 4, 5, 6);
    return result;  // 21
}
```

**Assembly:**
```nasm
section .text
    global add_six

add_six:
    ; Arguments: RDI=a, RSI=b, RDX=c, RCX=d, R8=e, R9=f
    mov rax, rdi
    add rax, rsi
    add rax, rdx
    add rax, rcx
    add rax, r8
    add rax, r9
    ret

main:
    mov rdi, 1                  ; arg1
    mov rsi, 2                  ; arg2
    mov rdx, 3                  ; arg3
    mov rcx, 4                  ; arg4
    mov r8, 5                   ; arg5
    mov r9, 6                   ; arg6
    call add_six                ; RAX = 21
    
    mov rdi, rax
    mov rax, 60
    syscall
```

### **Example 2: More Than Six Parameters**

**C Equivalent:**
```c
int add_many(int a, int b, int c, int d, int e, int f, int g, int h) {
    return a + b + c + d + e + f + g + h;
}

int main() {
    int result = add_many(1, 2, 3, 4, 5, 6, 7, 8);
    return result;  // 36
}
```

**Assembly:**
```nasm
section .text
    global add_many

add_many:
    ; RDI=a, RSI=b, RDX=c, RCX=d, R8=e, R9=f
    ; [rbp + 16]=g, [rbp + 24]=h (on stack)
    
    push rbp
    mov rbp, rsp
    
    mov rax, rdi                ; a
    add rax, rsi                ; + b
    add rax, rdx                ; + c
    add rax, rcx                ; + d
    add rax, r8                 ; + e
    add rax, r9                 ; + f
    add rax, [rbp + 16]         ; + g (7th arg on stack)
    add rax, [rbp + 24]         ; + h (8th arg on stack)
    
    pop rbp
    ret

main:
    ; First 6 args in registers
    mov rdi, 1
    mov rsi, 2
    mov rdx, 3
    mov rcx, 4
    mov r8, 5
    mov r9, 6
    
    ; 7th and 8th args on stack (push in reverse order!)
    push 8                      ; 8th arg
    push 7                      ; 7th arg
    
    call add_many               ; RAX = 36
    
    add rsp, 16                 ; Clean up stack (2 args × 8 bytes)
    
    mov rdi, rax
    mov rax, 60
    syscall
```

### **Stack Layout for 7+ Arguments**

```
Before CALL add_many:
┌──────────────┐
│  8 (arg 8)   │ ← RSP + 8
├──────────────┤
│  7 (arg 7)   │ ← RSP
└──────────────┘

After CALL (inside function):
┌──────────────┐
│  8 (arg 8)   │ ← RBP + 24
├──────────────┤
│  7 (arg 7)   │ ← RBP + 16
├──────────────┤
│  Return Addr │ ← RBP + 8
├──────────────┤
│  Saved RBP   │ ← RBP, RSP
└──────────────┘
```

---

## **Part 4: Return Values**

### **Single Integer Return**

**C Equivalent:**
```c
int get_value() {
    return 42;
}
```

**Assembly:**
```nasm
get_value:
    mov rax, 42
    ret
```

### **Large Value Return (128-bit)**

**C Equivalent:**
```c
#include <stdint.h>

typedef struct {
    uint64_t low;
    uint64_t high;
} uint128_t;

uint128_t get_large_value() {
    uint128_t result = {0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0};
    return result;
}
```

**Assembly:**
```nasm
get_large_value:
    ; Return 128-bit value in RDX:RAX
    mov rax, 0xFFFFFFFFFFFFFFFF    ; Low 64 bits
    mov rdx, 0x123456789ABCDEF0    ; High 64 bits
    ret
```

### **Pointer Return**

**C Equivalent:**
```c
char* get_message() {
    static char msg[] = "Hello!";
    return msg;
}
```

**Assembly:**
```nasm
section .data
    message db "Hello!", 0

section .text
get_message:
    mov rax, message            ; Return pointer in RAX
    ret
```

### **Boolean Return**

**C Equivalent:**
```c
#include <stdbool.h>

bool is_even(int n) {
    return (n & 1) == 0;
}
```

**Assembly:**
```nasm
is_even:
    ; RDI = n
    mov rax, rdi
    and rax, 1                  ; n & 1
    xor rax, 1                  ; Return 1 if even, 0 if odd
    ret                         ; Or: setz al to get 0/1
```

---

## **Part 5: Local Variables**

### **Allocating Local Variables**

**C Equivalent:**
```c
int compute(int x, int y) {
    int a = x + y;
    int b = x - y;
    int c = a * b;
    return c;
}
```

**Assembly:**
```nasm
compute:
    ; RDI = x, RSI = y
    push rbp
    mov rbp, rsp
    sub rsp, 32                 ; Allocate space for locals (aligned)
    
    ; int a = x + y
    mov eax, edi
    add eax, esi
    mov [rbp - 4], eax          ; a
    
    ; int b = x - y
    mov eax, edi
    sub eax, esi
    mov [rbp - 8], eax          ; b
    
    ; int c = a * b
    mov eax, [rbp - 4]
    imul eax, [rbp - 8]
    mov [rbp - 12], eax         ; c
    
    ; return c
    mov eax, [rbp - 12]
    
    leave
    ret
```

### **Optimized Version (Registers Only)**

**Assembly:**
```nasm
compute:
    ; RDI = x, RSI = y
    
    ; a = x + y
    lea eax, [rdi + rsi]        ; a in EAX
    
    ; b = x - y
    mov ecx, edi
    sub ecx, esi                ; b in ECX
    
    ; c = a * b
    imul eax, ecx               ; c in EAX
    
    ret                         ; Return c
```

---

## **Part 6: Recursive Functions**

### **Example: Fibonacci**

**C Equivalent:**
```c
int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    int result = fibonacci(10);  // 55
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global fibonacci

fibonacci:
    ; RDI = n
    push rbp
    mov rbp, rsp
    push rbx                    ; Save RBX (will use it)
    push r12                    ; Save R12 (will use it)
    
    ; Base case: if (n <= 1) return n
    cmp rdi, 1
    jg recursive_case
    mov rax, rdi                ; return n
    jmp fib_done
    
recursive_case:
    mov rbx, rdi                ; Save n
    
    ; Calculate fib(n-1)
    dec rdi                     ; n - 1
    call fibonacci              ; RAX = fib(n-1)
    mov r12, rax                ; Save result
    
    ; Calculate fib(n-2)
    lea rdi, [rbx - 2]          ; n - 2
    call fibonacci              ; RAX = fib(n-2)
    
    ; Return fib(n-1) + fib(n-2)
    add rax, r12
    
fib_done:
    pop r12
    pop rbx
    pop rbp
    ret

main:
    mov rdi, 10
    call fibonacci              ; RAX = 55
    
    mov rdi, rax
    mov rax, 60
    syscall
```

### **Tail Recursion Optimization**

**C Equivalent:**
```c
// Tail-recursive factorial
int factorial_helper(int n, int acc) {
    if (n <= 1) return acc;
    return factorial_helper(n - 1, n * acc);  // Tail call
}

int factorial(int n) {
    return factorial_helper(n, 1);
}
```

**Assembly:**
```nasm
factorial_helper:
    ; RDI = n, RSI = acc
    
tail_recursion_loop:
    cmp rdi, 1
    jle base_case
    
    ; acc = n * acc
    imul rsi, rdi
    
    ; n = n - 1
    dec rdi
    
    ; Tail call optimization: JMP instead of CALL
    jmp tail_recursion_loop     ; No stack growth!
    
base_case:
    mov rax, rsi                ; return acc
    ret

factorial:
    ; RDI = n
    mov rsi, 1                  ; acc = 1
    jmp factorial_helper        ; Tail call
```

---

## **Part 7: Function Pointers**

### **Calling Through Function Pointer**

**C Equivalent:**
```c
typedef int (*operation_t)(int, int);

int add(int a, int b) { return a + b; }
int sub(int a, int b) { return a - b; }

int apply(operation_t op, int a, int b) {
    return op(a, b);
}

int main() {
    int result1 = apply(add, 10, 5);  // 15
    int result2 = apply(sub, 10, 5);  // 5
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global add, sub, apply

add:
    ; RDI = a, RSI = b
    lea rax, [rdi + rsi]
    ret

sub:
    ; RDI = a, RSI = b
    mov rax, rdi
    sub rax, rsi
    ret

apply:
    ; RDI = function pointer, RSI = a, RDX = b
    push rbp
    mov rbp, rsp
    
    ; Move arguments
    mov rcx, rdi                ; Save function pointer
    mov rdi, rsi                ; arg1 = a
    mov rsi, rdx                ; arg2 = b
    
    ; Call through pointer
    call rcx                    ; call [function pointer]
    
    pop rbp
    ret

main:
    ; apply(add, 10, 5)
    mov rdi, add                ; Function pointer
    mov rsi, 10                 ; a
    mov rdx, 5                  ; b
    call apply                  ; RAX = 15
    
    ; apply(sub, 10, 5)
    mov rdi, sub
    mov rsi, 10
    mov rdx, 5
    call apply                  ; RAX = 5
    
    xor rdi, rdi
    mov rax, 60
    syscall
```

---

## **Part 8: Variadic Functions**

### **Variable Arguments (C-style)**

**C Equivalent:**
```c
#include <stdarg.h>

int sum_all(int count, ...) {
    va_list args;
    va_start(args, count);
    
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += va_arg(args, int);
    }
    
    va_end(args);
    return sum;
}

int main() {
    int result = sum_all(4, 10, 20, 30, 40);  // 100
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global sum_all

sum_all:
    ; RDI = count, RSI, RDX, RCX, R8, R9 = first 5 args
    ; More args on stack
    
    push rbp
    mov rbp, rsp
    
    xor rax, rax                ; sum = 0
    test rdi, rdi
    jz done                     ; if count == 0, return
    
    mov r10, rdi                ; counter
    
    ; First arg
    add rax, rsi
    dec r10
    jz done
    
    ; Second arg
    add rax, rdx
    dec r10
    jz done
    
    ; Third arg
    add rax, rcx
    dec r10
    jz done
    
    ; Fourth arg
    add rax, r8
    dec r10
    jz done
    
    ; Fifth arg
    add rax, r9
    dec r10
    jz done
    
    ; Remaining args on stack
    lea r11, [rbp + 16]         ; Start of stack args
    
sum_stack_args:
    add rax, [r11]
    add r11, 8
    dec r10
    jnz sum_stack_args
    
done:
    pop rbp
    ret

main:
    mov rdi, 4                  ; count
    mov rsi, 10                 ; arg1
    mov rdx, 20                 ; arg2
    mov rcx, 30                 ; arg3
    mov r8, 40                  ; arg4
    call sum_all                ; RAX = 100
    
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 9: Interfacing with C**

### **Calling C Functions from Assembly**

**C code (mylib.c):**
```c
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void print_number(int n) {
    printf("Number: %d\n", n);
}
```

**Assembly (main.asm):**
```nasm
section .text
    extern add, print_number
    global main

main:
    push rbp
    mov rbp, rsp
    
    ; Call add(10, 20)
    mov rdi, 10
    mov rsi, 20
    call add                    ; RAX = 30
    
    ; Call print_number(result)
    mov rdi, rax
    call print_number           ; Prints "Number: 30"
    
    xor eax, eax                ; return 0
    pop rbp
    ret
```

**Build:**
```bash
gcc -c mylib.c -o mylib.o
nasm -f elf64 main.asm -o main.o
gcc mylib.o main.o -o program -no-pie
./program
```

### **Calling Assembly from C**

**Assembly (functions.asm):**
```nasm
section .text
    global multiply, power

multiply:
    ; int multiply(int a, int b)
    ; RDI = a, RSI = b
    mov rax, rdi
    imul rax, rsi
    ret

power:
    ; int power(int base, int exp)
    ; RDI = base, RSI = exp
    mov rax, 1
    test rsi, rsi
    jz power_done
    
power_loop:
    imul rax, rdi
    dec rsi
    jnz power_loop
    
power_done:
    ret
```

**C code (main.c):**
```c
#include <stdio.h>

// Declare assembly functions
extern int multiply(int a, int b);
extern int power(int base, int exp);

int main() {
    int result1 = multiply(6, 7);       // 42
    int result2 = power(2, 10);         // 1024
    
    printf("6 * 7 = %d\n", result1);
    printf("2^10 = %d\n", result2);
    
    return 0;
}
```

**Build:**
```bash
nasm -f elf64 functions.asm -o functions.o
gcc main.c functions.o -o program
./program
```

---

## **Part 10: Advanced Techniques**

### **Inline Assembly in C**

**C with inline assembly:**
```c
#include <stdio.h>

int add_asm(int a, int b) {
    int result;
    __asm__ __volatile__ (
        "add %1, %2;"
        "mov %2, %0;"
        : "=r" (result)         // Output
        : "r" (a), "r" (b)      // Inputs
    );
    return result;
}

int main() {
    printf("Sum: %d\n", add_asm(10, 20));
    return 0;
}
```

### **Position-Independent Code (PIC)**

**Assembly:**
```nasm
section .data
    value dq 42

section .text
    global get_value

get_value:
    ; Non-PIC (absolute addressing)
    mov rax, [value]            ; ❌ Won't work in shared library
    ret

get_value_pic:
    ; PIC (RIP-relative addressing)
    mov rax, [rel value]        ; ✅ Works in shared library
    ret
```

### **Computed Goto (Jump Table)**

**C Equivalent:**
```c
int dispatch(int op, int a, int b) {
    switch(op) {
        case 0: return a + b;
        case 1: return a - b;
        case 2: return a * b;
        case 3: return a / b;
        default: return 0;
    }
}
```

**Assembly:**
```nasm
section .data
    jump_table dq op_add, op_sub, op_mul, op_div

section .text
dispatch:
    ; RDI = op, RSI = a, RDX = b
    
    ; Bounds check
    cmp rdi, 3
    ja invalid_op
    
    ; Jump through table
    mov rax, [jump_table + rdi*8]
    jmp rax
    
op_add:
    lea rax, [rsi + rdx]
    ret

op_sub:
    mov rax, rsi
    sub rax, rdx
    ret

op_mul:
    mov rax, rsi
    imul rax, rdx
    ret

op_div:
    mov rax, rsi
    xor rdx, rdx
    div rdx                     ; Note: should handle div by zero
    ret

invalid_op:
    xor rax, rax
    ret
```

---

## **✅ Practice Exercises**

### **Exercise 1: String Length Function**

Implement `strlen` that counts characters until null terminator:
```c
size_t strlen(const char *str);
```

### **Exercise 2: Array Sum Function**

```c
int array_sum(int *arr, int count);
```

### **Exercise 3: GCD (Greatest Common Divisor)**

Implement Euclidean algorithm recursively:
```c
int gcd(int a, int b);
```

### **Exercise 4: Callback Function**

Implement a function that takes a callback:
```c
void for_each(int *arr, int count, void (*callback)(int));
```

---

## **📋 Quick Reference**

### **Function Template**
```nasm
my_function:
    push rbp
    mov rbp, rsp
    push rbx                    ; Save callee-saved regs
    sub rsp, N                  ; Allocate locals (keep aligned!)
    
    ; Function body
    
    add rsp, N
    pop rbx
    pop rbp
    ret
```

### **Argument Registers (Linux x64)**
```
1st: RDI    2nd: RSI    3rd: RDX
4th: RCX    5th: R8     6th: R9
7+:  Stack (accessed via RBP)
```

### **Return Value**
```
RAX = integer/pointer return
RDX:RAX = 128-bit return
```

---

## **🎯 Knowledge Check**

Before moving to Topic 9, verify you understand:
- ✅ CALL pushes return address and jumps
- ✅ RET pops return address and returns
- ✅ First 6 args in RDI, RSI, RDX, RCX, R8, R9
- ✅ Return value in RAX
- ✅ Callee must save RBX, RBP, R12-R15
- ✅ Stack must be 16-byte aligned before CALL
- ✅ Function prologue/epilogue pattern

---

**🎉 Excellent!** You now understand functions and calling conventions!

**Next:** Topic 9: String Operations (Advanced string manipulation)

---

[← Previous Topic](topic-07-stack.md) | [Back to Main](../README.md) | [Next Topic →](topic-09-strings.md)

