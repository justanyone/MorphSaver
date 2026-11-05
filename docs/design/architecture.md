# MorphSaver architecture

Status: design accepted 2026-11-04 by the owner (interview). Built so far: `dispatch_chain`, exact-value `repeated_dispatch`,
rank, packet, markdown emit, CLI, fixtures. Everything else is a ticket in [tasks.md](../tasks.md).

## 1. Problem

In a repository over 100k lines, find the places where a set of `if/elif` or `match` arms, a family of look-alike functions,
or a recurring parameter clump would be simpler as a class hierarchy, a dispatch table or a dataclass; estimate honestly
whether the change saves lines and simplifies the architecture; and write each worthwhile change up as a task a coding
session can execute.

## 2. What the survey found (2026-11-04)

No existing tool does scan, judge and emit together.

| Piece | Does | Gap |
|---|---|---|
| JDeodorant (Eclipse, Java) | Detects the "type checking" smell: switch or if chain on a type field; offers Replace Conditional with Polymorphism and Replace Type Code with State/Strategy | Java, Eclipse, no task output. Its rule (discriminator is a type field or getter, more than one arm) is copied here. |
| python-oop-analyzer 0.1.0 | AST rule for single-site if/elif chains with `min_branches` | No repetition, no cost model, no tasks |
| ruff C901, PLR0912, PLR0911; radon cc | Complexity hotspots | Complexity is not "better as classes"; used as enrichment only |
| CodeGraph | Symbol graph, callers, blast radius, verbatim source | Not a detector; the right evidence source for packets |
| Claude Code refactoring skills (several public ones) and caveman `safe-refactor` | Prose: how to do one refactor safely | The last step only |
| RefAgent (arXiv 2511.03153) | Multi-agent LLM planner for Java | Model-driven over the whole repo; does not scale to 300k lines |

## 3. Calibration on two real repositories

A prototype scanner (Python `ast`, 80 lines) ran on the owner's two largest repositories:

| Tree | Lines | Same-discriminator chains, 4+ arms | 3+ arms | Same value set at 2+ sites | Runtime |
|---|---|---|---|---|---|
| repo A, `src/` | 300,824 | 10 | 31 | 2 (both `isinstance` on dict/list/str) | 7.9 s |
| repo B, `src/` | 450,883 | 6 | 19 | 1 (test helpers) | 6.6 s |

Largest single chains: 22 arms on an event name (61 arm lines), 8 arms on a tag name, 7 arms on a command kind, 6 on a field name.
Both repositories already use module-level dict dispatch tables (187 in repo A).

Consequences:
1. The textbook smell, the same switch repeated in several places, is nearly absent. A switch-only detector reports about 30 sites per repo and most are fine.
2. A single-site dispatch turned into classes usually adds lines. Savings come from repetition: the same arms re-dispatched at N sites, or N functions or modules with the same shape. So the scanners look for parallel structure, not just conditionals.
3. The deterministic stage is cheap (under 10 s per 300k lines). Judgment is the expensive stage. So: deterministic wide net, strict evidence packets, model judges only the top N.

## 4. Pipeline

```
morphsaver scan   <target>            -> .morphsaver/runs/<run>/candidates.json   deterministic, seconds
morphsaver rank   <target>            -> ranked.json                               deterministic cost model
morphsaver packet <target> --top 25   -> packets/<id>.md                           deterministic; source + callers + sketch
[session: judge]                      -> verdicts.json                             model reads packets, scores, rationale
morphsaver emit   <target> --format F -> tasks/*                                   deterministic; one task per accepted verdict
[session: execute one task]           -> branch + green tests                      existing safe-refactor recipe
```

Each step writes one file so a session can stop and resume. Files carry `schema` (see `morphsaver.SCHEMA_VERSION`); a reader
refuses an unknown version. Run directories are named by timestamp or `--run NAME`; `rank`, `packet`, `emit` default to the newest.

## 5. Scanners

A scanner is a module with `NAME` and `scan(tree, rel_path, policy) -> list[Candidate]`; cross-file scanners expose
`scan_all(candidates, policy)`. The tree is a Python `ast` in v1 (ADR 0009).

| Scanner | Signal | Supports |
|---|---|---|
| `dispatch_chain` (built) | if/elif or `match` with ≥ `min_arms` arms on one discriminator: name, attribute, subscript, `isinstance`, `type(x) is`, `in {set}`. Records discriminator kind: literal-set, enum, type, flag, mixed. | Polymorphism, or a dict table when single-site with one-line arms |
| `repeated_dispatch` (exact-set version built) | `dispatch_chain` hits grouped by normalised value set (quotes stripped, enum class stripped, type names), ignoring the discriminator's spelling. Jaccard ≥ 0.6, ≥ 2 sites. The JDeodorant/Fowler signal and the one that reliably saves lines. | Polymorphism: one class per value, one method per site |
| `parallel_functions` | ≥ 3 functions in one module (or ≥ 3 modules in one package) whose AST skeleton (identifiers and constants erased) matches ≥ 0.8, with name affinity (shared prefix/suffix or selected by a table) | Template Method or Strategy |
| `data_clump` | The same ≥ 3 parameter names in ≥ 4 signatures, or the same ≥ 3 dict keys read together in ≥ 4 places | Parameter object / dataclass; often a prerequisite |
| `flag_argument` | Boolean parameter tested at the top of ≥ 2 branches | Split function or Strategy |

