# Tasks

Each task is one ticket: plain description, then acceptance criteria a test or a reader can check. Sizes: s (one concern, few
files), m (several files), l (cross-cutting; avoid). Milestone 1 is what the owner called "something done": scan, rank, packet
and markdown emit for Python, with fixtures. Host-side tasks (H-) live in the host factory's own board, not here.

## Milestone 1: scan, rank, packet, markdown emit (Python)

### M1-01 Bootstrap repository (done 2026-11-04)
Layout, packaging, CLI with five subcommands, model with schema version, policy loader, `dispatch_chain` ported from the
prototype, exact-set `repeated_dispatch`, rank, packet, markdown emit, fixtures, tests, tools/test.sh, tools/gate.sh, CI, ADRs.

### M1-02 dispatch_chain: discriminator kinds and false positives (s)
Add the `flag` kind (`if x:` / `elif not x:` chains on one boolean), `type(x) is T`, and attribute subjects with calls
(`token.kind()`), and record whether every arm returns. Add a false-positive fixture file: a chain whose arms test different
subjects, a chain under `min_arms`, a guard clause ladder (`if not a: return`), and nested chains that must not be double-counted.
- `tests/fixtures/dispatch/false_positives.py` yields zero candidates with default policy.
- `chains.py` fixture gains a flag chain and a `type(x) is` chain; both found with the right kind.
- A nested chain inside an arm is one candidate per chain, not two for the outer.
- Runtime on a 300k-line tree stays under 15 s (number in the commit message).

### M1-03 repeated_dispatch: Jaccard grouping and enum resolution (m)
Group `dispatch_chain` candidates whose normalised value sets overlap by Jaccard ≥ `policy.jaccard` (default 0.6), independent
of discriminator spelling. Resolve `Enum.MEMBER` and bare member names to one token. Carry the highest policy level of the
members. Keep ids stable: hash of the sorted union of values.
- Fixture: the same 4 values dispatched in 3 files under 3 variable names, one with 3 of the 4 values, groups as one candidate with 3 sites.
- Fixture: two chains sharing only 1 of 4 values do not group.
- An enum chain and a string-literal chain with the same member names group.
- Deterministic: two runs give byte-identical `candidates.json` (extend the existing test).

### M1-04 parallel_functions scanner (m)
Hash the AST skeleton of every function (identifiers and constants erased, control structure kept). Group functions with
similarity ≥ `policy.skeleton_similarity` in the same module, or across modules of one package, when names share a prefix or
suffix of ≥ 4 characters or the functions are values of one dict literal. Minimum 3 members. Shape `template-method`.
- Fixture: four `_x_result` functions of one shape yield one candidate with 4 sites; four unrelated functions yield none.
- Fixture: three functions selected by one dict table across two modules of a package yield one candidate.
- `dup_lines` is the sum of member body lines; overhead uses one base plus one override per member.
- Runtime on a 300k-line tree under 60 s (number in the commit message).

### M1-05 data_clump scanner (s)
The same ≥ 3 parameter names in ≥ 4 function signatures of one package, or the same ≥ 3 subscript keys read from one
variable in ≥ 4 functions. Shape `dataclass-param`. Record the clump as `values`.
- Fixture true positive (5 functions sharing `host, port, token`) and false positive (3 functions sharing `self, x`): one candidate, then none.
- `self`, `cls` and single-letter names never count.

### M1-06 flag_argument scanner (s)
A boolean-typed or boolean-defaulted parameter tested at the top level of the function body in ≥ 2 places. Shape `split-function`.
- Fixture true positive and a false positive where the flag is only passed through.
- A flag tested once is not reported.

### M1-07 rank enrichment and calibration constants (m)
Behind `shutil.which`: ruff (`C901,PLR0912,PLR0911` locations), radon (`cc` rank), CodeGraph (caller counts via `codegraph node`).
Find tests by an `ast` walk of files matching the exclude globs that name the enclosing functions. Expose overhead constants in
`policy.toml` and document them in `docs/design/cost-model.md`.
- Missing tools degrade to one warning line, never an error; tests run with none installed.
- A fixture with a test file referencing one function gives that candidate `tests == [path]` and no penalty.
- Ordering stays deterministic with enrichment on (test with a fake `which`).

