# Topic 21: Memory Allocation Internals

## Overview

When you call `malloc()` in C, something magical seems to happen — memory appears. But under the hood, `malloc` is just user-space code that manages a pool of memory obtained from the kernel through syscalls. This topic dissects the entire memory allocation stack, from the high-level C API down to the kernel's page allocator, all explained at the assembly level.

```c
// What you write in C:
void *ptr = malloc(64);
free(ptr);

// What actually happens (simplified):
// 1. malloc checks its internal free list
// 2. If no suitable chunk: calls brk() or mmap() syscall
// 3. Kernel maps physical pages to virtual address space
// 4. malloc carves a chunk from the mapped region
// 5. Returns pointer to usable area (after metadata header)
```

---

## The Memory Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│                    User Space                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │  malloc() / free()  [glibc / musl / custom]       │  │
│  │  - Free list management                           │  │
│  │  - Chunk coalescing                               │  │
│  │  - Arena/thread-local caches                      │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │ syscall                      │
├──────────────────────────┼──────────────────────────────┤
│                    Kernel Space                         │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │  brk() / mmap() / munmap()                        │  │
│  │  - Virtual memory area (VMA) management           │  │
│  │  - Page table manipulation                        │  │
│  │  - Demand paging (page fault handler)             │  │
│  └───────────────────────┬───────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────┴───────────────────────────┐  │
│  │  Physical Page Allocator (buddy system)           │  │
│  │  - Free page frames                               │  │
│  │  - Zone management (DMA, Normal, HighMem)         │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Part 1: brk() — The Program Break

### What is the Program Break?

The program break is the boundary between the heap and unused virtual address space. Moving it up "allocates" more virtual address space for the heap.

```
Virtual Memory Layout:
                    Low Addresses
┌──────────────────┐ 0x400000
│    .text         │ (code)
├──────────────────┤
│    .data         │ (initialized globals)
├──────────────────┤
│    .bss          │ (uninitialized globals)
├──────────────────┤ ← Original brk
│                  │
│    HEAP          │ (grows upward ↓)
│                  │
├──────────────────┤ ← Current brk (after allocation)
│                  │
│   (unmapped)     │
│                  │
├──────────────────┤
│    STACK         │ (grows downward ↑)
├──────────────────┤
│   Kernel Space   │
└──────────────────┘ 0x7FFFFFFFFFFF
                    High Addresses
```

### brk() Syscall in Assembly

```nasm
; C equivalent:
; int brk(void *addr);           // set program break
; void *sbrk(intptr_t increment); // increment program break

section .data
    alloc_msg db "Allocated memory at: 0x", 0
    newline   db 10

section .bss
    heap_start resq 1
    heap_end   resq 1

section .text
    global _start

_start:
    ; Get current program break (brk(0) returns current break)
    mov rax, 12             ; sys_brk
    xor rdi, rdi            ; addr = 0 (query current break)
    syscall
    mov [heap_start], rax   ; Save initial break address
    mov [heap_end], rax

    ; Allocate 4096 bytes by moving break up
    mov rdi, rax
    add rdi, 4096           ; New break = current + 4096
    mov rax, 12             ; sys_brk
    syscall

    ; Check if allocation succeeded
    cmp rax, [heap_end]     ; If rax == old break, it failed
    je .alloc_failed

    mov [heap_end], rax     ; Save new break

    ; Now [heap_start] to [heap_end] is our heap
    ; Write something to our allocated memory
    mov rdi, [heap_start]
    mov byte [rdi], 'H'
    mov byte [rdi+1], 'i'

    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall

.alloc_failed:
    mov rax, 60
    mov rdi, 1
    syscall
```

### sbrk() Implementation in Assembly

```nasm
; sbrk equivalent - increment the program break by N bytes
; Input: RDI = number of bytes to allocate
; Output: RAX = pointer to start of new memory (old break)
;         On error: RAX = -1
sbrk:
    push rbx
    push rdi                ; Save requested size

    ; Get current break
    mov rax, 12             ; sys_brk
    push rdi                ; Save size
    xor rdi, rdi            ; Query current break
    syscall
    mov rbx, rax            ; RBX = old break (return value)

    ; Set new break
    pop rdi                 ; Restore requested size
    pop rdi                 ; Restore from stack
    add rdi, rbx            ; New break = old break + size
    mov rax, 12             ; sys_brk
    syscall

    ; Check success: new break should equal requested address
    cmp rax, rbx            ; If unchanged, allocation failed
    je .sbrk_fail

    mov rax, rbx            ; Return old break (start of new memory)
    pop rbx
    ret

.sbrk_fail:
    mov rax, -1
    pop rbx
    ret
```

