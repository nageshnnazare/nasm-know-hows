# Topic 27: Context Switching & Scheduling

## Overview

When the OS switches from running Process A to Process B, it must save every piece of A's execution state and restore B's — all without either process noticing. This is a **context switch**, and it's the foundation of multitasking. This topic explains exactly what state is saved, how the kernel performs the switch, and how the scheduler decides which process runs next.

```c
// From the process's perspective:
// - It was executing instruction N
// - "Instantly" it's executing instruction N+1
// - But between those two instructions, the OS may have:
//   1. Saved all our registers to memory
//   2. Ran a completely different process for 10ms
//   3. Restored our registers from memory
//   4. Resumed us exactly where we left off
// We never know the difference!
```

---

## Part 1: What Is Process Context?

```
Complete process context (everything that defines execution state):

┌─────────────────────────────────────────────────────────────────┐
│ CPU Registers (saved/restored on context switch):               │
│   General Purpose: RAX, RBX, RCX, RDX, RSI, RDI, RBP, RSP       │
│                    R8-R15                                       │
│   Instruction Pointer: RIP                                      │
│   Flags: RFLAGS                                                 │
│   Segment Registers: CS, DS, ES, FS, GS, SS                     │
│   FPU/SSE/AVX: x87 FPU state, XMM0-XMM15, YMM0-YMM15            │
│                MXCSR, FPU control/status words                  │
│   Debug Registers: DR0-DR3, DR6, DR7                            │
│                                                                 │
│ Memory State (switched via CR3):                                │
│   Page Tables (entire virtual address space mapping)            │
│   TLB entries (flushed on CR3 change, unless PCID)              │
│                                                                 │
│ Kernel State:                                                   │
│   Kernel stack (each process has its own)                       │
│   task_struct (process descriptor in kernel memory)             │
│   File descriptor table, signal masks, credentials...           │
└─────────────────────────────────────────────────────────────────┘

What ISN'T switched:
  - Kernel code and data (same in all processes)
  - Hardware state (I/O APIC, PCI devices)
  - CPU caches (L1/L2/L3) — NOT flushed, but effectively cold
  - Branch predictor state — NOT flushed, can cause slowdown
```

---

## Part 2: The Context Switch in Detail

### Voluntary Switch (Process Blocks on I/O)

```
Process A calls read(fd, buf, 4096):

1. A enters kernel via syscall
2. Kernel finds: data not ready (e.g., waiting for disk)
3. Kernel marks A as TASK_INTERRUPTIBLE (sleeping)
4. Kernel calls schedule()

schedule():
┌─────────────────────────────────────────────────────────────────┐
│ 1. Pick next process to run (scheduler algorithm)               │
│    next = pick_next_task()  → selects Process B                 │
│                                                                 │
│ 2. context_switch(A, B):                                        │
│    a. switch_mm(A->mm, B->mm):                                  │
│       - Load B's page tables: mov cr3, B->pgd                   │
│       - TLB flush happens (or PCID avoids it)                   │
│                                                                 │
│    b. switch_to(A, B):                                          │
│       - Save A's kernel registers on A's kernel stack           │
│       - Switch kernel stack pointer to B's kernel stack         │
│       - Restore B's kernel registers from B's kernel stack      │
│       - RET returns to wherever B was in the kernel!            │
│                                                                 │
│ 3. Now executing as Process B in kernel mode                    │
│ 4. B's previous kernel path completes                           │
│ 5. SYSRET back to B's user-mode code                            │
└─────────────────────────────────────────────────────────────────┘
```

### Involuntary Switch (Timer Preemption)

```
Process A is running in user mode (no syscall):

1. Timer interrupt fires (IRQ 0 → IDT vector 32)
2. CPU saves A's user state on A's kernel stack:
   [SS, RSP, RFLAGS, CS, RIP] — pushed by hardware
3. Timer handler runs:
   - Update timekeeping
   - Decrement A's time slice
   - If time slice expired: set TIF_NEED_RESCHED
4. On return from interrupt, kernel checks TIF_NEED_RESCHED:
   - If set: call schedule() instead of returning to user mode
5. schedule() → context_switch(A, B) [same as above]
6. A is suspended mid-instruction (from A's perspective)
```

