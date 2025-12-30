# 📘 Topic 12: Arrays & Strings

Master array manipulation and string operations in assembly, including powerful string instructions.

---

## **Overview**

Arrays and strings are fundamental data structures. Assembly provides:
- 📊 Direct memory manipulation for arrays
- 🔤 Specialized string instructions (REP prefix)
- ⚡ Highly optimized bulk operations
- 🎯 Fine-grained control over data processing

---

## **Part 1: Arrays in Assembly**

### **Declaring Arrays**

**C Equivalent:**
```c
int numbers[] = {10, 20, 30, 40, 50};
char name[] = "Hello";
int buffer[100];  // Uninitialized
```

**Assembly:**
```nasm
section .data
    ; Initialized arrays
    numbers dd 10, 20, 30, 40, 50       ; 5 ints (20 bytes)
    floats  dd 1.0, 2.5, 3.14          ; 3 floats
    name    db "Hello", 0               ; String (6 bytes including null)
    bytes   db 0x41, 0x42, 0x43        ; 3 bytes
    
section .bss
    ; Uninitialized arrays
    buffer  resb 100                    ; 100 bytes
    int_arr resd 50                     ; 50 ints (200 bytes)
    long_arr resq 20                    ; 20 longs (160 bytes)
```

---

### **Accessing Array Elements**

**C Equivalent:**
```c
int get_element(int *array, int index) {
    return array[index];
}
```

**Assembly:**
```nasm
; int get_element(int *array, int index)
; Args: array=RDI, index=ESI
get_element:
    mov eax, [rdi + rsi*4]      ; array[index], scale=4 for int
    ret
```

---

## **Part 2: Common Array Operations**

### **Example 1: Sum Array**

**C Equivalent:**
```c
int sum(int *arr, int size) {
    int total = 0;
    for (int i = 0; i < size; i++) {
        total += arr[i];
    }
    return total;
}
```

**Assembly:**
```nasm
sum:
    xor eax, eax                ; total = 0
    xor ecx, ecx                ; i = 0
loop:
    cmp ecx, esi
    jge done
    add eax, [rdi + rcx*4]
    inc ecx
    jmp loop
done:
    ret
```

---

### **Example 2: Find Maximum**

**C Equivalent:**
```c
int find_max(int *arr, int size) {
    int max = arr[0];
    for (int i = 1; i < size; i++) {
        if (arr[i] > max) max = arr[i];
    }
    return max;
}
```

**Assembly:**
```nasm
find_max:
    mov eax, [rdi]              ; max = arr[0]
    mov ecx, 1                  ; i = 1
loop:
    cmp ecx, esi
    jge done
    cmp eax, [rdi + rcx*4]
    jge skip
    mov eax, [rdi + rcx*4]      ; max = arr[i]
skip:
    inc ecx
    jmp loop
done:
    ret
```

---

## **Part 3: String Basics**

### **Strings in Assembly**

Strings are **byte arrays** terminated by null (0).

```nasm
section .data
    msg db "Hello", 0           ; 6 bytes: 'H','e','l','l','o',0
    msg_len equ $ - msg         ; Length = 6
```

---

### **Manual String Length**

**C Equivalent:**
```c
size_t strlen(const char *str) {
    size_t len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}
```

**Assembly:**
```nasm
my_strlen:
    xor eax, eax                ; len = 0
loop:
    cmp byte [rdi + rax], 0     ; Check for null
    je done
    inc rax
    jmp loop
done:
    ret
```

---

## **Part 4: String Instructions**

x86 provides specialized string instructions that operate on memory blocks.

### **Direction Flag (DF)**

Controls direction of string operations:
- `DF = 0`: Forward (increment addresses) - **use `cld`**
- `DF = 1`: Backward (decrement addresses) - **use `std`**

```nasm
cld                             ; Clear DF (forward direction)
std                             ; Set DF (backward direction)
```

---

### **String Instructions Overview**