---

## Part 2: mmap() — Memory Mapped Allocation

### Why mmap() for Large Allocations?

`brk()` has a critical limitation: you can only free memory at the top of the heap. If you `brk()` up by 1MB, use it, then want to free it, you can only do so if nothing was allocated above it. `mmap()` solves this by allocating independent virtual memory regions.

**Rule of thumb in glibc:**
- Allocations < 128KB (MMAP_THRESHOLD): Use brk()
- Allocations >= 128KB: Use mmap()

### mmap() Syscall in Assembly

```nasm
; C equivalent:
; void *mmap(void *addr, size_t length, int prot,
;            int flags, int fd, off_t offset);

; Syscall number: 9 (sys_mmap)
; Arguments:
;   RDI = addr (NULL for kernel to choose)
;   RSI = length (bytes)
;   RDX = prot (PROT_READ=1, PROT_WRITE=2, PROT_EXEC=4)
;   R10 = flags (MAP_PRIVATE=2, MAP_ANONYMOUS=32)
;   R8  = fd (-1 for anonymous mapping)
;   R9  = offset (0 for anonymous mapping)

section .text
    global _start

_start:
    ; Allocate 1 page (4096 bytes) of anonymous memory
    mov rax, 9              ; sys_mmap
    xor rdi, rdi            ; addr = NULL (kernel chooses)
    mov rsi, 4096           ; length = 4096 bytes (1 page)
    mov rdx, 3              ; prot = PROT_READ | PROT_WRITE
    mov r10, 34             ; flags = MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1              ; fd = -1 (not file-backed)
    xor r9, r9              ; offset = 0
    syscall

    ; Check for error (returns -errno on failure)
    cmp rax, -4096          ; Check if return is in error range
    ja .mmap_failed         ; Unsigned comparison catches -1 to -4095

    ; RAX now points to our mapped memory
    mov rdi, rax            ; Save pointer

    ; Use the memory
    mov qword [rdi], 0xDEADBEEF
    mov qword [rdi+8], 0xCAFEBABE

    ; Free the memory with munmap
    ; mov rdi, rdi          ; addr (already in RDI)
    mov rsi, 4096           ; length
    mov rax, 11             ; sys_munmap
    syscall

    ; Exit
    mov rax, 60
    xor rdi, rdi
    syscall

.mmap_failed:
    mov rax, 60
    mov rdi, 1
    syscall
```

### Allocating Executable Memory (JIT Compilation)

```nasm
; Allocate memory that can hold executable code (like a JIT compiler)
; prot = PROT_READ | PROT_WRITE | PROT_EXEC = 7
; WARNING: Most systems have W^X policy; allocate RW, write code, then mprotect to RX

section .text
    global _start

_start:
    ; Step 1: Allocate RW memory
    mov rax, 9              ; sys_mmap
    xor rdi, rdi            ; addr = NULL
    mov rsi, 4096           ; 1 page
    mov rdx, 3              ; PROT_READ | PROT_WRITE
    mov r10, 34             ; MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1
    xor r9, r9
    syscall
    mov r12, rax            ; Save pointer in callee-saved register

    ; Step 2: Write machine code into the buffer
    ; We'll write: mov eax, 42; ret (returns 42)
    mov byte [r12], 0xB8       ; mov eax, imm32
    mov dword [r12+1], 42      ; immediate value 42
    mov byte [r12+5], 0xC3     ; ret

    ; Step 3: Change protection to RX (remove write, add execute)
    mov rax, 10             ; sys_mprotect
    mov rdi, r12            ; addr
    mov rsi, 4096           ; length
    mov rdx, 5              ; PROT_READ | PROT_EXEC
    syscall

    ; Step 4: Call our generated code
    call r12                ; Call the JIT'd function
    ; RAX now contains 42

    ; Step 5: Exit with the returned value
    mov rdi, rax            ; Exit code = 42
    mov rax, 60
    syscall
```

---

## Part 3: How malloc() Actually Works

### The Chunk Structure

Every `malloc` implementation wraps each allocation in a chunk with metadata. Here's what glibc's `malloc` (ptmalloc2) uses:

