# 📘 Topic 11: Memory Addressing Modes

Master all x86-64 addressing modes for flexible and efficient memory access.

---

## **Overview**

**Memory addressing modes** determine how the CPU calculates the address of data in memory. Understanding these is crucial for:
- 🎯 Efficient array access
- 📊 Data structure manipulation
- ⚡ Performance optimization
- 🔍 Reading compiler output

---

## **Part 1: The Square Brackets [ ]**

**Square brackets mean**: "Go to this address and get/put the value there"

**Without brackets** = the address itself  
**With brackets** = the value at that address

```nasm
mov rax, array          ; RAX = address of array
mov rax, [array]        ; RAX = value at array
```

---

## **Part 2: All Addressing Modes**

### **1. Immediate (No Memory Access)**

**C Equivalent:**
```c
int x = 42;             // Constant value
```

**Assembly:**
```nasm
mov rax, 42             ; RAX = 42 (no memory access)
mov eax, 0x1234         ; EAX = 0x1234
```

---

### **2. Register Direct**

**C Equivalent:**
```c
int a = b;              // Register to register
```

**Assembly:**
```nasm
mov rax, rbx            ; RAX = RBX (no memory access)
mov eax, edx            ; EAX = EDX
```

---

### **3. Memory Direct (Absolute Address)**

**C Equivalent:**
```c
int x = *(int*)0x1000;  // Read from absolute address
```

**Assembly:**
```nasm
mov rax, [0x1000]       ; RAX = value at address 0x1000
mov [0x2000], rbx       ; Store RBX at address 0x2000
```

**Usage:** Rarely used (except for memory-mapped I/O).

---

### **4. Register Indirect**

**C Equivalent:**
```c
int *ptr = &value;
int x = *ptr;           // Dereference pointer
```

**Assembly:**
```nasm
mov rbx, array          ; RBX = address
mov rax, [rbx]          ; RAX = value at address in RBX
mov [rbx], rcx          ; Store RCX at address in RBX
```

---

### **5. Register + Displacement**

**C Equivalent:**
```c
struct Point {
    int x;              // offset 0
    int y;              // offset 4
};
struct Point *p;
int y_value = p->y;     // Access field at offset
```

**Assembly:**
```nasm
; RBX points to struct
mov eax, [rbx + 0]      ; Access x (offset 0)
mov eax, [rbx + 4]      ; Access y (offset 4)
mov eax, [rbx + 8]      ; Access next field

; Array access
mov rax, [array + 16]   ; Access element 16 bytes into array
```

---

### **6. Base + Index**

**C Equivalent:**
```c
int array[10];
int index = 5;
int value = array[index];   // Dynamic index
```

**Assembly:**
```nasm
mov rbx, array          ; base = array address
mov rcx, 5              ; index = 5
mov eax, [rbx + rcx]    ; value = array[index]
```

---

### **7. Base + Index*Scale (SIB - Scale-Index-Base)**

**Most powerful addressing mode!**

**Format:** `[base + index*scale + displacement]`

**Where:**
- `base` = any register (RBX, RSI, etc.)
- `index` = any register except RSP
- `scale` = 1, 2, 4, or 8
- `displacement` = constant offset (-2³¹ to 2³¹-1)

**C Equivalent:**
```c
int array[100];
int index = 10;
int value = array[index];   // array + index * sizeof(int)
```

**Assembly:**
```nasm
; Access int array (4 bytes per element)
mov rbx, array          ; base
mov rcx, 10             ; index
mov eax, [rbx + rcx*4]  ; value = array[index]
                        ; Address = base + index*4

; Access long array (8 bytes per element)
mov rax, [rbx + rcx*8]  ; Address = base + index*8

; With displacement
mov eax, [rbx + rcx*4 + 16]  ; Skip first 4 elements (16 bytes)
```

---

## **Part 3: Scale Factor Examples**

```nasm
; Scale = 1 (byte arrays, char)
mov al, [rsi + rdi*1]       ; char array[index]

; Scale = 2 (word arrays, short)
mov ax, [rsi + rdi*2]       ; short array[index]

; Scale = 4 (dword arrays, int, float)
mov eax, [rsi + rdi*4]      ; int array[index]

; Scale = 8 (qword arrays, long, double, pointers)
mov rax, [rsi + rdi*8]      ; long array[index]
```

---

## **Part 4: RIP-Relative Addressing (x86-64)**

**Position-independent code** - address relative to current instruction.

**C Equivalent:**
```c
static int global_var = 42;
int x = global_var;         // Compiler uses RIP-relative
```

