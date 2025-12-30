# Linux x86-64 Syscall Reference

Complete reference for Linux system calls in 64-bit assembly.

---

## **Quick Reference: Syscall Registers**

### **Register Usage (System V AMD64 ABI)**

```
┌─────────────┬──────────────────────────────────┐
│ Register    │ Purpose                          │
├─────────────┼──────────────────────────────────┤
│ RAX         │ Syscall number (input)           │
│             │ Return value (output)            │
├─────────────┼──────────────────────────────────┤
│ RDI         │ 1st argument                     │
│ RSI         │ 2nd argument                     │
│ RDX         │ 3rd argument                     │
│ R10         │ 4th argument (not RCX!)          │
│ R8          │ 5th argument                     │
│ R9          │ 6th argument                     │
├─────────────┼──────────────────────────────────┤
│ RCX, R11    │ Destroyed by syscall             │
└─────────────┴──────────────────────────────────┘

Note: R10 is used instead of RCX because syscall uses RCX internally!
```

### **Basic Syscall Template**

```nasm
mov rax, <syscall_number>   ; Syscall number
mov rdi, <arg1>             ; 1st argument
mov rsi, <arg2>             ; 2nd argument
mov rdx, <arg3>             ; 3rd argument
; mov r10, <arg4>           ; 4th argument (if needed)
; mov r8, <arg5>            ; 5th argument (if needed)
; mov r9, <arg6>            ; 6th argument (if needed)
syscall                     ; Make the call

; RAX now contains return value (or negative error code)
```

---

## **Detailed Syscall Argument Table**

### **File I/O Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│   0    │ read    │ 0               │ int fd          │ void *buf       │ size_t count    │ -           │ -           │
│   1    │ write   │ 1               │ int fd          │ void *buf       │ size_t count    │ -           │ -           │
│   2    │ open    │ 2               │ char *pathname  │ int flags       │ mode_t mode     │ -           │ -           │
│   3    │ close   │ 3               │ int fd          │ -               │ -               │ -           │ -           │
│   4    │ stat    │ 4               │ char *pathname  │ struct stat *buf│ -               │ -           │ -           │
│   5    │ fstat   │ 5               │ int fd          │ struct stat *buf│ -               │ -           │ -           │
│   8    │ lseek   │ 8               │ int fd          │ off_t offset    │ int whence      │ -           │ -           │
│  16    │ ioctl   │ 16              │ int fd          │unsigned long req│unsigned long arg│ -           │ -           │
│  17    │ pread64 │ 17              │ int fd          │ void *buf       │ size_t count    │ off_t offset│ -           │
│  18    │ pwrite64│ 18              │ int fd          │ void *buf       │ size_t count    │ off_t offset│ -           │
│  32    │ dup     │ 32              │ int oldfd       │ -               │ -               │ -           │ -           │
│  33    │ dup2    │ 33              │ int oldfd       │ int newfd       │ -               │ -           │ -           │
│  72    │ fcntl   │ 72              │ int fd          │ int cmd         │unsigned long arg│ -           │ -           │
│  73    │ flock   │ 73              │ int fd          │ int operation   │ -               │ -           │ -           │
│  74    │ fsync   │ 74              │ int fd          │ -               │ -               │ -           │ -           │
│  76    │ truncate│ 76              │ char *path      │ off_t length    │ -               │ -           │ -           │
│  77    │ ftruncate│77              │ int fd          │ off_t length    │ -               │ -           │ -           │
│  85    │ creat   │ 85              │ char *pathname  │ mode_t mode     │ -               │ -           │ -           │
│  86    │ link    │ 86              │ char *oldpath   │ char *newpath   │ -               │ -           │ -           │
│  87    │ unlink  │ 87              │ char *pathname  │ -               │ -               │ -           │ -           │
│  88    │ symlink │ 88              │ char *target    │ char *linkpath  │ -               │ -           │ -           │
│  89    │ readlink│ 89              │ char *pathname  │ char *buf       │ size_t bufsiz   │ -           │ -           │
│  90    │ chmod   │ 90              │ char *pathname  │ mode_t mode     │ -               │ -           │ -           │
│  92    │ chown   │ 92              │ char *pathname  │ uid_t owner     │ gid_t group     │ -           │ -           │
│  95    │ umask   │ 95              │ mode_t mask     │ -               │ -               │ -           │ -           │
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘
```

### **Process Management Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│  57    │ fork    │ 57              │ -               │ -               │ -               │ -           │ -           │
│  58    │ vfork   │ 58              │ -               │ -               │ -               │ -           │ -           │
│  59    │ execve  │ 59              │ char *pathname  │ char **argv     │ char **envp     │ -           │ -           │
│  60    │ exit    │ 60              │ int status      │ -               │ -               │ -           │ -           │
│  61    │ wait4   │ 61              │ pid_t pid       │ int *status     │ int options     │ rusage *ru  │ -           │
│  62    │ kill    │ 62              │ pid_t pid       │ int sig         │ -               │ -           │ -           │
│ 102    │ getuid  │ 102             │ -               │ -               │ -               │ -           │ -           │
│ 104    │ getgid  │ 104             │ -               │ -               │ -               │ -           │ -           │
│ 105    │ setuid  │ 105             │ uid_t uid       │ -               │ -               │ -           │ -           │
│ 106    │ setgid  │ 106             │ gid_t gid       │ -               │ -               │ -           │ -           │
│ 107    │ geteuid │ 107             │ -               │ -               │ -               │ -           │ -           │
│ 108    │ getegid │ 108             │ -               │ -               │ -               │ -           │ -           │
│ 110    │ getppid │ 110             │ -               │ -               │ -               │ -           │ -           │
│ 111    │ getpgrp │ 111             │ -               │ -               │ -               │ -           │ -           │
│ 186    │ gettid  │ 186             │ -               │ -               │ -               │ -           │ -           │
│ 231    │ exit_group│231            │ int status      │ -               │ -               │ -           │ -           │
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘
```