---

## Part 3: The switch_to Macro (Assembly)

### Simplified Linux switch_to (x86-64)

```nasm
; This is kernel code — the actual assembly that swaps processes
; Simplified from arch/x86/kernel/process_64.c / entry_64.S

; switch_to(prev, next):
; Saves prev's callee-saved registers, switches stack, restores next's

; Input:  RDI = prev task_struct, RSI = next task_struct
; The task_struct contains a 'thread' field with saved SP and other state

; Offsets in task_struct (simplified):
THREAD_SP    equ 0x08       ; Saved kernel RSP
THREAD_FLAGS equ 0x10       ; Thread flags

__switch_to_asm:
    ; Save prev's callee-saved registers on prev's kernel stack
    push rbp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Save prev's kernel stack pointer
    mov [rdi + THREAD_SP], rsp    ; prev->thread.sp = RSP

    ; Load next's kernel stack pointer
    mov rsp, [rsi + THREAD_SP]    ; RSP = next->thread.sp

    ; Restore next's callee-saved registers from next's kernel stack
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp

    ; Return to wherever next was when it was switched out
    ; (the return address is on next's kernel stack)
    ret

; That's it! The RET pops next's saved RIP and continues
; next's kernel execution path, which eventually returns to user mode
```

### What's on Each Process's Kernel Stack

```
Process A's kernel stack (when A is switched OUT):
┌────────────────────────────────┐ High address
│ User SS                        │ ← Pushed by hardware (interrupt/syscall entry)
│ User RSP                       │
│ User RFLAGS                    │
│ User CS                        │
│ User RIP                       │
├────────────────────────────────┤
│ ... kernel syscall path ...    │ ← Whatever kernel functions were executing
├────────────────────────────────┤
│ Return address (to schedule()) │ ← Where switch_to should return
│ RBP (saved by switch_to)       │ ← Callee-saved registers
│ RBX                            │
│ R12                            │
│ R13                            │
│ R14                            │
│ R15                            │
└────────────────────────────────┘ ← RSP saved in A->thread.sp

When A is selected again:
1. Its RSP is restored from A->thread.sp
2. Pop R15-RBP restores its callee-saved registers
3. RET returns to schedule()'s caller
4. Kernel path continues (finishes syscall/interrupt handling)
5. SYSRET/IRET returns to user mode with A's saved user registers
```

---

## Part 4: FPU/SSE/AVX State Switching

### Lazy FPU Context Switching

```
FPU/SSE state is LARGE (512 bytes for FXSAVE, up to 2KB+ for AVX-512)
Saving/restoring it on every context switch would be expensive.

Optimization: Lazy FPU switching
1. On context switch: set CR0.TS bit (Task Switched)
2. DON'T save FPU state yet
3. If the new process uses an FPU instruction:
   → CPU generates #NM exception (Device Not Available)
   → Kernel handler: save old process's FPU, load new process's FPU
   → Clear TS bit, retry instruction

Modern approach: Eager FPU switching (Linux ≥ 4.2)
- Always save/restore FPU state on context switch
- Uses XSAVE/XRSTOR (handles SSE, AVX, AVX-512 in one shot)
- Simpler and actually faster on modern CPUs (no #NM overhead)
```

