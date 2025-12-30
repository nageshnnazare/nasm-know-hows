# Topic 16: Linux System Calls

## Overview

System calls (syscalls) are the interface between user-space programs and the kernel. They allow programs to request services from the operating system: file I/O, process management, memory allocation, network operations, and more.

```c
// C equivalent - syscalls are typically wrapped in libc functions:
#include <unistd.h>
#include <sys/syscall.h>

// High-level wrapper:
write(1, "Hello\n", 6);

// Low-level syscall:
syscall(SYS_write, 1, "Hello\n", 6);
```

---

## Syscall Mechanism

### How Syscalls Work

1. **User program** sets up syscall number and arguments in registers
2. **Executes** `syscall` instruction (64-bit) or `int 0x80` (32-bit)
3. **CPU switches** from user mode to kernel mode
4. **Kernel** validates parameters, performs the operation
5. **Return value** placed in RAX/EAX
6. **CPU switches** back to user mode
7. **Program continues** execution

```
User Space:         Kernel Space:
┌─────────────┐     ┌──────────────┐
│ Your Code   │     │              │
│             │     │   Kernel     │
│ syscall ────┼────>│   Handler    │
│             │     │              │
│ <───────────┼─────│  Returns     │
└─────────────┘     └──────────────┘
```

### 64-bit Linux Syscall Convention (x86-64)

```nasm
; C equivalent:
; ssize_t write(int fd, const void *buf, size_t count);
; syscall(SYS_write, fd, buf, count);

mov rax, 1              ; Syscall number (SYS_write)
mov rdi, fd             ; Argument 1: file descriptor
mov rsi, buffer         ; Argument 2: buffer address
mov rdx, count          ; Argument 3: byte count
syscall                 ; Execute syscall
; RAX now contains return value (bytes written, or -errno on error)
```

**Register Mapping:**

| Argument | Register | Notes |
|----------|----------|-------|
| Syscall # | RAX | Set before syscall |
| Arg 1 | RDI | |
| Arg 2 | RSI | |
| Arg 3 | RDX | |
| Arg 4 | R10 | (NOT RCX!) |
| Arg 5 | R8 | |
| Arg 6 | R9 | |
| Return | RAX | Positive = success, negative = -errno |

**Why R10 instead of RCX?** The `syscall` instruction uses RCX to save the return address (RIP), so R10 is used for the 4th argument instead.

### 32-bit Linux Syscall Convention (i386)

```nasm
; C equivalent:
; ssize_t write(int fd, const void *buf, size_t count);

mov eax, 4              ; Syscall number (sys_write = 4 in 32-bit)
mov ebx, fd             ; Argument 1
mov ecx, buffer         ; Argument 2
mov edx, count          ; Argument 3
int 0x80                ; Execute syscall (32-bit method)
; EAX contains return value
```

**Register Mapping (32-bit):**

| Argument | Register |
|----------|----------|
| Syscall # | EAX |
| Arg 1 | EBX |
| Arg 2 | ECX |
| Arg 3 | EDX |
| Arg 4 | ESI |
| Arg 5 | EDI |
| Arg 6 | EBP |
| Return | EAX |

---

## Common System Calls

### File I/O Syscalls

#### `read` - Read from File Descriptor

```nasm
; C equivalent:
; ssize_t read(int fd, void *buf, size_t count);

section .bss
    buffer resb 1024

section .text
    mov rax, 0              ; sys_read
    mov rdi, 0              ; stdin (fd = 0)
    lea rsi, [buffer]       ; Buffer address
    mov rdx, 1024           ; Max bytes to read
    syscall
    ; RAX = number of bytes read, or -1 on error
```

#### `write` - Write to File Descriptor

```nasm
; C equivalent:
; ssize_t write(int fd, const void *buf, size_t count);

section .data
    msg db "Hello, World!", 10     ; Message with newline
    msg_len equ $ - msg

section .text
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout (fd = 1)
    lea rsi, [msg]          ; Message address
    mov rdx, msg_len        ; Message length
    syscall
    ; RAX = number of bytes written
```

#### `open` - Open File