### **Memory Management Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│   9    │ mmap    │ 9               │ void *addr      │ size_t length   │ int prot        │ int flags   │ int fd      │
│  10    │ mprotect│ 10              │ void *addr      │ size_t len      │ int prot        │ -           │ -           │
│  11    │ munmap  │ 11              │ void *addr      │ size_t length   │ -               │ -           │ -           │
│  12    │ brk     │ 12              │ void *addr      │ -               │ -               │ -           │ -           │
│  25    │ mremap  │ 25              │ void *old_addr  │ size_t old_size │ size_t new_size │ int flags   │void *new_addr│
│  26    │ msync   │ 26              │ void *addr      │ size_t length   │ int flags       │ -           │ -           │
│  28    │ madvise │ 28              │ void *addr      │ size_t length   │ int advice      │ -           │ -           │
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘

Note: mmap has a 6th argument - R9 (arg6) = off_t offset
```

### **Time and Timer Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│  35    │ nanosleep│35              │ timespec *req   │ timespec *rem   │ -               │ -           │ -           │
│ 201    │ time    │ 201             │ time_t *tloc    │ -               │ -               │ -           │ -           │
│ 228    │ clock_gettime│228         │ clockid_t clk_id│ timespec *tp    │ -               │ -           │ -           │
│ 229    │ clock_settime│229         │ clockid_t clk_id│ timespec *tp    │ -               │ -           │ -           │
│ 230    │ clock_getres│230          │ clockid_t clk_id│ timespec *res   │ -               │ -           │ -           │
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘
```