```
Allocated chunk:
┌────────────────────────┐ ← chunk pointer (hidden from user)
│  prev_size (8 bytes)   │  Size of previous chunk (if free)
├────────────────────────┤
│  size | flags (8 bytes)│  Chunk size + AMP flags (3 LSBs)
├────────────────────────┤ ← pointer returned to user
│                        │
│  User data             │
│  (requested size,      │
│   rounded up to        │
│   16-byte alignment)   │
│                        │
└────────────────────────┘ ← next chunk starts here

Free chunk:
┌────────────────────────┐
│  prev_size (8 bytes)   │
├────────────────────────┤
│  size | flags (8 bytes)│
├────────────────────────┤
│  fd (forward ptr)      │  → next free chunk
├────────────────────────┤
│  bk (backward ptr)     │  → previous free chunk
├────────────────────────┤
│  (unused space)        │
├────────────────────────┤
│  prev_size copy        │  (at end of chunk, for coalescing)
└────────────────────────┘

Flags in size field (3 least significant bits):
  Bit 0 (P): PREV_INUSE - previous chunk is allocated
  Bit 1 (M): IS_MMAPPED - chunk was allocated via mmap
  Bit 2 (A): NON_MAIN_ARENA - chunk belongs to non-main arena
```

### Implementing a Simple malloc in Assembly

```nasm
; Minimal malloc/free implementation using brk()
; Supports: allocation, free, first-fit free list

section .bss
    heap_base   resq 1      ; Start of our heap
    heap_top    resq 1      ; Current top of heap
    free_list   resq 1      ; Head of free list (singly-linked)

section .text
    global my_malloc
    global my_free
    global malloc_init

; Chunk header structure (16 bytes):
;   [0..7]  = size (including header) | flags
;   [8..15] = next_free (only when free; overlaps with user data)
HEADER_SIZE equ 16
FLAG_FREE   equ 1           ; Bit 0: chunk is free
SIZE_MASK   equ ~7          ; Mask off flag bits

; Initialize the allocator
; Call once before using malloc/free
malloc_init:
    push rbx
    ; Get initial program break
    mov rax, 12             ; sys_brk
    xor rdi, rdi
    syscall
    mov [heap_base], rax
    mov [heap_top], rax
    mov qword [free_list], 0  ; Empty free list
    pop rbx
    ret

; my_malloc(size_t size) -> void*
; Input: RDI = requested size
; Output: RAX = pointer to usable memory, or 0 on failure
my_malloc:
    push rbx
    push r12
    push r13

    ; Round up size to 16-byte alignment + header
    add rdi, HEADER_SIZE + 15
    and rdi, ~15            ; Align to 16 bytes
    mov r12, rdi            ; R12 = total chunk size needed

    ; Search free list (first-fit)
    mov rax, [free_list]    ; Current free chunk
    xor rbx, rbx           ; Previous chunk (for unlinking)

.search_free:
    test rax, rax
    jz .no_free_chunk       ; End of free list

    ; Get chunk size (mask off flags)
    mov rcx, [rax]          ; Load size|flags
    mov rdx, rcx
    and rdx, SIZE_MASK      ; Actual size

    ; Is this chunk big enough?
    cmp rdx, r12
    jge .found_free

    ; Move to next free chunk
    mov rbx, rax            ; prev = current
    mov rax, [rax + 8]     ; current = current->next_free
    jmp .search_free

.found_free:
    ; Unlink from free list
    mov rcx, [rax + 8]     ; next_free of found chunk
    test rbx, rbx
    jz .unlink_head
    mov [rbx + 8], rcx     ; prev->next_free = found->next_free
    jmp .mark_used
.unlink_head:
    mov [free_list], rcx   ; free_list = found->next_free

.mark_used:
    ; Clear free flag, keep size
    mov rcx, [rax]
    and rcx, ~FLAG_FREE     ; Clear free bit
    mov [rax], rcx

    ; Return pointer past header
    add rax, HEADER_SIZE
    pop r13
    pop r12
    pop rbx
    ret

.no_free_chunk:
    ; Extend heap using brk()
    mov rax, 12             ; sys_brk
    xor rdi, rdi            ; Get current break
    syscall
    mov r13, rax            ; R13 = current break (chunk start)

    ; Set new break
    lea rdi, [rax + r12]   ; New break = current + chunk_size
    mov rax, 12             ; sys_brk
    syscall

    ; Verify success
    lea rcx, [r13 + r12]
    cmp rax, rcx
    jl .alloc_fail          ; brk didn't move enough

    ; Write chunk header
    mov [r13], r12          ; size (no flags set = allocated)
    mov [heap_top], rax     ; Update heap top

    ; Return pointer past header
    lea rax, [r13 + HEADER_SIZE]
    pop r13
    pop r12
    pop rbx
    ret

.alloc_fail:
    xor rax, rax            ; Return NULL
    pop r13
    pop r12
    pop rbx
    ret

; my_free(void *ptr)
; Input: RDI = pointer previously returned by my_malloc
my_free:
    test rdi, rdi
    jz .free_done           ; free(NULL) is a no-op

    ; Get chunk header (ptr - HEADER_SIZE)
    sub rdi, HEADER_SIZE

    ; Set free flag
    mov rax, [rdi]
    or rax, FLAG_FREE
    mov [rdi], rax

    ; Prepend to free list
    mov rax, [free_list]
    mov [rdi + 8], rax      ; chunk->next_free = old head
    mov [free_list], rdi    ; free_list = chunk

.free_done:
    ret
```