```
┌──────────┬─────────────────────────────────────────────────┐
│ Instr    │ Operation                                       │
├──────────┼─────────────────────────────────────────────────┤
│ MOVSB    │ Move byte: [RDI] = [RSI], RSI++, RDI++         │
│ MOVSW    │ Move word (2 bytes)                             │
│ MOVSD    │ Move dword (4 bytes)                            │
│ MOVSQ    │ Move qword (8 bytes)                            │
├──────────┼─────────────────────────────────────────────────┤
│ LODSB    │ Load byte: AL = [RSI], RSI++                   │
│ LODSW    │ Load word: AX = [RSI], RSI += 2                │
│ LODSD    │ Load dword: EAX = [RSI], RSI += 4              │
│ LODSQ    │ Load qword: RAX = [RSI], RSI += 8              │
├──────────┼─────────────────────────────────────────────────┤
│ STOSB    │ Store byte: [RDI] = AL, RDI++                  │
│ STOSW    │ Store word: [RDI] = AX, RDI += 2               │
│ STOSD    │ Store dword: [RDI] = EAX, RDI += 4             │
│ STOSQ    │ Store qword: [RDI] = RAX, RDI += 8             │
├──────────┼─────────────────────────────────────────────────┤
│ SCASB    │ Scan byte: Compare AL with [RDI], RDI++        │
│ SCASW    │ Scan word                                       │
│ SCASD    │ Scan dword                                      │
│ SCASQ    │ Scan qword                                      │
├──────────┼─────────────────────────────────────────────────┤
│ CMPSB    │ Compare byte: [RSI] with [RDI], RSI++, RDI++   │
│ CMPSW    │ Compare word                                    │
│ CMPSD    │ Compare dword                                   │
│ CMPSQ    │ Compare qword                                   │
└──────────┴─────────────────────────────────────────────────┘
```

---

### **REP Prefix - Repeat**

Repeats string instruction RCX times:

```nasm
rep movsb                       ; Repeat MOVSB RCX times
rep stosb                       ; Repeat STOSB RCX times
```

**Conditional repeats:**
```nasm
repe cmpsb                      ; Repeat while equal (and RCX > 0)
repne scasb                     ; Repeat while not equal (and RCX > 0)
```

---

## **Part 5: String Operations Examples**

### **Example 1: Memory Copy (memcpy)**

**C Equivalent:**
```c
void *memcpy(void *dest, const void *src, size_t n) {
    char *d = dest;
    const char *s = src;
    while (n--) {
        *d++ = *s++;
    }
    return dest;
}
```

**Assembly (Manual):**
```nasm
my_memcpy:
    mov rax, rdi                ; Save dest
    test rdx, rdx
    jz done
loop:
    mov cl, [rsi]
    mov [rdi], cl
    inc rsi
    inc rdi
    dec rdx
    jnz loop
done:
    ret
```

**Assembly (Optimized with REP):**
```nasm
my_memcpy:
    mov rax, rdi                ; Save dest
    mov rcx, rdx                ; Count
    cld                         ; Forward direction
    rep movsb                   ; Copy RCX bytes from RSI to RDI
    ret
```

---

### **Example 2: Memory Set (memset)**

**C Equivalent:**
```c
void *memset(void *s, int c, size_t n) {
    unsigned char *p = s;
    while (n--) {
        *p++ = (unsigned char)c;
    }
    return s;
}
```

**Assembly:**
```nasm
my_memset:
    mov rax, rdi                ; Save dest
    mov al, sil                 ; Value to set (2nd arg, low byte)
    mov rcx, rdx                ; Count
    cld
    rep stosb                   ; Set RCX bytes at RDI to AL
    ret
```

---

### **Example 3: String Copy (strcpy)**

**C Equivalent:**
```c
char *strcpy(char *dest, const char *src) {
    char *orig = dest;
    while ((*dest++ = *src++) != '\0');
    return orig;
}
```

**Assembly:**
```nasm
my_strcpy:
    mov rax, rdi                ; Save dest
loop:
    lodsb                       ; AL = [RSI++]
    stosb                       ; [RDI++] = AL
    test al, al
    jnz loop
    ret
```

