# 📘 Topic 7: The Stack

Master the stack - your program's temporary workspace for function calls, local variables, and more.

---

## **Overview**

The **stack** is a special region of memory used for:
- 📦 Temporary storage (push/pop)
- 🔄 Function calls and returns
- 📍 Local variables
- 💾 Preserving register values
- 🎯 Passing function arguments (in 32-bit)

---

## **Part 1: What is the Stack?**

### **The Stack Memory Region**

```
High Memory
┌─────────────────┐
│     Stack       │ ← Grows DOWNWARD (decreasing addresses)
│       ↓         │
│                 │
│                 │
│       ↑         │
│     Heap        │ ← Grows UPWARD (increasing addresses)
├─────────────────┤
│   .bss section  │
├─────────────────┤
│   .data section │
├─────────────────┤
│   .text section │
└─────────────────┘
Low Memory
```

### **Key Characteristics**

- **LIFO**: Last In, First Out (like a stack of plates)
- **Grows downward**: Adding items decreases RSP
- **Automatic management**: CPU tracks top with RSP register
- **Fast access**: Directly in CPU's L1 cache
- **Limited size**: Typically 1-8 MB (can overflow!)

---

## **Part 2: Stack Pointer (RSP)**

### **The RSP Register**

```nasm
; RSP = Register Stack Pointer
; Always points to the TOP of the stack (most recently pushed item)

; Example stack state:
; RSP → 0x7fffffffe000: [0x42]  ← Top of stack
;       0x7fffffffe008: [0x10]
;       0x7fffffffe010: [0x99]
```

### **⚠️ Critical Rules**

```nasm
; 1. NEVER manually modify RSP unless you know what you're doing
mov rsp, rax            ; ❌ DANGEROUS! Can crash your program

; 2. Keep stack aligned to 16 bytes (System V ABI requirement)
; 3. Balance every PUSH with a POP (or stack adjustment)
```

---

## **Part 3: PUSH Instruction**

### **Syntax**

```nasm
push operand            ; Push operand onto stack
```

### **What PUSH Does (Step-by-Step)**

```nasm
push rax

; Equivalent to:
sub rsp, 8              ; 1. Decrease stack pointer by 8 bytes
mov [rsp], rax          ; 2. Store RAX at new top of stack
```

### **Visual Example**

**C Equivalent:**
```c
// Conceptual stack implementation
#define STACK_SIZE 1024
uint64_t stack[STACK_SIZE];
int stack_pointer = STACK_SIZE;  // Points to next free slot

void push(uint64_t value) {
    stack_pointer--;              // Grow downward
    stack[stack_pointer] = value;
}
```

**Assembly:**
```nasm
; Before: RSP = 0x1000
push rax        ; RAX = 0x42

; After:  RSP = 0x0FF8 (0x1000 - 8)
;         [0x0FF8] = 0x42

Stack Memory:
0x0FF8: [0x42]  ← RSP (new top)
0x1000: [old data]
```

### **PUSH Examples**

```nasm
; Push register
push rax
push rbx
push rcx

; Push immediate (sign-extended)
push 42
push 0x100

; Push memory
push qword [var]
push qword [rax + 8]

; Push 32-bit (decreases RSP by 8, but only stores 4 bytes - padding added)
push eax                ; Actually pushes 8 bytes (upper 4 are sign-extended)
```

---

## **Part 4: POP Instruction**

### **Syntax**

```nasm
pop operand             ; Pop from stack into operand
```

### **What POP Does (Step-by-Step)**

```nasm
pop rbx

; Equivalent to:
mov rbx, [rsp]          ; 1. Load value from top of stack
add rsp, 8              ; 2. Increase stack pointer by 8 bytes
```

### **Visual Example**

**C Equivalent:**
```c
uint64_t pop() {
    uint64_t value = stack[stack_pointer];
    stack_pointer++;      // Shrink upward
    return value;
}
```

**Assembly:**
```nasm
; Before: RSP = 0x0FF8
;         [0x0FF8] = 0x42
pop rbx

; After:  RSP = 0x1000 (0x0FF8 + 8)
;         RBX = 0x42

Stack Memory:
0x0FF8: [0x42]  ← Old data (not erased, just ignored)
0x1000: [...]   ← RSP (new top)
```

### **POP Examples**

```nasm
; Pop to register
pop rax
pop rbx

; Pop and discard (common for cleanup)
add rsp, 8              ; More efficient than: pop rax (when value not needed)

; Cannot pop to immediate
pop 42                  ; ❌ ERROR!

; Can pop to memory
pop qword [var]
```