### **Directory and Path Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│  79    │ getcwd  │ 79              │ char *buf       │ size_t size     │ -               │ -           │ -           │
│  80    │ chdir   │ 80              │ char *path      │ -               │ -               │ -           │ -           │
│  81    │ fchdir  │ 81              │ int fd          │ -               │ -               │ -           │ -           │
│  82    │ rename  │ 82              │ char *oldpath   │ char *newpath   │ -               │ -           │ -           │
│  83    │ mkdir   │ 83              │ char *pathname  │ mode_t mode     │ -               │ -           │ -           │
│  84    │ rmdir   │ 84              │ char *pathname  │ -               │ -               │ -           │ -           │
│ 161    │ chroot  │ 161             │ char *path      │ -               │ -               │ -           │ -           │
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘
```

### **Socket/Network Syscalls**

```
┌────────┬─────────┬─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────────┬─────────────┐
│ Number │ Syscall │ RAX             │ RDI (arg1)      │ RSI (arg2)      │ RDX (arg3)      │ R10 (arg4)  │ R8 (arg5)   │
├────────┼─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┼─────────────┤
│  41    │ socket  │ 41              │ int domain      │ int type        │ int protocol    │ -           │ -           │
│  42    │ connect │ 42              │ int sockfd      │ sockaddr *addr  │ socklen_t addrlen│ -          │ -           │
│  43    │ accept  │ 43              │ int sockfd      │ sockaddr *addr  │ socklen_t *addrlen│ -         │ -           │
│  44    │ sendto  │ 44              │ int sockfd      │ void *buf       │ size_t len      │ int flags   │ sockaddr *dst│
│  45    │ recvfrom│ 45              │ int sockfd      │ void *buf       │ size_t len      │ int flags   │ sockaddr *src│
│  46    │ sendmsg │ 46              │ int sockfd      │ msghdr *msg     │ int flags       │ -           │ -           │
│  47    │ recvmsg │ 47              │ int sockfd      │ msghdr *msg     │ int flags       │ -           │ -           │
│  48    │ shutdown│ 48              │ int sockfd      │ int how         │ -               │ -           │ -           │
│  49    │ bind    │ 49              │ int sockfd      │ sockaddr *addr  │ socklen_t addrlen│ -          │ -           │
│  50    │ listen  │ 50              │ int sockfd      │ int backlog     │ -               │ -           │ -           │
│  54    │ setsockopt│54             │ int sockfd      │ int level       │ int optname     │ void *optval│ socklen_t len│
│  55    │ getsockopt│55             │ int sockfd      │ int level       │ int optname     │ void *optval│ socklen_t *len│
└────────┴─────────┴─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────────┴─────────────┘

Note: sendto/recvfrom have 6th argument - R9 (arg6) = socklen_t addrlen (for sendto)
```

---

## **Common File I/O Syscalls**

### **read (0)** - Read from file descriptor

```nasm
; ssize_t read(int fd, void *buf, size_t count)
mov rax, 0              ; syscall number: read
mov rdi, <fd>           ; file descriptor (0 = stdin)
mov rsi, <buffer>       ; pointer to buffer
mov rdx, <count>        ; number of bytes to read
syscall
; RAX = number of bytes read, or -1 on error
```

**Example:**
```nasm
section .bss
    buffer resb 64

section .text
    mov rax, 0          ; sys_read
    mov rdi, 0          ; stdin
    mov rsi, buffer     ; buffer address
    mov rdx, 64         ; read up to 64 bytes
    syscall
    ; RAX contains bytes read
```

---

### **write (1)** - Write to file descriptor

```nasm
; ssize_t write(int fd, const void *buf, size_t count)
mov rax, 1              ; syscall number: write
mov rdi, <fd>           ; file descriptor (1 = stdout, 2 = stderr)
mov rsi, <buffer>       ; pointer to data
mov rdx, <count>        ; number of bytes to write
syscall
; RAX = number of bytes written, or -1 on error
```

**Example:**
```nasm
section .data
    msg db "Hello, World!", 10

section .text
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg        ; message address
    mov rdx, 14         ; message length
    syscall
    ; RAX contains bytes written
```

---

### **open (2)** - Open file

```nasm
; int open(const char *pathname, int flags, mode_t mode)
mov rax, 2              ; syscall number: open
mov rdi, <filename>     ; pointer to filename string
mov rsi, <flags>        ; flags (O_RDONLY=0, O_WRONLY=1, O_RDWR=2, etc.)
mov rdx, <mode>         ; permissions (e.g., 0644)
syscall
; RAX = file descriptor, or -1 on error
```

**Common flags:**
- O_RDONLY = 0
- O_WRONLY = 1
- O_RDWR = 2
- O_CREAT = 64 (0x40)
- O_TRUNC = 512 (0x200)
- O_APPEND = 1024 (0x400)

**Example:**
```nasm
section .data
    filename db "output.txt", 0

section .text
    mov rax, 2          ; sys_open
    mov rdi, filename   ; filename
    mov rsi, 577        ; O_CREAT | O_WRONLY | O_TRUNC (64+1+512)
    mov rdx, 0644o      ; permissions: rw-r--r--
    syscall
    ; RAX = file descriptor
```

---

### **close (3)** - Close file descriptor

```nasm
; int close(int fd)
mov rax, 3              ; syscall number: close
mov rdi, <fd>           ; file descriptor to close
syscall
; RAX = 0 on success, -1 on error
```

**Example:**
```nasm
    mov rax, 3          ; sys_close
    mov rdi, [file_fd]  ; file descriptor
    syscall
