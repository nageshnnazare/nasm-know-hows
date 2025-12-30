# 📘 Topic 2: Registers & Data Types

Welcome to the core of assembly programming! Registers are your fastest storage locations - think of them as variables that live directly in the CPU.

---

## **Part 1: What Are Registers?**

**Registers** are small, ultra-fast storage locations built into the CPU.

```
Speed Comparison:
┌─────────────┬──────────────┬─────────────┐
│  Location   │  Access Time │  Analogy    │
├─────────────┼──────────────┼─────────────┤
│  Registers  │  < 1 cycle   │  Your hands │
│  L1 Cache   │  ~4 cycles   │  Your desk  │
│  RAM        │  ~100 cycles │  File room  │
│  SSD/HDD    │  ~100,000+   │  Warehouse  │
└─────────────┴──────────────┴─────────────┘
```

**Why use registers?**
- ⚡ Fastest way to store/manipulate data
- 🎯 CPU instructions work directly on registers
- 💾 Limited quantity (only 16 general-purpose in x64)

---

## **Part 2: The x86-64 Register Set**

### **General Purpose Registers (GPRs)**

In 64-bit mode, you have **16 general-purpose registers**:

```
Original 8 (from 8086 era):
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│ RAX │ RBX │ RCX │ RDX │ RSI │ RDI │ RBP │ RSP │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

Extended 8 (added in x64):
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ R8 │ R9 │ R10│ R11│ R12│ R13│ R14│ R15│
└────┴────┴────┴────┴────┴────┴────┴────┘
```

---

## **Part 3: Register Sizes - THE KEY CONCEPT!**

Each register can be accessed at **different sizes**. Here's the magic:

### **RAX Register Family Tree**

```
┌──────────────────────────────────────────────────────────────┐
│                      RAX (64-bit)                            │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                    (bits 63-0)                        │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                                 │
                                 └──────────────┐
                                                │
                        ┌───────────────────────────────────┐
                        │        EAX (32-bit)               │
                        │  ┌─────────────────────────────┐  │
                        │  │      (bits 31-0)            │  │
                        │  └─────────────────────────────┘  │
                        └───────────────────────────────────┘
                                        │
                                        └─────────┐
                                                  │
                                ┌─────────────────────────┐
                                │   AX (16-bit)           │
                                │  ┌───────────────────┐  │
                                │  │  (bits 15-0)      │  │
                                │  └───────────────────┘  │
                                └─────────────────────────┘
                                          │
                        ┌─────────────────┴──────────────────┐
                        │                                    │
                ┌───────────────┐                   ┌────────────────┐
                │  AH (8-bit)   │                   │  AL (8-bit)    │
                │  ┌─────────┐  │                   │  ┌──────────┐  │
                │  │ (15-8)  │  │                   │  │  (7-0)   │  │
                │  └─────────┘  │                   │  └──────────┘  │
                └───────────────┘                   └────────────────┘
```

### **All Register Sizes**

```nasm
; 64-bit (full register) - "R" prefix
mov rax, 0x123456789ABCDEF0
mov rbx, 0xFFFFFFFFFFFFFFFF
mov rcx, 100

; 32-bit (lower half) - "E" prefix
mov eax, 0x12345678         ; Upper 32 bits of RAX zeroed!
mov ebx, 42
mov ecx, 1000

; 16-bit (lowest 16 bits) - original names
mov ax, 0x1234              ; Doesn't affect upper 48 bits
mov bx, 100
mov cx, 50

; 8-bit (lowest/high byte)
mov al, 0x42                ; Lowest 8 bits of RAX
mov ah, 0x13                ; Bits 8-15 of RAX (only for A,B,C,D)
mov bl, 65                  ; ASCII 'A'
```

### **Complete Register Name Table**