### How glibc malloc Decides: brk vs mmap

```nasm
; Pseudocode of glibc's malloc decision in assembly form:
;
; if (size >= MMAP_THRESHOLD) {    ; typically 128KB
;     return mmap_alloc(size);
; }
; if (free_list has suitable chunk) {
;     return reuse_chunk();
; }
; return brk_alloc(size);

; This shows the mmap path for large allocations:
mmap_alloc:
    ; Input: RDI = size needed
    push rbx
    mov rbx, rdi

    ; Add space for mmap header (stores size for munmap)
    add rbx, 32            ; 16 header + 16 alignment padding
    add rbx, 4095
    and rbx, ~4095          ; Round up to page boundary

    ; mmap anonymous memory
    mov rax, 9              ; sys_mmap
    xor rdi, rdi            ; addr = NULL
    mov rsi, rbx            ; length (page-aligned)
    mov rdx, 3              ; PROT_READ | PROT_WRITE
    mov r10, 34             ; MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1
    xor r9, r9
    syscall

    cmp rax, -4096
    ja .mmap_fail

    ; Store metadata: total mapped size and IS_MMAPPED flag
    mov qword [rax], 0     ; prev_size = 0
    mov rcx, rbx
    or rcx, 2              ; Set IS_MMAPPED flag (bit 1)
    mov [rax + 8], rcx     ; size | IS_MMAPPED

    ; Return usable pointer
    add rax, 16
    pop rbx
    ret

.mmap_fail:
    xor rax, rax
    pop rbx
    ret

; Free an mmap'd chunk: just munmap it
mmap_free:
    ; Input: RDI = user pointer
    sub rdi, 16            ; Back to chunk start
    mov rsi, [rdi + 8]    ; Get size
    and rsi, SIZE_MASK      ; Mask off flags
    mov rax, 11            ; sys_munmap
    syscall
    ret
```

---

## Part 4: Free List Strategies

### Understanding Fragmentation

```
After many malloc/free cycles:

Heap: [USED 32][FREE 16][USED 64][FREE 48][USED 16][FREE 24][USED 128]
                   ↓                  ↓                  ↓
           free_list → [16 bytes] → [48 bytes] → [24 bytes] → NULL

Problem: Request for 80 bytes FAILS even though total free = 88 bytes!
This is "external fragmentation"
```

### Bin Organization (glibc approach)

