# Q&A: Signals, Traps, and Exception Handling

## The Question

> How do signals actually get delivered to my assembly program? What's the difference between a signal and an exception? How does SIGSEGV work? Can I catch a segfault and keep running? What about SIGINT (Ctrl+C)?

---

## Quick Answer

Signals are the Unix mechanism for asynchronous notifications. Some come from hardware exceptions (SIGSEGV from page faults, SIGFPE from divide-by-zero), some from other processes (`kill`), and some from the kernel (SIGCHLD when a child exits). The kernel delivers signals by modifying your process's stack and registers when returning from kernel mode to user mode, effectively "injecting" a call to your signal handler.

---

## Signal vs Exception vs Interrupt

```
Exception (CPU generates):
  ├─ #PF (Page Fault)    → Kernel may handle internally (demand paging, COW)
  │                       → OR convert to signal: SIGSEGV
  ├─ #DE (Divide Error)  → Kernel converts to: SIGFPE
  ├─ #UD (Invalid Opcode)→ Kernel converts to: SIGILL
  ├─ #BP (Breakpoint)    → Kernel converts to: SIGTRAP
  └─ #GP (General Prot.) → Kernel converts to: SIGSEGV

Interrupt (hardware generates):
  ├─ Timer (IRQ 0)       → Kernel handles internally (scheduling)
  ├─ Keyboard (IRQ 1)    → Kernel feeds to TTY, may generate: SIGINT, SIGTSTP
  └─ Disk (IRQ 14)       → Kernel handles internally (I/O completion)

Signal (software mechanism):
  ├─ From exceptions     → SIGSEGV, SIGFPE, SIGILL, SIGBUS, SIGTRAP
  ├─ From kill()         → Any signal (SIGTERM, SIGUSR1, etc.)
  ├─ From kernel         → SIGCHLD, SIGPIPE, SIGALRM
  └─ From terminal       → SIGINT (Ctrl+C), SIGTSTP (Ctrl+Z), SIGQUIT (Ctrl+\)
```

---

## How Signal Delivery Works

### The Delivery Mechanism

```
Your process is running in user mode:
  mov rax, [some_address]    ← executing normally

A signal arrives (e.g., another process called kill(your_pid, SIGUSR1)):

1. Signal is PENDING (marked in your task_struct)
   - Signals aren't delivered while in user mode!
   - They wait for the next transition through kernel

2. Next time you enter kernel (syscall, interrupt, exception):
   - Timer interrupt fires (or you call read(), etc.)
   - Kernel handles the event
   
3. On RETURN to user mode, kernel checks pending signals:
   - do_signal() → "hey, SIGUSR1 is pending!"
   
4. Kernel modifies your user-mode stack and registers:

   Before:                           After kernel manipulation:
   Stack:                            Stack:
   ┌────────────────┐                ┌────────────────────────────┐
   │ (your data)    │                │ (your data)                │
   │                │                ├────────────────────────────┤
   │                │                │ ucontext_t:                │
   │                │                │  saved RIP (where you were)│
   │                │                │   saved registers          │
   │                │                │   saved signal mask        │
   │                │                │ siginfo_t:                 │
   │                │                │   signal number, sender... │
   │                │                ├────────────────────────────┤
   │                │                │ rt_sigreturn trampoline    │
   └────────────────┘                └────────────────────────────┘
   
   Registers:                        Registers:
   RIP = your_code_address           RIP = signal_handler  ← CHANGED!
   RSP = your_stack                  RSP = (above the saved frame)
   RDI = (whatever)                  RDI = signal_number

5. SYSRET to user mode → you "magically" start executing signal handler!

6. Signal handler returns (ret):
   → Executes rt_sigreturn trampoline on stack
   → sys_rt_sigreturn syscall
   → Kernel restores original registers from ucontext on stack
   → Returns to your ORIGINAL code as if nothing happened
```

### In Assembly Terms