### M1-08 packet: callers and tests sections, sketch check (s)
Add sections for callers (file:line) and tests when enrichment ran; make the sketch `ast.parse` clean for every shape; keep the cap.
- Every packet for the fixtures has all sections and parses as markdown with one H1.
- `ast.parse(sketch)` succeeds for all five shapes (test).
- A candidate with 40 sites produces a packet under `packet_max_lines` with a cut note.

### M1-09 markdown emit: dependencies and duplicates (s)
Emit a `depends_on` line when a `data_clump` candidate shares a function with an accepted polymorphism candidate; skip a task
whose file already exists with the same content; write an index `tasks/README.md` listing titles and line deltas.
- Byte-identical output on two runs (existing test extended to three candidates).
- A `data_clump` plus `repeated_dispatch` fixture gives the dependency line on the polymorphism task.

### M1-10 Calibration on two large repositories (m)
Run the full pipeline on two Python repositories over 250k lines; judge the top 25 by hand; record precision per scanner,
runtime, and the thresholds changed in `docs/calibration.md`. No scanner code change without a fixture.
- `docs/calibration.md` has a table: scanner, candidates, judged, true positives, precision, runtime.
- Threshold changes land in `docs/policy.example.toml` with one line of reason each.

### M1-11 Packaging and install check (s)
`pipx install .` works from a clean environment; `morphsaver --version` prints the version; README commands run as written;
CI green on 3.11, 3.12, 3.13; a tagged `v0.1.0` release.
- A CI job installs with pipx and runs `morphsaver run tests/fixtures/dispatch`.

## Milestone 2: judge support and emitters

### M2-01 `morphsaver check` for verdicts (s)
A subcommand that validates `verdicts.json`: schema, every candidate judged, verdict in the fixed set, `ask-owner` on every
`caution`/`deny`, rationale non-empty. Exit 2 with one line per fault.
- Fixture verdict files: one valid, three invalid (missing verdict, bad word, caution without ask-owner).

### M2-02 github emitter (s)
One issue body per accepted candidate for `gh issue create --body-file`; title and labels deterministic; a `tasks/gh.sh` that
creates them in order with dependencies as "blocked by #" text.
- Byte-identical output; no network in tests.

### M2-03 build-factory emitter (m)
POST one task per accepted candidate to `MORPHSAVER_TASK_API`, bearer token from `MORPHSAVER_TASK_TOKEN_FILE`, project from
`MORPHSAVER_TASK_PROJECT`, key from the candidate id, 2 to 8 acceptance criteria, dependencies by key. Dry run by default;
`--execute` posts. Test against a local fake HTTP server.
- Re-emitting the same verdicts posts nothing (key exists).
- Nothing about any particular factory, host or account appears in the module (grep in the gate).

### M2-04 `morphsaver diff` between runs (s)
List candidates new, gone and changed between two run directories by id. Used by a factory to file only new work.
- Fixture: add a chain, run twice, diff shows one new id.

### M2-05 Two-tier judge support (s)
`morphsaver packet --only accept --min-score N` re-packets a subset from `verdicts.json` for a second, stronger judge.
- The second pass writes `verdicts.json` with `tier: 2` on re-judged candidates; `check` accepts both.

## Milestone 3: more languages

### M3-01 Parse-tree backend interface and TypeScript via tree-sitter (l, split before starting)
### M3-02 Go (m)  ### M3-03 Rust (m)  ### M3-04 Ada (m)

## Host-side tasks (filed on the host factory's board, listed here for the picture)

- H-01 Register the MorphSaver project in the factory's project table and dispatch loop at lower priority than the main projects; factory checkout; `tools/test.sh` and `tools/gate.sh` as test and gate commands.
- H-02 Add `.morphsaver/policy.toml` to the factory's own repository (include `src/**`, exclude tests; no deny by owner decision).
- H-03 Factory cycle step: pinned MorphSaver version, `morphsaver run` on the factory repo every N hours with no model call, `morphsaver diff` against the last run, one judge task per batch of new packets.
- H-04 Judge task kind: worker follows `skills/morphsaver-judge`, runs `morphsaver check`, then `emit --format <factory>` so each accepted verdict becomes one fix task with the candidate id in its key.
- H-05 Cap: at most K open MorphSaver fix tasks per project (reuse the factory's existing refactor cap setting).