```
┌────────┬────────┬────────┬────────┬────────┐
│ 64-bit │ 32-bit │ 16-bit │ 8-high │ 8-low  │
├────────┼────────┼────────┼────────┼────────┤
│  RAX   │  EAX   │   AX   │   AH   │   AL   │
│  RBX   │  EBX   │   BX   │   BH   │   BL   │
│  RCX   │  ECX   │   CX   │   CH   │   CL   │
│  RDX   │  EDX   │   DX   │   DH   │   DL   │
├────────┼────────┼────────┼────────┼────────┤
│  RSI   │  ESI   │   SI   │   -    │  SIL*  │
│  RDI   │  EDI   │   DI   │   -    │  DIL*  │
│  RBP   │  EBP   │   BP   │   -    │  BPL*  │
│  RSP   │  ESP   │   SP   │   -    │  SPL*  │
├────────┼────────┼────────┼────────┼────────┤
│  R8    │  R8D   │  R8W   │   -    │  R8B   │
│  R9    │  R9D   │  R9W   │   -    │  R9B   │
│  R10   │  R10D  │  R10W  │   -    │  R10B  │
│  R11   │  R11D  │  R11W  │   -    │  R11B  │
│  R12   │  R12D  │  R12W  │   -    │  R12B  │
│  R13   │  R13D  │  R13W  │   -    │  R13B  │
│  R14   │  R14D  │  R14W  │   -    │  R14B  │
│  R15   │  R15D  │  R15W  │   -    │  R15B  │
└────────┴────────┴────────┴────────┴────────┘

* SIL, DIL, BPL, SPL available in 64-bit mode only
```

---

## **Part 4: Critical Rule - 32-bit Zeroing**

### **⚠️ IMPORTANT BEHAVIOR:**

```nasm
; Writing to 32-bit register ZEROS upper 32 bits!
mov rax, 0xFFFFFFFFFFFFFFFF    ; RAX = 0xFFFFFFFFFFFFFFFF
mov eax, 0x12345678            ; RAX = 0x0000000012345678
                               ;       ^^^^^^^^ ZEROED!

; Writing to 16-bit or 8-bit PRESERVES upper bits
mov rax, 0xFFFFFFFFFFFFFFFF    ; RAX = 0xFFFFFFFFFFFFFFFF
mov ax, 0x1234                 ; RAX = 0xFFFFFFFFFFFF1234
                               ;       ^^^^^^^^^^^^ PRESERVED

mov rax, 0xFFFFFFFFFFFFFFFF    ; RAX = 0xFFFFFFFFFFFFFFFF
mov al, 0x42                   ; RAX = 0xFFFFFFFFFFFFFF42
                               ;       ^^^^^^^^^^^^^^ PRESERVED
```

**Why this matters:**

```nasm
; Example: Breaking code unintentionally
mov rax, buffer_address        ; RAX points to a memory address
mov eax, 5                     ; OOPS! Upper 32 bits zeroed
                               ; RAX might now point to invalid memory!
```

---

## **Part 5: Register Purposes (Conventions)**

While most registers are "general purpose," they have **traditional roles**:

### **The Original Eight**

```nasm
; RAX - Accumulator (arithmetic, return values)
mov rax, 10
mul rbx                        ; Result goes in RAX
; Return value from functions in RAX

; RBX - Base (often saved by functions, general purpose)
mov rbx, array_base
mov al, [rbx + 5]             ; Access array element

; RCX - Counter (loops, string operations)
mov rcx, 10
my_loop:
    ; ... do something ...
    loop my_loop              ; Decrements RCX automatically

; RDX - Data (I/O operations, 128-bit arithmetic)
mul rbx                       ; RDX:RAX = RAX * RBX
div rbx                       ; Uses RDX:RAX as dividend

; RSI - Source Index (string/memory operations)
mov rsi, source_string
lodsb                         ; Load byte from [RSI] into AL

; RDI - Destination Index (string/memory operations)
mov rdi, dest_string
stosb                         ; Store AL into [RDI]

; RBP - Base Pointer (stack frames, local variables)
push rbp
mov rbp, rsp                  ; Standard function prologue
; Access params as [rbp+16], locals as [rbp-4]

; RSP - Stack Pointer (CRITICAL - points to top of stack)
push rax                      ; RSP decremented, data stored
pop rbx                       ; Data loaded, RSP incremented
; Don't mess with RSP unless you know what you're doing!
```

