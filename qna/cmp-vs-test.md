# CMP vs TEST - What's the Difference?

## Question
*What is the difference between CMP and TEST instructions?*

---

## Quick Answer

```
┌────────┬─────────────────┬──────────────────────────────┐
│ Instr  │ Operation       │ Primary Use                  │
├────────┼─────────────────┼──────────────────────────────┤
│ CMP    │ Subtraction     │ Comparing values (equality,  │
│        │ (doesn't store) │ greater/less than)           │
├────────┼─────────────────┼──────────────────────────────┤
│ TEST   │ AND             │ Testing bits, checking zero, │
│        │ (doesn't store) │ checking sign                │
└────────┴─────────────────┴──────────────────────────────┘
```

---

## Detailed Explanation

### **CMP - Compare (Subtraction)**

```nasm
cmp destination, source     ; Performs: destination - source
                           ; Sets flags, discards result
```

**What it does:**
- Subtracts `source` from `destination`
- Sets arithmetic flags based on the result
- **Does NOT store** the result (unlike SUB)

**Flags set:** CF, ZF, SF, OF, AF, PF (all arithmetic flags)

**Example:**
```nasm
mov rax, 10
cmp rax, 5              ; Internally: 10 - 5 = 5

; Flags after CMP:
; ZF = 0 (result is not zero)
; SF = 0 (result is positive)
; CF = 0 (no borrow needed)
; OF = 0 (no signed overflow)
```

---

### **TEST - Test Bits (AND)**

```nasm
test operand1, operand2    ; Performs: operand1 & operand2
                           ; Sets flags, discards result
```

**What it does:**
- Performs bitwise AND of `operand1` and `operand2`
- Sets logic flags based on the result
- **Does NOT store** the result (unlike AND)

**Flags set:** ZF, SF, PF (logic flags), **CF and OF cleared to 0**

**Example:**
```nasm
mov rax, 10              ; RAX = 0b00001010
test rax, rax            ; Internally: 0b00001010 & 0b00001010 = 0b00001010

; Flags after TEST:
; ZF = 0 (result is not zero)
; SF = 0 (bit 63 is 0)
; CF = 0 (always cleared by TEST)
; OF = 0 (always cleared by TEST)
```

---

## Side-by-Side Comparison

### **The Math**

```nasm
mov rax, 10
mov rbx, 5

; CMP does subtraction
cmp rax, rbx            ; Computes: 10 - 5 = 5
                        ; Sets flags based on 5

; TEST does AND
test rax, rbx           ; Computes: 0b1010 & 0b0101 = 0b0000
                        ; Sets flags based on 0
```

### **Flag Behavior**

```nasm
; After: cmp rax, 10
; All arithmetic flags affected:
; - CF can be 0 or 1 (based on borrow)
; - ZF can be 0 or 1 (based on equality)
; - SF can be 0 or 1 (based on sign of result)
; - OF can be 0 or 1 (based on overflow)

; After: test rax, 10
; Logic flags affected, arithmetic cleared:
; - CF always 0 (cleared by TEST)
; - ZF can be 0 or 1 (based on AND result)
; - SF can be 0 or 1 (based on MSB of result)
; - OF always 0 (cleared by TEST)
```

---

## When to Use Each

### **Use CMP when:**

#### **1. Comparing for Equality**
```nasm
cmp rax, 42
je equal                ; Jump if RAX == 42
jne not_equal           ; Jump if RAX != 42
```

#### **2. Comparing Magnitude (Greater/Less)**
```nasm
cmp rax, rbx
jg greater              ; RAX > RBX (signed)
jl less                 ; RAX < RBX (signed)
ja above                ; RAX > RBX (unsigned)
jb below                ; RAX < RBX (unsigned)
```

#### **3. Range Checking**
```nasm
cmp rax, 10
jl too_small            ; RAX < 10
cmp rax, 100
jg too_large            ; RAX > 100
```

#### **4. Checking Against Non-Zero Values**
```nasm
cmp rax, 0              ; Check if zero
je is_zero

cmp rax, -1             ; Check if -1
je is_minus_one
```

---

### **Use TEST when:**

#### **1. Checking if Zero**
```nasm
test rax, rax           ; Better than cmp rax, 0
jz is_zero              ; Jump if RAX == 0
jnz not_zero            ; Jump if RAX != 0
```

