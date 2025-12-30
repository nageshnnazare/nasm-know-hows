# Push and Pop Explained

## Question
*What does push and pop do in assembly?*

---

## Answer

In assembly language, `push` and `pop` are fundamental instructions for working with the **stack**, which is a Last-In-First-Out (LIFO) data structure in memory.

---

## PUSH Instruction

**`push`** adds data onto the top of the stack:

1. **Decrements** the stack pointer (ESP/RSP on x86/x64)
2. **Writes** the value to the memory location now pointed to by the stack pointer

```nasm
push eax        ; Save eax register on stack
push 0x42       ; Push immediate value onto stack
```

**What happens internally:**
- Stack grows "downward" (toward lower memory addresses)
- ESP = ESP - 4 (on 32-bit) or RSP = RSP - 8 (on 64-bit)
- Memory[ESP] = value

---

## POP Instruction

**`pop`** removes data from the top of the stack:

1. **Reads** the value from the memory location pointed to by the stack pointer
2. **Increments** the stack pointer

```nasm
pop ebx         ; Restore value from stack into ebx
```

**What happens internally:**
- Value = Memory[ESP]
- ESP = ESP + 4 (on 32-bit) or RSP = RSP + 8 (on 64-bit)

---

## Common Uses

### **1. Saving/Restoring Registers:**
```nasm
push eax        ; Save eax
push ebx        ; Save ebx
; ... do work that modifies eax and ebx ...
pop ebx         ; Restore ebx (LIFO order!)
pop eax         ; Restore eax
```

### **2. Function Calling Conventions:**
```nasm
push arg3       ; Push arguments in reverse order
push arg2
push arg1
call function   ; Call function
add esp, 12     ; Clean up stack (3 args × 4 bytes)
```

### **3. Local Variables:**
```nasm
push ebp        ; Save old base pointer
mov ebp, esp    ; Set up new stack frame
sub esp, 16     ; Allocate 16 bytes for locals
```

---

## Key Points

- **Order matters**: Pop must be in reverse order of push (LIFO)
- **Stack alignment**: Must keep stack balanced (every push needs a corresponding pop or stack adjustment)
- **Stack overflow**: Pushing too much can overflow the stack
- **Fast**: Stack operations are very fast (often single CPU cycle)

---

## Bonus Question: Swapping EAX and EBX with Push/Pop

### Question
*How do I swap the values in eax, ebx with push & pop?*

### Answer

**C Equivalent (conceptual stack):**
```c
#include <stdint.h>

// Simulating push/pop with an array
int32_t stack[100];
int32_t stack_pointer = 0;

void push(int32_t value) {
    stack[stack_pointer++] = value;
}

int32_t pop() {
    return stack[--stack_pointer];
}

int main() {
    int32_t eax = 5;
    int32_t ebx = 10;
    
    // Swap using push/pop
    push(eax);      // Stack: [5]
    push(ebx);      // Stack: [5, 10]
    eax = pop();    // eax = 10, Stack: [5]
    ebx = pop();    // ebx = 5, Stack: []
    
    // Result: eax = 10, ebx = 5 (swapped!)
    return 0;
}
```

**Assembly:**
You can swap the values in `eax` and `ebx` using push and pop like this:

```nasm
push eax        ; Stack: [eax]
push ebx        ; Stack: [ebx, eax]
pop eax         ; eax now has ebx's value, Stack: [eax]
pop ebx         ; ebx now has eax's value, Stack: []
```

### **How It Works (Step-by-Step)**

Let's say `eax = 5` and `ebx = 10`:

1. **`push eax`** → Stack contains: `[5]`
2. **`push ebx`** → Stack contains: `[10, 5]` (10 on top)
3. **`pop eax`** → `eax = 10`, Stack contains: `[5]`
4. **`pop ebx`** → `ebx = 5`, Stack is empty

Result: **eax = 10, ebx = 5** ✓ Swapped!

---

## Alternative Swap Methods

### **Using xchg (simpler):**
```nasm
xchg eax, ebx   ; One instruction swap!
```

### **Using XOR trick (no extra memory):**
```nasm
xor eax, ebx
xor ebx, eax
xor eax, ebx
```

### **Using a temporary register:**
```nasm
mov ecx, eax
mov eax, ebx
mov ebx, ecx
```

The `push/pop` method is useful when you need to understand stack operations, but `xchg` is the most practical for simply swapping two registers.

---

## Visual Representation

```
Stack Memory (grows downward):
┌──────────┐
│  (high)  │
├──────────┤
│          │
│   ...    │
│          │
├──────────┤ ← RSP after two pushes
│   EBX    │   (top of stack)
├──────────┤
│   EAX    │
├──────────┤ ← RSP (initial)
│   ...    │
│          │
│  (low)   │
└──────────┘
```

---

**Related Topics:**
- Stack Frames
- Function Calling Conventions
- Stack Alignment

---

[← Back to Q&A Index](../README.md#-qa-section---deep-dives)