```nasm
; glibc organizes free chunks into bins by size:
;
; Fast bins (sizes 16-80, step 16):
;   Single-linked LIFO lists, never coalesced
;   bin[0] = 16-byte chunks
;   bin[1] = 32-byte chunks
;   bin[2] = 48-byte chunks
;   bin[3] = 64-byte chunks
;   bin[4] = 80-byte chunks
;
; Small bins (sizes 96-512, step 16):
;   Doubly-linked FIFO lists
;
; Large bins (sizes > 512):
;   Sorted by size, doubly-linked
;
; Unsorted bin:
;   Recently freed chunks awaiting sorting

; Fast bin lookup (given a size):
; bin_index = (size >> 4) - 1
; For size=32: index = (32 >> 4) - 1 = 1

section .bss
    fastbins resq 5         ; 5 fast bin heads (16,32,48,64,80)

; Fast bin free (O(1)):
; Chunks go to head of appropriate bin
fastbin_free:
    ; RDI = chunk pointer (with header)
    mov rax, [rdi]          ; Get chunk size
    and rax, SIZE_MASK
    shr rax, 4
    dec rax                 ; bin index
    lea rcx, [fastbins]
    
    ; Push onto bin's free list (single-linked stack)
    mov rdx, [rcx + rax*8] ; Old head
    mov [rdi + 8], rdx     ; chunk->next = old head
    mov [rcx + rax*8], rdi ; bin[i] = chunk
    ret

; Fast bin malloc (O(1)):
fastbin_malloc:
    ; RDI = requested size (already aligned)
    mov rax, rdi
    shr rax, 4
    dec rax                 ; bin index
    lea rcx, [fastbins]
    
    ; Pop from bin's free list
    mov rdx, [rcx + rax*8] ; Head of bin
    test rdx, rdx
    jz .fastbin_empty       ; No cached chunks
    
    mov rsi, [rdx + 8]    ; next = head->next
    mov [rcx + rax*8], rsi ; bin[i] = next
    
    ; Return chunk (clear free flag if needed)
    lea rax, [rdx + HEADER_SIZE]
    ret

.fastbin_empty:
    xor rax, rax           ; Fall through to slower path
    ret
```

### Chunk Coalescing (Merging Adjacent Free Chunks)

```nasm
; When free() is called, check if adjacent chunks are also free
; and merge them to reduce fragmentation

; Given: RDI = chunk being freed
coalesce:
    push rbx
    push r12
    mov r12, rdi

    ; Check if NEXT chunk is free
    mov rax, [r12]          ; Our size
    and rax, SIZE_MASK
    lea rbx, [r12 + rax]   ; Next chunk address

    ; Verify next chunk is within heap bounds
    cmp rbx, [heap_top]
    jge .check_prev

    mov rcx, [rbx]         ; Next chunk's size|flags
    test rcx, FLAG_FREE    ; Is it free?
    jz .check_prev

    ; Merge with next chunk: our_size += next_size
    and rcx, SIZE_MASK
    mov rax, [r12]
    and rax, SIZE_MASK
    add rax, rcx
    or rax, FLAG_FREE      ; Keep free flag
    mov [r12], rax         ; Update our size

    ; Remove next chunk from free list
    ; (simplified: would need to search and unlink)

.check_prev:
    ; Check if PREVIOUS chunk is free (using prev_size field)
    ; Bit 0 (PREV_INUSE) of our size tells us
    mov rax, [r12]
    test rax, 1            ; PREV_INUSE flag
    jnz .done              ; Previous is in use, can't merge

    ; Previous is free: merge backward
    ; prev_size field tells us previous chunk's size
    mov rcx, [r12 - 8]    ; prev_size (stored at end of prev chunk)
    sub r12, rcx           ; Back up to previous chunk start

    ; Combine sizes
    mov rax, [r12]
    and rax, SIZE_MASK
    mov rdx, [r12]         ; Reload (size of prev)
    and rdx, SIZE_MASK
    add rax, rdx           ; Combined size
    or rax, FLAG_FREE
    mov [r12], rax

.done:
    mov rax, r12           ; Return merged chunk address
    pop r12
    pop rbx
    ret
```

---

## Part 5: What Happens at Page Fault

When `brk()` or `mmap()` returns successfully, the kernel hasn't actually allocated physical memory yet. It only updates the page tables to mark the virtual addresses as valid. Physical pages are allocated on **first access** via the page fault mechanism.

```
Timeline of a malloc'd byte being used:

1. malloc(64) returns 0x55555576a2a0
   → brk() expanded virtual address space
   → Page table entry: Valid=0, Present=0
   → NO physical memory used yet!

2. mov byte [0x55555576a2a0], 'A'    ← First write
   → CPU walks page table, finds page not present
   → TRIGGERS PAGE FAULT (exception #14)
   → Kernel page fault handler:
     a. Checks VMA: is this address valid? YES (within brk range)
     b. Allocates a physical page (4KB) from buddy allocator
     c. Zeros the page (security: don't leak other process data)
     d. Updates page table: PTE points to physical page, Present=1
     e. Returns to user code — instruction is RETRIED
   → Write succeeds on retry

3. mov byte [0x55555576a2a1], 'B'    ← Same page, no fault
   → Page already present, direct access
```

