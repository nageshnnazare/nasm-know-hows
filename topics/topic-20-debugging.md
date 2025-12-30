# Topic 20: Debugging and Tools

## Overview

Debugging assembly code requires specialized tools and techniques. This topic covers essential debugging workflows, tools for analysis, and strategies for finding and fixing bugs in low-level code.

```bash
# Essential toolkit:
gdb        # The GNU debugger
objdump    # Disassemble binaries
strace     # Trace system calls
valgrind   # Memory debugging
readelf    # Examine ELF files
hexdump    # View binary data
```

---

## GDB - The GNU Debugger

### Basic GDB Workflow

```bash
# Compile with debug symbols
nasm -f elf64 -g -F dwarf program.asm -o program.o
ld program.o -o program

# Or with C:
gcc -g program.c -o program

# Start GDB
gdb ./program
```

### Essential GDB Commands

```gdb
# Starting and stopping
(gdb) run [args]              # Start program
(gdb) run < input.txt         # Start with input redirection
(gdb) start                   # Start and break at main
(gdb) quit                    # Exit GDB

# Breakpoints
(gdb) break main              # Break at function
(gdb) break *0x401000         # Break at address
(gdb) break program.asm:42    # Break at source line
(gdb) info breakpoints        # List breakpoints
(gdb) delete 1                # Delete breakpoint 1
(gdb) disable 2               # Disable breakpoint 2
(gdb) enable 2                # Enable breakpoint 2

# Execution control
(gdb) continue                # Continue execution
(gdb) next                    # Next source line (step over calls)
(gdb) step                    # Step into function calls
(gdb) stepi                   # Single instruction step
(gdb) nexti                   # Next instruction (step over calls)
(gdb) finish                  # Run until current function returns
(gdb) until *0x401050         # Run until address

# Examining state
(gdb) info registers          # Show all registers
(gdb) info registers rax rbx  # Show specific registers
(gdb) print $rax              # Print register value
(gdb) print /x $rax           # Print in hex
(gdb) print /t $rax           # Print in binary
(gdb) print /d $rax           # Print in decimal

# Memory examination
(gdb) x/10x $rsp              # Examine 10 hex values at RSP
(gdb) x/10i $rip              # Disassemble 10 instructions at RIP
(gdb) x/s 0x404000            # Display string at address
(gdb) x/4gx $rsp              # Examine 4 giant (8-byte) hex values

# Memory modification
(gdb) set $rax = 0            # Set register
(gdb) set *(int*)0x404000 = 42  # Write to memory

# Watchpoints (break on memory change)
(gdb) watch *0x404000         # Break when memory changes
(gdb) watch $rax              # Break when register changes
(gdb) rwatch *0x404000        # Break on read
(gdb) awatch *0x404000        # Break on read or write

# Stack examination
(gdb) backtrace               # Show call stack
(gdb) frame 2                 # Switch to frame 2
(gdb) info frame              # Show current frame info

# Disassembly
(gdb) disassemble main        # Disassemble function
(gdb) disassemble /r main     # With raw bytes
(gdb) set disassembly-flavor intel  # Use Intel syntax
```

### TUI Mode (Text User Interface)

```gdb
(gdb) tui enable              # Enable TUI
(gdb) layout asm              # Show assembly
(gdb) layout regs             # Show registers
(gdb) layout split            # Show source and assembly
(gdb) focus cmd               # Focus command window
(gdb) refresh                 # Redraw screen

# Or start with:
gdb -tui ./program
```

### Example Debugging Session

```nasm
; buggy.asm - Contains an off-by-one error
section .data
    array dd 1, 2, 3, 4, 5
    count equ 5

section .text
global _start

_start:
    xor eax, eax            ; sum = 0
    xor ecx, ecx            ; i = 0
    
loop:
    cmp ecx, count
    jge done
    add eax, [array + rcx*4]
    inc ecx
    jmp loop                ; BUG: Should be conditional
    
done:
    ; Exit
    mov rdi, rax
    mov rax, 60
    syscall
```

**Debugging session:**

```gdb
$ gdb ./buggy
(gdb) break _start
(gdb) run

# Step through
(gdb) display /x $eax          # Always show EAX
(gdb) display /x $ecx          # Always show ECX

(gdb) stepi                    # Execute xor eax, eax
# EAX = 0

(gdb) stepi                    # Execute xor ecx, ecx
# ECX = 0

(gdb) stepi                    # Execute cmp ecx, count
(gdb) stepi                    # Execute jge done (not taken)
(gdb) stepi                    # Execute add eax, [array]
# EAX = 1, ECX = 0

(gdb) stepi                    # Execute inc ecx
# ECX = 1

(gdb) stepi                    # Execute jmp loop (UNCONDITIONAL!)
# Notice: We always jump back, ECX never reaches count!

# Found the bug: jmp should be replaced with conditional logic
# or the loop structure needs fixing
```