### **Calling Convention (System V AMD64 - Linux)**

When calling functions, arguments go in specific registers:

```nasm
; Function arguments (in order):
; 1st arg → RDI
; 2nd arg → RSI
; 3rd arg → RDX
; 4th arg → RCX
; 5th arg → R8
; 6th arg → R9
; More args → Stack

; Example: printf(format, arg1, arg2)
mov rdi, format_string        ; 1st arg (format)
mov rsi, 42                   ; 2nd arg
mov rdx, 100                  ; 3rd arg
xor rax, rax                  ; printf expects RAX=0 (no vector args)
call printf

; Return value always in RAX
```

---

## **Part 6: Data Types in NASM**

### **Defining Data**

```nasm
section .data
    ; DB - Define Byte (8-bit, 1 byte)
    byte_val    db 0x42               ; Single byte
    char_val    db 'A'                ; ASCII character
    string_val  db "Hello", 0         ; String with null terminator
    byte_array  db 10, 20, 30, 40    ; Array of bytes
    
    ; DW - Define Word (16-bit, 2 bytes)
    word_val    dw 0x1234
    word_array  dw 100, 200, 300
    
    ; DD - Define Doubleword (32-bit, 4 bytes)
    dword_val   dd 0x12345678
    int_val     dd 1000000
    float_val   dd 3.14159            ; 32-bit float
    
    ; DQ - Define Quadword (64-bit, 8 bytes)
    qword_val   dq 0x123456789ABCDEF0
    long_val    dq 9223372036854775807
    double_val  dq 2.71828182845      ; 64-bit double
    pointer     dq 0                  ; 64-bit pointer
    
    ; DT - Define Ten Bytes (80-bit, 10 bytes)
    extended    dt 3.14159265358979   ; 80-bit extended precision
    
    ; Multiple values
    numbers     dd 1, 2, 3, 4, 5      ; 5 doublewords (20 bytes)
    
    ; TIMES - Repeat
    buffer      times 64 db 0         ; 64 bytes of zeros
    spaces      times 80 db ' '       ; 80 space characters
```

### **Reserving Uninitialized Data**

```nasm
section .bss
    ; RESB - Reserve Bytes
    buffer      resb 256              ; 256 bytes
    
    ; RESW - Reserve Words
    input       resw 1                ; 1 word (2 bytes)
    
    ; RESD - Reserve Doublewords
    counter     resd 1                ; 1 dword (4 bytes)
    array       resd 100              ; 100 dwords (400 bytes)
    
    ; RESQ - Reserve Quadwords
    pointer     resq 1                ; 1 qword (8 bytes)
    big_array   resq 1000             ; 1000 qwords (8000 bytes)
```

---

## **Part 7: Practical Examples**

### **Example 1: Working with Different Sizes**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    uint8_t  byte_val  = 0xFF;
    uint16_t word_val  = 0x1234;
    uint32_t dword_val = 0x12345678;
    uint64_t qword_val = 0x123456789ABCDEF0ULL;
    
    // Load different sizes (C compiler maps these to appropriate registers)
    uint8_t  a8  = byte_val;   // Maps to AL
    uint16_t a16 = word_val;   // Maps to AX
    uint32_t a32 = dword_val;  // Maps to EAX
    uint64_t a64 = qword_val;  // Maps to RAX
    
    // Note: In C, you work with typed variables. 
    // The compiler manages register allocation automatically.
    
    return 0;
}
```

**Assembly:**
```nasm
section .data
    byte_val    db 0xFF
    word_val    dw 0x1234
    dword_val   dd 0x12345678
    qword_val   dq 0x123456789ABCDEF0

