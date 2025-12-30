# 🚀 NASM Quick Reference Guide

A fast reference for common NASM operations and patterns.

---

## 📋 Build Commands

```bash
# 64-bit Assembly
nasm -f elf64 program.asm -o program.o
ld -o program program.o
./program

# 32-bit Assembly
nasm -f elf32 program.asm -o program.o
ld -m elf_i386 -o program program.o
./program

# With Debug Info
nasm -f elf64 -g -F dwarf program.asm
ld -o program program.o
gdb ./program

# Check exit code
echo $?
```

---

## 📦 Program Template

```nasm
; program.asm - Description here

section .data
    ; Initialized data goes here
    message db "Hello", 10, 0
    number  dd 42

section .bss
    ; Uninitialized data goes here
    buffer resb 64
    counter resd 1

section .text
    global _start

_start:
    ; Your code here
    
    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## 🔧 Common Operations

### **Zero a Register**
```nasm
xor rax, rax        ; Fastest, smallest (preferred)
xor eax, eax        ; Even smaller, zeros full RAX
```

### **Move Data**
```nasm
mov rax, 42         ; Immediate to register
mov rax, rbx        ; Register to register
mov rax, [rbx]      ; Memory to register
mov [rbx], rax      ; Register to memory
```

### **Arithmetic**
```nasm
add rax, 10         ; RAX = RAX + 10
sub rax, 5          ; RAX = RAX - 5
inc rax             ; RAX = RAX + 1
dec rax             ; RAX = RAX - 1
neg rax             ; RAX = -RAX
```

### **Bitwise**
```nasm
and rax, rbx        ; RAX = RAX & RBX
or  rax, rbx        ; RAX = RAX | RBX
xor rax, rbx        ; RAX = RAX ^ RBX
not rax             ; RAX = ~RAX
shl rax, 2          ; RAX = RAX << 2 (multiply by 4)
shr rax, 2          ; RAX = RAX >> 2 (divide by 4)
```

---

## 🔄 Control Flow

### **Unconditional Jump**
```nasm
jmp label           ; Always jump
```

### **Conditional Jumps (Signed)**
```nasm
cmp rax, rbx        ; Compare RAX with RBX
je  label           ; Jump if equal
jne label           ; Jump if not equal
jg  label           ; Jump if greater (RAX > RBX)
jge label           ; Jump if greater or equal
jl  label           ; Jump if less (RAX < RBX)
jle label           ; Jump if less or equal
```

### **Conditional Jumps (Unsigned)**
```nasm
ja  label           ; Jump if above (unsigned >)
jae label           ; Jump if above or equal
jb  label           ; Jump if below (unsigned <)
jbe label           ; Jump if below or equal
```

### **Test and Jump**
```nasm
test rax, rax       ; AND without storing result
jz label            ; Jump if zero
jnz label           ; Jump if not zero
```

### **Loops**
```nasm
mov rcx, 10         ; Loop counter
loop_start:
    ; ... code ...
    loop loop_start ; Decrements RCX, jumps if not zero
```

---

## 📚 Stack Operations

```nasm
push rax            ; Save RAX on stack
pop rbx             ; Restore into RBX

; Function prologue
push rbp
mov rbp, rsp
sub rsp, 16         ; Allocate 16 bytes for locals

; Function epilogue
leave               ; Equivalent to: mov rsp, rbp; pop rbp
ret                 ; Return from function
```

---

## 📞 Linux Syscalls (64-bit)

### **Register Convention**
```
RAX = syscall number (input) / return value (output)
RDI = arg1
RSI = arg2
RDX = arg3
R10 = arg4 (NOT RCX!)
R8  = arg5
R9  = arg6

Note: RCX and R11 are destroyed by syscall
```

### **Common Syscalls**

```nasm
; sys_read (0) - Read from file descriptor
mov rax, 0          ; sys_read
mov rdi, 0          ; stdin
mov rsi, buffer     ; buffer pointer
mov rdx, 64         ; max bytes to read
syscall
; RAX = bytes read (or negative on error)

; sys_write (1) - Write to file descriptor
mov rax, 1          ; sys_write
mov rdi, 1          ; stdout
mov rsi, buffer     ; message pointer
mov rdx, length     ; message length
syscall
; RAX = bytes written (or negative on error)

; sys_open (2) - Open file
mov rax, 2          ; sys_open
mov rdi, filename   ; path to file
mov rsi, 0          ; flags (0=O_RDONLY, 1=O_WRONLY, 2=O_RDWR)
mov rdx, 0644o      ; mode (permissions)
syscall
; RAX = file descriptor (or negative on error)

