---
name: morphsaver-judge
description: Judge MorphSaver refactor packets and write verdicts.json. Use after a morphsaver scan when asked to decide which candidates to refactor.
---

# MorphSaver judge

Input: `<repo>/.morphsaver/runs/<run>/packets/*.md` and `ranked.json`. Output: `verdicts.json` in the same directory,
same schema as `ranked.json` with `verdict`, `rationale` and optional `revised_lines_saved` filled on each candidate.

## Rules
- Read packets in rank order. Judge every packet; a candidate with no packet gets verdict `reject` and rationale `no packet`.
- You may not add candidates. Only the scanner finds; you decide.
- Verdicts: `accept` (classes or the proposed shape), `dict-table` (a lookup table is enough), `reject`, `ask-owner`.
- `policy: deny` or `caution` on a packet means the verdict is `ask-owner`, whatever you think of the code.
- Answer the three questions in the packet before the verdict. Put the answers in `rationale`, one paragraph.
- If the estimate `lines_saved` is wrong, set `revised_lines_saved` and say why in the rationale.
- Prefer `dict-table` when the discriminator is a closed set of few literals and each arm is one or two lines.
- Prefer `accept` when the same value set is dispatched at two or more sites, or when arms carry state or behaviour that will grow.
- Write the file with `json.dump(..., indent=1, sort_keys=True)` and keep `"step": "judge"`.

Then run `morphsaver emit <repo> --format markdown` (or the format the owner names) and report the task count.