```

---

## **Process Management Syscalls**

### **exit (60)** - Terminate process

```nasm
; void exit(int status)
mov rax, 60             ; syscall number: exit
mov rdi, <exit_code>    ; exit status (0 = success)
syscall
; Does not return!
```

**Example:**
```nasm
    mov rax, 60         ; sys_exit
    xor rdi, rdi        ; exit code 0 (success)
    syscall
```

---

### **fork (57)** - Create child process

```nasm
; pid_t fork(void)
mov rax, 57             ; syscall number: fork
syscall
; RAX = 0 in child, child PID in parent, -1 on error
```

**Example:**
```nasm
    mov rax, 57         ; sys_fork
    syscall
    test rax, rax
    jz child_process    ; RAX = 0 in child
    ; Parent process (RAX = child PID)
    jmp parent_process
child_process:
    ; Child code here
```

---

### **execve (59)** - Execute program

```nasm
; int execve(const char *pathname, char *const argv[], char *const envp[])
mov rax, 59             ; syscall number: execve
mov rdi, <pathname>     ; program path
mov rsi, <argv>         ; argument array
mov rdx, <envp>         ; environment array
syscall
; Does not return on success, returns -1 on error
```

---

### **wait4 (61)** - Wait for process

```nasm
; pid_t wait4(pid_t pid, int *status, int options, struct rusage *rusage)
mov rax, 61             ; syscall number: wait4
mov rdi, <pid>          ; PID to wait for (-1 = any child)
mov rsi, <status_ptr>   ; pointer to status variable
mov rdx, <options>      ; options (0 = block until exit)
mov r10, <rusage_ptr>   ; resource usage (NULL = don't care)
syscall
; RAX = PID of exited child, -1 on error
```

---

## **Memory Management Syscalls**

### **brk (12)** - Change data segment size

```nasm
; int brk(void *addr)
mov rax, 12             ; syscall number: brk
mov rdi, <new_break>    ; new program break address (0 = query)
syscall
; RAX = new program break address
```

---

### **mmap (9)** - Map memory

```nasm
; void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)
mov rax, 9              ; syscall number: mmap
mov rdi, <addr>         ; address hint (0 = kernel chooses)
mov rsi, <length>       ; length in bytes
mov rdx, <prot>         ; protection (PROT_READ=1, PROT_WRITE=2, PROT_EXEC=4)
mov r10, <flags>        ; flags (MAP_PRIVATE=2, MAP_ANONYMOUS=32)
mov r8, <fd>            ; file descriptor (-1 for anonymous)
mov r9, <offset>        ; offset in file
syscall
; RAX = address of mapped region, or -1 on error
```

**Example: Allocate anonymous memory**
```nasm
    mov rax, 9          ; sys_mmap
    xor rdi, rdi        ; addr = 0 (kernel chooses)
    mov rsi, 4096       ; length = 4096 bytes (1 page)
    mov rdx, 3          ; prot = PROT_READ | PROT_WRITE
    mov r10, 34         ; flags = MAP_PRIVATE | MAP_ANONYMOUS
    mov r8, -1          ; fd = -1 (no file)
    xor r9, r9          ; offset = 0
    syscall
    ; RAX = address of allocated memory
```

---

### **munmap (11)** - Unmap memory

```nasm
; int munmap(void *addr, size_t length)
mov rax, 11             ; syscall number: munmap
mov rdi, <addr>         ; address of mapped region
mov rsi, <length>       ; length in bytes
syscall
; RAX = 0 on success, -1 on error
```

---

## **Time and Sleep Syscalls**

### **nanosleep (35)** - Sleep for specified time

```nasm
; int nanosleep(const struct timespec *req, struct timespec *rem)
mov rax, 35             ; syscall number: nanosleep
mov rdi, <timespec_ptr> ; pointer to timespec structure
mov rsi, <remaining_ptr>; pointer to remaining time (or NULL)
syscall
; RAX = 0 on success, -1 on error
```

**Timespec structure:**
```nasm
section .data
    timespec:
        dq 1            ; seconds
        dq 500000000    ; nanoseconds (0.5 seconds)
```

**Example: Sleep for 1 second**
```nasm
section .data
    sleep_time:
        dq 1            ; 1 second
        dq 0            ; 0 nanoseconds

