"""packet: one bounded markdown file per top-N candidate, for the judge to read.

Verbatim source comes from the target files (CodeGraph adapter is a later ticket). Hard cap policy.packet_max_lines.
"""
from __future__ import annotations

from pathlib import Path

from .model import Candidate
from .policy import Policy

SKETCH = {
    "dict-table": "HANDLERS = {{\n    {first}: handle_{first_id},\n    ...\n}}\nresult = HANDLERS[{disc}](...)\n",
    "strategy-classes": (
        "class Base:\n    def apply(self, ...): raise NotImplementedError\n\n"
        + "class {first_cls}(Base):\n    def apply(self, ...): ...  # arm body for {first}\n\n"
        + "REGISTRY = {{{first}: {first_cls}(), ...}}\nresult = REGISTRY[{disc}].apply(...)\n"
    ),
    "template-method": "class Base:\n    def run(self):\n        self.step_a(); self.step_b()\n    def step_a(self): ...\n",
    "dataclass-param": "@dataclass(frozen=True)\nclass Params:\n    ...  # the clumped fields\n",
    "split-function": "def thing_when_flag(...): ...\ndef thing_when_not_flag(...): ...\n",
}

JUDGE_QUESTIONS = """## Judge: answer these three, then give a verdict

1. Is the discriminator a stable domain concept that will grow new values (favours classes), or a closed set of a few flags (favours a table)?
2. Does the refactor cross a policy line (`policy` above is caution or deny)? If so the verdict is ask-owner.
3. Would a reader of this codebase find the class version simpler than what is there now?

Verdict: one of accept | dict-table | reject | ask-owner, one paragraph of rationale, and a revised lines_saved if you disagree.
"""


def _source(target: Path, rel: str, line: int, end: int) -> str:
    lines = (target / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(f"{n:5d}  {lines[n - 1]}" for n in range(line, min(end, len(lines)) + 1))


def build(target: Path, c: Candidate, policy: Policy) -> str:
    out = [f"# {c.id}", "",
           f"scanner: {c.scanner}   shape: {c.shape}   policy: {c.policy}   verdict: {c.verdict or '-'}",
           (f"score: {c.score}   lines_saved: {c.lines_saved} (dup {c.dup_lines} - overhead {c.overhead_lines})   "
            f"sites: {len(c.sites)}   callers: {'unknown' if c.callers < 0 else c.callers}   tests: {len(c.tests)}"),
           f"discriminator kind: {c.discriminator_kind}   values: {', '.join(c.values[:20])}{' ...' if len(c.values) > 20 else ''}",
           "", "## Sites", ""]
    budget = policy.packet_max_lines - 60
    for s in c.sites:
        out += [f"### {s.file}:{s.line}-{s.end_line} `{s.function}` ({s.kind}, {s.arms} arms on `{s.discriminator}`)", "", "```python"]
        src = _source(target, s.file, s.line, s.end_line).splitlines()
        if len(src) > budget:
            src = src[:budget] + [f"... {len(src) - budget} more lines cut by packet_max_lines"]
        budget -= len(src)
        out += src + ["```", ""]
        if budget <= 0:
            out.append("... further sites cut by packet_max_lines")
            break
    first = c.values[0] if c.values else "value"
    first_id = "".join(ch if ch.isalnum() else "_" for ch in first).lower()
    first_cls = "".join(w.capitalize() for w in first_id.split("_")) or "First"
    disc = c.sites[0].discriminator if c.sites else "key"
    out += ["## Proposed shape: " + c.shape, "", "```python",
            SKETCH[c.shape].format(first=repr(first), first_id=first_id, first_cls=first_cls, disc=disc), "```", "",
            JUDGE_QUESTIONS]
    return "\n".join(out)