---

### **Example 4: String Length (strlen)**

**C Equivalent:**
```c
size_t strlen(const char *s) {
    size_t len = 0;
    while (s[len]) len++;
    return len;
}
```

**Assembly (with SCASB):**
```nasm
my_strlen:
    mov rax, rdi                ; Save start
    xor al, al                  ; Search for null (0)
    mov rcx, -1                 ; Max count (search forever)
    cld
    repne scasb                 ; Scan until AL found or RCX=0
    ; RDI now points one past null
    mov rax, rdi
    sub rax, [rsp+8]            ; Original rdi (from caller)
    dec rax                     ; Don't count null
    ret
    
; Simpler version:
my_strlen_simple:
    xor rax, rax
loop:
    cmp byte [rdi + rax], 0
    je done
    inc rax
    jmp loop
done:
    ret
```

---

### **Example 5: String Compare (strcmp)**

**C Equivalent:**
```c
int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}
```

**Assembly:**
```nasm
my_strcmp:
loop:
    mov al, [rdi]
    mov cl, [rsi]
    cmp al, cl
    jne not_equal
    test al, al                 ; Check if null
    jz equal
    inc rdi
    inc rsi
    jmp loop
    
equal:
    xor eax, eax                ; Return 0
    ret
    
not_equal:
    movzx eax, al
    movzx ecx, cl
    sub eax, ecx
    ret
```

---

## **Part 6: Multi-Dimensional Arrays**

**C Equivalent:**
```c
int matrix[3][4] = {
    {1, 2, 3, 4},
    {5, 6, 7, 8},
    {9, 10, 11, 12}
};

int get(int row, int col) {
    return matrix[row][col];
}
```

**Assembly:**
```nasm
section .data
    matrix dd 1,2,3,4, 5,6,7,8, 9,10,11,12
    COLS equ 4

section .text
; int get(int row, int col)
; Args: row=EDI, col=ESI
get:
    imul edi, COLS              ; row * COLS
    add edi, esi                ; row * COLS + col
    mov rbx, matrix
    mov eax, [rbx + rdi*4]      ; matrix[row][col]
    ret
```

---

## **✅ Practice Exercises**

### **Exercise 1: Reverse String**

```c
void reverse(char *str) {
    int len = strlen(str);
    for (int i = 0; i < len/2; i++) {
        char temp = str[i];
        str[i] = str[len-1-i];
        str[len-1-i] = temp;
    }
}
```

<details>
<summary>Solution</summary>

```nasm
reverse:
    push rbx
    mov rbx, rdi                ; str
    call my_strlen              ; RAX = len
    xor rcx, rcx                ; i = 0
    lea rdx, [rax - 1]          ; j = len - 1
loop:
    cmp rcx, rdx
    jge done
    ; Swap str[i] and str[j]
    mov al, [rbx + rcx]
    mov ah, [rbx + rdx]
    mov [rbx + rcx], ah
    mov [rbx + rdx], al
    inc rcx
    dec rdx
    jmp loop
done:
    pop rbx
    ret
```
</details>

---

## **📋 Quick Reference**

```nasm
; String Instructions
cld             ; Clear direction flag (forward)
std             ; Set direction flag (backward)
rep movsb       ; Copy RCX bytes: RSI → RDI
rep stosb       ; Fill RCX bytes: AL → RDI
repne scasb     ; Find AL in [RDI], max RCX bytes

; Array Access
mov eax, [array + rcx*4]        ; array[index] (int)
mov rax, [array + rcx*8]        ; array[index] (long/ptr)
lea rax, [base + index*8 + off] ; Calculate address
```

---

**🎉 Great!** You've mastered arrays and strings!

**Next:** Topic 13: Multiplication & Division

---

[← Previous Topic](topic-11-memory-addressing.md) | [Back to Main](../README.md) | [Next Topic →](topic-13-mul-div.md)