section .text
    mov rax, 35         ; sys_nanosleep
    mov rdi, sleep_time ; timespec pointer
    xor rsi, rsi        ; don't care about remaining time
    syscall
```

---

### **time (201)** - Get current time

```nasm
; time_t time(time_t *tloc)
mov rax, 201            ; syscall number: time
mov rdi, <time_ptr>     ; pointer to store time (or NULL)
syscall
; RAX = seconds since epoch (Jan 1, 1970)
```

---

## **Directory and File System Syscalls**

### **getcwd (79)** - Get current working directory

```nasm
; char *getcwd(char *buf, size_t size)
mov rax, 79             ; syscall number: getcwd
mov rdi, <buffer>       ; buffer to store path
mov rsi, <size>         ; size of buffer
syscall
; RAX = pointer to buffer on success, -1 on error
```

---

### **chdir (80)** - Change directory

```nasm
; int chdir(const char *path)
mov rax, 80             ; syscall number: chdir
mov rdi, <path>         ; path to new directory
syscall
; RAX = 0 on success, -1 on error
```

---

### **mkdir (83)** - Create directory

```nasm
; int mkdir(const char *pathname, mode_t mode)
mov rax, 83             ; syscall number: mkdir
mov rdi, <pathname>     ; directory path
mov rsi, <mode>         ; permissions (e.g., 0755)
syscall
; RAX = 0 on success, -1 on error
```

---

### **rmdir (84)** - Remove directory

```nasm
; int rmdir(const char *pathname)
mov rax, 84             ; syscall number: rmdir
mov rdi, <pathname>     ; directory path
syscall
; RAX = 0 on success, -1 on error
```

---

### **unlink (87)** - Delete file

```nasm
; int unlink(const char *pathname)
mov rax, 87             ; syscall number: unlink
mov rdi, <pathname>     ; file path
syscall
; RAX = 0 on success, -1 on error
```

---

## **Complete Syscall Number Reference**

### **File Operations**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│   0    │ read    - Read from file descriptor            │
│   1    │ write   - Write to file descriptor             │
│   2    │ open    - Open file                            │
│   3    │ close   - Close file descriptor                │
│   4    │ stat    - Get file status                      │
│   5    │ fstat   - Get file status by fd                │
│   6    │ lstat   - Get file status (no follow symlink)  │
│   8    │ lseek   - Reposition file offset               │
│  16    │ ioctl   - Control device                       │
│  17    │ pread64 - Read from fd at offset               │
│  18    │ pwrite64- Write to fd at offset                │
│  19    │ readv   - Read into multiple buffers           │
│  20    │ writev  - Write from multiple buffers          │
│  32    │ dup     - Duplicate file descriptor            │
│  33    │ dup2    - Duplicate fd to specific number      │
│  72    │ fcntl   - File control                         │
│  73    │ flock   - File locking                         │
│  74    │ fsync   - Synchronize file state               │
│  75    │ fdatasync - Sync file data                     │
│  76    │ truncate - Truncate file to length             │
│  77    │ ftruncate - Truncate file by fd                │
│  78    │ getdents - Get directory entries               │
│  85    │ creat   - Create file                          │
│  86    │ link    - Make hard link                       │
│  87    │ unlink  - Delete file                          │
│  88    │ symlink - Make symbolic link                   │
│  89    │ readlink - Read symbolic link                  │
│  90    │ chmod   - Change file permissions              │
│  91    │ fchmod  - Change file permissions by fd        │
│  92    │ chown   - Change file owner                    │
│  93    │ fchown  - Change file owner by fd              │
│  94    │ lchown  - Change file owner (no follow)        │
│  95    │ umask   - Set file creation mask               │
└────────┴─────────────────────────────────────────────────┘
```