```nasm
; C equivalent:
; int open(const char *pathname, int flags, mode_t mode);
; // flags: O_RDONLY=0, O_WRONLY=1, O_RDWR=2, O_CREAT=64, O_TRUNC=512
; // mode: 0644 (rw-r--r--) = 0x1A4

section .data
    filename db "output.txt", 0
    
section .text
    mov rax, 2              ; sys_open
    lea rdi, [filename]     ; Pathname
    mov rsi, 0x41           ; O_WRONLY | O_CREAT (0x01 | 0x40)
    mov rdx, 0o644          ; Mode: rw-r--r--
    syscall
    ; RAX = file descriptor (or -1 on error)
```

**Common Flags:**

| Flag | Value | Description |
|------|-------|-------------|
| O_RDONLY | 0 | Read only |
| O_WRONLY | 1 | Write only |
| O_RDWR | 2 | Read and write |
| O_CREAT | 0x40 | Create file if doesn't exist |
| O_TRUNC | 0x200 | Truncate to 0 length |
| O_APPEND | 0x400 | Append mode |
| O_EXCL | 0x80 | Fail if file exists (with O_CREAT) |

#### `close` - Close File Descriptor

```nasm
; C equivalent:
; int close(int fd);

mov rax, 3              ; sys_close
mov rdi, [file_fd]      ; File descriptor to close
syscall
; RAX = 0 on success, -1 on error
```

### Complete File I/O Example

```nasm
section .data
    filename db "test.txt", 0
    content db "Hello from assembly!", 10
    content_len equ $ - content

section .bss
    fd resq 1               ; File descriptor

section .text
global _start

_start:
    ; C equivalent:
    ; int fd = open("test.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    ; if (fd < 0) exit(1);
    ; write(fd, content, content_len);
    ; close(fd);
    ; exit(0);
    
    ; Open file
    mov rax, 2              ; sys_open
    lea rdi, [filename]
    mov rsi, 0x241          ; O_WRONLY | O_CREAT | O_TRUNC
    mov rdx, 0o644
    syscall
    
    test rax, rax
    js error                ; Jump if negative (error)
    mov [fd], rax           ; Save fd
    
    ; Write to file
    mov rax, 1              ; sys_write
    mov rdi, [fd]
    lea rsi, [content]
    mov rdx, content_len
    syscall
    
    ; Close file
    mov rax, 3              ; sys_close
    mov rdi, [fd]
    syscall
    
    ; Exit success
    mov rax, 60             ; sys_exit
    xor rdi, rdi            ; Exit code 0
    syscall

error:
    mov rax, 60
    mov rdi, 1              ; Exit code 1
    syscall
```

---

## Process Management

### `exit` - Terminate Process

```nasm
; C equivalent:
; void exit(int status);

mov rax, 60             ; sys_exit
mov rdi, 0              ; Exit code (0 = success)
syscall
```

### `fork` - Create Child Process

```nasm
; C equivalent:
; pid_t fork(void);
; // Returns: 0 in child, child PID in parent, -1 on error

mov rax, 57             ; sys_fork
syscall

test rax, rax
jz child_code           ; RAX = 0, we're in child
js error                ; RAX < 0, error occurred
; RAX > 0, we're in parent, RAX = child PID

parent_code:
    ; Parent-specific code
    jmp done

child_code:
    ; Child-specific code
    
done:
    ; Continue...
```

### `execve` - Execute Program

```nasm
; C equivalent:
; int execve(const char *pathname, char *const argv[], char *const envp[]);

section .data
    prog db "/bin/ls", 0
    arg0 db "/bin/ls", 0
    arg1 db "-la", 0
    argv dq arg0, arg1, 0       ; NULL-terminated array
    envp dq 0                   ; Empty environment

section .text
    mov rax, 59             ; sys_execve
    lea rdi, [prog]         ; Program path
    lea rsi, [argv]         ; Arguments array
    lea rdx, [envp]         ; Environment array
    syscall
    ; If execve returns, it failed
```

### `wait4` - Wait for Process

```nasm
; C equivalent:
; pid_t wait4(pid_t pid, int *status, int options, struct rusage *rusage);

section .bss
    status resd 1

section .text
    mov rax, 61             ; sys_wait4
    mov rdi, -1             ; Wait for any child
    lea rsi, [status]       ; Status location
    xor rdx, rdx            ; Options = 0
    xor r10, r10            ; rusage = NULL
    syscall
    ; RAX = PID of terminated child
```

