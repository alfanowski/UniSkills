# Reading Strategy

> Concrete locators and filters per artifact type. The principle is always the same: cheapest
> sufficient view first, expand only on evidence.

## 1. Code repositories

| Need | Cheap first move | Then |
| --- | --- | --- |
| What changed | `git diff --stat`, `git log --oneline -20` | `git diff -U3 -- <path>` for touched files only |
| Where a symbol lives | `rg -n "def name|function name|class Name"` | open the definition, then `rg -n "name\\("` for call sites |
| Entry points | manifest files (`pyproject`, `package.json`, `Cargo.toml`, `go.mod`), `main`/`cmd` dirs | trace one path end to end |
| Data model | migrations, schema files, ORM models | check indexes and constraints before judging queries |
| Test intent | test names + assertions, not full bodies | open only the failing test |
| Config surface | `rg -n "os.environ|process.env|config\\."` | read defaults and validation together |

Rules of thumb:

- `rg -l` before `cat`; `rg -n -C2` before reading the file.
- Read a function's signature and body before its comments; comments describe intent, code describes
  behavior, and they disagree often enough to matter.
- Prefer `git log -S"symbol"` (pickaxe) over reading history chronologically.
- Generated files, lockfiles, and vendored directories are not evidence unless the question is about
  them. Say so when you skip them.

## 2. Logs and traces

1. Reduce to counts first: `sort | uniq -c | sort -rn | head -30`.
2. Establish the time window before filtering by message.
3. Extract the stable fields (request id, status, duration) with `jq`/`awk`, not by eyeballing.
4. Compare a failing window against a baseline window of the same shape.
5. Keep the raw lines for the specific events you cite; do not cite aggregates you cannot reproduce.

Never paste an unfiltered multi-thousand-line log. State the filter, the window, and the total count
so the reader can judge whether the slice is representative.

## 3. Documents, specs, papers

- Read the table of contents and the abstract/conclusion first; decide whether the body is needed.
- For specs, find the normative section (`MUST`/`SHOULD`) rather than reading front matter.
- For papers, separate claim, method, and result; read the method before believing the result.
- For vendor docs, check the version selector and the changelog entry that introduced the behavior.

## 4. Binaries and artifacts

- Identify before analyzing: `file`, size, hash, sections, imports.
- Strings and imports are cheap triage, not proof of behavior.
- Disassemble the function under question, not the whole image.
- Keep offsets stable: record the artifact hash so offsets remain meaningful later.

## 5. Incident timelines

Build the timeline from timestamps in a single timezone, then annotate:
`t0 deploy`, `t1 first error`, `t2 alert`, `t3 mitigation`. Only then ask what caused the transition
between two adjacent states. Without a timeline, "root cause" is usually the loudest symptom.

## 6. Re-read triggers (legitimate)

Re-open a file only when:

- it changed (different commit, different mtime, edited during the session);
- a claim depends on an exact line you did not capture;
- a contradiction appeared that the earlier reading cannot explain.

"I forgot" is not a re-read trigger — that is what the checkpoint is for.

## 7. Output shaping cheat sheet

```bash
git diff --stat                      # size before content
git diff -U0 -- path                 # minimal hunks
rg -n -C2 'pattern' --glob '!vendor' # context without the file
jq '.items[] | {id, status, ms}'     # projection, not raw JSON
awk '{print $1}' file | sort | uniq -c | sort -rn | head
sed -n '120,180p' file               # explicit range with a reason
wc -l file                           # justify a skip decision
```

Every command in a report should be reproducible: include the working directory and the commit when
it matters.