---

## **Part 5: Common Stack Patterns**

### **Pattern 1: Temporary Storage**

**C Equivalent:**
```c
int compute(int a, int b) {
    int temp_rax = a + b;  // Save intermediate result
    int result = temp_rax * 2;
    return result;
}
```

**Assembly:**
```nasm
; Need to use RAX but want to preserve its value
push rax                ; Save RAX
; ... do work that modifies RAX ...
mov rax, [value]
add rax, 100
pop rax                 ; Restore original RAX
```

### **Pattern 2: Register Preservation**

**C Equivalent:**
```c
void my_function() {
    // C compiler automatically saves registers that need preservation
    int saved_rbx = /* current rbx value */;
    // ... function body ...
    // Restore rbx before return
}
```

**Assembly:**
```nasm
my_function:
    ; Save callee-saved registers
    push rbx
    push r12
    push r13
    
    ; Function body (can freely use RBX, R12, R13)
    mov rbx, 100
    ; ...
    
    ; Restore registers in REVERSE order
    pop r13
    pop r12
    pop rbx
    ret
```

### **Pattern 3: Swap Using Stack**

**C Equivalent:**
```c
void swap_with_stack(int *a, int *b) {
    int temp1 = *a;
    int temp2 = *b;
    *a = temp2;
    *b = temp1;
}
```

**Assembly:**
```nasm
; Swap RAX and RBX using stack
push rax        ; Stack: [rax]
push rbx        ; Stack: [rbx, rax]
pop rax         ; RAX = old RBX, Stack: [rax]
pop rbx         ; RBX = old RAX, Stack: []
```

### **Pattern 4: Multiple Register Save/Restore**

**C Equivalent:**
```c
void preserve_all_registers() {
    // Save all general-purpose registers
    uint64_t saved[16];
    // ... assembly handles this with push/pop ...
}
```

**Assembly:**
```nasm
; Save all volatile registers before syscall
push rax
push rcx
push rdx
push rsi
push rdi
push r8
push r9
push r10
push r11

; ... make syscall ...

; Restore in reverse order
pop r11
pop r10
pop r9
pop r8
pop rdi
pop rsi
pop rdx
pop rcx
pop rax
```

---

## **Part 6: Stack Frames**

### **What is a Stack Frame?**

A **stack frame** is a section of the stack dedicated to a single function call, containing:
- Return address
- Saved registers
- Local variables
- Function parameters (in 32-bit)

### **Stack Frame Layout**

```
High Addresses
┌──────────────────┐
│  Caller's Frame  │
├──────────────────┤
│  Return Address  │ ← Pushed by CALL
├──────────────────┤
│  Saved RBP       │ ← Pushed by function prologue
├──────────────────┤ ← RBP points here (frame base)
│  Local Var 1     │ [rbp - 8]
├──────────────────┤
│  Local Var 2     │ [rbp - 16]
├──────────────────┤
│  Local Var 3     │ [rbp - 24]
└──────────────────┘ ← RSP points here (stack top)
Low Addresses
```

### **Function Prologue (Setup)**

**C Equivalent:**
```c
void my_function() {
    // Compiler generates prologue automatically
    // Saves frame pointer, allocates locals
    int local1, local2, local3;
    // ... function body ...
}
```

**Assembly:**
```nasm
my_function:
    ; === PROLOGUE ===
    push rbp                ; Save caller's base pointer
    mov rbp, rsp            ; Set up new frame base
    sub rsp, 32             ; Allocate space for local variables
    
    ; === FUNCTION BODY ===
    ; Access locals relative to RBP:
    mov qword [rbp - 8], 100    ; local1 = 100
    mov qword [rbp - 16], 200   ; local2 = 200
    mov qword [rbp - 24], 300   ; local3 = 300
    
    ; === EPILOGUE ===
    mov rsp, rbp            ; Deallocate locals (restore RSP)
    pop rbp                 ; Restore caller's base pointer
    ret                     ; Return to caller
```

### **Alternative: ENTER and LEAVE**

**Assembly:**
```nasm
my_function:
    ; ENTER creates stack frame
    enter 32, 0             ; Equivalent to: push rbp; mov rbp, rsp; sub rsp, 32
    
    ; Function body
    mov qword [rbp - 8], 42
    
    ; LEAVE destroys stack frame
    leave                   ; Equivalent to: mov rsp, rbp; pop rbp
    ret

; Note: ENTER/LEAVE are slower than manual prologue/epilogue!
```

---

## **Part 7: Calling Conventions (System V AMD64)**

