# Understanding Memory Addressing with [ ] Brackets

## Question
*In `mov rbx, array_base` and `mov al, [rbx + 5]`, what does the `[ ]` syntax mean?*

---

## The Key Concept

The **square brackets `[ ]`** mean **"go to this memory address and get/put the value there"** - this is called **memory dereferencing** or **indirect addressing**.

```nasm
; WITHOUT brackets - direct value
mov rax, 5              ; RAX = 5 (the number 5)

; WITH brackets - memory access
mov rax, [5]            ; RAX = (value stored at memory address 5)
```

Think of it like this:
- **No brackets**: "Give me the number"
- **Brackets**: "Go to this address and give me what's there"

---

## Analogy: House Addresses

```
Without brackets:
  mov rax, 123
  "The number is 123"
  
With brackets:
  mov rax, [123]
  "Go to house number 123 and tell me what's inside"
```

---

## Your Example Explained

```nasm
mov rbx, array_base     ; RBX = address of array (like "123 Main St")
mov al, [rbx + 5]       ; Go to address (RBX + 5) and load 1 byte into AL
```

### **Step-by-Step:**

```nasm
section .data
    array_base db 10, 20, 30, 40, 50, 60, 70, 80
    ; Memory layout (assume array_base starts at address 0x1000):
    ; Address:  0x1000  0x1001  0x1002  0x1003  0x1004  0x1005  0x1006  0x1007
    ; Value:      10      20      30      40      50      60      70      80

section .text
    mov rbx, array_base      ; RBX = 0x1000 (address of first element)
    mov al, [rbx + 5]        ; AL = value at address (0x1000 + 5) = 0x1005
                             ; AL = 60
```

**What happens:**
1. `RBX` contains `0x1000` (the memory address)
2. `[rbx + 5]` means "address `0x1000 + 5 = 0x1005`"
3. CPU goes to address `0x1005` and reads 1 byte
4. That byte (value `60`) is loaded into `AL`

---

## Visual Representation

```
Memory:
┌──────────┬─────┐
│ Address  │ Val │
├──────────┼─────┤
│ 0x1000   │ 10  │ ← array_base (RBX points here)
│ 0x1001   │ 20  │
│ 0x1002   │ 30  │
│ 0x1003   │ 40  │
│ 0x1004   │ 50  │
│ 0x1005   │ 60  │ ← [rbx + 5] reads from here
│ 0x1006   │ 70  │
│ 0x1007   │ 80  │
└──────────┴─────┘

mov al, [rbx + 5]
          │
          └── Go to this address and read the value
```

---

## Comparison: With vs Without Brackets

```nasm
section .data
    value dq 42
    ptr   dq value          ; ptr stores the ADDRESS of value

section .text
    ; WITHOUT brackets - load the address itself
    mov rax, value          ; RAX = 0x12345... (memory address of value)
    mov rbx, ptr            ; RBX = 0x12345... (same address)
    
    ; WITH brackets - load the value AT the address
    mov rax, [value]        ; RAX = 42 (the actual value)
    mov rbx, [ptr]          ; RBX = 0x12345... (address stored in ptr)
    mov rcx, [rbx]          ; RCX = 42 (go to address in RBX, read value)
```

---

## Memory Addressing Modes

The brackets support several addressing modes:

### **1. Direct Address**
```nasm
mov rax, [0x1000]           ; Read from address 0x1000
mov [0x2000], rbx           ; Write RBX to address 0x2000
```

### **2. Register Indirect**
```nasm
mov rax, [rbx]              ; Read from address stored in RBX
mov [rdi], rax              ; Write RAX to address stored in RDI
```

### **3. Register + Displacement**
```nasm
mov rax, [rbx + 8]          ; Address = RBX + 8
mov al, [rsi + 100]         ; Address = RSI + 100
mov [rdi + 16], rcx         ; Write to address RDI + 16
```

### **4. Base + Index**
```nasm
mov rax, [rbx + rcx]        ; Address = RBX + RCX
mov al, [rsi + rdx]         ; Address = RSI + RDX
```

