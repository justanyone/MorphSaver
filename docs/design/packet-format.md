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

## Callers
callers: unknown                      (no CodeGraph run)
callers: <n> (locations are not stored in candidates.json)

## Tests
- <test file>                         (one line per Candidate.tests)
tests: none recorded

## Judge: answer these three, then give a verdict
1. growing domain concept or closed flag set?
2. crosses a policy line?
3. simpler for a reader of this codebase?
Verdict: accept | dict-table | reject | ask-owner, one paragraph, revised lines_saved if you disagree.
```

Every sketch is Python that `ast.parse` accepts for all five shapes. Names come from the candidate: the first value, the discriminator. Any text is turned into a valid identifier.
The Sites section is cut with a note when the budget runs out. Every line counts, the tail sections included, so a packet never exceeds `packet_max_lines`.
Later tickets add: ruff/radon codes that hit. Callers with file:line need the CodeGraph adapter to store locations.
A packet must stay readable by a cheap model: no whole-file dumps, no more than 400 lines.