```nasm
; Demonstrating demand paging:
; Allocate 1MB but only touch 1 page — only 4KB physical memory used

section .text
    global _start

_start:
    ; Allocate 1MB (256 pages)
    mov rax, 9              ; sys_mmap
    xor rdi, rdi
    mov rsi, 1048576        ; 1MB
    mov rdx, 3              ; PROT_READ | PROT_WRITE
    mov r10, 34             ; MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1
    xor r9, r9
    syscall
    mov r12, rax            ; Save base

    ; Only touch first byte — only 1 physical page allocated
    mov byte [r12], 42

    ; The other 255 pages remain un-faulted
    ; Physical memory used: ~4KB, not 1MB!

    ; Now touch last page — second page fault, second physical page
    mov byte [r12 + 1048575], 99

    ; Physical memory used: ~8KB (2 pages)

    mov rax, 60
    xor rdi, rdi
    syscall
```

---

## Part 6: Thread-Local Allocation (Arenas)

In multi-threaded programs, a single lock on the heap would be a bottleneck. Modern allocators use per-thread arenas:

```
Thread 1 Arena:          Thread 2 Arena:         Thread 3 Arena:
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ Fast bins      │      │ Fast bins      │      │ Fast bins      │
│ Small bins     │      │ Small bins     │      │ Small bins     │
│ Large bins     │      │ Large bins     │      │ Large bins     │
│ Top chunk      │      │ Top chunk      │      │ Top chunk      │
└───────┬────────┘      └───────┬────────┘      └───────┬────────┘
        │                       │                       │
        └── mmap'd region ──────┴── mmap'd region ──────┘
```

```nasm
; Per-thread allocation using thread-local storage (TLS)
; Each thread has its own cache of free chunks

; Using the arch_prctl syscall to access thread-local data:
; or using FS segment register (Linux TLS convention)

; Read TLS base:
; mov rax, [fs:0]  ; TLS base address

; Thread-local free list (conceptual):
; struct thread_cache {
;     void *free_list[NUM_BINS];
;     size_t cached_count;
; };

; Accessing thread-local allocator cache:
get_thread_cache:
    ; The FS register points to thread control block (TCB)
    ; TLS variables are at negative offsets from FS base
    mov rax, [fs:-8]       ; Our thread_cache pointer
    ret
```

---

## Part 7: Memory Alignment

### Why Alignment Matters

```nasm
; Aligned access: address is multiple of data size
mov rax, [rbp-8]           ; Address ending in 0 or 8: aligned QWORD

; Unaligned access: address NOT multiple of data size
mov rax, [rbp-5]           ; Address ending in B: unaligned!
; Works on x86 but may be:
;   - Split across cache lines (2x memory access)
;   - Split across pages (very expensive, may fault on some CPUs)

; malloc guarantees 16-byte alignment (glibc on 64-bit):
; Every returned pointer is a multiple of 16
; This ensures SSE/AVX instructions work:
movaps xmm0, [rax]        ; REQUIRES 16-byte alignment (faults otherwise)
movups xmm0, [rax]        ; Unaligned version (slower but safe)

; Custom aligned allocation using mmap:
aligned_alloc_page:
    ; Allocate on page boundary (4096-byte alignment)
    mov rax, 9
    xor rdi, rdi            ; NULL = kernel chooses page-aligned addr
    mov rsi, 4096
    mov rdx, 3              ; RW
    mov r10, 34             ; PRIVATE | ANONYMOUS
    mov r8, -1
    xor r9, r9
    syscall
    ; RAX is guaranteed page-aligned (multiple of 4096)
    ret
```

### posix_memalign / aligned_alloc Implementation

```nasm
; Allocate with custom alignment
; Input: RDI = alignment (must be power of 2), RSI = size
; Output: RAX = aligned pointer
my_aligned_alloc:
    push rbx
    push r12
    mov r12, rdi            ; alignment
    mov rbx, rsi            ; size

    ; Allocate extra space: size + alignment + header
    lea rdi, [rbx + r12 + HEADER_SIZE]
    call my_malloc          ; Get unaligned block
    test rax, rax
    jz .aligned_fail

    ; Find aligned address within the block
    mov rcx, rax
    add rcx, r12
    dec rcx
    neg r12                 ; Create alignment mask
    and rcx, r12            ; Round up to alignment

    ; Store original pointer just before aligned address (for free)
    mov [rcx - 8], rax     ; Stash real pointer

    mov rax, rcx
    pop r12
    pop rbx
    ret

.aligned_fail:
    xor rax, rax
    pop r12
    pop rbx
    ret
```