---

## Memory Management

### `brk` - Change Data Segment Size

```nasm
; C equivalent:
; int brk(void *addr);
; // Returns: 0 on success, -1 on error

mov rax, 12             ; sys_brk
mov rdi, 0              ; Query current break
syscall
; RAX = current program break (end of heap)

; Extend heap by 4096 bytes
add rax, 4096
mov rdi, rax
mov rax, 12
syscall
```

### `mmap` - Memory Mapping

```nasm
; C equivalent:
; void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
; // PROT_READ=1, PROT_WRITE=2, PROT_EXEC=4
; // MAP_PRIVATE=2, MAP_ANONYMOUS=0x20

mov rax, 9              ; sys_mmap
xor rdi, rdi            ; addr = NULL (kernel chooses)
mov rsi, 4096           ; length = 4096 bytes
mov rdx, 3              ; prot = PROT_READ | PROT_WRITE
mov r10, 0x22           ; flags = MAP_PRIVATE | MAP_ANONYMOUS
mov r8, -1              ; fd = -1 (not file-backed)
xor r9, r9              ; offset = 0
syscall
; RAX = address of mapped region, or -errno on error
```

### `munmap` - Unmap Memory

```nasm
; C equivalent:
; int munmap(void *addr, size_t length);

mov rax, 11             ; sys_munmap
mov rdi, [mapped_addr]  ; Address to unmap
mov rsi, 4096           ; Length
syscall
; RAX = 0 on success
```

---

## Time and Date

### `time` - Get Current Time

```nasm
; C equivalent:
; time_t time(time_t *tloc);

section .bss
    current_time resq 1

section .text
    mov rax, 201            ; sys_time
    lea rdi, [current_time] ; Output location (or 0 for RAX only)
    syscall
    ; RAX = seconds since epoch (1970-01-01 00:00:00 UTC)
```

### `clock_gettime` - High-Resolution Time

```nasm
; C equivalent:
; int clock_gettime(clockid_t clk_id, struct timespec *tp);
; // CLOCK_REALTIME = 0, CLOCK_MONOTONIC = 1

section .bss
    timespec:
        tv_sec resq 1       ; Seconds
        tv_nsec resq 1      ; Nanoseconds

section .text
    mov rax, 228            ; sys_clock_gettime
    mov rdi, 1              ; CLOCK_MONOTONIC
    lea rsi, [timespec]
    syscall
    ; RAX = 0 on success
```

### `nanosleep` - Sleep for Duration

```nasm
; C equivalent:
; int nanosleep(const struct timespec *req, struct timespec *rem);

section .data
    sleep_time:
        dq 1                ; 1 second
        dq 500000000        ; 500 million nanoseconds (0.5 sec)
                            ; Total: 1.5 seconds

section .text
    mov rax, 35             ; sys_nanosleep
    lea rdi, [sleep_time]   ; Requested time
    xor rsi, rsi            ; Remaining time (NULL)
    syscall
    ; RAX = 0 if completed, -1 if interrupted
```

---

## Process Information

### `getpid` - Get Process ID

```nasm
; C equivalent:
; pid_t getpid(void);

mov rax, 39             ; sys_getpid
syscall
; RAX = process ID
```

### `getuid` - Get User ID

```nasm
; C equivalent:
; uid_t getuid(void);

mov rax, 102            ; sys_getuid
syscall
; RAX = user ID
```

### `uname` - Get System Information

```nasm
; C equivalent:
; int uname(struct utsname *buf);

section .bss
    utsname:
        sysname resb 65
        nodename resb 65
        release resb 65
        version resb 65
        machine resb 65
        domainname resb 65

section .text
    mov rax, 63             ; sys_uname
    lea rdi, [utsname]
    syscall
    ; RAX = 0 on success
    ; utsname now contains: "Linux", hostname, kernel version, etc.
```

---

## Advanced I/O

### `ioctl` - Device Control

