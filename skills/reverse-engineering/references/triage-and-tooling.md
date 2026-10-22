# Triage and Tooling

> Triage is 20% of the effort and decides 80% of the path. Do it before installing anything.

## 1. Identity block

Record before analysis:

```text
path | sha256 | size | mtime | format (file) | arch guess | provenance | authorization
```

Every offset, address, and version claim in the final report is relative to this hash. Without it, the
report is not reproducible.

## 2. Triage checklist

| Question | Cheap method | What it tells you |
| --- | --- | --- |
| What container format? | `file`, magic bytes, header hexdump | ELF/Mach-O/PE/firmware/archive/script |
| What architecture? | header fields, `readelf -h`, `otool -hv` | ISA, bitness, endianness |
| Linked or static? | imports/exports table | available symbols, external capability |
| Interpreted or native? | shebang, embedded runtime strings, section names | analysis path differs completely |
| Packed or obfuscated? | section entropy, packer signatures, import count | whether static analysis will be readable |
| Compiler / language? | CRT strings, exception tables, runtime strings | ABI and idiom expectations |
| Stripped? | symbol table presence | effort estimate for structure recovery |
| Protections? | PIE, NX, stack canary, RELRO, CFG | exploitability context, not a goal by itself |

## 3. Method selection

| Situation | Path | Why |
| --- | --- | --- |
| Symbols present, source-like structure | Static, decompiler-assisted | Fast, low risk |
| Stripped but small, question is local | Static, disassembly around the question | Avoids environment setup |
| Behavior depends on runtime input | Dynamic + static confirmation | Static cannot see the actual data |
| Packed / virtualized | Unpack first, then static | Reading packed code produces nonsense |
| Format recovery | Differential analysis over many samples | Field boundaries come from variation |
| Protocol recovery | Capture, replay, mutate one field at a time | Establishes field semantics empirically |

## 4. Tool discovery and fallbacks

Never assume a tool exists. Discover, then record what you actually used.

| Capability | Common tools | If absent |
| --- | --- | --- |
| Format/arch identification | `file`, `readelf`, `objdump`, `otool`, `lief` | Parse headers manually with a hex dump and the spec |
| Disassembly | `objdump`, `llvm-objdump`, Ghidra, IDA, Hopper, `rizin` | `objdump` is usually available; otherwise read raw bytes against the ISA manual |
| Decompilation | Ghidra, IDA, Binary Ninja, RetDec | Reason from disassembly; mark conclusions `LIKELY` |
| Debugging | `gdb`, `lldb`, WinDbg, `rr` | Add instrumentation only if you can rebuild; otherwise stay static |
| Dynamic tracing | `strace`, `ltrace`, `bpftrace`, Frida | Logs, network capture, or a controlled harness |
| Network capture | `tcpdump`, Wireshark, `mitmproxy` | Application logs at the boundary |
| Entropy / packing | `binwalk`, `radare2`, YARA, `ent` | Manual entropy over sections |
| Hashing | `sha256sum`, `shasum -a 256` | Always available; never skip |

If a capability is missing, say which conclusion is now weaker. Do not describe a result you could not
produce.

## 5. Dynamic analysis safety

- Never execute an unknown artifact on the analysis host.
- A container shares the host kernel; it is not a security boundary against a kernel exploit.
- A VM is better, but is only as safe as its isolation, snapshot policy, and network configuration.
- Disable or simulate network access unless the question requires it; if required, isolate and log.
- Snapshot before execution; assume the artifact will attempt persistence.
- Record the exact environment so the observation is reproducible.

## 6. Evidence hygiene

- Keep raw tool output, not just your summary. Summaries lose the disambiguation you will need later.
- Pin tool versions: a decompiler update changes pseudocode and invalidates comparisons.
- Record commands verbatim; a result you cannot reproduce is an anecdote.
- Distinguish "the tool did not show X" from "X is not present". Absence in a view is not absence in the
  artifact.