```nasm
; FPU state save/restore instructions:

; FXSAVE/FXRSTOR: Save/restore x87 FPU + SSE state (512 bytes)
; fxsave [rdi]           ; Save FPU+SSE state to memory
; fxrstor [rsi]          ; Restore FPU+SSE state from memory

; XSAVE/XRSTOR: Save/restore extended state (FPU+SSE+AVX+...)
; The mask in EDX:EAX selects which components to save:
;   Bit 0: x87 FPU
;   Bit 1: SSE (XMM registers)
;   Bit 2: AVX (upper YMM)
;   Bit 5: AVX-512 opmask
;   Bit 6: AVX-512 upper ZMM (ZMM0-15 upper)
;   Bit 7: AVX-512 ZMM16-31

; Save all supported state:
; mov eax, 0xFFFFFFFF
; mov edx, 0xFFFFFFFF
; xsave [rdi]            ; Save to 'rdi' (must be 64-byte aligned)

; Restore:
; xrstor [rsi]           ; Restore from 'rsi'

; On context switch, the kernel does approximately:
; xsave [prev_task + FPU_OFFSET]     ; Save current FPU state
; xrstor [next_task + FPU_OFFSET]    ; Load next task's FPU state
```

---

## Part 5: Thread Context Switching

### Threads vs Processes

```
Process switch:                    Thread switch (same process):
- Save all registers              - Save all registers (SAME)
- Switch page tables (CR3)        - NO page table switch!
- Flush TLB (expensive!)          - NO TLB flush!
- Switch kernel stack             - Switch kernel stack (SAME)
- All caches effectively cold     - Caches stay warm!

Thread switch is MUCH cheaper because:
- Same address space → same page tables → no CR3 write
- No TLB flush → cached translations still valid
- Shared memory → cache lines stay hot
- Cost: ~1-2μs (vs ~3-5μs for full process switch)
```

### Thread Local Storage (TLS)

```nasm
; Each thread has its own TLS area, accessed via FS segment register
; The kernel sets FS base for each thread during context switch

; arch_prctl(ARCH_SET_FS, addr) — set FS base
; arch_prctl(ARCH_GET_FS, &addr) — get FS base

section .bss
    my_tls resb 4096       ; Thread-local storage area

section .text
; Set up TLS for current thread:
setup_tls:
    mov rax, 158           ; sys_arch_prctl
    mov rdi, 0x1002        ; ARCH_SET_FS
    lea rsi, [rel my_tls]
    syscall
    ret

; Access thread-local variable:
; Variable at offset 0 in TLS:
get_thread_var:
    mov rax, [fs:0]        ; Read from FS-relative address
    ret

set_thread_var:
    mov [fs:0], rdi        ; Write to FS-relative address
    ret

; The kernel's context switch includes:
; wrmsrl(MSR_FS_BASE, next->thread.fsbase)
; This changes what FS:0 points to for the new thread
```

---

## Part 6: Scheduler Algorithms

### CFS (Completely Fair Scheduler)

```
Linux's default scheduler (CFS) uses a red-black tree of processes
sorted by "virtual runtime" (vruntime).

Key concept: vruntime
- Each process accumulates vruntime as it runs
- Process with LOWEST vruntime is selected next
- Higher-priority processes accumulate vruntime SLOWER
- Result: all processes get "fair" share of CPU time

Red-Black Tree (sorted by vruntime):
           ┌───────────┐
           │ vruntime=5│ (next to run = leftmost)
           └─────┬─────┘
          ┌──────┴──────┐
     ┌────┴────┐   ┌────┴────┐
     │ vr=3    │   │ vr=8    │
     └────┬────┘   └────┬────┘
    ┌─────┴───┐    ┌────┴────┐
    │ vr=1    │    │ vr=7    │ ← leftmost = pick this one!
    └─────────┘    └─────────┘

Time slice calculation:
  slice = (scheduling_period / nr_running) * (nice_weight / total_weight)
  
  Default scheduling_period: 6ms (if ≤8 runnable tasks)
  For nice 0 (default): weight = 1024
  For nice -20 (highest): weight = 88761
  For nice 19 (lowest): weight = 15
```

### Schedule Decision Points

