# Packet format

One markdown file per candidate in `packets/<id>.md`, built by `morphsaver/packet.py`, capped at `packet_max_lines`.

```
# <id>
scanner, shape, policy, verdict line
score, lines_saved (dup - overhead), sites, callers, tests line
discriminator kind and values line

## Sites
### <file>:<line>-<end> `<function>` (<kind>, <arms> arms on `<discriminator>`)
```python  line-numbered verbatim source  ```
(repeated per site; cut with a note when the budget runs out)

## Proposed shape: <shape>
```python  template sketch, not model-written  ```

## Judge: answer these three, then give a verdict
1. growing domain concept or closed flag set?
2. crosses a policy line?
3. simpler for a reader of this codebase?
Verdict: accept | dict-table | reject | ask-owner, one paragraph, revised lines_saved if you disagree.
```

Later tickets add: callers with file:line (CodeGraph), test files that reference the functions, ruff/radon codes that hit.
A packet must stay readable by a cheap model: no whole-file dumps, no more than 400 lines.