### **5. Base + Index*Scale + Displacement (SIB)**
```nasm
; Format: [base + index*scale + displacement]
; Scale can be 1, 2, 4, or 8

mov rax, [rbx + rcx*4]      ; Address = RBX + (RCX * 4)
mov al, [rsi + rdx*8 + 16]  ; Address = RSI + (RDX * 8) + 16

; Perfect for arrays!
; array[i] where each element is 4 bytes:
mov eax, [array + rcx*4]
```

### **6. Label (Named Address)**
```nasm
section .data
    myvar dq 100

section .text
    mov rax, myvar          ; RAX = address of myvar
    mov rax, [myvar]        ; RAX = 100 (value AT myvar)
```

---

## Practical Examples

### **Example 1: Array Access**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    uint8_t numbers[] = {5, 10, 15, 20, 25};
    uint8_t *ptr = numbers;  // ptr points to numbers[0]
    
    // Access individual elements (two ways)
    uint8_t value1 = ptr[0];     // value1 = 5  (numbers[0])
    uint8_t value2 = ptr[1];     // value2 = 10 (numbers[1])
    uint8_t value3 = *(ptr + 2); // value3 = 15 (numbers[2]) - pointer arithmetic
    
    // Using index variable
    int index = 2;
    uint8_t value4 = ptr[index]; // value4 = 15 (numbers[2])
    
    return 0;
}
```

**Assembly:**
```nasm
section .data
    numbers db 5, 10, 15, 20, 25    ; Array of 5 bytes

section .text
    global _start

_start:
    mov rbx, numbers        ; RBX = address of numbers[0]
    
    ; Access individual elements
    mov al, [rbx + 0]       ; AL = 5  (numbers[0])
    mov al, [rbx + 1]       ; AL = 10 (numbers[1])
    mov al, [rbx + 2]       ; AL = 15 (numbers[2])
    mov al, [rbx + 3]       ; AL = 20 (numbers[3])
    mov al, [rbx + 4]       ; AL = 25 (numbers[4])
    
    ; Using index register
    mov rcx, 2              ; index = 2
    mov al, [rbx + rcx]     ; AL = 15 (numbers[2])
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 2: 32-bit Integer Array**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    int32_t ints[] = {100, 200, 300, 400, 500};
    int32_t *ptr = ints;  // ptr points to ints[0]
    
    int index = 2;  // We want ints[2]
    
    // C automatically multiplies index by sizeof(int32_t) = 4
    int32_t value = ptr[index];  // value = 300
    
    // Equivalent pointer arithmetic:
    // int32_t value = *(ptr + index);
    
    return 0;
}
```

**Assembly:**
```nasm
section .data
    ; Array of 32-bit integers (4 bytes each)
    ints dd 100, 200, 300, 400, 500

section .text
    global _start

_start:
    mov rbx, ints           ; RBX = base address
    mov rcx, 2              ; index = 2 (want ints[2])
    
    ; Access ints[2] - need to multiply index by 4 (size of int)
    mov eax, [rbx + rcx*4]  ; EAX = 300
    
    ; Alternative without scale:
    mov rcx, 8              ; offset = 2 * 4 = 8 bytes
    mov eax, [rbx + rcx]    ; EAX = 300
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 3: Writing to Memory**

**C Equivalent:**
```c
#include <stdint.h>

int main() {
    char buffer[10];  // 10-byte buffer
    char *ptr = buffer;
    
    // Write values to buffer
    ptr[0] = 'H';
    ptr[1] = 'e';
    ptr[2] = 'l';
    ptr[3] = 'l';
    ptr[4] = 'o';
    ptr[5] = '\0';  // Null terminator
    
    // Now buffer contains "Hello\0"
    
    return 0;
}
```

**Assembly:**
```nasm
section .bss
    buffer resb 10          ; 10-byte buffer

section .text
    global _start

_start:
    mov rbx, buffer         ; RBX = address of buffer
    
    ; Write values to buffer
    mov byte [rbx + 0], 'H'
    mov byte [rbx + 1], 'e'
    mov byte [rbx + 2], 'l'
    mov byte [rbx + 3], 'l'
    mov byte [rbx + 4], 'o'
    mov byte [rbx + 5], 0   ; Null terminator
    
    ; Now buffer contains "Hello\0"
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

### **Example 4: Pointer Dereference**

```nasm
section .data
    value   dq 42           ; A 64-bit value
    ptr     dq value        ; ptr stores ADDRESS of value