```nasm
; C equivalent:
; int ioctl(int fd, unsigned long request, ...);
; // Example: Get terminal size

section .bss
    winsize:
        ws_row resw 1
        ws_col resw 1
        ws_xpixel resw 1
        ws_ypixel resw 1

section .text
    mov rax, 16             ; sys_ioctl
    mov rdi, 1              ; stdout
    mov rsi, 0x5413         ; TIOCGWINSZ (get window size)
    lea rdx, [winsize]
    syscall
    ; winsize.ws_row and ws_col now contain terminal dimensions
```

### `select` - I/O Multiplexing

```nasm
; C equivalent:
; int select(int nfds, fd_set *readfds, fd_set *writefds,
;            fd_set *exceptfds, struct timeval *timeout);

section .bss
    readfds resb 128        ; fd_set structure

section .data
    timeout:
        dq 5                ; 5 seconds
        dq 0                ; 0 microseconds

section .text
    ; Setup: FD_ZERO and FD_SET for stdin (fd 0)
    lea rdi, [readfds]
    mov rcx, 16             ; 128 bytes / 8
    xor rax, rax
    rep stosq               ; Zero out fd_set
    
    mov byte [readfds], 1   ; Set bit 0 (stdin)
    
    ; Call select
    mov rax, 23             ; sys_select
    mov rdi, 1              ; nfds = highest fd + 1
    lea rsi, [readfds]      ; read fds
    xor rdx, rdx            ; write fds = NULL
    xor r10, r10            ; except fds = NULL
    lea r8, [timeout]       ; timeout
    syscall
    ; RAX = number of ready fds, 0 = timeout, -1 = error
```

---

## Practical Example: Echo Server Skeleton

```nasm
section .data
    bind_addr:
        sa_family dw 2          ; AF_INET
        sa_port dw 0x5000       ; Port 80 (network byte order)
        sa_addr dd 0            ; INADDR_ANY
        sa_zero times 8 db 0
    
    backlog equ 5

section .bss
    sockfd resq 1
    clientfd resq 1
    buffer resb 1024

section .text
global _start

_start:
    ; C equivalent:
    ; int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    ; bind(sockfd, (struct sockaddr*)&bind_addr, sizeof(bind_addr));
    ; listen(sockfd, backlog);
    ; while (1) {
    ;     int clientfd = accept(sockfd, NULL, NULL);
    ;     // Read and echo data
    ;     close(clientfd);
    ; }
    
    ; Create socket
    mov rax, 41             ; sys_socket
    mov rdi, 2              ; AF_INET
    mov rsi, 1              ; SOCK_STREAM
    xor rdx, rdx            ; protocol = 0
    syscall
    test rax, rax
    js exit_error
    mov [sockfd], rax
    
    ; Bind
    mov rax, 49             ; sys_bind
    mov rdi, [sockfd]
    lea rsi, [bind_addr]
    mov rdx, 16             ; addrlen
    syscall
    test rax, rax
    js exit_error
    
    ; Listen
    mov rax, 50             ; sys_listen
    mov rdi, [sockfd]
    mov rsi, backlog
    syscall
    test rax, rax
    js exit_error
    
accept_loop:
    ; Accept
    mov rax, 43             ; sys_accept
    mov rdi, [sockfd]
    xor rsi, rsi            ; addr = NULL
    xor rdx, rdx            ; addrlen = NULL
    syscall
    test rax, rax
    js accept_loop          ; Ignore errors, continue
    mov [clientfd], rax
    
    ; Read from client
    mov rax, 0              ; sys_read
    mov rdi, [clientfd]
    lea rsi, [buffer]
    mov rdx, 1024
    syscall
    test rax, rax
    jle close_client        ; EOF or error
    mov r12, rax            ; Save bytes read
    
    ; Echo back
    mov rax, 1              ; sys_write
    mov rdi, [clientfd]
    lea rsi, [buffer]
    mov rdx, r12            ; Bytes to write
    syscall
    
close_client:
    ; Close client connection
    mov rax, 3              ; sys_close
    mov rdi, [clientfd]
    syscall
    
    jmp accept_loop
    
exit_error:
    mov rax, 60
    mov rdi, 1
    syscall
```

---

## Error Handling