; sys_close (3) - Close file descriptor
mov rax, 3          ; sys_close
mov rdi, fd         ; file descriptor
syscall
; RAX = 0 on success, negative on error

; sys_exit (60) - Exit program
mov rax, 60         ; sys_exit
xor rdi, rdi        ; exit code (0 = success)
syscall
; Does not return
```

### **Syscall Quick Numbers**
```
┌────┬───────────┬────┬───────────┬────┬──────────┐
│  0 │ read      │  9 │ mmap      │ 57 │ fork     │
│  1 │ write     │ 11 │ munmap    │ 59 │ execve   │
│  2 │ open      │ 12 │ brk       │ 60 │ exit     │
│  3 │ close     │ 35 │ nanosleep │ 61 │ wait4    │
│  4 │ stat      │ 79 │ getcwd    │ 80 │ chdir    │
│  5 │ fstat     │ 83 │ mkdir     │ 87 │ unlink   │
└────┴───────────┴────┴───────────┴────┴──────────┘
```

**File Descriptors:**
- 0 = stdin
- 1 = stdout
- 2 = stderr

**For complete reference see:** [Linux Syscall Reference](syscall-reference.md)

---

## 🗂️ Data Types

```nasm
section .data
    ; Define with initial values
    byte_val    db 0x42             ; 1 byte
    word_val    dw 0x1234           ; 2 bytes
    dword_val   dd 0x12345678       ; 4 bytes
    qword_val   dq 0x123456789ABC   ; 8 bytes
    
    string_val  db "Hello", 0       ; String with null
    array_val   dd 1, 2, 3, 4, 5    ; Array of 5 ints
    
    buffer      times 64 db 0       ; 64 zero bytes

section .bss
    ; Reserve without initial values
    buffer2     resb 256            ; Reserve 256 bytes
    counter     resd 1              ; Reserve 1 dword
    pointer     resq 1              ; Reserve 1 qword