---

## Objdump - Disassembly Tool

### Basic Usage

```bash
# Disassemble entire program
objdump -d program

# Intel syntax
objdump -d -M intel program

# With source code interleaved
objdump -d -S program

# Specific section
objdump -d -j .text program

# Show all headers
objdump -x program

# Full disassembly with symbols
objdump -D -M intel program > disassembly.txt
```

### Example Output

```bash
$ objdump -d -M intel program

program:     file format elf64-x86-64

Disassembly of section .text:

0000000000401000 <_start>:
  401000:   48 31 c0                xor    rax,rax
  401003:   48 31 c9                xor    rcx,rcx
  401006:   48 39 0d f3 0f 00 00    cmp    QWORD PTR [rip+0xff3],rcx
  40100d:   7e 0e                   jle    40101d <done>
  
000000000040100f <loop>:
  40100f:   48 03 04 8d e0 0f 40    add    rax,QWORD PTR [rcx*4+0x400fe0]
  401016:   00 
  401017:   48 ff c1                inc    rcx
  40101a:   eb ed                   jmp    401009 <loop+0xfffffffffffffffa>
  
000000000040101c <done>:
  40101c:   48 89 c7                mov    rdi,rax
  40101f:   48 c7 c0 3c 00 00 00    mov    rax,0x3c
  401026:   0f 05                   syscall
```

**Analysis:**
- Addresses (column 1)
- Machine code bytes (column 2)
- Assembly instructions (column 3)

---

## Strace - System Call Tracer

### Basic Usage

```bash
# Trace all syscalls
strace ./program

# Show syscall stats
strace -c ./program

# Filter specific syscalls
strace -e trace=open,read,write ./program

# Show only file operations
strace -e trace=file ./program

# Show timestamps
strace -t ./program

# Show time spent in each syscall
strace -T ./program

# Attach to running process
strace -p <pid>
```

### Example Output

```bash
$ strace ./hello

execve("./hello", ["./hello"], 0x7fff...) = 0
write(1, "Hello, World!\n", 14)          = 14
exit_group(0)                            = ?
+++ exited with 0 +++
```

**Use cases:**
- Debug file access issues
- Find missing files
- Trace network operations
- Identify performance bottlenecks (slow syscalls)
- Understand program behavior

---

## Valgrind - Memory Debugger

### Memcheck - Memory Error Detection

```bash
# Basic memory check
valgrind --leak-check=full ./program

# With detailed allocation tracking
valgrind --leak-check=full --track-origins=yes ./program

# Show reachable leaks too
valgrind --leak-check=full --show-reachable=yes ./program
```

### Common Errors Detected

```c
// C example with errors (for demonstration)

int main() {
    int *ptr = malloc(100 * sizeof(int));
    
    // 1. Invalid write (beyond allocated memory)
    ptr[100] = 42;  // Valgrind: Invalid write of size 4
    
    // 2. Invalid read
    int x = ptr[100];  // Valgrind: Invalid read of size 4
    
    // 3. Memory leak (forgot to free)
    return 0;  // Valgrind: 400 bytes in 1 blocks definitely lost
}
```

**Valgrind output:**

```
==12345== Invalid write of size 4
==12345==    at 0x401234: main (test.c:5)
==12345==  Address 0x5204190 is 0 bytes after a block of size 400 alloc'd

==12345== LEAK SUMMARY:
==12345==    definitely lost: 400 bytes in 1 blocks
```

### Cachegrind - Cache Profiler

```bash
# Profile cache usage
valgrind --tool=cachegrind ./program

# View results
cg_annotate cachegrind.out.<pid>

# Show specific function
cg_annotate --show=my_function cachegrind.out.<pid>
```

### Callgrind - Call Graph Profiler

```bash
# Generate call graph
valgrind --tool=callgrind ./program

# Visualize with kcachegrind
kcachegrind callgrind.out.<pid>
```

---

## Readelf - ELF File Analysis

### Common Commands

```bash
# Show ELF header
readelf -h program

# Show section headers
readelf -S program

# Show program headers (segments)
readelf -l program

# Show symbol table
readelf -s program

# Show dynamic section
readelf -d program

# Show relocations
readelf -r program
```