Enrichment when installed (never required): ruff `C901/PLR0912/PLR0911` locations raise priority inside hot functions; radon
`cc` rank; CodeGraph caller counts for blast radius; test references found by an `ast` walk of test files.

## 6. Cost model

```
dup_lines   = sum of arm-body lines across all sites in the group
overhead    = n_arms * class_overhead(4) + base_overhead(6) + registry(n_arms)
lines_saved = dup_lines - overhead                      # signed; negative is reported (ADR 0005)
score       = lines_saved * (sites_weight if sites > 1 and lines_saved > 0 else 1) + site_bonus * (sites - 1)
              - callers * risk_weight - (no tests ? penalty)
```

A single-site candidate with `lines_saved <= 0` keeps shape `dict-table`. The judge can promote it.

## 7. Packet

One markdown file per top-N candidate, capped at `packet_max_lines` (400): header with score components and policy;
verbatim line-numbered source of every site; discriminator values; callers and tests (when enrichment ran); a template
sketch of the target shape (not model-written); the three judge questions. Format: [packet-format.md](packet-format.md).

## 8. Judge and execute (sessions)

The judge is a session skill (`skills/morphsaver-judge`). Rubric: is the discriminator a growing domain concept or a closed
flag set; does the refactor cross a policy line; would a reader find the class version simpler. Verdicts: `accept`,
`dict-table`, `reject`, `ask-owner`. The judge may not add candidates (ADR 0004). A cheap model does the first pass;
a stronger model re-reads `accept`s above a threshold when the host wants two tiers.

Execute is a session skill too (`skills/morphsaver-execute`): behaviour-preserving, listed tests green, one site per commit
when more than 3 sites, signed line delta in the commit.

## 9. Emit

One task per accepted candidate, text deterministic from verdict and packet. Formats: `markdown` (built), `github` issue
bodies, and a build-factory plugin that posts rows to an HTTP task service configured by `MORPHSAVER_TASK_API`,
`MORPHSAVER_TASK_TOKEN_FILE` and `MORPHSAVER_TASK_PROJECT` (ADR 0008). Task shape: title, sites, target shape, sketch,
tests to keep green, policy flags, estimated line delta, rules, acceptance criteria, dependencies (a `data_clump` task
before the polymorphism task that needs it).

## 10. State on disk

`<target>/.morphsaver/policy.toml` is committed; `<target>/.morphsaver/runs/` is git-ignored (ADR 0002). The policy has
thresholds, weights, include/exclude globs, and `deny`/`caution` globs. Nothing is denied by default (ADR 0011).

## 11. Repository layout

```
morphsaver/            cli, model, policy, rank, packet, scanners/, emit/
skills/                morphsaver-scan, morphsaver-judge, morphsaver-execute (Claude Code); AGENTS.md mirrors them for Codex
docs/design/           this file, cost-model.md, packet-format.md
docs/adr/              decisions, one file per ADR
docs/tasks.md          tickets with acceptance criteria
docs/calibration.md    numbers from real runs
tests/fixtures/<scanner>/   one true positive and one known false positive per scanner
tools/test.sh, tools/gate.sh   what a build factory runs
```

## 12. Tradeoffs considered

- Deterministic pre-filter vs model-only scan: model-only costs tokens proportional to repo size and is not reproducible; deterministic-only cannot tell "simpler for a reader". Chosen: deterministic wide net, model judges a bounded top-N, so cost per run is fixed by N.
- Single-site conditionals: most hits are single-site and classes there cost lines. Chosen: report them as `dict-table` and let the judge promote, rather than hide a 22-arm handler the owner may want to see.
- Policy file: without it the tool keeps proposing protected code; with it the deny list needs upkeep. Chosen: policy file, nothing denied by default, `ask-owner` verdict so a flagged hit is never silently dropped.
- Honest savings: negative numbers look odd but stop the tool from "finding" refactors that grow the code.
- Clone detection: full token-clone detection finds more duplication but produces thousands of hits on 300k lines. Chosen: `parallel_functions` restricted to same module or package with name affinity; revisit after calibration.
- Languages: Python `ast` is exact and free; tree-sitter adds one grammar per language. Chosen: Python v1, scanner interface ready for a parse-tree backend.
- Where the model runs: judge and execute are session skills, so one repo serves Claude Code, Codex, or anything that runs a CLI and reads markdown. No API keys in the tool.
- Separate repo vs a module of the host factory: separate costs a version pin; gains publishability and keeps host text out. Chosen: separate, with the factory as an emitter plugin plus a policy file in the factory's own repo.
