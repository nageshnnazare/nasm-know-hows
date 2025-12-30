# 📘 Topic 1: Setup & First Program

Welcome to your first assembly lesson! Let's get you set up and writing your first NASM program.

---

## **Part 1: Installation**

Check if NASM is already installed:

```bash
nasm -version
```

If not installed, install it:

```bash
# Red Hat/CentOS/Rocky
sudo yum install nasm

# Or if you have dnf
sudo dnf install nasm

# You'll also need a linker (gcc provides ld)
sudo yum install gcc
```

---

## **Part 2: The Assembly Workflow**

Understanding the build process:

```
┌─────────────┐
│  hello.asm  │  ← Your source code (human-readable)
└──────┬──────┘
       │ nasm -f elf64 hello.asm
       ▼
┌─────────────┐
│  hello.o    │  ← Object file (machine code, not executable yet)
└──────┬──────┘
       │ ld -o hello hello.o
       ▼
┌─────────────┐
│   hello     │  ← Executable (ready to run!)
└─────────────┘
```

---

## **Part 3: Program Structure**

NASM programs have **three main sections**:

### **`.data` section** - Initialized data (variables with values)
```nasm
section .data
    message db "Hello", 0    ; Define byte(s), null-terminated
    number  dd 42            ; Define doubleword (32-bit)
```

### **`.bss` section** - Uninitialized data (reserved space)
```nasm
section .bss
    buffer resb 64           ; Reserve 64 bytes
    counter resd 1           ; Reserve 1 doubleword
```

### **`.text` section** - Your actual code
```nasm
section .text
    global _start            ; Entry point for linker

_start:
    ; Your instructions here
    mov eax, 1               ; Exit syscall
    xor ebx, ebx             ; Return 0
    int 0x80                 ; Call kernel
```

---

## **Part 4: Your First Program - Hello World**

**C Equivalent:**
```c
#include <unistd.h>

int main() {
    const char *msg = "Hello, Assembly!\n";
    size_t msg_len = 17;
    
    // Write to stdout
    write(1, msg, msg_len);
    
    // Exit with code 0
    return 0;
}
```

Create a file called `hello.asm`:

```nasm
; hello.asm - My first NASM program!
; This program prints "Hello, Assembly!" to the console

section .data
    ; Define our message with a newline at the end
    msg db "Hello, Assembly!", 10    ; 10 is newline character '\n'
    msg_len equ $ - msg               ; Calculate length (current pos - start)

section .text
    global _start

_start:
    ; Write message to stdout
    ; syscall: sys_write (rax = 1)
    ; rdi = file descriptor (1 = stdout)
    ; rsi = pointer to message
    ; rdx = message length
    
    mov rax, 1          ; syscall number for sys_write
    mov rdi, 1          ; file descriptor 1 = stdout
    mov rsi, msg        ; address of message
    mov rdx, msg_len    ; length of message
    syscall             ; make the system call
    
    ; Exit program
    ; syscall: sys_exit (rax = 60)
    ; rdi = exit code
    
    mov rax, 60         ; syscall number for sys_exit
    xor rdi, rdi        ; exit code 0 (success)
    syscall             ; make the system call
```

---

## **Part 5: Build and Run**

**Step 1: Assemble** (convert .asm to .o)
```bash
nasm -f elf64 hello.asm -o hello.o
```
- `-f elf64`: output format for 64-bit Linux
- `-o hello.o`: output filename

**Step 2: Link** (convert .o to executable)
```bash
ld -o hello hello.o
```
- `-o hello`: output executable name

**Step 3: Run**
```bash
./hello
```

You should see:
```
Hello, Assembly!
```

**Check exit code:**
```bash
echo $?
```
Should print `0` (success)

---

## **Part 6: Understanding the Code**

### **Line-by-Line Breakdown:**

```nasm
msg db "Hello, Assembly!", 10
```
- `msg` = label (like a variable name)
- `db` = Define Byte (allocates bytes in memory)
- `10` = ASCII code for newline