```nasm
; What the kernel effectively does to your process:

; Save current state onto your stack:
; sub rsp, sizeof(ucontext_t)
; mov [rsp + UC_RIP], original_rip
; mov [rsp + UC_RSP], original_rsp
; mov [rsp + UC_RAX], original_rax
; ... (all registers)
;
; Set up signal handler call:
; mov rdi, signal_number        ; First argument
; mov rsi, address_of_siginfo   ; Second argument (if SA_SIGINFO)
; mov rdx, address_of_ucontext  ; Third argument (if SA_SIGINFO)
; mov rip, handler_address      ; "Return" to handler instead of original code
;
; Place return trampoline:
; [stack]: mov rax, 15  ; sys_rt_sigreturn
;          syscall
```

---

## Catching SIGSEGV (Segmentation Fault)

### Why You Might Want To

```
Use cases for catching SIGSEGV:
  1. Implement your own virtual memory system (JIT, GC, memory-mapped DB)
  2. Graceful error reporting before crash
  3. Implement stack growth (like the kernel does)
  4. Guard page detection (array bounds checking without branch overhead!)
  5. NaN-boxing and pointer tagging in language runtimes
```

### The Tricky Part: Resuming After a Fault

```nasm
; If your handler just returns, the CPU will re-execute the faulting instruction
; → Infinite loop of: fault → handle → fault → handle → ...
;
; Solutions:
;   1. Modify the saved RIP in ucontext to skip past faulting instruction
;   2. Use siglongjmp to jump to a different code path
;   3. Fix the memory (mmap the page) so the instruction succeeds on retry

; Option 1: Skip the instruction (advance RIP)
my_segv_handler:
    ; RDX = ucontext_t pointer (third argument with SA_SIGINFO)
    ; The RIP is at a known offset in the mcontext within ucontext
    ; On Linux x86-64: offset to RIP in ucontext is 0xA8
    
    add qword [rdx + 0xA8], 7    ; Skip 7-byte instruction (approximate!)
    ret                           ; "Return" → rt_sigreturn → resume at new RIP

; Option 3: Fix the fault (map the page)
my_segv_handler_fix:
    ; RSI = siginfo_t pointer
    ; siginfo_t.si_addr (offset 16) = the faulting address
    mov rdi, [rsi + 16]          ; Faulting address
    and rdi, ~0xFFF              ; Round down to page boundary
    
    ; Map the page
    mov rax, 9                   ; sys_mmap
    ; RDI already = page-aligned address
    mov rsi, 4096               ; 1 page
    mov rdx, 3                  ; PROT_READ | PROT_WRITE
    mov r10, 50                 ; MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED (0x32)
    mov r8, -1
    xor r9, r9
    syscall
    
    ret                         ; Return → instruction retried → page now exists!
```

---

## Signal Lifecycle

```
1. Signal GENERATED:
   - kill(pid, sig)
   - Kernel generates on exception
   - raise(sig) = kill(getpid(), sig)

2. Signal PENDING:
   - Stored in task_struct bitmask
   - One bit per signal type (1-64)
   - Standard signals: can't queue (multiple SIGINTs = one pending)
   - Real-time signals (32-64): can queue

3. Signal BLOCKED? (check process signal mask)
   - If blocked: stays pending until unblocked
   - Use sigprocmask to block/unblock

4. Signal DELIVERED (on return to user mode):
   - If handler installed: call handler (stack modification)
   - If SIG_IGN: discard
   - If SIG_DFL: default action (terminate, core dump, stop, ignore)

5. After handler returns:
   - rt_sigreturn restores original state
   - Process continues where it was interrupted
```

---

## Common Signals Quick Reference

