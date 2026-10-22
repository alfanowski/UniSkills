# Low-Level Verification

> Read this only when the question requires instruction-level evidence. The goal is to resolve *this*
> question, not to annotate an entire function.

## 1. Establish the frame before reading instructions

1. **ISA and mode** — x86-64, AArch64, ARM32/Thumb, RISC-V, MIPS, WebAssembly. Never mix them.
2. **Bitness and endianness** — 32/64-bit, little/big. Affects every load and immediate.
3. **ABI** — System V AMD64, Windows x64, AAPCS64, or a vendor ABI. Determines argument registers,
   stack alignment, and return conventions.
4. **Runtime** — native, managed (JVM/CLR), or interpreted. Managed code has metadata that changes the
   approach entirely.
5. **Build characteristics** — optimization level, PIE, static vs dynamic linking, LTO. These change how
   much source structure survives.

## 2. Calling conventions (common cases)

| ABI | Integer args | Float args | Return | Callee-saved |
| --- | --- | --- | --- | --- |
| System V AMD64 | RDI, RSI, RDX, RCX, R8, R9 | XMM0–7 | RAX (RDX:RAX for 128-bit) | RBX, RBP, R12–R15 |
| Windows x64 | RCX, RDX, R8, R9 | XMM0–3 | RAX | RBX, RBP, RDI, RSI, R12–R15 |
| AAPCS64 (AArch64) | X0–X7 | V0–V7 | X0 / V0 | X19–X28, FP, LR |
| ARM32 AAPCS | R0–R3 | — | R0 | R4–R11 |
| RISC-V LP64 | a0–a7 | fa0–fa7 | a0 | s0–s11 |

Verify against the actual binary; variants exist. If the calling convention is wrong, every argument
inference downstream is wrong.

## 3. Stack frame and prologue/epilogue

Typical x86-64 frame:

```asm
push rbp            ; save caller frame
mov  rbp, rsp       ; establish frame
sub  rsp, 0x30      ; locals
...
leave               ; mov rsp, rbp; pop rbp
ret
```

- Locals are usually at negative offsets from `rbp`; incoming stack arguments at positive offsets.
- Optimized builds may omit the frame pointer (`-fomit-frame-pointer`); then locals are relative to `rsp`
  and offsets shift with every push.
- Leaf functions may use the red zone (128 bytes below `rsp`) without adjusting the stack.

## 4. Width and signedness

The most common decompiler errors:

| Pattern | Trap |
| --- | --- |
| `movsx` vs `movzx` | Sign-extending vs zero-extending a narrow load; changes negative values |
| 32-bit write zero-extends | On x86-64, writing `eax` clears the upper 32 bits of `rax` |
| `imul` vs `mul` | Signed vs unsigned; high-half behavior differs |
| `sar` vs `shr` | Arithmetic vs logical shift; negative numbers diverge |
| `cmp` + `jl/jb` | Signed vs unsigned branch condition |
| Truncation on store | Writing a 64-bit value into a 32-bit field loses the high half silently |

Always check the operand size suffix or register width. A decompiler that shows `int` where the
instruction is 64-bit is producing fiction.

## 5. Control flow

- **Direct vs indirect calls** — indirect calls through vtables or function pointers need the table's
  contents, not just the call site.
- **Tail calls** — a `jmp` to another function is a call with no return; decompilers sometimes render it
  as a loop.
- **Switch tables** — jump tables appear as computed jumps; recover the table bounds before enumerating
  cases.
- **Exception handling** — unwinding tables (`.eh_frame`, `.pdata`) define try/catch regions that
  decompilers may flatten.
- **Inlined code** — small functions disappear into callers; the same logic may appear in ten places.

## 6. Data and memory semantics

- Struct layout: field order follows declaration, but padding depends on alignment rules of the ABI.
- Arrays vs pointer arithmetic: `[base + index*4]` implies a 4-byte element; confirm by the store width.
- String handling: length-prefixed vs NUL-terminated changes every boundary check.
- Endianness matters when reading multi-byte fields from a file or network buffer.

## 7. Decompiler artifacts to distrust

| Artifact | Meaning |
| --- | --- |
| Impossible type (`int` holding a pointer) | Type recovery failed; trust the instruction width |
| Variable reused for unrelated values | Register coalescing; split it manually |
| Missing `return` | Decompiler lost the epilogue or the branch is `noreturn` |
| "Unreachable" code | Jump table or indirect branch target it could not resolve |
| Bogus array indexing | Struct field access mis-modelled as an array |
| Clean `if/else` around a computed jump | Switch reconstruction guess |

Rule: the decompiler proposes, the disassembly disposes. Any load-bearing claim must be verifiable in the
instruction stream.

## 8. Verification record

For each instruction-level claim:

```text
Claim:        <what the code does>
Address:      0x<...> (artifact sha256 pinned)
Instructions: <the exact sequence, verbatim>
ABI/width:    <calling convention, operand sizes>
Cross-check:  <second method: dynamic trace, second decompiler, sample comparison>
Confidence:   VERIFIED | DERIVED | LIKELY | HYPOTHESIS
```

## 9. What cannot be recovered

- Original variable and function names (unless symbols or debug info survive).
- Source-level types after aggressive optimization.
- Comments, macros, and preprocessor structure.
- Dead code eliminated by the compiler.
- The exact source that produced a given binary, when multiple sources compile identically.

Say this plainly instead of presenting a reconstruction as the original.