```nasm
; The scheduler is invoked at these points:

; 1. Voluntary: process blocks on I/O/lock
;    read() → no data → mark SLEEPING → schedule()

; 2. Timer tick: TIF_NEED_RESCHED set
;    Timer IRQ → check timeslice → set flag → on return: schedule()

; 3. Wake up: higher-priority task becomes runnable
;    I/O completion → wake up blocked task → if higher priority: preempt

; 4. Yield: process voluntarily gives up CPU
;    sched_yield syscall:
yield_cpu:
    mov rax, 24            ; sys_sched_yield
    syscall
    ; We might be switched out and back, or just continue
    ret

; 5. Process exit: must schedule another process
;    exit() → do_exit() → schedule() (never returns)
```

---

## Part 7: Measuring Context Switch Cost

```nasm
; Benchmark context switch overhead using pipe ping-pong:
; Parent and child alternate sending one byte through a pipe
; Each send+receive requires 2 context switches

section .bss
    pipe_r2w resd 2        ; Pipe: parent reads, child writes
    pipe_w2r resd 2        ; Pipe: parent writes, child reads
    byte_buf resb 1
    time_start resq 1
    time_end resq 1

section .data
    iterations equ 100000

section .text
    global _start

_start:
    ; Create two pipes
    mov rax, 22             ; sys_pipe
    lea rdi, [rel pipe_r2w]
    syscall
    mov rax, 22
    lea rdi, [rel pipe_w2r]
    syscall

    ; Fork
    mov rax, 57
    syscall
    test rax, rax
    jz .child

.parent:
    ; Close unused ends
    mov rax, 3
    mov edi, [rel pipe_r2w + 4]  ; Close write end of r2w
    syscall
    mov rax, 3
    mov edi, [rel pipe_w2r]      ; Close read end of w2r
    syscall

    ; Get start time
    ; Use clock_gettime for high precision
    sub rsp, 16
    mov rax, 228            ; sys_clock_gettime
    mov rdi, 1              ; CLOCK_MONOTONIC
    mov rsi, rsp            ; timespec buffer
    syscall
    mov rax, [rsp]          ; seconds
    imul rax, 1000000000
    add rax, [rsp + 8]     ; + nanoseconds
    mov [time_start], rax

    ; Ping-pong loop
    mov ecx, iterations
.parent_loop:
    push rcx

    ; Write one byte (triggers child to wake)
    mov rax, 1              ; sys_write
    mov edi, [rel pipe_w2r + 4]  ; Write end
    lea rsi, [rel byte_buf]
    mov rdx, 1
    syscall

    ; Read one byte (blocks until child writes)
    mov rax, 0              ; sys_read
    mov edi, [rel pipe_r2w]      ; Read end
    lea rsi, [rel byte_buf]
    mov rdx, 1
    syscall

    pop rcx
    dec ecx
    jnz .parent_loop

    ; Get end time
    mov rax, 228
    mov rdi, 1
    mov rsi, rsp
    syscall
    mov rax, [rsp]
    imul rax, 1000000000
    add rax, [rsp + 8]
    mov [time_end], rax
    add rsp, 16

    ; Calculate: (end - start) / (iterations * 2) = ns per context switch
    mov rax, [time_end]
    sub rax, [time_start]
    ; RAX = total nanoseconds
    ; Divide by (iterations * 2) for per-switch time
    xor rdx, rdx
    mov rcx, iterations * 2
    div rcx
    ; RAX = nanoseconds per context switch (typically 1000-5000)

    ; Wait for child and exit
    mov rax, 61
    mov rdi, -1
    xor rsi, rsi
    xor rdx, rdx
    xor r10, r10
    syscall

    mov rdi, rax            ; Exit with ns/switch as code (truncated)
    mov rax, 60
    syscall

.child:
    ; Close unused ends
    mov rax, 3
    mov edi, [rel pipe_r2w]      ; Close read end of r2w
    syscall
    mov rax, 3
    mov edi, [rel pipe_w2r + 4]  ; Close write end of w2r
    syscall

    mov ecx, iterations
.child_loop:
    push rcx

    ; Read one byte (blocks until parent writes)
    mov rax, 0
    mov edi, [rel pipe_w2r]      ; Read end
    lea rsi, [rel byte_buf]
    mov rdx, 1
    syscall

    ; Write one byte back
    mov rax, 1
    mov edi, [rel pipe_r2w + 4]  ; Write end
    lea rsi, [rel byte_buf]
    mov rdx, 1
    syscall

    pop rcx
    dec ecx
    jnz .child_loop

    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Part 8: CPU Affinity and NUMA

```nasm
; CPU affinity: pin a process to specific CPU cores
; Avoids migration overhead (cache cold start on new core)