```nasm
msg_len equ $ - msg
```
- `equ` = equate (like `#define` in C)
- `$` = current position in memory
- `$ - msg` = length of message

```nasm
mov rax, 1
```
- Move value `1` into register `rax`
- In Linux, syscall number 1 = `write`

```nasm
syscall
```
- Transfers control to the kernel
- Kernel looks at `rax` to know which syscall to execute

---

## **Part 7: 32-bit Version** (Alternative)

**C Equivalent (same as 64-bit):**
```c
#include <unistd.h>

int main() {
    const char *msg = "Hello from 32-bit!\n";
    write(1, msg, 19);
    return 0;
}
// Note: The C code is identical - the compiler handles 32 vs 64-bit differences
```

If you want to try 32-bit assembly:

```nasm
; hello32.asm - 32-bit version

section .data
    msg db "Hello from 32-bit!", 10
    msg_len equ $ - msg

section .text
    global _start

_start:
    ; sys_write
    mov eax, 4          ; syscall 4 = write (32-bit)
    mov ebx, 1          ; stdout
    mov ecx, msg        ; message address
    mov edx, msg_len    ; message length
    int 0x80            ; interrupt (32-bit syscall method)
    
    ; sys_exit
    mov eax, 1          ; syscall 1 = exit (32-bit)
    xor ebx, ebx        ; exit code 0
    int 0x80
```

**Build 32-bit:**
```bash
nasm -f elf32 hello32.asm -o hello32.o
ld -m elf_i386 -o hello32 hello32.o
./hello32
```

---

## **Part 8: Common Mistakes & Debugging**

### **❌ Forgot `global _start`**
```
ld: warning: cannot find entry symbol _start
```
**Fix:** Add `global _start` in `.text` section

### **❌ Wrong format**
```
hello.o: file not recognized: file format not recognized
```
**Fix:** Use `-f elf64` for 64-bit or `-f elf32` for 32-bit

### **❌ Segmentation fault**
```
Segmentation fault (core dumped)
```
**Fix:** Check your syscall numbers and register usage

### **🔧 Debug with GDB:**
```bash
nasm -f elf64 -g -F dwarf hello.asm  # Add debug info
ld -o hello hello.o
gdb ./hello
```

---

## **✅ Practice Exercises**

### **Exercise 1: Modify the Message**
Change "Hello, Assembly!" to print your name

### **Exercise 2: Multiple Prints**
Print two different messages (hint: call sys_write twice)

### **Exercise 3: Different Exit Code**
Make the program exit with code 42 instead of 0
- Hint: Change the value in `rdi` before the exit syscall
- Verify with `echo $?`

### **Exercise 4: No Newline**
Remove the newline (the `10`) and see what happens to your prompt

### **Exercise 5: Color Output**
Print colored text using ANSI codes:
```nasm
msg db 27, "[31mRed Text!", 27, "[0m", 10  ; 27 = ESC character
```

---

## **📋 Quick Reference: Linux 64-bit Syscalls**

| Syscall | RAX | RDI | RSI | RDX |
|---------|-----|-----|-----|-----|
| sys_read | 0 | fd | buffer | count |
| sys_write | 1 | fd | buffer | count |
| sys_exit | 60 | exit_code | - | - |

**File Descriptors:**
- 0 = stdin (keyboard input)
- 1 = stdout (console output)
- 2 = stderr (error output)

---

## **🎯 Knowledge Check**

Before moving to Topic 2, make sure you can:
- ✅ Assemble and link a NASM program
- ✅ Explain the three sections: `.data`, `.bss`, `.text`
- ✅ Understand what `syscall` does
- ✅ Calculate string length with `$ - label`
- ✅ Successfully run your Hello World program

---

**🎉 Congratulations!** You've written and executed your first assembly program!

**Next:** [Topic 2: Registers & Data Types](topic-02-registers.md)

---

[← Back to Main](../README.md) | [Next Topic →](topic-02-registers.md)