### Example: Analyzing Sections

```bash
$ readelf -S program

Section Headers:
  [Nr] Name              Type             Address           Offset
       Size              EntSize          Flags  Link  Info  Align
  [ 1] .text             PROGBITS         0000000000401000  00001000
       00000000000001a0  0000000000000000  AX       0     0     16
  [ 2] .rodata           PROGBITS         00000000004011a0  000011a0
       0000000000000020  0000000000000000   A       0     0     8
  [ 3] .data             PROGBITS         00000000004021c0  000021c0
       0000000000000010  0000000000000000  WA       0     0     8
  [ 4] .bss              NOBITS           00000000004021d0  000021d0
       0000000000000008  0000000000000000  WA       0     0     8

Key:
  A = Allocate, X = Execute, W = Write
```

---

## Hexdump - Binary Data Viewer

### Viewing Binary Files

```bash
# Standard hex dump
hexdump -C program.o

# 16-bit values
hexdump -e '16/2 "%04x " "\n"' file.bin

# Show strings in binary
strings program

# Search for specific byte sequence
hexdump -C file.bin | grep "48 89 e5"
```

### Example Output

```bash
$ hexdump -C program | head -20

00000000  7f 45 4c 46 02 01 01 00  00 00 00 00 00 00 00 00  |.ELF............|
00000010  02 00 3e 00 01 00 00 00  00 10 40 00 00 00 00 00  |..>.......@.....|
00000020  40 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |@...............|
...
```

---

## Common Debugging Scenarios

### Scenario 1: Segmentation Fault

```gdb
$ gdb ./program
(gdb) run
Program received signal SIGSEGV, Segmentation fault.
0x0000000000401015 in loop ()

(gdb) info registers
rax            0x5                 5
rbx            0x0                 0
rcx            0x6                 6  <-- Suspicious value
...

(gdb) x/10i $rip-10
=> 0x401015 <loop+6>:   mov    eax,DWORD PTR [rbx+rcx*4]
   
# Problem: RBX is 0 (null pointer)!
# Accessing [0 + 6*4] = [24] -> SEGFAULT

(gdb) backtrace
#0  0x401015 in loop ()
#1  0x401008 in _start ()

# Debug: Check where RBX should have been initialized
```

### Scenario 2: Infinite Loop

```gdb
(gdb) run
^C  # Ctrl+C to interrupt

Program received signal SIGINT, Interrupt.
0x0000000000401018 in loop ()

(gdb) disassemble
=> 0x401018 <loop+9>:    jmp    0x40100f <loop>

(gdb) print $rcx
$1 = 1000000  # Very high value - loop counter not terminating

(gdb) break loop
(gdb) commands
> print $rcx
> continue
> end

(gdb) run
# Watch RCX values to see if it ever reaches exit condition
```

### Scenario 3: Wrong Result

```gdb
(gdb) break done
(gdb) run
Breakpoint 1, done ()

(gdb) print /d $eax
$1 = 120  # Expected 15

# Work backwards
(gdb) break loop
(gdb) run
(gdb) print $eax
$2 = 0  # Initial value correct

(gdb) continue  # After first iteration
$3 = 1

(gdb) continue  # After second iteration
$4 = 2

# Ah! Should be cumulative sum (1, 3, 6, 10, 15)
# but we're getting indices (1, 2, 3, 4, 5)
# Bug: Adding ECX instead of array value!
```

---

## Advanced Debugging Techniques

### Conditional Breakpoints

```gdb
# Break only when condition is true
(gdb) break loop if $rcx == 5

# Break after N hits
(gdb) break loop
(gdb) ignore 1 100  # Ignore breakpoint 1 for 100 hits

# Complex condition
(gdb) break *0x401020 if $rax > 1000 && $rbx != 0
```

### Scripting GDB

```gdb
# commands.gdb
break _start
commands
  silent
  printf "RAX: %llx\n", $rax
  continue
end

run
```

```bash
# Run with script
gdb -x commands.gdb ./program
```

### Core Dumps

```bash
# Enable core dumps
ulimit -c unlimited

# Run program (it crashes)
./program
Segmentation fault (core dumped)

# Analyze core dump
gdb ./program core
(gdb) backtrace
(gdb) info registers
(gdb) x/10i $rip
```

### Remote Debugging

```bash
# On target machine:
gdbserver :1234 ./program

# On development machine:
gdb ./program
(gdb) target remote target_ip:1234
(gdb) continue
```

---

## Reverse Engineering Basics

### Static Analysis