---

## Part 8: Debugging Memory Issues

### Detecting Use-After-Free

```nasm
; Secure free: overwrite memory to catch use-after-free
secure_free:
    ; RDI = pointer to free
    test rdi, rdi
    jz .done

    ; Get chunk size from header
    mov rax, [rdi - HEADER_SIZE]
    and rax, SIZE_MASK
    sub rax, HEADER_SIZE   ; Usable size

    ; Fill with poison pattern (0xDEADBEEF...)
    push rdi
    push rcx
    mov rcx, rax
    shr rcx, 3             ; Count in qwords
    mov rax, 0xDEADBEEFDEADBEEF
    rep stosq              ; Fill with poison
    pop rcx
    pop rdi

    ; Now actually free
    call my_free
.done:
    ret

; Detecting double-free:
safe_free:
    ; RDI = pointer
    test rdi, rdi
    jz .ok

    sub rdi, HEADER_SIZE
    mov rax, [rdi]
    test rax, FLAG_FREE    ; Already free?
    jnz .double_free       ; BUG! Double free detected

    ; Normal free path
    add rdi, HEADER_SIZE
    call my_free
.ok:
    ret

.double_free:
    ; Print error and abort
    mov rax, 1             ; sys_write
    mov rdi, 2             ; stderr
    lea rsi, [rel .errmsg]
    mov rdx, .errlen
    syscall
    mov rax, 60
    mov rdi, 134           ; SIGABRT exit code
    syscall

section .rodata
.errmsg: db "*** DOUBLE FREE DETECTED ***", 10
.errlen equ $ - .errmsg
```

### Memory Layout Inspection with /proc/self/maps

```nasm
; Read our own memory map (equivalent to cat /proc/self/maps)
section .data
    maps_path db "/proc/self/maps", 0

section .bss
    maps_buf resb 4096

section .text
print_memory_map:
    ; Open /proc/self/maps
    mov rax, 2             ; sys_open
    lea rdi, [rel maps_path]
    xor rsi, rsi           ; O_RDONLY
    xor rdx, rdx
    syscall
    mov r12, rax           ; fd

    ; Read and print
.read_loop:
    mov rax, 0             ; sys_read
    mov rdi, r12
    lea rsi, [rel maps_buf]
    mov rdx, 4096
    syscall
    test rax, rax
    jle .read_done

    ; Write to stdout
    mov rdx, rax           ; bytes read
    mov rax, 1             ; sys_write
    mov rdi, 1             ; stdout
    lea rsi, [rel maps_buf]
    syscall
    jmp .read_loop

.read_done:
    ; Close file
    mov rax, 3             ; sys_close
    mov rdi, r12
    syscall
    ret
```

---

## Exercises

1. **Basic brk allocator**: Write a program that allocates 3 separate buffers using brk(), writes strings to each, prints them all, then exits.

2. **mmap allocator**: Allocate 10 pages with mmap, use only pages 0, 4, and 9. Use `strace` to observe page faults.

3. **Free list malloc**: Extend the simple malloc implementation to support chunk splitting (when a free chunk is much larger than requested, split it).

4. **Memory pool**: Implement a fixed-size object pool (all allocations are same size) — this is what kernel slab allocators do.

5. **Fragmentation demo**: Write a program that alternately allocates and frees chunks of different sizes, then attempts a large allocation that fails due to fragmentation. Demonstrate how coalescing fixes it.

---

## Key Takeaways

| Concept | Assembly Reality |
|---------|-----------------|
| `malloc(n)` | Check free list → brk/mmap → return chunk+16 |
| `free(p)` | Add chunk to free list (maybe coalesce) |
| Small allocs | brk() extends heap linearly |
| Large allocs | mmap() creates independent mapping |
| Demand paging | Physical pages allocated on first access (page fault) |
| Alignment | malloc returns 16-byte aligned; page boundary = 4096 |
| Thread safety | Per-thread arenas avoid lock contention |

---

## Next Topic

[Topic 22: Process Internals →](topic-22-process-internals.md) — How fork(), exec(), and process creation work at the assembly level.
