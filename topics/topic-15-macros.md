# 📘 Topic 15: Macros & Directives

Master NASM's powerful preprocessor for code generation, conditional assembly, and creating reusable code templates.

---

## **Overview**

**Macros** and **directives** let you:
- 🔄 Create reusable code templates
- 🎛️ Conditional compilation
- 📦 Organize large projects
- ⚡ Generate repetitive code automatically
- 🛠️ Build domain-specific assembly "languages"

---

## **Part 1: Simple Macros**

### **%define - Simple Text Replacement**

Like `#define` in C.

**C Equivalent:**
```c
#define BUFFER_SIZE 1024
#define MAX(a,b) ((a) > (b) ? (a) : (b))
```

**NASM:**
```nasm
%define BUFFER_SIZE 1024
%define SYSCALL_WRITE 1
%define SYSCALL_EXIT 60

section .bss
    buffer resb BUFFER_SIZE         ; Expands to: resb 1024

section .text
    mov rax, SYSCALL_WRITE          ; Expands to: mov rax, 1
```

---

### **%assign - Numeric Constants**

Can be redefined (unlike `%define`).

```nasm
%assign COUNTER 0
%assign COUNTER COUNTER+1           ; COUNTER = 1
%assign COUNTER COUNTER+1           ; COUNTER = 2
```

---

## **Part 2: Multi-Line Macros**

### **Basic Macro Syntax**

```nasm
%macro macro_name parameter_count
    ; Macro body
    ; %1, %2, %3... refer to parameters
%endmacro
```

---

### **Example 1: Print Macro**

**C Equivalent:**
```c
#define PRINT_STR(msg, len) \
    write(1, msg, len)
```

**NASM:**
```nasm
%macro print_string 2               ; 2 parameters
    mov rax, 1                      ; sys_write
    mov rdi, 1                      ; stdout
    mov rsi, %1                     ; message (1st parameter)
    mov rdx, %2                     ; length (2nd parameter)
    syscall
%endmacro

; Usage:
section .data
    msg db "Hello!", 10
    len equ $ - msg

section .text
    print_string msg, len           ; Expands to mov/syscall sequence
```

---

### **Example 2: Exit Macro**

```nasm
%macro exit 1                       ; 1 parameter: exit code
    mov rax, 60
    mov rdi, %1
    syscall
%endmacro

; Usage:
exit 0                              ; Exit with code 0
exit 42                             ; Exit with code 42
```

---

### **Example 3: Function Prologue/Epilogue**

**C Equivalent:**
```c
// Every function does this:
void func() {
    // Prologue
    // ... body ...
    // Epilogue
}
```

**NASM:**
```nasm
%macro prologue 0
    push rbp
    mov rbp, rsp
%endmacro

%macro epilogue 0
    mov rsp, rbp
    pop rbp
    ret
%endmacro

my_function:
    prologue
    ; Function body here
    epilogue
```

---

### **Example 4: Save/Restore Registers**

```nasm
%macro pushall 0
    push rax
    push rbx
    push rcx
    push rdx
    push rsi
    push rdi
%endmacro

%macro popall 0
    pop rdi
    pop rsi
    pop rdx
    pop rcx
    pop rbx
    pop rax
%endmacro

my_function:
    pushall
    ; Use all registers freely
    popall
    ret
```

---

## **Part 3: Macro Parameters**

### **Parameter Types**

```nasm
%macro demo 3
    mov rax, %1                     ; 1st parameter
    mov rbx, %2                     ; 2nd parameter
    mov rcx, %3                     ; 3rd parameter
%endmacro

demo 10, 20, 30                     ; Expands to 3 mov instructions
```

---

### **Default Parameters**

```nasm
%macro greet 1-2 "World"            ; 1-2 params, default 2nd = "World"
    section .data
        %%msg db %1, " ", %2, 10
        %%len equ $ - %%msg
    section .text
        print_string %%msg, %%len
%endmacro

greet "Hello"                       ; Uses default: "Hello World"
greet "Hi", "There"                 ; Custom: "Hi There"
```

---

### **Variable Number of Parameters**

```nasm
%macro sum 1-*                      ; 1 or more parameters
    xor rax, rax
    %rep %0                         ; %0 = number of parameters
        add rax, %1
        %rotate 1                   ; Shift parameters
    %endrep
%endmacro

sum 10                              ; RAX = 10
sum 10, 20, 30                      ; RAX = 60
```

---

## **Part 4: Local Labels**

Prevent label conflicts when macro is used multiple times.

```nasm
%macro my_abs 1                     ; Absolute value
    test %1, %1
    jns %%positive                  ; %%label creates unique label
    neg %1
%%positive:
%endmacro

my_abs rax                          ; Creates label like ..@1.positive
my_abs rbx                          ; Creates different label ..@2.positive
```

---

## **Part 5: Conditional Assembly**

### **%if Directives**

```nasm
%define DEBUG 1

%if DEBUG
    ; Debug code included
    mov rdi, error_msg
    call print
%endif

%ifdef FEATURE_X
    ; Include if FEATURE_X is defined
    call feature_x_init
%endif

%ifndef FEATURE_Y
    ; Include if FEATURE_Y is NOT defined
    call fallback_init
%endif
```

---

### **Compile-Time Conditions**

