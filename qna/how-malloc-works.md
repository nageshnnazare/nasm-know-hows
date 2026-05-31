# Q&A: How Does malloc() Actually Work?

## The Question

> When I call `malloc(64)` in C (or implement my own in assembly), what actually happens from the application level down to physical memory? How does `free()` know how much to free? Where does fragmentation come from?

---

## Quick Answer

`malloc(n)` does NOT call the kernel every time. It manages a pool of pre-obtained memory using a free list. Only when the pool is empty does it request more from the kernel via `brk()` (small allocations) or `mmap()` (large allocations). `free()` doesn't return memory to the kernel — it adds the chunk back to the free list for reuse.

---

## The Full Story

### Level 0: What malloc Returns

```
You call:  void *p = malloc(64);
You get:   p = 0x55555576a2b0 (a virtual address)
You think: "I have 64 bytes starting at p"

Reality:   malloc actually allocated ~80 bytes:
           ┌──────────────────────────────────────────┐
           │ [16 bytes header] [64 bytes for you] [...] │
           └──────────────────────────────────────────┘
            ↑                   ↑
            chunk start         pointer returned to you
            (0x55555576a2a0)    (0x55555576a2b0)
```

### Level 1: The Hidden Header

Every allocation has metadata stored BEFORE the pointer you receive:

```
Offset from returned pointer:
  -16 bytes: prev_size (8 bytes) — size of previous chunk (for coalescing)
  -8 bytes:  size | flags (8 bytes) — THIS chunk's size + 3 flag bits

So when you call free(p):
  1. Go to p - 16 → find the chunk header
  2. Read the size field → knows exactly how much to free
  3. Check flags → is this mmap'd? Is previous chunk free?
```

### Level 2: Free List Bins

glibc malloc organizes free chunks by size for O(1) allocation:

```
Fast bins (16-80 bytes, step 16) — LIFO, single-linked, never coalesced:
  fastbin[0]: 16-byte chunks → □ → □ → □ → NULL
  fastbin[1]: 32-byte chunks → □ → □ → NULL
  fastbin[2]: 48-byte chunks → □ → NULL
  fastbin[3]: 64-byte chunks → □ → □ → □ → □ → NULL
  fastbin[4]: 80-byte chunks → NULL

Small bins (96-1024 bytes) — FIFO, doubly-linked, coalesced on free:
  smallbin[0]: 96-byte chunks  → □ ↔ □ ↔ □
  smallbin[1]: 112-byte chunks → □ ↔ □
  ...

Large bins (>1024 bytes) — sorted by size, doubly-linked:
  largebin[0]: 1024-2048 → □(1100) ↔ □(1500) ↔ □(2000)
  ...

Unsorted bin — recently freed chunks awaiting classification:
  unsorted → □ → □ → □ → NULL
```

### Level 3: malloc Decision Tree

```
malloc(n):
  1. n < 32 bytes? → return from tcache (per-thread cache)
  2. n < 80 bytes? → return from fastbin[size_to_index(n)]
  3. n < 1024 bytes? → return from smallbin[size_to_index(n)]
  4. Otherwise:
     a. Consolidate fastbins into unsorted bin
     b. Search unsorted bin for exact or close fit
     c. Search large bins for best fit
     d. Split the "top chunk" (wilderness)
     e. If top chunk too small: extend heap with brk()
     f. If n >= 128KB: use mmap() directly
```

### Level 4: Why free() Doesn't Return Memory

```
After free(p):
  - Chunk is added to free list (available for future malloc)
  - Physical pages are NOT returned to kernel
  - Virtual address space is NOT released
  - Process RSS (resident set) stays the same

Why?
  - brk() can only release memory at the TOP of the heap
  - If any chunk above is still allocated, can't shrink
  - Future mallocs will reuse freed chunks (fast, no syscall)
  
When IS memory returned?
  - mmap'd chunks (>128KB): munmap'd immediately by free()
  - glibc's malloc_trim(): explicitly release top of heap
  - Process exit: kernel reclaims everything
```

---

## Assembly-Level Implementation

### malloc in ~30 Lines of Assembly (Simplified)

```nasm
; Minimal brk-based allocator:
my_malloc:
    ; RDI = requested size
    add rdi, 16            ; Add header size
    add rdi, 15
    and rdi, ~15           ; Align to 16 bytes
    
    ; Extend heap
    push rdi               ; Save total size
    mov rax, 12            ; sys_brk
    xor rdi, rdi           ; Get current break
    syscall
    mov rbx, rax           ; Old break = chunk start
    
    pop rdi                ; Total size
    lea rdi, [rbx + rdi]   ; New break
    mov rax, 12            ; sys_brk
    syscall
    
    ; Write header
    pop rdi                ; (need to recalculate)
    ; Actually, simpler version:
    mov qword [rbx], rdi   ; Store size in header
    
    ; Return pointer past header
    lea rax, [rbx + 16]
    ret
```

---

## Common Bugs Explained

### Use-After-Free

```
p = malloc(64);    → chunk allocated, p valid
free(p);           → chunk on free list, p now DANGLING
*p = 42;           → writing to freed chunk!
                      Might corrupt free list metadata!
                      Might silently work (until next malloc uses that chunk)
```

### Double Free

```
free(p);           → chunk added to free list
free(p);           → SAME chunk added AGAIN!
                      free list now has a cycle: ... → chunk → ... → chunk → ...
                      Next two mallocs return SAME pointer!
                      Both callers think they own the memory exclusively!
```

### Heap Overflow

```
p = malloc(64);
memcpy(p, data, 100);  → wrote 36 bytes past end of chunk!
                          Corrupted NEXT chunk's header!
                          Next free/malloc will read garbage size → crash/exploit
```

---

## TL;DR

| Question | Answer |
|----------|--------|
| Does malloc syscall every time? | No — only when its pool is empty |
| Which syscall? | brk() for small (<128KB), mmap() for large |
| How does free know the size? | Hidden header 16 bytes before your pointer |
| Does free return memory to OS? | Usually no (only for mmap'd chunks) |
| What's the minimum allocation? | 32 bytes (header + alignment) |
| Why is malloc fast? | Per-thread caches, size-indexed bins, no syscall usually |
| What causes fragmentation? | Alternating alloc/free of different sizes |
