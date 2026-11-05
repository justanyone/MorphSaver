"""packet: one bounded markdown file per top-N candidate, for the judge to read.

Verbatim source comes from the target files (CodeGraph adapter is a later ticket). Hard cap policy.packet_max_lines.
"""
from __future__ import annotations

import re
from pathlib import Path

from .model import Candidate
from .policy import Policy

SKETCH = {
    "dict-table": "HANDLERS = {{\n    {first}: handle_{first_id},\n}}\nresult = HANDLERS[{disc}](value)\n",
    "strategy-classes": (
        "class Base:\n    def apply(self, value):\n        raise NotImplementedError\n\n"
        + "class {first_cls}(Base):\n    def apply(self, value):\n        return value  # arm body\n\n"
        + "REGISTRY = {{{first}: {first_cls}()}}\nresult = REGISTRY[{disc}].apply(value)\n"
    ),
    "template-method": "class Base:\n    def run(self):\n        self.step_a()\n        self.step_b()\n    def step_a(self):\n        pass\n",
    "dataclass-param": "from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Params:\n    field_a: object  # the clumped fields\n",
    "split-function": "def thing_when_flag(value):\n    pass\n\ndef thing_when_not_flag(value):\n    pass\n",
}

JUDGE_QUESTIONS = """## Judge: answer these three, then give a verdict

1. Is the discriminator a stable domain concept that will grow new values (favours classes), or a closed set of a few flags (favours a table)?
2. Does the refactor cross a policy line (`policy` above is caution or deny)? If so the verdict is ask-owner.
3. Would a reader of this codebase find the class version simpler than what is there now?

Verdict: one of accept | dict-table | reject | ask-owner, one paragraph of rationale, and a revised lines_saved if you disagree.
"""


def _ident(text: str, default: str) -> str:
    """Turn any text into a valid Python identifier (letters, digits, underscore; no leading digit)."""
    word = re.sub(r"\W", "_", text).strip("_").lower()
    if not word:
        return default
    return word if not word[0].isdigit() else f"{default}_{word}"


def _source(target: Path, rel: str, line: int, end: int) -> str:
    lines = (target / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(f"{n:5d}  {lines[n - 1]}" for n in range(line, min(end, len(lines)) + 1))


def _callers_lines(c: Candidate) -> list[str]:
    if c.callers < 0:
        return ["callers: unknown"]
    return [f"callers: {c.callers} (locations are not stored in candidates.json)"]


def _tests_lines(c: Candidate) -> list[str]:
    if not c.tests:
        return ["tests: none recorded"]
    return [f"- {t}" for t in c.tests]


def build(target: Path, c: Candidate, policy: Policy) -> str:
    first = c.values[0] if c.values else "value"
    first_id = _ident(first, "value")
    first_cls = "".join(w.capitalize() for w in first_id.split("_") if w) or "First"
    disc = _ident(c.sites[0].discriminator if c.sites else "", "key")
    sketch = SKETCH[c.shape].format(first=repr(first), first_id=first_id, first_cls=first_cls, disc=disc)
    tail = ["## Proposed shape: " + c.shape, "", "```python", *sketch.splitlines(), "```", "",
            "## Callers", "", *_callers_lines(c), "",
            "## Tests", "", *_tests_lines(c), "",
            JUDGE_QUESTIONS]
    out = [f"# {c.id}", "",
           f"scanner: {c.scanner}   shape: {c.shape}   policy: {c.policy}   verdict: {c.verdict or '-'}",
           (f"score: {c.score}   lines_saved: {c.lines_saved} (dup {c.dup_lines} - overhead {c.overhead_lines})   "
            f"sites: {len(c.sites)}   callers: {'unknown' if c.callers < 0 else c.callers}   tests: {len(c.tests)}"),
           f"discriminator kind: {c.discriminator_kind}   values: {', '.join(c.values[:20])}{' ...' if len(c.values) > 20 else ''}",
           "", "## Sites", ""]
    # Every emitted line counts against the cap: the tail, one reserved cut note, and the head.
    budget = policy.packet_max_lines - len(out) - len(tail) - 1
    for i, s in enumerate(c.sites):
        head = [f"### {s.file}:{s.line}-{s.end_line} `{s.function}` ({s.kind}, {s.arms} arms on `{s.discriminator}`)", "", "```python"]
        room = budget - len(head) - 2          # 2 = closing fence and blank line
        if room <= 0:
            out.append(f"... {len(c.sites) - i} further sites cut by packet_max_lines")
            budget = -1
            break
        src = _source(target, s.file, s.line, s.end_line).splitlines()
        if len(src) > room:
            src = src[:room - 1] + [f"... {len(src) - room + 1} more lines cut by packet_max_lines"]
        out += head + src + ["```", ""]
        budget -= len(head) + len(src) + 2
    return "\n".join(out + tail)