; sched_setaffinity(pid, cpusetsize, mask):
; The mask is a bitmask where bit N = allowed on CPU N

section .bss
    cpu_mask resb 128      ; CPU affinity mask (supports up to 1024 CPUs)

section .text
; Pin current process to CPU 0 only:
pin_to_cpu0:
    ; Set bit 0 in mask (only CPU 0 allowed)
    lea rdi, [rel cpu_mask]
    mov qword [rdi], 1     ; Bit 0 = CPU 0

    mov rax, 203           ; sys_sched_setaffinity
    xor rdi, rdi           ; pid = 0 (self)
    mov rsi, 128           ; cpusetsize
    lea rdx, [rel cpu_mask]
    syscall
    ret

; Pin to CPUs 0 and 2:
pin_to_cpu02:
    lea rdi, [rel cpu_mask]
    mov qword [rdi], 5     ; Binary: 101 = CPUs 0 and 2

    mov rax, 203
    xor rdi, rdi
    mov rsi, 128
    lea rdx, [rel cpu_mask]
    syscall
    ret

; Get current CPU number (without syscall, using vDSO):
; Or via cpuid instruction:
get_current_cpu:
    ; rdtscp also returns CPU ID in ECX on modern CPUs
    rdtscp                 ; RAX:RDX = timestamp, ECX = CPU_ID
    mov eax, ecx          ; Return CPU number
    ret

; NUMA awareness:
; On NUMA systems, memory access time depends on which CPU accesses it
; Memory local to CPU 0 is faster for CPU 0 than for CPU 1
;
; sys_mbind, sys_set_mempolicy — control memory placement
; sys_migrate_pages — move pages between NUMA nodes
```

---

## Part 9: Process States

```
Linux Process States:

┌─────────────┐     fork()      ┌─────────────┐
│             │────────────────→│  TASK_NEW    │
│   (parent)  │                 │  (created)   │
└─────────────┘                 └──────┬───────┘
                                       │ wake_up_new_task()
                                       ▼
                            ┌────────────────────┐
            schedule()      │                    │     schedule()
         ┌─────────────────→│ TASK_RUNNING       │←─────────────────┐
         │                  │ (on run queue)     │                  │
         │                  └──┬──────────────┬──┘                  │
         │                     │              │                     │
         │         selected by │              │ preempted/yield     │
         │         scheduler   │              │                     │
         │                     ▼              │                     │
         │              ┌──────────────┐      │                     │
         │              │  RUNNING     │──────┘                     │
         │              │  (on CPU)    │                            │
         │              └──┬───────┬───┘                            │
         │                 │       │                                │
         │    blocks on    │       │  exit()                        │
         │    I/O/lock     │       │                                │
         │                 ▼       ▼                                │
         │  ┌──────────────────┐  ┌────────────────┐                │
         │  │ TASK_            │  │ TASK_DEAD      │                │
         │  │ INTERRUPTIBLE    │  │ (zombie until  │                │
         │  │ (sleeping,       │  │  parent waits) │                │
         │  │  wake on signal) │  └────────────────┘                │
         │  └───────┬──────────┘                                    │
         │          │  event/signal                                 │
         └──────────┘                                               │
                                                                    │
              ┌──────────────────────────┐                          │
              │ TASK_UNINTERRUPTIBLE     │  event completes         │
              │ (deep sleep, no signals) │──────────────────────────┘
              │ e.g., disk I/O wait      │
              └──────────────────────────┘