### **Register Usage Rules**

```
┌─────────────────────────────────────────────────┐
│  CALLER-SAVED (Volatile)                        │
│  Caller must save these before calling         │
│  RAX, RCX, RDX, RSI, RDI, R8-R11                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  CALLEE-SAVED (Non-volatile)                    │
│  Function must preserve these                   │
│  RBX, RBP, R12-R15                              │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  SPECIAL                                        │
│  RSP: Stack pointer (always callee-saved)       │
└─────────────────────────────────────────────────┘
```

### **Function Call Example**

**C Equivalent:**
```c
int add_three(int a, int b, int c) {
    return a + b + c;
}

int main() {
    int result = add_three(10, 20, 30);
    return result;
}
```

**Assembly:**
```nasm
add_three:
    ; Arguments arrive in: RDI=a, RSI=b, RDX=c
    ; No need to save caller-saved regs (we don't call anyone)
    
    mov rax, rdi            ; RAX = a
    add rax, rsi            ; RAX = a + b
    add rax, rdx            ; RAX = a + b + c
    ret                     ; Return value in RAX

main:
    ; Set up arguments
    mov rdi, 10             ; 1st arg
    mov rsi, 20             ; 2nd arg
    mov rdx, 30             ; 3rd arg
    
    call add_three          ; Call function
    ; Result in RAX = 60
    
    ; Exit
    mov rdi, rax
    mov rax, 60
    syscall
```

---

## **Part 8: Stack Alignment**

### **16-Byte Alignment Requirement**

**The Rule**: RSP must be aligned to 16 bytes at function call boundaries.

```nasm
; Before CALL: RSP must be 16-byte aligned
; After CALL: RSP is misaligned (CALL pushes 8-byte return address)
; Inside function: Prologue must restore alignment

main:
    ; RSP is 16-byte aligned here
    
    push rbp                ; RSP now misaligned (-8)
    mov rbp, rsp
    sub rsp, 16             ; Allocate 16 bytes (now aligned again!)
    
    call other_func         ; RSP must be 16-aligned before this!
    
    leave
    ret
```

### **Why Alignment Matters**

**C Equivalent (conceptual):**
```c
// SSE/AVX instructions require aligned memory
#include <xmmintrin.h>

void example() {
    __m128 vec;  // Must be 16-byte aligned
    // If stack is misaligned, this crashes!
}
```

**Assembly:**
```nasm
; Aligned load (fast)
movaps xmm0, [rsp]      ; ✅ Works if RSP is 16-aligned
                        ; ❌ CRASHES if misaligned!

; Unaligned load (slower but safe)
movups xmm0, [rsp]      ; ✅ Always works (slower)
```

---

## **Part 9: Practical Examples**

### **Example 1: Factorial with Stack**

**C Equivalent:**
```c
int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int result = factorial(5);
    return result;  // 120
}
```

**Assembly:**
```nasm
section .text
    global factorial

factorial:
    ; RDI = n
    push rbp
    mov rbp, rsp
    push rbx                ; Save RBX (callee-saved)
    
    ; Base case: if (n <= 1) return 1
    cmp rdi, 1
    jg recursive_case
    mov rax, 1              ; Return 1
    jmp factorial_done
    
recursive_case:
    mov rbx, rdi            ; Save n in RBX
    dec rdi                 ; n - 1
    call factorial          ; factorial(n - 1)
    imul rax, rbx           ; n * factorial(n-1)
    
factorial_done:
    pop rbx                 ; Restore RBX
    pop rbp
    ret
```

### **Example 2: Nested Function Calls**

**C Equivalent:**
```c
int func_a(int x) {
    return x * 2;
}

int func_b(int x) {
    int temp = func_a(x);
    return temp + 10;
}

int main() {
    int result = func_b(5);  // result = 20
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global main

func_a:
    ; RDI = x
    mov rax, rdi
    shl rax, 1              ; x * 2
    ret

func_b:
    ; RDI = x
    push rbp
    mov rbp, rsp
    sub rsp, 16             ; Align stack
    
    ; RDI already contains x
    call func_a             ; temp = func_a(x)
    add rax, 10             ; temp + 10
    
    leave
    ret

main:
    mov rdi, 5
    call func_b             ; RAX = 20
    
    mov rdi, rax
    mov rax, 60
    syscall
```

### **Example 3: Local Variables**

**C Equivalent:**
```c
int compute() {
    int a = 10;
    int b = 20;
    int c = 30;
    int sum = a + b + c;
    return sum;
}

int main() {
    int result = compute();
    return result;
}
```