```

---

## 🎯 Register Reference

### **64-bit Registers**
```
RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP
R8, R9, R10, R11, R12, R13, R14, R15
```

### **32-bit (lower 32 bits, zeros upper)**
```
EAX, EBX, ECX, EDX, ESI, EDI, EBP, ESP
R8D, R9D, R10D, R11D, R12D, R13D, R14D, R15D
```

### **16-bit (lower 16 bits)**
```
AX, BX, CX, DX, SI, DI, BP, SP
R8W, R9W, R10W, R11W, R12W, R13W, R14W, R15W
```

### **8-bit (lowest byte)**
```
AL, BL, CL, DL, SIL, DIL, BPL, SPL
R8B, R9B, R10B, R11B, R12B, R13B, R14B, R15B
```

### **8-bit (high byte, legacy)**
```
AH, BH, CH, DH
```

### **Register Roles**
```
RAX - Accumulator, return values
RBX - Base pointer (callee-saved)
RCX - Counter for loops
RDX - Data, I/O operations
RSI - Source index
RDI - Destination index
RBP - Base pointer (stack frame)
RSP - Stack pointer (don't modify directly!)
```

---

## 🔍 Memory Addressing

```nasm
; Direct
mov rax, [0x1000]           ; Read from address 0x1000

; Register indirect
mov rax, [rbx]              ; Read from address in RBX

; Register + displacement
mov rax, [rbx + 8]          ; Read from RBX + 8

; Base + index
mov rax, [rbx + rcx]        ; Read from RBX + RCX

; Base + index*scale + displacement
mov rax, [rbx + rcx*4 + 8]  ; Read from RBX + (RCX*4) + 8

; Label
mov rax, [myvar]            ; Read from address of myvar
```

**Size specifiers:**
```nasm
mov byte [rbx], 42          ; 1 byte
mov word [rbx], 42          ; 2 bytes
mov dword [rbx], 42         ; 4 bytes
mov qword [rbx], 42         ; 8 bytes
```

---

## 🎪 String Operations

```nasm
; Set direction flag
cld                 ; Forward (increment)
std                 ; Backward (decrement)

; String instructions (work with RSI/RDI)
movsb               ; Move byte [RSI] to [RDI], inc both
lodsb               ; Load byte [RSI] to AL, inc RSI
stosb               ; Store AL to [RDI], inc RDI
cmpsb               ; Compare [RSI] with [RDI], inc both
scasb               ; Compare AL with [RDI], inc RDI

; With REP prefix
rep movsb           ; Repeat RCX times
repe cmpsb          ; Repeat while equal
repne scasb         ; Repeat while not equal
```

---

## 🔢 Arithmetic (Advanced)

### **Multiplication**
```nasm
; Unsigned multiply
mov rax, 10
mov rbx, 20
mul rbx             ; RDX:RAX = RAX * RBX

; Signed multiply
imul rbx            ; RDX:RAX = RAX * RBX (signed)
imul rax, rbx       ; RAX = RAX * RBX (truncated)
imul rax, rbx, 10   ; RAX = RBX * 10
```

### **Division**
```nasm
; Unsigned divide
mov rax, 100
xor rdx, rdx        ; Clear RDX (high part)
mov rbx, 10
div rbx             ; RAX = quotient, RDX = remainder

; Signed divide
mov rax, 100
cqo                 ; Sign-extend RAX into RDX
mov rbx, 10
idiv rbx            ; RAX = quotient, RDX = remainder
```

---

## 🏃 Function Calling (System V AMD64)

### **Call Function**
```nasm
; Arguments in: RDI, RSI, RDX, RCX, R8, R9, then stack
mov rdi, arg1
mov rsi, arg2
mov rdx, arg3
call my_function
; Return value in RAX
```

### **Define Function**
```nasm
my_function:
    push rbp
    mov rbp, rsp
    sub rsp, 16         ; Allocate locals
    
    ; Function body
    ; Access args: [rbp+16], [rbp+24], etc.
    ; Access locals: [rbp-4], [rbp-8], etc.
    
    mov rax, result     ; Return value
    
    leave               ; Restore stack
    ret
```

---

## 🐛 Debugging

```bash
# Compile with debug info
nasm -f elf64 -g -F dwarf program.asm
ld -o program program.o

# Run in GDB
gdb ./program

# GDB commands
(gdb) break _start      # Set breakpoint
(gdb) run               # Run program
(gdb) stepi             # Step one instruction
(gdb) info registers    # Show all registers
(gdb) x/10x $rsp        # Examine stack (10 hex values)
(gdb) disassemble       # Show assembly
(gdb) quit              # Exit GDB
```

---

## 🛠️ Useful Tools

```bash
# Disassemble
objdump -d program -M intel

# View sections
objdump -h program

# Size of sections
size program

# Trace system calls
strace ./program

# Check for memory errors
valgrind ./program

# View hex dump
hexdump -C program

# File info
file program
```

---

## 💡 Tips & Tricks

### **Always Zero with XOR**
```nasm
xor eax, eax        ; 2 bytes (preferred)
mov eax, 0          ; 5 bytes (slower, bigger)
```

### **Test for Zero**
```nasm
test rax, rax       ; Sets ZF if RAX is zero
jz is_zero          ; Jump if zero
```

### **Swap Registers**
```nasm
xchg rax, rbx       ; Swap RAX and RBX (one instruction)
```

### **Load Effective Address (LEA)**
```nasm
lea rax, [rbx + rcx*4 + 8]  ; RAX = RBX + RCX*4 + 8 (no memory access)
```

### **Sign Extend**
```nasm
movsx rax, al       ; Sign-extend AL to RAX
movzx rax, al       ; Zero-extend AL to RAX
```

---

## 📖 Quick Bit Flags

```
CF - Carry Flag (unsigned overflow)
ZF - Zero Flag (result is zero)
SF - Sign Flag (result is negative)
OF - Overflow Flag (signed overflow)
PF - Parity Flag (even number of 1 bits)
```

---

## 🎓 Common Patterns

### **Array Iteration**
```nasm
xor rcx, rcx            ; index = 0
loop_start:
    mov al, [array + rcx]
    ; process AL
    inc rcx
    cmp rcx, array_len
    jl loop_start
```

### **String Length**
```nasm
xor rax, rax            ; length = 0
strlen_loop:
    cmp byte [rsi + rax], 0
    je strlen_done
    inc rax
    jmp strlen_loop
strlen_done:
    ; RAX contains length
```

### **If-Else**
```nasm
cmp rax, 10
jl else_branch
    ; if RAX >= 10
    ; ...
    jmp end_if
else_branch:
    ; else
    ; ...
end_if:
```

---

## 📚 Resources

- **NASM Manual**: https://www.nasm.us/docs.php
- **Intel Manuals**: https://software.intel.com/content/www/us/en/develop/articles/intel-sdm.html
- **Linux Syscall Table**: https://filippo.io/linux-syscall-table/
- **x86-64 ABI**: https://refspecs.linuxbase.org/elf/x86_64-abi-0.99.pdf

---

[← Back to Main](README.md)