```
Signal    Number  Default    Generated By
────────────────────────────────────────────────────
SIGKILL     9    terminate  Cannot be caught or ignored!
SIGSTOP    19    stop       Cannot be caught or ignored!
SIGINT      2    terminate  Ctrl+C (terminal)
SIGTERM    15    terminate  kill command (polite request)
SIGSEGV    11    core dump  Invalid memory access
SIGFPE      8    core dump  Arithmetic error (div by 0)
SIGILL      4    core dump  Illegal instruction
SIGBUS      7    core dump  Bus error (alignment, bad mmap)
SIGTRAP     5    core dump  Breakpoint (INT 3, ptrace)
SIGCHLD    17    ignore     Child process state change
SIGPIPE    13    terminate  Write to broken pipe/socket
SIGALRM    14    terminate  alarm() timer expired
SIGUSR1    10    terminate  User-defined signal 1
SIGUSR2    12    terminate  User-defined signal 2
SIGTSTP    20    stop       Ctrl+Z (terminal)
SIGCONT    18    continue   Resume stopped process
```

---

## Signal Handling Setup in Assembly

```nasm
; Installing a signal handler requires rt_sigaction:
; struct sigaction {
;     void (*sa_handler)(int);          offset 0
;     unsigned long sa_flags;            offset 8
;     void (*sa_restorer)(void);         offset 16
;     sigset_t sa_mask[1];               offset 24 (128 bytes on x86-64)
; };

; sa_flags important values:
;   SA_SIGINFO (4):     Handler gets siginfo_t and ucontext_t
;   SA_RESTART (0x10000000): Restart interrupted syscalls
;   SA_RESTORER (0x04000000): sa_restorer field is set (required on x86-64!)
;   SA_NODEFER (0x40000000): Don't block signal during handler

section .data
    align 8
    sigaction_struct:
        dq handler_func              ; sa_handler
        dq 0x04000004               ; sa_flags = SA_RESTORER | SA_SIGINFO
        dq sig_restore              ; sa_restorer
        times 16 db 0              ; sa_mask (128 bytes, all zeros = don't block)

section .text
; The restorer — kernel requires this for proper signal return:
sig_restore:
    mov rax, 15                    ; sys_rt_sigreturn
    syscall
    ; Never returns — kernel restores original context

; Install handler:
install_handler:
    ; RDI = signal number to handle
    mov rax, 13                    ; sys_rt_sigaction
    ; RDI = signum (already set)
    lea rsi, [rel sigaction_struct] ; act
    xor rdx, rdx                  ; oldact = NULL
    mov r10, 8                    ; sigsetsize (sizeof(sigset_t))
    syscall
    ret
```

---

## The Async-Signal-Safety Problem

```
Inside a signal handler, you're limited to "async-signal-safe" functions!

Why? A signal can interrupt your code ANYWHERE:
  - In the middle of malloc() → calling malloc in handler = deadlock/corruption!
  - In the middle of printf() → calling printf in handler = buffer corruption!
  - While holding a lock → acquiring same lock in handler = deadlock!

Safe in signal handlers:
  ✓ write() (syscall — no user-space state)
  ✓ _exit() 
  ✓ read()
  ✓ Simple variable assignment (to volatile sig_atomic_t)
  ✓ All syscalls (they're atomic from user-space perspective)

UNSAFE in signal handlers:
  ✗ malloc() / free()
  ✗ printf() / puts()
  ✗ Any function that uses locks internally
  ✗ exit() (calls atexit handlers which may use unsafe functions)
```

---

## TL;DR

| Question | Answer |
|----------|--------|
| How are signals delivered? | Kernel modifies your stack/RIP before returning to user mode |
| When can signals arrive? | Only when transitioning from kernel → user mode |
| What's SIGSEGV? | Page fault on invalid address → kernel sends SIGSEGV |
| Can I catch SIGSEGV? | Yes! Install handler with rt_sigaction |
| Can I resume after SIGSEGV? | Yes: modify RIP in ucontext, or mmap the page |
| What can't be caught? | SIGKILL (9) and SIGSTOP (19) — by kernel design |
| Is my handler safe? | Only if you use async-signal-safe functions (mostly syscalls) |
| What's the restorer? | Trampoline code that calls sys_rt_sigreturn to restore context |
| Signals vs interrupts? | Signals = software (process-level); Interrupts = hardware (CPU-level) |