section .text
    global _start

_start:
    ; Method 1: Direct access
    mov rax, [value]        ; RAX = 42
    
    ; Method 2: Through pointer
    mov rbx, [ptr]          ; RBX = address of value
    mov rax, [rbx]          ; RAX = 42 (dereference pointer)
    
    ; This is like C code:
    ; int value = 42;
    ; int *ptr = &value;
    ; int x = *ptr;         // x = 42
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Size Specifications

Sometimes you need to tell NASM the size explicitly:

```nasm
mov rax, [rbx]              ; Size inferred from RAX (64-bit)
mov [rbx], rax              ; Size inferred from RAX (64-bit)

; But what about this?
mov [rbx], 100              ; ERROR: Size ambiguous!

; Solution: Specify size explicitly
mov byte [rbx], 100         ; Store 1 byte
mov word [rbx], 100         ; Store 2 bytes
mov dword [rbx], 100        ; Store 4 bytes
mov qword [rbx], 100        ; Store 8 bytes
```

**Size keywords:**
- `byte` - 8 bits (1 byte)
- `word` - 16 bits (2 bytes)
- `dword` - 32 bits (4 bytes)
- `qword` - 64 bits (8 bytes)

---

## Common Patterns

### **String/Array Iteration**

```nasm
section .data
    str db "Hello", 0

section .text
    mov rsi, str            ; RSI = address of string
    xor rcx, rcx            ; RCX = index = 0
    
loop_start:
    mov al, [rsi + rcx]     ; Load character
    test al, al             ; Check if zero
    jz loop_end             ; Exit if null terminator
    
    ; Process character in AL...
    
    inc rcx                 ; Next character
    jmp loop_start
    
loop_end:
    ; Done
```

### **Stack Frame Access**

```nasm
; Function with local variables
my_function:
    push rbp
    mov rbp, rsp
    sub rsp, 16             ; Allocate 16 bytes for locals
    
    ; Access local variables
    mov dword [rbp - 4], 10     ; local1 = 10
    mov dword [rbp - 8], 20     ; local2 = 20
    
    ; Access function parameters (passed on stack)
    mov rax, [rbp + 16]         ; First parameter
    mov rbx, [rbp + 24]         ; Second parameter
    
    leave
    ret
```

---

## Memory Safety Warning

```nasm
; ✅ SAFE - valid address
mov rbx, buffer
mov al, [rbx]

; ❌ DANGEROUS - uninitialized pointer
mov rbx, 0
mov al, [rbx]               ; SEGFAULT! Accessing address 0

; ❌ DANGEROUS - random value
mov al, [rax]               ; SEGFAULT if RAX has garbage value

; ❌ DANGEROUS - out of bounds
section .data
    arr db 1, 2, 3
section .text
    mov rbx, arr
    mov al, [rbx + 1000]    ; Reading past end of array!
```

---

## TL;DR - The `[ ]` Summary

```
┌─────────────────────────────────────────────────────────┐
│  SYNTAX              │  MEANING                         │
├──────────────────────┼──────────────────────────────────┤
│  mov rax, 5          │  RAX = 5                         │
│  mov rax, [5]        │  RAX = memory[5]                 │
│  mov rax, rbx        │  RAX = RBX                       │
│  mov rax, [rbx]      │  RAX = memory[RBX]               │
│  mov rax, [rbx + 8]  │  RAX = memory[RBX + 8]           │
│  mov rax, [rbx + rcx]│  RAX = memory[RBX + RCX]         │
│  mov rax, [rbx+rcx*4]│  RAX = memory[RBX + RCX*4]       │
└──────────────────────┴──────────────────────────────────┘

KEY RULE:
  [ ] = "Go to this address and access memory there"
  No [ ] = "Use this value directly"
```

---

**Related Topics:**
- [Topic 2: Registers & Data Types](../topics/topic-02-registers.md)
- Pointer arithmetic
- Array indexing
- C pointers vs assembly addressing

---

[← Back to Q&A Index](../README.md#-qa-section---deep-dives)

