# int 0x80 vs syscall - When to Use Which?

## Question
*When to use int 0x80, and when to use syscall?*

---

## Quick Answer

| Method | Architecture | Use When |
|--------|-------------|----------|
| **`int 0x80`** | 32-bit | Writing 32-bit programs or need legacy compatibility |
| **`syscall`** | 64-bit | Writing modern 64-bit programs (preferred) |

---

## Detailed Comparison

### **1. Architecture Requirement**

**`int 0x80`** - Legacy 32-bit Method
- Works on: 32-bit x86 processors
- Can work on 64-bit processors running in 32-bit mode
- Been around since the 386 processor

**`syscall`** - Modern 64-bit Method
- Works on: 64-bit x86-64 processors only
- Introduced with AMD's x86-64 architecture
- **Does NOT work on pure 32-bit systems**

---

## **2. Register Usage - CRITICAL DIFFERENCE!**

### **`int 0x80` (32-bit registers)**

```nasm
mov eax, 4          ; syscall number in EAX
mov ebx, 1          ; arg1 in EBX
mov ecx, msg        ; arg2 in ECX
mov edx, len        ; arg3 in EDX
mov esi, arg4       ; arg4 in ESI (if needed)
mov edi, arg5       ; arg5 in EDI (if needed)
int 0x80            ; trigger interrupt
```

### **`syscall` (64-bit registers)**

```nasm
mov rax, 1          ; syscall number in RAX
mov rdi, 1          ; arg1 in RDI
mov rsi, msg        ; arg2 in RSI
mov rdx, len        ; arg3 in RDX
mov r10, arg4       ; arg4 in R10 (if needed)
mov r8, arg5        ; arg5 in R8 (if needed)
mov r9, arg6        ; arg6 in R9 (if needed)
syscall             ; fast system call
```

**Key Difference:**
- `int 0x80`: EAX, EBX, ECX, EDX, ESI, EDI
- `syscall`: RAX, RDI, RSI, RDX, R10, R8, R9

---

## **3. Syscall Numbers - DIFFERENT VALUES!**

The same system call has **different numbers** in 32-bit vs 64-bit!

| Operation | 32-bit (`int 0x80`) | 64-bit (`syscall`) |
|-----------|---------------------|-------------------|
| sys_read  | 3 | 0 |
| sys_write | 4 | 1 |
| sys_open  | 5 | 2 |
| sys_close | 6 | 3 |
| sys_exit  | 1 | 60 |

**Example - Exit syscall:**

```nasm
; 32-bit exit
mov eax, 1          ; exit is syscall #1 in 32-bit
xor ebx, ebx        ; exit code 0
int 0x80

; 64-bit exit
mov rax, 60         ; exit is syscall #60 in 64-bit!
xor rdi, rdi        ; exit code 0
syscall
```

---

## **4. Performance**

**`syscall` is MUCH faster** than `int 0x80`:

- **`int 0x80`**: ~300 CPU cycles (slow context switch)
- **`syscall`**: ~100 CPU cycles (optimized fast path)

`syscall` was designed specifically to be faster by avoiding the overhead of interrupt handling.

---

## **5. Practical Examples**

### **Complete 32-bit Program (`int 0x80`)**

**C Equivalent (same for both 32-bit and 64-bit):**
```c
#include <unistd.h>

int main() {
    const char *msg = "32-bit mode!\n";
    size_t len = 13;
    
    // write(1, msg, len)
    write(1, msg, len);
    
    // exit(0)
    return 0;
}
```

**Assembly (32-bit):**
```nasm
; Build: nasm -f elf32 prog32.asm && ld -m elf_i386 -o prog32 prog32.o

section .data
    msg db "32-bit mode!", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; write(1, msg, len)
    mov eax, 4          ; sys_write = 4
    mov ebx, 1          ; stdout
    mov ecx, msg        ; buffer
    mov edx, len        ; count
    int 0x80

    ; exit(0)
    mov eax, 1          ; sys_exit = 1
    xor ebx, ebx        ; status 0
    int 0x80
```

### **Complete 64-bit Program (`syscall`)**

**C Equivalent (same as 32-bit version):**
```c
#include <unistd.h>

int main() {
    const char *msg = "64-bit mode!\n";
    size_t len = 13;
    
    // write(1, msg, len)
    write(1, msg, len);
    
    // exit(0)
    return 0;
}
// Note: The C code is identical - only the assembly differs!
```