section .text
    global _start

_start:
    ; Load different sizes
    mov al, [byte_val]        ; AL = 0xFF
    mov ax, [word_val]        ; AX = 0x1234
    mov eax, [dword_val]      ; EAX = 0x12345678
    mov rax, [qword_val]      ; RAX = 0x123456789ABCDEF0
    
    ; Mix and match
    xor rax, rax              ; RAX = 0
    mov al, 0xFF              ; RAX = 0x00000000000000FF
    mov ah, 0x11              ; RAX = 0x00000000000011FF
    mov ax, 0x2233            ; RAX = 0x0000000000002233
    mov eax, 0x44556677       ; RAX = 0x0000000044556677 (upper cleared!)
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 2: Register Manipulation**

**C Equivalent (using unions to show bit manipulation):**
```c
#include <stdint.h>
#include <stdio.h>

// Union allows accessing same memory as different types
union Register {
    uint64_t rax;  // 64-bit view
    uint32_t eax;  // 32-bit view (low part)
    uint16_t ax;   // 16-bit view (low part)
    struct {
        uint8_t al;  // 8-bit low
        uint8_t ah;  // 8-bit high
    };
};

int main() {
    union Register reg;
    
    reg.rax = 0xAAAAAAAAAAAAAAAAULL;  // Full 64-bit
    // In real CPU: mov eax zeros upper 32 bits
    // C simulation:
    reg.eax = 0xBBBBBBBB;              // Only affects lower 32
    reg.rax &= 0xFFFFFFFF;             // Manually zero upper (CPU does auto)
    
    reg.rax = 0xCCCCCCCCCCCCCCCCULL;
    reg.ax = 0xDDDD;                   // Only affects lower 16
    
    return 0;
}
```

**Assembly:**
```nasm
section .text
    global _start

_start:
    ; Demonstrate register sizes
    mov rax, 0xAAAAAAAAAAAAAAAA    ; RAX = 0xAAAAAAAAAAAAAAAA
    mov eax, 0xBBBBBBBB            ; RAX = 0x00000000BBBBBBBB
    
    mov rax, 0xCCCCCCCCCCCCCCCC    ; RAX = 0xCCCCCCCCCCCCCCCC
    mov ax, 0xDDDD                 ; RAX = 0xCCCCCCCCCCCCDDDD
    
    mov rax, 0x1122334455667788    ; RAX = 0x1122334455667788
    mov al, 0x99                   ; RAX = 0x1122334455667799
    mov ah, 0xAA                   ; RAX = 0x112233445566AA99
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 3: Using Register Roles**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int32_t numbers[] = {5, 10, 15, 20, 25};
    int32_t count = 5;
    int32_t sum = 0;
    
    // Sum array - compiler typically uses:
    // - accumulator register for sum (RAX)
    // - counter register for index (RCX)
    for (int i = 0; i < count; i++) {
        sum += numbers[i];
    }
    
    // sum now equals 75
    return 0;
}
```

**Assembly:**
```nasm
section .data
    numbers dd 5, 10, 15, 20, 25    ; Array of 5 numbers
    count   equ 5

section .bss
    sum resd 1

section .text
    global _start

_start:
    ; Sum array using traditional register roles
    xor rax, rax              ; RAX = accumulator (sum)
    mov rbx, numbers          ; RBX = base (array address)
    xor rcx, rcx              ; RCX = counter (index)
    mov rdx, count            ; RDX = data (loop limit)
    
sum_loop:
    add eax, [rbx + rcx*4]    ; Add numbers[rcx] to sum
    inc rcx                    ; Increment counter
    cmp rcx, rdx              ; Compare with limit
    jl sum_loop               ; Loop if less
    
    ; Store result
    mov [sum], eax            ; sum = 75
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## **Part 8: Common Mistakes**

### **❌ Mistake 1: Size Mismatch**

```nasm
section .data
    value dd 0x12345678       ; 32-bit value