**Why better than CMP?**
- Shorter encoding (2-3 bytes vs 4-7 bytes)
- Clearer intent
- Faster on some CPUs

#### **2. Checking Specific Bits**
```nasm
test al, 0x01           ; Check bit 0
jnz bit_is_set

test al, 0x80           ; Check bit 7 (sign bit)
jnz bit7_set

test rax, 0xFF00        ; Check if any bits 8-15 are set
jnz has_high_bits
```

#### **3. Checking Even/Odd**
```nasm
test rax, 1             ; Check bit 0
jz is_even              ; Bit 0 = 0, even
jnz is_odd              ; Bit 0 = 1, odd
```

#### **4. Checking Sign (Negative)**
```nasm
test rax, rax
js is_negative          ; Jump if sign flag set
jns is_positive         ; Jump if sign flag clear
```

#### **5. Multiple Bit Checks**
```nasm
test al, 0b11110000     ; Check if any upper 4 bits set
jnz has_upper_bits

test al, 0b00001111     ; Check if any lower 4 bits set
jnz has_lower_bits
```

---

## Practical Examples

### **Example 1: Zero Check**

```nasm
; ❌ Less efficient with CMP
mov rax, [value]
cmp rax, 0              ; 4-7 bytes encoding
je is_zero

; ✅ More efficient with TEST
mov rax, [value]
test rax, rax           ; 2-3 bytes encoding
jz is_zero
```

### **Example 2: Range Check (Use CMP)**

```nasm
; Check if RAX is in range [10, 20]
cmp rax, 10
jl out_of_range         ; RAX < 10
cmp rax, 20
jg out_of_range         ; RAX > 20
; In range!
```

**Can't use TEST for this** - TEST can't compare magnitudes!

### **Example 3: Bit Flags (Use TEST)**

```nasm
; Check status flags (bit field)
; Bit 0 = ready, Bit 1 = error, Bit 2 = done

test al, 0x01           ; Check ready bit
jz not_ready

test al, 0x02           ; Check error bit
jnz has_error

test al, 0x04           ; Check done bit
jnz is_done
```

**Can't use CMP for this** - CMP is for comparing values, not testing bits!

### **Example 4: Null Pointer Check**

```nasm
; Check if pointer is NULL

; Method 1: CMP
cmp rax, 0
je null_pointer

; Method 2: TEST (preferred)
test rax, rax
jz null_pointer         ; More idiomatic
```

### **Example 5: Powers of 2 Check**

```nasm
; Check if RAX is a power of 2
; Power of 2 has exactly one bit set
; Algorithm: (x & (x-1)) == 0 for powers of 2

mov rbx, rax
dec rbx                 ; RBX = RAX - 1
test rax, rbx           ; RAX & (RAX-1)
jz is_power_of_two      ; Zero means power of 2
```

**Must use TEST** - We're checking a bitwise operation result!

---

## Performance Comparison

### **Instruction Encoding Size**

```nasm
; CMP encodings
cmp rax, 0              ; 7 bytes: 48 83 F8 00
cmp rax, rbx            ; 3 bytes: 48 39 D8
cmp eax, 42             ; 3 bytes: 83 F8 2A

; TEST encodings  
test rax, rax           ; 3 bytes: 48 85 C0
test eax, eax           ; 2 bytes: 85 C0
test al, 0x01           ; 2 bytes: A8 01
```

**Winner for zero check:** TEST (smaller encoding)

### **CPU Performance**

On modern CPUs (Intel/AMD), both are similarly fast:
- **Latency:** 1 cycle (both)
- **Throughput:** 4 per cycle (both)

But TEST has advantages:
- ✅ Smaller code = better cache usage
- ✅ More readable for bit testing
- ✅ Doesn't involve subtraction logic

---

## Common Mistakes

### **Mistake 1: Using CMP for Bit Testing**

```nasm
; ❌ WRONG: Trying to test bit 0 with CMP
cmp rax, 1
je bit_is_set           ; This checks if RAX == 1, not if bit 0 is set!

; If RAX = 5 (0b0101), bit 0 is set but RAX != 1
; CMP will say "not equal"!

; ✅ CORRECT: Use TEST
test rax, 1
jnz bit_is_set          ; This correctly checks bit 0
```

### **Mistake 2: Using TEST for Magnitude Comparison**