**Assembly (64-bit):**
```nasm
; Build: nasm -f elf64 prog64.asm && ld -o prog64 prog64.o

section .data
    msg db "64-bit mode!", 10
    len equ $ - msg

section .text
    global _start

_start:
    ; write(1, msg, len)
    mov rax, 1          ; sys_write = 1
    mov rdi, 1          ; stdout
    mov rsi, msg        ; buffer
    mov rdx, len        ; count
    syscall

    ; exit(0)
    mov rax, 60         ; sys_exit = 60
    xor rdi, rdi        ; status 0
    syscall
```

---

## **6. What Happens If You Mix Them Up?**

### **❌ Using `int 0x80` in 64-bit mode**

```nasm
; This WILL work but is WRONG and SLOW
section .text
    global _start
_start:
    mov eax, 4          ; Wrong! Using 32-bit syscall numbers
    mov ebx, 1
    mov ecx, msg
    mov edx, len
    int 0x80            ; Works but uses compatibility layer (slow!)
```

**Problems:**
- ✗ Uses slow compatibility mode
- ✗ Only accesses lower 32 bits of registers
- ✗ Different syscall numbers may cause confusion
- ✓ Will technically work on Linux (for compatibility)

### **❌ Using `syscall` in 32-bit mode**

```nasm
; This will CRASH!
mov rax, 1
syscall             ; ILLEGAL INSTRUCTION on 32-bit CPU!
```

**Result:** `Illegal instruction (core dumped)`

---

## **7. How to Detect Your Architecture**

Check what you're running:

```bash
# Check if your kernel is 64-bit
uname -m
# Output: x86_64 (64-bit) or i686/i386 (32-bit)

# Check what format your program is
file ./your_program
# Output examples:
# ELF 32-bit LSB executable  -> use int 0x80
# ELF 64-bit LSB executable  -> use syscall
```

---

## **8. Decision Tree**

```
Are you writing for 64-bit Linux?
│
├─ YES → Use `syscall`
│        • Use 64-bit registers (rax, rdi, rsi, rdx...)
│        • Use 64-bit syscall numbers
│        • Assemble with: nasm -f elf64
│        • Link with: ld (default)
│
└─ NO (32-bit or compatibility)
         → Use `int 0x80`
         • Use 32-bit registers (eax, ebx, ecx, edx...)
         • Use 32-bit syscall numbers
         • Assemble with: nasm -f elf32
         • Link with: ld -m elf_i386
```

---

## **9. Modern Best Practice**

**For new code in 2025:**
- ✅ **Use `syscall`** - You're almost certainly on 64-bit
- ✅ Faster and more efficient
- ✅ Better register usage (more registers available)
- ✅ Native to modern CPUs

**Only use `int 0x80` if:**
- You're maintaining legacy 32-bit code
- You're learning for historical purposes
- You're targeting ancient 32-bit systems

---

## **10. Quick Reference Card**

```nasm
╔════════════════════════════════════════════════════════╗
║  32-BIT (int 0x80)     │    64-BIT (syscall)          ║
╠════════════════════════════════════════════════════════╣
║  nasm -f elf32         │    nasm -f elf64             ║
║  ld -m elf_i386        │    ld                        ║
║                        │                              ║
║  mov eax, 4  ; write   │    mov rax, 1    ; write    ║
║  mov ebx, 1            │    mov rdi, 1               ║
║  mov ecx, msg          │    mov rsi, msg             ║
║  mov edx, len          │    mov rdx, len             ║
║  int 0x80              │    syscall                  ║
║                        │                              ║
║  mov eax, 1  ; exit    │    mov rax, 60   ; exit     ║
║  xor ebx, ebx          │    xor rdi, rdi             ║
║  int 0x80              │    syscall                  ║
╚════════════════════════════════════════════════════════╝
```

---

## TL;DR

- **64-bit program? → Use `syscall`** (faster, modern, RAX/RDI/RSI/RDX)
- **32-bit program? → Use `int 0x80`** (legacy, EAX/EBX/ECX/EDX)
- **Different syscall numbers!** (write is 4 vs 1, exit is 1 vs 60)
- **Don't mix them** or you'll get confused/slow code

Since you're on a modern Linux system (`x86_64`), **stick with `syscall` for all your 64-bit programs!**

---

**See Also:**
- [Topic 1: Setup & First Program](../topics/topic-01-setup.md)
- Linux Syscall Table: https://filippo.io/linux-syscall-table/

---

[← Back to Q&A Index](../README.md#-qa-section---deep-dives)