section .text
    mov al, [value]           ; ✓ Loads 0x78 (first byte)
    mov ax, [value]           ; ✓ Loads 0x5678 (first word)
    mov eax, [value]          ; ✓ Loads 0x12345678 (full dword)
    mov rax, [value]          ; ⚠️ Loads 8 bytes (past end of value!)
```

### **❌ Mistake 2: Forgetting 32-bit Zeroing**

```nasm
mov rax, 0xFFFFFFFFFFFFFFFF
mov eax, 1                    ; RAX = 0x0000000000000001, not 0xFFFFFFFF00000001!
```

### **❌ Mistake 3: Using Undefined Registers**

```nasm
mov r16, 100                  ; ERROR: No such register!
mov rxc, 50                   ; ERROR: It's RCX, not RXC!
```

---

## **✅ Practice Exercises**

### **Exercise 1: Register Explorer**
Write a program that:
1. Loads 0xFFFFFFFFFFFFFFFF into RAX
2. Moves 0x11223344 into EAX
3. Print RAX's value (you'll see upper 32 bits are zero)

### **Exercise 2: Byte Manipulation**
```nasm
; Start with RAX = 0
; Set AL = 'H' (0x48)
; Set AH = 'i' (0x69)
; What is the value of AX?
```

### **Exercise 3: Array Access**
Create an array of 5 bytes: `[10, 20, 30, 40, 50]`
- Load the 3rd element (30) into AL using RBX as base register

### **Exercise 4: Size Detective**
```nasm
section .data
    mystery db 0x12, 0x34, 0x56, 0x78

section .text
    mov al, [mystery]         ; AL = ?
    mov ax, [mystery]         ; AX = ?
    mov eax, [mystery]        ; EAX = ?
```
What are the values? (Hint: Little-endian!)

### **Exercise 5: Data Definition**
Define these in `.data` section:
- Your age (1 byte)
- Current year (2 bytes)
- Your favorite number (4 bytes)
- A 10-byte buffer initialized to zeros

---

## **📋 Quick Reference Card**

```
┌────────────────────────────────────────────────┐
│  REGISTER SIZES                                │
├──────────┬──────────┬─────────┬────────────────┤
│  Size    │  Suffix  │  Bits   │  Example       │
├──────────┼──────────┼─────────┼────────────────┤
│  Byte    │  B       │  8      │  AL, BL, R8B   │
│  Word    │  W       │  16     │  AX, BX, R8W   │
│  Dword   │  D       │  32     │  EAX, R8D      │
│  Qword   │  (none)  │  64     │  RAX, R8       │
└──────────┴──────────┴─────────┴────────────────┘

┌────────────────────────────────────────────────┐
│  DATA TYPES                                    │
├──────────┬──────────┬─────────┬────────────────┤
│  Define  │  Reserve │  Size   │  Purpose       │
├──────────┼──────────┼─────────┼────────────────┤
│  DB      │  RESB    │  1 byte │  char, byte    │
│  DW      │  RESW    │  2 bytes│  short         │
│  DD      │  RESD    │  4 bytes│  int, float    │
│  DQ      │  RESQ    │  8 bytes│  long, double  │
└──────────┴──────────┴─────────┴────────────────┘
```

---

## **🎯 Knowledge Check**

Before moving to Topic 3, verify you understand:
- ✅ The 16 general-purpose registers
- ✅ How to access RAX as EAX, AX, AH, AL
- ✅ That 32-bit writes zero the upper 32 bits
- ✅ Traditional register roles (RSP, RBP, RCX, etc.)
- ✅ DB, DW, DD, DQ data types
- ✅ RESB, RESW, RESD, RESQ for uninitialized data

---

**🎉 Excellent!** You now understand the CPU's register architecture!

**Next:** Topic 3: Basic Instructions (Coming soon!)

---

[← Previous Topic](topic-01-setup.md) | [Back to Main](../README.md) | [Next Topic →](./topic-03-basic-instructions.md)