```nasm
; ❌ WRONG: Trying to check if RAX > 10
test rax, 10
jg greater              ; This doesn't work! TEST does AND, not subtraction

; ✅ CORRECT: Use CMP
cmp rax, 10
jg greater
```

### **Mistake 3: Forgetting TEST Clears CF/OF**

```nasm
; Checking carry flag after TEST
add rax, rbx            ; May set CF
test rax, rax           ; CF cleared to 0!
jc carry_set            ; This will NEVER jump!

; If you need to preserve flags:
add rax, rbx            ; May set CF
jc carry_set            ; Check CF immediately
test rax, rax           ; Now safe to use TEST
```

---

## Equivalent Operations

### **Both Can Check Zero**

```nasm
; These are equivalent for zero check:
cmp rax, 0
je is_zero

test rax, rax
jz is_zero

or rax, rax             ; Also works but less common
jz is_zero
```

### **Both Can Check Sign**

```nasm
; For checking if negative (signed):
cmp rax, 0
jl is_negative          ; Less than zero

test rax, rax
js is_negative          ; Sign flag set (MSB = 1)
```

---

## Decision Tree

```
Need to check a value?
│
├─ Comparing two values?
│  └─ Use CMP
│     ├─ Equality: je/jne
│     ├─ Greater/Less: jg/jl, ja/jb
│     └─ Range: multiple CMPs
│
├─ Checking if zero?
│  └─ Use TEST (more efficient)
│     └─ test reg, reg; jz/jnz
│
├─ Checking specific bits?
│  └─ Use TEST
│     └─ test reg, mask; jz/jnz
│
├─ Checking sign?
│  └─ Use TEST (clearer intent)
│     └─ test reg, reg; js/jns
│
└─ Even/Odd check?
   └─ Use TEST
      └─ test reg, 1; jz(even)/jnz(odd)
```

---

## Memory Reference

### **CMP vs TEST Quick Reference**

```
┌────────────────────────┬─────────────┬─────────────┐
│ Operation              │ Use CMP     │ Use TEST    │
├────────────────────────┼─────────────┼─────────────┤
│ x == y                 │     ✅      │      -      │
│ x != y                 │     ✅      │      -      │
│ x > y                  │     ✅      │      -      │
│ x < y                  │     ✅      │      -      │
│ x >= y                 │     ✅      │      -      │
│ x <= y                 │     ✅      │      -      │
├────────────────────────┼─────────────┼─────────────┤
│ x == 0                 │     ✅      │     ✅✅    │
│ x != 0                 │     ✅      │     ✅✅    │
│ x < 0 (negative)       │     ✅      │     ✅✅    │
│ x >= 0 (positive/zero) │     ✅      │     ✅✅    │
├────────────────────────┼─────────────┼─────────────┤
│ Test bit N             │      -      │     ✅      │
│ Even/Odd               │      -      │     ✅      │
│ Multiple bits set      │      -      │     ✅      │
│ Power of 2             │      -      │     ✅      │
└────────────────────────┴─────────────┴─────────────┘

Legend: ✅ Works  ✅✅ Better choice  - Not suitable
```

---

## TL;DR

**CMP:**
- Does **subtraction** (operand1 - operand2)
- Use for **comparing magnitudes** (equal, greater, less)
- Sets all arithmetic flags (CF, ZF, SF, OF, AF, PF)
- Think: "Is A bigger/smaller/equal to B?"

**TEST:**
- Does **bitwise AND** (operand1 & operand2)
- Use for **testing bits** and **zero checks**
- Sets logic flags (ZF, SF, PF), clears CF and OF
- Shorter encoding for zero checks
- Think: "Are these bits set?"

**Golden Rules:**
1. Use **CMP** when comparing two different values
2. Use **TEST** for zero checks (`test reg, reg`)
3. Use **TEST** for bit testing (`test reg, mask`)
4. When in doubt for zero: **TEST is better**

---

## Related Topics

- [Topic 4: Flags & Comparisons](../topics/topic-04-flags.md)
- [Topic 3: Basic Instructions](../topics/topic-03-basic-instructions.md)
- [Topic 5: Conditional Jumps](../topics/topic-05-jumps.md) *(coming soon)*

---

[← Back to Q&A Index](../README.md#-qa-section---deep-dives)