```bash
# Find entry point
readelf -h program | grep Entry
  Entry point address:               0x401000

# Find interesting strings
strings program
strings -n 8 program  # Min length 8

# Extract sections
objcopy --dump-section .text=text.bin program
```

### Dynamic Analysis

```bash
# Trace execution
ltrace ./program  # Trace library calls
strace ./program  # Trace syscalls

# Attach to running process
gdb -p $(pidof program)
```

### Patching Binaries

```bash
# Using hex editor
hexedit program

# Or with dd
echo -ne '\x90\x90' | dd of=program bs=1 seek=$((0x1234)) conv=notrunc

# Or with objcopy
objcopy --update-section .text=patched.bin program program_patched
```

---

## Best Practices

### Development Workflow

1. **Write incrementally** - Test small pieces
2. **Use assertions** - Validate assumptions
3. **Add debug output** - Print key values
4. **Version control** - Commit working states
5. **Document assumptions** - Comment tricky code

### Debug Build vs Release Build

```makefile
# Debug build
debug: CFLAGS = -g -O0 -DDEBUG
debug: program

# Release build  
release: CFLAGS = -O3 -DNDEBUG
release: program
```

### Defensive Programming

```nasm
; Check for null pointer
test rdi, rdi
jz .error_null_pointer

; Verify array bounds
cmp rcx, [array_size]
jae .error_out_of_bounds

; Validate syscall return
test rax, rax
js .error_syscall_failed
```

---

## Debugging Checklist

### Before Debugging
- [ ] Can you reproduce the bug?
- [ ] Do you have debug symbols?
- [ ] Is the code under version control?
- [ ] Do you have a minimal test case?

### During Debugging
- [ ] Read error messages carefully
- [ ] Check return values
- [ ] Verify assumptions
- [ ] Use the right tool (gdb vs valgrind vs strace)
- [ ] Take notes on what you try

### Common Bug Locations
- [ ] Off-by-one errors in loops
- [ ] Uninitialized registers/memory
- [ ] Wrong register size (RAX vs EAX vs AX vs AL)
- [ ] Incorrect calling convention
- [ ] Stack misalignment
- [ ] Signed vs unsigned comparison
- [ ] Endianness issues
- [ ] Buffer overflows

---

## Tool Summary

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **GDB** | Interactive debugging | Logic errors, crashes |
| **Objdump** | Disassembly | Understanding compiled code |
| **Strace** | Syscall tracing | File I/O, network issues |
| **Valgrind** | Memory debugging | Leaks, invalid accesses |
| **Readelf** | ELF analysis | Understanding binary structure |
| **Hexdump** | Binary viewing | Low-level data inspection |
| **Ltrace** | Library call tracing | Understanding library usage |
| **Perf** | Performance profiling | Finding bottlenecks |

---

## Practice Exercises

### Exercise 1: Fix the Bugs

Given a buggy assembly program, use GDB to find and fix:
1. Segmentation fault
2. Incorrect calculation
3. Memory leak

### Exercise 2: Reverse Engineering

Disassemble a simple program and determine:
1. What it does
2. Its input/output
3. Algorithm used

### Exercise 3: Performance Analysis

Use `perf` to profile a program and identify:
1. Hottest function
2. Cache miss rate
3. Branch misprediction rate

---

## Summary

### Essential Skills
1. **GDB proficiency** - Step through code, examine state
2. **Disassembly reading** - Understand compiler output
3. **Tool selection** - Right tool for the problem
4. **Systematic approach** - Reproduce, isolate, fix, verify

### Key Tools
- **GDB**: Interactive debugging
- **Strace**: System call tracing
- **Valgrind**: Memory debugging
- **Objdump**: Static analysis

### Debugging Mindset
1. Understand what the code *should* do
2. Observe what it *actually* does
3. Form hypotheses about the cause
4. Test hypotheses systematically
5. Fix root cause, not symptoms

### Resources
- GDB manual: `info gdb`
- Intel manuals: software.intel.com
- Linux syscall reference: man7.org
- Stack Overflow: assembly debugging questions

---

## Congratulations!

You've completed the comprehensive NASM x86-64 assembly programming tutorial! You now have the knowledge to:

- Write efficient assembly code
- Interface with C and operating systems
- Optimize for performance
- Debug complex low-level issues
- Understand how computers work at the lowest level

**Next steps:**
- Practice writing assembly programs
- Contribute to open-source projects
- Explore compiler output for your C code
- Study CPU architecture in depth
- Build your own tools and libraries

Happy hacking! 🚀