```

```nasm
; Observing process states from assembly:
; Read /proc/self/status for our own state
; Read /proc/[pid]/stat for another process's state

; State characters in /proc/[pid]/stat:
;   R = Running
;   S = Sleeping (interruptible)
;   D = Disk sleep (uninterruptible)
;   Z = Zombie
;   T = Stopped (by signal or debugger)
;   t = Tracing stop
;   X = Dead

section .data
    stat_path db "/proc/self/stat", 0

section .bss
    stat_buf resb 512

section .text
read_own_state:
    mov rax, 2
    lea rdi, [rel stat_path]
    xor rsi, rsi
    xor rdx, rdx
    syscall
    mov r12, rax

    mov rax, 0
    mov rdi, r12
    lea rsi, [rel stat_buf]
    mov rdx, 512
    syscall

    mov rax, 3
    mov rdi, r12
    syscall

    ; Parse: find state character (3rd field)
    ; Format: pid (comm) state ...
    ; Find the ')' then skip space
    lea rdi, [rel stat_buf]
.find_paren:
    cmp byte [rdi], ')'
    je .found
    inc rdi
    jmp .find_paren
.found:
    add rdi, 2             ; Skip ') '
    movzx eax, byte [rdi]  ; State character (R, S, D, etc.)
    ret
```

---

## Part 10: Coroutines — User-Space Context Switching

```nasm
; You can implement your OWN context switching in user space!
; This is how coroutines, green threads, and async runtimes work
; (Go goroutines, Python asyncio, Rust async)

; Coroutine context (what we need to save):
struc coroutine
    .rsp resq 1            ; Saved stack pointer
    .stack resq 1          ; Stack base (for cleanup)
    .stack_size resq 1     ; Stack size
    .finished resb 1       ; Is this coroutine done?
endstruc

section .bss
    ; Two coroutines
    coro_a resb coroutine_size
    coro_b resb coroutine_size
    current_coro resq 1    ; Pointer to current coroutine

    ; Stacks for coroutines (8KB each)
    align 16
    stack_a resb 8192
    stack_b resb 8192

section .data
    msg_a db "Coroutine A running", 10
    msg_a_len equ $ - msg_a
    msg_b db "Coroutine B running", 10
    msg_b_len equ $ - msg_b
    msg_done db "Both coroutines finished!", 10
    msg_done_len equ $ - msg_done

section .text
    global _start

; Switch from current coroutine to target
; Input: RDI = target coroutine context pointer
; This is our user-space "context switch"!
coro_switch:
    ; Save current state
    mov rax, [current_coro]

    ; Save callee-saved registers on current stack
    push rbp
    push rbx
    push r12
    push r13
    push r14
    push r15

    ; Save current RSP
    mov [rax + coroutine.rsp], rsp

    ; Switch to target
    mov [current_coro], rdi
    mov rsp, [rdi + coroutine.rsp]

    ; Restore target's registers
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp

    ret                    ; "Returns" into target's execution!

; Coroutine A's function
coro_a_func:
    ; Print 3 times, yielding to B each time
    mov ecx, 3
.loop:
    push rcx
    mov rax, 1
    mov rdi, 1
    lea rsi, [rel msg_a]
    mov rdx, msg_a_len
    syscall

    ; Yield to coroutine B
    lea rdi, [rel coro_b]
    call coro_switch

    pop rcx
    dec ecx
    jnz .loop

    ; Mark finished and switch back
    mov rax, [current_coro]
    mov byte [rax + coroutine.finished], 1
    lea rdi, [rel coro_b]  ; Switch to B (which will notice A is done)
    call coro_switch
    ; Never returns

; Coroutine B's function
coro_b_func:
    mov ecx, 3