### **Process Control**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│  57    │ fork    - Create child process                 │
│  58    │ vfork   - Create child (share memory)          │
│  59    │ execve  - Execute program                      │
│  60    │ exit    - Terminate process                    │
│  61    │ wait4   - Wait for process                     │
│  62    │ kill    - Send signal                          │
│  96    │ getpriority - Get scheduling priority          │
│  97    │ setpriority - Set scheduling priority          │
│ 102    │ getuid  - Get user ID                          │
│ 104    │ getgid  - Get group ID                         │
│ 105    │ setuid  - Set user ID                          │
│ 106    │ setgid  - Set group ID                         │
│ 107    │ geteuid - Get effective user ID                │
│ 108    │ getegid - Get effective group ID               │
│ 110    │ getppid - Get parent process ID                │
│ 111    │ getpgrp - Get process group                    │
│ 186    │ gettid  - Get thread ID                        │
│ 231    │ exit_group - Exit all threads                  │
└────────┴─────────────────────────────────────────────────┘
```

### **Memory Management**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│   9    │ mmap    - Map memory                           │
│  10    │ mprotect - Set memory protection               │
│  11    │ munmap  - Unmap memory                         │
│  12    │ brk     - Change data segment size             │
│  25    │ mremap  - Remap memory                         │
│  26    │ msync   - Synchronize memory with storage      │
│  27    │ mincore - Determine if pages are in memory     │
│  28    │ madvise - Give advice about memory usage       │
│  29    │ shmget  - Get shared memory segment            │
│  30    │ shmat   - Attach shared memory                 │
│  31    │ shmctl  - Shared memory control                │
└────────┴─────────────────────────────────────────────────┘
```

### **Signals**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│  13    │ rt_sigaction - Set signal action               │
│  14    │ rt_sigprocmask - Set signal mask               │
│  15    │ rt_sigreturn - Return from signal              │
│  34    │ pause   - Wait for signal                      │
│  62    │ kill    - Send signal to process               │
│ 127    │ rt_sigpending - Get pending signals            │
│ 128    │ rt_sigtimedwait - Wait for signal with timeout │
│ 129    │ rt_sigqueueinfo - Queue signal                 │
│ 130    │ rt_sigsuspend - Wait for signal                │
└────────┴─────────────────────────────────────────────────┘
```

### **Time and Timer**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│  35    │ nanosleep - High-resolution sleep              │
│  96    │ gettimeofday - Get time (deprecated)           │
│ 163    │ settimeofday - Set time (deprecated)           │
│ 201    │ time    - Get current time                     │
│ 228    │ clock_gettime - Get time from clock            │
│ 229    │ clock_settime - Set time for clock             │
│ 230    │ clock_getres - Get clock resolution            │
│ 222    │ timer_create - Create timer                    │
│ 223    │ timer_settime - Set timer                      │
│ 224    │ timer_gettime - Get timer                      │
│ 226    │ timer_delete - Delete timer                    │
└────────┴─────────────────────────────────────────────────┘
```

### **Directories**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│  79    │ getcwd  - Get current directory                │
│  80    │ chdir   - Change directory                     │
│  81    │ fchdir  - Change directory by fd               │
│  82    │ rename  - Rename file                          │
│  83    │ mkdir   - Create directory                     │
│  84    │ rmdir   - Remove directory                     │
│ 161    │ chroot  - Change root directory                │
└────────┴─────────────────────────────────────────────────┘
```

### **Networking (Socket)**
```
┌────────┬─────────────────────────────────────────────────┐
│ Number │ Syscall                                         │
├────────┼─────────────────────────────────────────────────┤
│  41    │ socket  - Create socket                        │
│  42    │ connect - Connect socket                       │
│  43    │ accept  - Accept connection                    │
│  44    │ sendto  - Send message                         │
│  45    │ recvfrom - Receive message                     │
│  46    │ sendmsg - Send message (advanced)              │
│  47    │ recvmsg - Receive message (advanced)           │
│  48    │ shutdown - Shut down socket                    │
│  49    │ bind    - Bind socket to address               │
│  50    │ listen  - Listen for connections               │
│  51    │ getsockname - Get socket name                  │
│  52    │ getpeername - Get peer name                    │
│  53    │ socketpair - Create socket pair                │
│  54    │ setsockopt - Set socket options                │
│  55    │ getsockopt - Get socket options                │
└────────┴─────────────────────────────────────────────────┘
```

---

## **Error Handling**

Syscalls return:
- **Positive value or zero**: Success (meaning depends on syscall)
- **Negative value**: Error (negate to get errno)

### **Common Error Codes**

```
┌───────┬─────────┬──────────────────────────────────────┐
│ Code  │ Name    │ Description                          │
├───────┼─────────┼──────────────────────────────────────┤
│  -1   │ EPERM   │ Operation not permitted              │
│  -2   │ ENOENT  │ No such file or directory            │
│  -3   │ ESRCH   │ No such process                      │
│  -4   │ EINTR   │ Interrupted system call              │
│  -5   │ EIO     │ I/O error                            │
│  -9   │ EBADF   │ Bad file descriptor                  │
│ -11   │ EAGAIN  │ Try again                            │
│ -12   │ ENOMEM  │ Out of memory                        │
│ -13   │ EACCES  │ Permission denied                    │
│ -14   │ EFAULT  │ Bad address                          │
│ -17   │ EEXIST  │ File exists                          │
│ -20   │ ENOTDIR │ Not a directory                      │
│ -21   │ EISDIR  │ Is a directory                       │
│ -22   │ EINVAL  │ Invalid argument                     │
│ -24   │ EMFILE  │ Too many open files                  │
│ -28   │ ENOSPC  │ No space left on device              │
│ -30   │ EROFS   │ Read-only file system                │
│ -32   │ EPIPE   │ Broken pipe                          │
└───────┴─────────┴──────────────────────────────────────┘
```

### **Checking for Errors**

```nasm
    mov rax, 2              ; sys_open
    mov rdi, filename
    mov rsi, 0              ; O_RDONLY
    syscall
    
    ; Check for error
    test rax, rax
    js error_handler        ; Jump if negative (sign flag set)
    
    ; Success - RAX contains file descriptor
    mov [file_fd], rax
    jmp continue
    