**Assembly:**
```nasm
section .data
    value dq 100

section .text
    ; RIP-relative (x86-64 only)
    mov rax, [rel value]    ; Address = RIP + offset to value
    
    ; Explicit form (NASM)
    mov rax, [value wrt ..gotpc]
    
    ; Default in 64-bit
    mov rax, [value]        ; NASM uses RIP-relative by default
```

**Why use it:**
- ✅ Code can be loaded at any address (PIE/PIC)
- ✅ More compact encoding
- ✅ Required for shared libraries

---

## **Part 5: Practical Examples**

### **Example 1: Array Iteration**

**C Equivalent:**
```c
int sum_array(int *array, int count) {
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += array[i];
    }
    return sum;
}
```

**Assembly (Method 1: Index):**
```nasm
; int sum_array(int *array, int count)
; Args: array=RDI, count=ESI
sum_array:
    xor eax, eax            ; sum = 0
    xor ecx, ecx            ; i = 0
    
loop:
    cmp ecx, esi
    jge done
    
    add eax, [rdi + rcx*4]  ; sum += array[i] (SIB addressing!)
    inc ecx
    jmp loop
    
done:
    ret
```

**Assembly (Method 2: Pointer):**
```nasm
sum_array:
    xor eax, eax            ; sum = 0
    lea rdx, [rdi + rsi*4]  ; end = array + count*4
    
loop:
    cmp rdi, rdx
    jge done
    
    add eax, [rdi]          ; sum += *ptr (register indirect!)
    add rdi, 4              ; ptr++
    jmp loop
    
done:
    ret
```

---

### **Example 2: Struct Access**

**C Equivalent:**
```c
struct Person {
    int age;        // offset 0
    int height;     // offset 4
    long id;        // offset 8
};

int get_height(struct Person *p) {
    return p->height;
}
```

**Assembly:**
```nasm
; int get_height(struct Person *p)
; Arg: p in RDI
get_height:
    mov eax, [rdi + 4]      ; return p->height (displacement!)
    ret
```

---

### **Example 3: 2D Array Access**

**C Equivalent:**
```c
int matrix[ROWS][COLS];
int get_element(int row, int col) {
    return matrix[row][col];
}
```

**Assembly:**
```nasm
; Assume COLS = 10, each element is 4 bytes
; Address = base + (row * COLS + col) * 4

section .data
    matrix times 100 dd 0   ; 10x10 matrix

section .text
; int get_element(int row, int col)
; Args: row=EDI, col=ESI
get_element:
    ; Calculate: row * COLS (10)
    imul edi, 10            ; row * COLS
    
    ; Calculate: (row * COLS + col) * 4
    add edi, esi            ; row * COLS + col
    
    mov rbx, matrix
    mov eax, [rbx + rdi*4]  ; matrix[row][col] (SIB!)
    ret
```

---

### **Example 4: String Operations**

**C Equivalent:**
```c
char *strcpy(char *dest, const char *src) {
    char *orig_dest = dest;
    while (*src != '\0') {
        *dest++ = *src++;
    }
    *dest = '\0';
    return orig_dest;
}
```

**Assembly:**
```nasm
; char *strcpy(char *dest, const char *src)
; Args: dest=RDI, src=RSI
strcpy:
    mov rax, rdi            ; Save orig_dest
    
loop:
    mov cl, [rsi]           ; Load byte from src (register indirect!)
    mov [rdi], cl           ; Store to dest
    
    test cl, cl             ; Check if null
    jz done
    
    inc rsi                 ; src++
    inc rdi                 ; dest++
    jmp loop
    
done:
    ret
```

---

## **Part 6: Address Calculation Examples**

### **Calculate Effective Address (LEA)**

LEA doesn't access memory - it just calculates the address!

**C Equivalent:**
```c
int *ptr = &array[index];   // Get address, not value
int offset = index * 4 + 10; // Calculate without memory access
```

**Assembly:**
```nasm
; Get address (doesn't dereference)
lea rax, [rbx + rcx*4]      ; RAX = rbx + rcx*4 (no memory access!)

; Use for arithmetic
lea rax, [rdi + rdi*4]      ; RAX = rdi * 5 (1 + 4)
lea rax, [rdi + rdi*8]      ; RAX = rdi * 9 (1 + 8)
lea rax, [rdi + rsi + 10]   ; RAX = rdi + rsi + 10
```

---

## **Part 7: Size Specifiers**

When size is ambiguous, use size specifiers:

```nasm
; Ambiguous
mov [rbx], 42               ; ❌ ERROR: What size?

; Clear
mov byte [rbx], 42          ; ✓ 1 byte
mov word [rbx], 42          ; ✓ 2 bytes
mov dword [rbx], 42         ; ✓ 4 bytes
mov qword [rbx], 42         ; ✓ 8 bytes

; Not ambiguous (size inferred from register)
mov [rbx], al               ; ✓ 1 byte (AL is 8-bit)
mov [rbx], ax               ; ✓ 2 bytes (AX is 16-bit)
mov [rbx], eax              ; ✓ 4 bytes (EAX is 32-bit)
mov [rbx], rax              ; ✓ 8 bytes (RAX is 64-bit)
```

---

## **Part 8: Common Patterns**

### **Pattern 1: Array Element Access**

```nasm
; array[index]
mov eax, [array + rcx*4]    ; For int array (4 bytes)
mov rax, [array + rcx*8]    ; For long/pointer array (8 bytes)
```

### **Pattern 2: Struct Field Access**

```nasm
; struct->field
mov eax, [rbx + OFFSET]     ; Access field at offset
```

### **Pattern 3: Pointer Arithmetic**

```nasm
; ptr++
add rdi, 4                  ; Advance by 4 bytes (int*)
add rdi, 8                  ; Advance by 8 bytes (long*)
```

### **Pattern 4: Array of Structs**

```nasm
; array[index].field
; Address = base + index*sizeof(struct) + field_offset
mov eax, [rbx + rcx*16 + 4] ; Assuming 16-byte structs, field at offset 4
```

---

## **Part 9: Performance Considerations**

### **Cache-Friendly Access**

```nasm
; ✓ GOOD: Sequential access (cache-friendly)
mov rcx, 0
loop:
    mov eax, [array + rcx*4]
    ; Process eax
    inc rcx
    cmp rcx, 100
    jl loop

; ❌ BAD: Random access (cache-unfriendly)
mov rcx, 0
loop:
    ; Random index calculation
    mov eax, [array + random_index*4]
```

### **Alignment**

```nasm
; Aligned access (faster)
section .data
    align 16
    aligned_array dq 1, 2, 3, 4

; Misaligned access (slower, may cause crashes on some CPUs)
mov rax, [rbx + 1]          ; Misaligned 64-bit read
```

---

## **✅ Practice Exercises**

### **Exercise 1: Array Sum**

Calculate the sum of a double array (8-byte elements).

<details>
<summary>Solution</summary>

```nasm
; double sum_doubles(double *array, int count)
; Args: array=RDI, count=ESI
sum_doubles:
    xorpd xmm0, xmm0        ; sum = 0.0
    xor ecx, ecx            ; i = 0
    
loop:
    cmp ecx, esi
    jge done
    
    addsd xmm0, [rdi + rcx*8]   ; sum += array[i] (scale=8!)
    inc ecx
    jmp loop
    
done:
    ; Result in XMM0
    ret
```
</details>

---

### **Exercise 2: Reverse Array**

Reverse an array in place.

<details>
<summary>Solution</summary>

```nasm
; void reverse(int *array, int count)
; Args: array=RDI, count=ESI
reverse:
    xor ecx, ecx            ; left = 0
    lea edx, [esi - 1]      ; right = count - 1
    
loop:
    cmp ecx, edx
    jge done
    
    ; Swap array[left] and array[right]
    mov eax, [rdi + rcx*4]
    mov ebx, [rdi + rdx*4]
    mov [rdi + rcx*4], ebx
    mov [rdi + rdx*4], eax
    
    inc ecx                 ; left++
    dec edx                 ; right--
    jmp loop
    
done:
    ret
```
</details>

---

## **📋 Quick Reference**

### **Addressing Modes**
```nasm
[register]                  ; Register indirect
[register + disp]           ; Register + displacement
[base + index]              ; Base + index
[base + index*scale]        ; SIB
[base + index*scale + disp] ; Full SIB
[rel label]                 ; RIP-relative
```

### **Scale Values**
```
1 → byte/char
2 → word/short
4 → dword/int/float
8 → qword/long/double/pointer
```

---

## **🎯 Knowledge Check**

- ✅ All 7 addressing modes and when to use each
- ✅ SIB addressing (Scale-Index-Base)
- ✅ Scale factors for different data types
- ✅ RIP-relative addressing and why it matters
- ✅ LEA for address calculation
- ✅ Size specifiers (byte/word/dword/qword)
- ✅ Performance implications of different modes

---

**🎉 Excellent!** You've mastered memory addressing!

**Next:** Topic 12: Arrays & Strings

---

[← Previous Topic](topic-10-procedures.md) | [Back to Main](../README.md) | [Next Topic →](topic-12-arrays-strings.md)