.loop:
    push rcx
    mov rax, 1
    mov rdi, 1
    lea rsi, [rel msg_b]
    mov rdx, msg_b_len
    syscall

    ; Yield to coroutine A
    lea rdi, [rel coro_a]
    call coro_switch

    pop rcx
    dec ecx
    jnz .loop

    ; Mark finished and return to main
    mov rax, [current_coro]
    mov byte [rax + coroutine.finished], 1
    lea rdi, [rel coro_a]  ; Switch back (main is using coro_a's context)
    call coro_switch

_start:
    ; Initialize coroutine A
    lea rax, [rel stack_a + 8192 - 8]  ; Top of stack A
    mov qword [rax], coro_a_func       ; "Return address" = entry point
    sub rax, 48                         ; Space for 6 saved registers
    ; Initialize saved registers to 0
    mov qword [rax], 0     ; R15
    mov qword [rax+8], 0   ; R14
    mov qword [rax+16], 0  ; R13
    mov qword [rax+24], 0  ; R12
    mov qword [rax+32], 0  ; RBX
    mov qword [rax+40], 0  ; RBP
    mov [coro_a + coroutine.rsp], rax
    mov byte [coro_a + coroutine.finished], 0

    ; Initialize coroutine B
    lea rax, [rel stack_b + 8192 - 8]
    mov qword [rax], coro_b_func
    sub rax, 48
    mov qword [rax], 0
    mov qword [rax+8], 0
    mov qword [rax+16], 0
    mov qword [rax+24], 0
    mov qword [rax+32], 0
    mov qword [rax+40], 0
    mov [coro_b + coroutine.rsp], rax
    mov byte [coro_b + coroutine.finished], 0

    ; Use main's stack as a pseudo-coroutine for returning
    ; Start by running coroutine A
    ; (We need a "main" context to switch back to)
    ; Store our current context in coro_a temporarily for the initial switch

    ; Actually, let's set current to a dummy and switch to A
    ; Simpler: just call coro_a_func after setting up switch infrastructure

    ; Set current coroutine (main uses coro_a's slot initially for bookkeeping)
    lea rax, [rel coro_a]
    mov [current_coro], rax

    ; Start coroutine A (first switch — enters coro_a_func)
    lea rdi, [rel coro_a]
    call coro_switch

    ; When all coroutines finish, we end up back here
    mov rax, 1
    mov rdi, 1
    lea rsi, [rel msg_done]
    mov rdx, msg_done_len
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Exercises

1. **Context switch timer**: Use the pipe ping-pong technique to measure context switch time on your system. Compare with `perf sched latency`.

2. **CPU affinity**: Pin a process to CPU 0, measure loop performance. Then let it float across CPUs and measure again. Observe the difference.

3. **User-space threads**: Extend the coroutine example to support N coroutines (use an array and round-robin scheduling).

4. **Priority experiment**: Fork two children — one with `nice -20` (highest priority) and one with `nice 19` (lowest). Have both increment counters in a tight loop for 1 second. Compare final counts.

5. **State observer**: Write a program that forks, has the child loop through different states (running, sleeping, stopped), while the parent reads `/proc/child_pid/stat` and reports state transitions.

---

## Key Takeaways

| Concept | What Happens |
|---------|-------------|
| Context switch | Save registers + switch stack + switch page tables |
| Voluntary switch | Process blocks (I/O, lock) → calls schedule() |
| Involuntary | Timer interrupt → set NEED_RESCHED → schedule() on return |
| switch_to() | Push callee-saved regs, swap RSP, pop next's regs, RET |
| FPU state | XSAVE/XRSTOR handles all FP/SIMD registers (~2KB) |
| Thread switch | Same as process but NO CR3 change (much faster) |
| CFS scheduler | Red-black tree sorted by vruntime; pick lowest |
| Coroutines | User-space switch: save/restore RSP + callee-saved regs |
| Cost | Process switch: ~3-5μs, Thread switch: ~1-2μs |

---

## Next Topic

[Topic 28: Synchronization Primitives →](topic-28-synchronization.md) — Atomic operations, spinlocks, mutexes, and the futex syscall at the assembly level.