Syscalls return negative errno values on error in RAX.

```nasm
; C equivalent:
; int fd = open("file.txt", O_RDONLY);
; if (fd < 0) {
;     // Handle error
;     if (errno == ENOENT) { /* file not found */ }
; }

mov rax, 2              ; sys_open
lea rdi, [filename]
mov rsi, 0              ; O_RDONLY
syscall

test rax, rax
js handle_error         ; Jump if negative (error)

; Success path
mov [fd], rax
jmp continue

handle_error:
    neg rax             ; Make positive (errno value)
    cmp rax, 2          ; ENOENT = 2 (file not found)
    je file_not_found
    cmp rax, 13         ; EACCES = 13 (permission denied)
    je permission_denied
    ; ... other error cases
```

**Common Error Codes:**

| Code | Name | Description |
|------|------|-------------|
| 1 | EPERM | Operation not permitted |
| 2 | ENOENT | No such file or directory |
| 9 | EBADF | Bad file descriptor |
| 11 | EAGAIN | Resource temporarily unavailable |
| 12 | ENOMEM | Out of memory |
| 13 | EACCES | Permission denied |
| 14 | EFAULT | Bad address |
| 22 | EINVAL | Invalid argument |
| 32 | EPIPE | Broken pipe |

---

## Performance Considerations

### Syscall Overhead

- **Context switch**: ~100-1000 cycles (user → kernel → user)
- **Validation**: Kernel must validate all parameters
- **Batching**: Combine operations when possible

```nasm
; C equivalent:
; // SLOW: Many syscalls
; for (int i = 0; i < 1000; ++i) {
;     write(fd, &data[i], 1);  // 1000 syscalls!
; }
;
; // FAST: Single syscall
; write(fd, data, 1000);  // 1 syscall

; Bad: 1000 separate write syscalls
mov rcx, 1000
write_loop:
    mov rax, 1
    mov rdi, [fd]
    lea rsi, [data + rcx - 1]
    mov rdx, 1
    syscall
    loop write_loop

; Good: Single write
mov rax, 1
mov rdi, [fd]
lea rsi, [data]
mov rdx, 1000
syscall
```

### Avoiding Syscalls

Use buffering and batch operations:

```nasm
; C equivalent:
; // Use buffered I/O
; FILE *f = fopen("file.txt", "w");
; for (int i = 0; i < 1000; ++i) {
;     fprintf(f, "%d\n", i);  // Buffered internally
; }
; fclose(f);  // Flush buffer

section .bss
    buffer resb 4096
    buf_pos resq 1

section .text
    ; Write to buffer, flush only when full
    ; (Implementation omitted for brevity)
```

---

## Summary

### Key Concepts
1. **Syscalls** are the interface to the kernel
2. Use **`syscall`** instruction (64-bit) or **`int 0x80`** (32-bit)
3. Arguments passed in **registers** (RAX, RDI, RSI, RDX, R10, R8, R9)
4. Return value in **RAX** (negative = error)
5. Syscalls are **expensive** - minimize when possible

### Common Syscalls
- **File I/O**: read (0), write (1), open (2), close (3)
- **Process**: exit (60), fork (57), execve (59), wait4 (61)
- **Memory**: brk (12), mmap (9), munmap (11)
- **Time**: time (201), clock_gettime (228), nanosleep (35)
- **Network**: socket (41), bind (49), listen (50), accept (43)

### Best Practices
1. Always check return values for errors
2. Use appropriate flags and permissions
3. Close file descriptors when done
4. Batch operations to reduce syscall count
5. Handle interrupted syscalls (EINTR)

---

## Practice Exercises

### Exercise 1: Cat Command

Implement a simple `cat` program that reads a file and writes to stdout.

### Exercise 2: Copy Command

Implement `cp` that copies one file to another.

### Exercise 3: Process Information

Write a program that prints its PID, UID, and current time.

---

## Next Topic

In **Topic 17: Interfacing with C**, we'll learn how to call assembly from C and vice versa, link with C libraries, and use C's standard library functions from assembly.

**Preview:**
- Calling conventions review
- Linking with C code
- Using libc functions
- Creating reusable assembly libraries
- Inline assembly in C

