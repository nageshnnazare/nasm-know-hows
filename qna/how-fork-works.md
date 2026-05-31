# Q&A: How Does fork() Actually Work?

## The Question

> When I call `fork()`, the documentation says it "creates a copy of the process." But copying gigabytes of memory would be insanely slow. How does fork actually work? What's Copy-on-Write? And why does `fork()` return different values in parent and child?

---

## Quick Answer

`fork()` does NOT copy memory. It duplicates the process descriptor (task_struct) and page tables, but marks all writable pages as read-only in BOTH processes. Only when either process tries to WRITE to a page does the kernel actually copy that specific page. This is **Copy-on-Write (COW)** — making fork nearly instant regardless of process size.

---

## The Full Story

### Step 1: What Gets Duplicated (Immediately)

```
Created instantly on fork():
  ✓ task_struct (process descriptor) — new PID, new scheduling state
  ✓ Page table entries (PTEs) — pointing to SAME physical pages
  ✓ File descriptor table — new table, same underlying file objects  
  ✓ Signal handlers — copied
  ✓ Memory map (VMA list) — new VMAs pointing to same pages
  ✓ Credentials (UID, GID)
  ✓ Kernel stack (small, for kernel-mode execution)
  
NOT copied:
  ✗ Physical memory pages (shared, COW)
  ✗ Page cache data
  ✗ Open file positions (shared via file object reference)
  ✗ PID (child gets new one)
```

### Step 2: Page Table Manipulation

```
Before fork():
  Parent PTE for page at 0x7fff0000:
    Physical page: 0x1A3000
    Permissions: RW (read-write)

After fork():
  Parent PTE for 0x7fff0000:
    Physical page: 0x1A3000 (SAME!)
    Permissions: R- (read-ONLY now!)  ← Changed!
    
  Child PTE for 0x7fff0000:
    Physical page: 0x1A3000 (SAME!)
    Permissions: R- (read-ONLY now!)
    
  Physical page 0x1A3000:
    Reference count: 2 (both processes point to it)

Time taken: proportional to number of PTEs, NOT amount of data
  - 1GB process with 256K pages: copy ~256K × 8 bytes = 2MB of PTEs
  - NOT copying 1GB of actual data!
```

### Step 3: Copy-on-Write in Action

```
Parent writes to 0x7fff0000:
  1. CPU tries to write → PTE says read-only → PAGE FAULT
  2. Kernel page fault handler checks:
     - Is this a COW page? (VMA says writable, but PTE says read-only = COW)
     - YES!
  3. Kernel action:
     a. Allocate new physical page (0x2B4000)
     b. Copy content from old page (0x1A3000) to new page (0x2B4000)
     c. Update PARENT's PTE: physical = 0x2B4000, permissions = RW
     d. Decrement reference count on old page (2 → 1)
     e. If ref count reaches 1: restore write permission in other PTE
  4. Return to user code — write instruction RETRIED and succeeds

Result:
  Parent PTE: 0x2B4000 (RW) — private copy
  Child PTE:  0x1A3000 (RW) — now sole owner, write restored
```

### Step 4: The Return Value Magic

```nasm
; How fork returns DIFFERENT values to parent and child:
;
; When fork() is called:
;   1. Kernel creates child task_struct
;   2. Kernel sets up child's kernel stack with saved registers
;   3. In child's saved registers: RAX = 0
;   4. In parent's execution path: RAX = child's PID
;   5. Both "return" from the syscall, but with different RAX values

; From the kernel's perspective (pseudocode):
; pid = create_child_task()
; child->saved_regs.rax = 0         ; Child will see 0
; parent_return_value = child->pid  ; Parent will see child PID
; schedule(child)                    ; Put child on run queue
; return parent_return_value        ; Return to parent
```

### Step 5: Fork with exec (The Common Pattern)

```
fork() + execve() — why COW makes this efficient:

Without COW:
  fork(): Copy entire address space (slow!)
  execve(): Immediately throw it all away and load new program (waste!)

With COW:
  fork(): Share all pages read-only (fast! ~microseconds)
  execve(): Release shared page references (just decrement counters)
            Load new program (only map what's needed)
  
  Result: The "copy" in fork was never actually made!
  Child never wrote to inherited pages → no actual copying happened!
```

---

## Common Fork Patterns

### Safe fork + exec

```nasm
; Parent:
;   fork() → gets child PID
;   waitpid(child) → blocks until child exits
;
; Child:
;   fork() → gets 0
;   close unnecessary FDs
;   execve(new_program)
;   _exit(127) if exec fails  ← NOT exit()! (would flush parent's stdio)
```

### vfork (Ultra-Fast Fork)

```nasm
; vfork() — even faster than COW fork:
;   - Child SHARES parent's address space entirely (no PTE copy!)
;   - Parent is SUSPENDED until child calls exec or _exit
;   - Child must NOT modify any memory (would corrupt parent!)
;   - Only useful for immediate fork+exec pattern
;
; sys_vfork = 58
;
; Danger: If child doesn't immediately exec/exit, undefined behavior!
; Modern alternative: posix_spawn() or clone(CLONE_VFORK)
```

---

## Why Fork Returns Twice

This confuses everyone at first. Think of it this way:

```
         fork()
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
 Parent        Child
 RAX=1001      RAX=0
 (child PID)   (I'm the child)
    │             │
    │             │
 continues     continues
 same code     same code
```

Both processes execute the exact same code after fork. The ONLY way to tell them apart is checking the return value. That's why the pattern is always:

```nasm
mov rax, 57      ; sys_fork
syscall
test rax, rax
jz .child        ; RAX=0 → child
; RAX>0 → parent (and RAX = child's PID)
```

---

## TL;DR

| Question | Answer |
|----------|--------|
| Does fork copy all memory? | No! Just page table entries (~2MB for 1GB process) |
| When is memory actually copied? | Only when someone writes (Copy-on-Write) |
| Is fork slow for large processes? | No — COW makes it fast (~microseconds) |
| Why different return values? | Kernel sets RAX=0 in child's saved regs, RAX=pid in parent |
| What if child never writes? | No pages ever copied (fork+exec pattern) |
| What's shared after fork? | Physical pages (until written), open file descriptions |
| What's NOT shared? | PID, page tables (separate copies), parent PID |
| vfork vs fork? | vfork shares address space entirely (dangerous, fast) |