error_handler:
    ; RAX contains negative error code
    neg rax                 ; Convert to positive errno
    ; Handle error...
    
continue:
```

---

## **Practical Examples**

### **Example 1: Print String to stdout**

```nasm
section .data
    message db "Hello, World!", 10
    msg_len equ $ - message

section .text
    global _start

_start:
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    mov rsi, message        ; buffer
    mov rdx, msg_len        ; length
    syscall
    
    mov rax, 60             ; sys_exit
    xor rdi, rdi            ; exit code 0
    syscall
```

### **Example 2: Read from stdin**

```nasm
section .bss
    buffer resb 100

section .text
    mov rax, 0              ; sys_read
    mov rdi, 0              ; stdin
    mov rsi, buffer         ; buffer
    mov rdx, 100            ; max bytes
    syscall
    ; RAX = bytes read
```

### **Example 3: Open, Write, Close File**

```nasm
section .data
    filename db "output.txt", 0
    content db "File content here", 10
    content_len equ $ - content

section .bss
    fd resq 1

section .text
    ; Open file
    mov rax, 2              ; sys_open
    mov rdi, filename
    mov rsi, 577            ; O_CREAT | O_WRONLY | O_TRUNC
    mov rdx, 0644o          ; permissions
    syscall
    mov [fd], rax           ; Save file descriptor
    
    ; Write to file
    mov rax, 1              ; sys_write
    mov rdi, [fd]           ; file descriptor
    mov rsi, content
    mov rdx, content_len
    syscall
    
    ; Close file
    mov rax, 3              ; sys_close
    mov rdi, [fd]
    syscall
```

### **Example 4: Allocate Memory with mmap**

```nasm
    ; Allocate 4KB of memory
    mov rax, 9              ; sys_mmap
    xor rdi, rdi            ; addr = NULL (kernel chooses)
    mov rsi, 4096           ; length = 4096
    mov rdx, 3              ; prot = READ | WRITE
    mov r10, 34             ; flags = PRIVATE | ANONYMOUS
    mov r8, -1              ; fd = -1
    xor r9, r9              ; offset = 0
    syscall
    ; RAX = address of allocated memory
```

---

## **Quick Tips**

1. **Always check return values** - Negative = error
2. **Use R10 for 4th arg** - Not RCX (syscall uses it internally)
3. **RCX and R11 are destroyed** - Save them if needed
4. **Null-terminate strings** - For path arguments
5. **Use octal for permissions** - 0644o, 0755o, etc.

---

## **Resources**

- **Linux Syscall Table**: https://filippo.io/linux-syscall-table/
- **Man Pages**: `man 2 <syscall_name>` (e.g., `man 2 write`)
- **Header Files**: `/usr/include/asm/unistd_64.h`
- **Kernel Source**: `arch/x86/entry/syscalls/syscall_64.tbl`

---

## **Related Topics**

- [Topic 1: Setup & First Program](topics/topic-01-setup.md)
- [int 0x80 vs syscall](qna/int-vs-syscall.md)

---

[← Back to Main](README.md)