```nasm
%if BUFFER_SIZE > 1024
    %warning "Buffer size is very large!"
%endif

%if CPU_BITS == 64
    ; 64-bit specific code
    mov rax, large_value
%else
    ; 32-bit specific code
    mov eax, small_value
%endif
```

---

### **%rep - Repetition**

```nasm
; Generate 10 nops
%rep 10
    nop
%endrep

; Unroll loop
%assign i 0
%rep 5
    mov eax, [array + i*4]
    add ebx, eax
    %assign i i+1
%endrep
```

---

## **Part 6: File Inclusion**

### **%include**

```nasm
; macros.inc
%macro print 2
    mov rax, 1
    mov rdi, 1
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

; main.asm
%include "macros.inc"

section .text
    global _start
_start:
    print msg, len
    exit 0
```

---

### **%pathsearch**

```nasm
%pathsearch syscalls "syscalls.inc"
%include syscalls                   ; Search in include paths
```

---

## **Part 7: Advanced Macro Techniques**

### **Macro Overloading (by parameter count)**

```nasm
%macro print 1                      ; 1 parameter version
    ; Assume null-terminated string
    call strlen
    print_string %1, rax
%endmacro

%macro print 2                      ; 2 parameter version
    print_string %1, %2
%endmacro

print msg                           ; Calls 1-param version
print msg, 10                       ; Calls 2-param version
```

---

### **String Manipulation**

```nasm
%define CONCAT(a,b) a %+ b

CONCAT(my_, function):              ; Expands to: my_function:
    ret

%define STRINGIFY(x) `x`
%define CREATE_MSG(name) db STRINGIFY(name), 0

section .data
    CREATE_MSG(Hello)               ; Expands to: db "Hello", 0
```

---

## **Part 8: Practical Macro Library**

### **System Call Macros**

```nasm
%macro sys_write 2                  ; fd, message, length
    mov rax, 1
    mov rdi, %1
    mov rsi, %2
    syscall
%endmacro

%macro sys_exit 1                   ; exit_code
    mov rax, 60
    mov rdi, %1
    syscall
%endmacro

%macro sys_open 3                   ; filename, flags, mode
    mov rax, 2
    mov rdi, %1
    mov rsi, %2
    mov rdx, %3
    syscall
%endmacro
```

---

### **Debug Macros**

```nasm
%ifdef DEBUG
    %macro dbg_print 2
        pushall
        print_string %1, %2
        popall
    %endmacro
%else
    %macro dbg_print 2
        ; Empty in release build
    %endmacro
%endif
```

---

### **Alignment Macros**

```nasm
%macro align_stack 0
    ; Ensure 16-byte alignment
    mov rbp, rsp
    and rsp, -16
%endmacro

%macro restore_stack 0
    mov rsp, rbp
%endmacro
```

---

## **Part 9: Complete Example**

```nasm
; config.inc
%define VERSION "1.0.0"
%define BUFFER_SIZE 4096
%define DEBUG 1

; macros.inc
%macro print 2
    mov rax, 1
    mov rdi, 1
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

%macro exit 1
    mov rax, 60
    mov rdi, %1
    syscall
%endmacro

%ifdef DEBUG
    %macro debug 1
        print %1, debug_msg_len
    %endmacro
%else
    %macro debug 1
        ; No-op in release
    %endmacro
%endif

; main.asm
%include "config.inc"
%include "macros.inc"

section .data
    version db "Version: " %+ VERSION, 10
    version_len equ $ - version
    
%ifdef DEBUG
    debug_msg db "[DEBUG] Program started", 10
    debug_msg_len equ $ - debug_msg
%endif

section .text
    global _start

_start:
    print version, version_len
    debug debug_msg
    
    ; Main program logic
    
    exit 0
```

---

## **Part 10: Best Practices**

### **DO:**
- ✅ Use macros for repeated patterns
- ✅ Use local labels (`%%label`)
- ✅ Document macro parameters
- ✅ Use meaningful macro names
- ✅ Group related macros in include files

### **DON'T:**
- ❌ Overuse macros (readability!)
- ❌ Create overly complex macros
- ❌ Forget side effects (register usage)
- ❌ Use macros for single-use code
- ❌ Ignore macro expansion size

---

## **✅ Practice Exercises**

### **Exercise 1: Create a MIN/MAX Macro**

<details>
<summary>Solution</summary>

```nasm
%macro min 3                        ; dest, a, b
    mov %1, %2
    cmp %1, %3
    jle %%done
    mov %1, %3
%%done:
%endmacro

%macro max 3
    mov %1, %2
    cmp %1, %3
    jge %%done
    mov %1, %3
%%done:
%endmacro

; Usage:
min rax, rbx, rcx                   ; RAX = min(RBX, RCX)
max rdx, rsi, rdi                   ; RDX = max(RSI, RDI)
```
</details>

---

## **📋 Quick Reference**

```nasm
; Defines
%define NAME value
%assign COUNT 0

; Macros
%macro name param_count
    ; body with %1, %2, %3...
%endmacro

; Conditionals
%if condition
%elif condition
%else
%endif

; Loops
%rep count
%endrep

; Include
%include "file.inc"
```

---

**🎉 Excellent!** You've mastered macros and directives!

**Next:** Topic 16: Linux System Calls

---

[← Previous Topic](topic-14-shifts.md) | [Back to Main](../README.md) | [Next Topic →](topic-16-syscalls.md)