**Assembly:**
```nasm
section .text
    global compute

compute:
    push rbp
    mov rbp, rsp
    sub rsp, 32             ; Allocate 4 local variables (aligned)
    
    ; int a = 10
    mov dword [rbp - 4], 10
    
    ; int b = 20
    mov dword [rbp - 8], 20
    
    ; int c = 30
    mov dword [rbp - 12], 30
    
    ; int sum = a + b + c
    mov eax, [rbp - 4]      ; EAX = a
    add eax, [rbp - 8]      ; EAX = a + b
    add eax, [rbp - 12]     ; EAX = a + b + c
    mov [rbp - 16], eax     ; sum = a + b + c
    
    ; return sum
    mov eax, [rbp - 16]
    
    leave
    ret
```

---

## **Part 10: Stack Pitfalls**

### **❌ Mistake 1: Unbalanced Stack**

```nasm
; BAD: More pushes than pops
my_func:
    push rax
    push rbx
    pop rax                 ; ❌ RBX never popped!
    ret                     ; Returns to WRONG address!
```

### **❌ Mistake 2: Stack Overflow**

**C Equivalent:**
```c
void infinite_recursion() {
    infinite_recursion();  // Stack overflow!
}
```

**Assembly:**
```nasm
; Infinite recursion - will crash
bad_func:
    call bad_func           ; ❌ Each call uses stack space
    ret                     ; Never reached
```

### **❌ Mistake 3: Misalignment**

```nasm
; BAD: Calling function with misaligned stack
main:
    push rax                ; RSP now misaligned
    call my_func            ; ❌ May crash if my_func uses SSE
    pop rax
```

### **✅ Fix: Proper Alignment**

```nasm
; GOOD: Maintain alignment
main:
    push rax
    sub rsp, 8              ; Dummy push to re-align
    call my_func            ; ✅ RSP is 16-aligned
    add rsp, 8
    pop rax
```

---

## **Part 11: Stack Debugging**

### **Viewing the Stack**

```nasm
; In GDB:
; x/16gx $rsp         - View 16 quadwords from stack
; info frame          - Show current stack frame
; backtrace           - Show call stack
```

### **Common Issues**

```
Issue                  | Symptom                    | Solution
-----------------------|----------------------------|------------------
Stack overflow         | Segmentation fault         | Reduce recursion depth
Unbalanced push/pop    | Return to wrong address    | Count push/pop pairs
Misalignment           | Bus error / SSE crash      | Use sub rsp, 8
Stack corruption       | Random crashes             | Check buffer overflows
```

---

## **✅ Practice Exercises**

### **Exercise 1: Stack Calculator**

Implement a stack-based calculator:
```nasm
; push 10
; push 20
; add       ; Pop two values, push sum
; push 5
; mul       ; Pop two values, push product
; pop       ; Get result
```

### **Exercise 2: String Reverse**

Reverse a string using the stack:
```nasm
; Push each character onto stack
; Pop them back (reversed order)
```

### **Exercise 3: Fibonacci with Stack**

Implement recursive Fibonacci preserving all registers correctly.

---

## **📋 Quick Reference**

### **Stack Operations**
```nasm
push rax            ; Push RAX onto stack (RSP -= 8)
pop rbx             ; Pop from stack into RBX (RSP += 8)
```

### **Stack Frame Setup**
```nasm
; Prologue
push rbp
mov rbp, rsp
sub rsp, N          ; N must maintain 16-byte alignment

; Epilogue
mov rsp, rbp
pop rbp
ret
```

### **Calling Convention (Linux x64)**
```
Arguments: RDI, RSI, RDX, RCX, R8, R9, then stack
Return: RAX
Caller-saved: RAX, RCX, RDX, RSI, RDI, R8-R11
Callee-saved: RBX, RBP, R12-R15
```

---

## **🎯 Knowledge Check**

Before moving to Topic 8, verify you understand:
- ✅ Stack grows downward (toward lower addresses)
- ✅ RSP always points to top of stack
- ✅ PUSH decrements RSP, POP increments RSP
- ✅ Stack frames store local variables and return addresses
- ✅ 16-byte alignment requirement for function calls
- ✅ Caller-saved vs callee-saved registers
- ✅ Function prologue and epilogue

---

**🎉 Excellent!** You now understand the stack and how functions use it!

**Next:** Topic 8: Functions & Procedures (Advanced function techniques)

---

[← Previous Topic](topic-06-loops.md) | [Back to Main](../README.md) | [Next Topic →](topic-08-functions.md)

