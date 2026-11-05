# Calibration

## 2026-11-04 prototype (dispatch_chain, exact-set repeated_dispatch)

| Tree | Lines | Chains, 4+ arms | Chains, 3+ arms | Same value set at 2+ sites | Runtime |
|---|---|---|---|---|---|
| repo A `src/` | 300,824 | 10 | 31 | 2 | 7.9 s |
| repo B `src/` | 450,883 | 6 | 19 | 1 | 6.6 s |

Largest single chains: 22 arms on an event name (61 arm lines, state-machine handler), 8 arms on an HTML tag name, 7 arms on a
command kind, 6 arms on a field name, 4 arms with 64 lines in a parameter validator. Both repositories already use module-level
dict dispatch tables (187 in repo A).

Reading: the textbook repeated-switch smell is rare in code that already uses tables. The value will come from
`parallel_functions` and `data_clump` (not yet measured) and from judging the few large single-site handlers.

Precision per scanner: not measured yet (ticket M1-10).

## 2026-11-05 calibration

Two distinct local repositories were available. Python source was copied into
ignored run directories in this worktree. No source checkout was changed.
The inputs contain `src/`, `tests/`, and `scripts/`. Counts use physical Python
lines, including blank lines and comments. The default policy excludes tests.
No target policy file was copied. These are new inputs, not the prototype inputs.

| Input | Python files | Python lines | Source copy/count | Test/script copy/count |
|---|---:|---:|---:|---:|
| repo A | 3,395 | 994,231 | 0.273 s | 7.123 s |
| repo B | 1,209 | 822,724 | 1.795 s | 1.403 s |

Each input uses `python3 -m morphsaver run <input> --top 25 --run calibration`.
Scan, rank, and packet times use a monotonic clock at each CLI output line.
Scan time includes interpreter startup. These are elapsed times, not CPU times.

The results below separate broad attempts from source-only runs.
No default has changed. The preliminary sample does not support a threshold change.

### Offline checks

The focused rank and CLI checks passed: 35 tests.
The fixture baseline used 26 Python files and took 0.051 s.
Candidate counts were: `dispatch_chain` 20, `repeated_dispatch` 4,
`parallel_functions` 2, `data_clump` 2, and `flag_argument` 2.
This is a combined fixture scan with path exclusions disabled. It is not a
precision sample. No scanner, schema, state, or launch behavior was changed.

### Later fixture tickets

Add fixtures for these cases before a later scanner change:

- Repo B candidate `data_clump-8a0a7c6671` mixes a page limit with connection
  and identity fields. Repeated names do not establish one parameter object.
- Repo B candidates `data_clump-1d3781bb31` and `data_clump-661958eeaf`
  overlap. Subset groups can use the packet budget without adding a new task.
- Data-clump estimates count function bodies as saved lines. A parameter
  object does not remove those bodies. Add a cost-model regression fixture.

### Definition and dependencies

The global top 25 does not guarantee a sample for each scanner. Report N/A when
no candidate from a scanner was judged. Do not treat N/A as zero precision.
A later stratified sample is needed before tuning each scanner's thresholds.
There is no threshold-only fix for fields with different meanings or lifetimes.

The broad repo B run scanned 412 files and found 274 candidates. It did not
finish ranking within the 180 s limit. The attempt took 180.126 s.
The broad repo A scan took 204.108 s and found 838 candidates in 423 files.
Its ranking reported invalid or unavailable CodeGraph output at 380.809 s.
No packets were available from these broad attempts at that checkpoint.
The source-only retries use a standard-library baseline with optional tool
executables absent from `PATH`. No external repository index was queried by
those retries. The broad attempts had optional enrichment enabled.

The final offline gate was GREEN in 4.964 s. Ruff passed. All 77 tests passed.
The self-scan found 3 candidates in 18 files. No test required network access.
No live observations or service tests were needed for this document change.

### Repo B: source-only standard-library run

The input policy includes `src/**/*.py`. All thresholds keep their defaults.
Optional tool executables were absent from `PATH`. Ranking still uses AST test
references. This run scanned 292 files with 0 syntax errors.

| Scanner | Candidates | Judged | True positives | Precision | Runtime |
|---|---:|---:|---:|---:|---|
| `dispatch_chain` | 10 | 0 | 0 | N/A | Shared scan: 12.622 s |
| `repeated_dispatch` | 0 | 0 | 0 | N/A | Shared scan: 12.622 s |
| `parallel_functions` | 68 | 0 | 0 | N/A | Shared scan: 12.622 s |
| `data_clump` | 116 | 25 | 6 | 24% | Shared scan: 12.622 s |
| `flag_argument` | 3 | 0 | 0 | N/A | Shared scan: 12.622 s |

Runtime covers the combined scan. Per-scanner time was not instrumented.
Rank took 20.725 s. Packet generation took 0.111 s.
The full CLI run took 33.506 s. Manual review time was not recorded.

The review used packet headers, source signatures, and shown source excerpts.
It is a preliminary review of the capped packets. Full packet review remains.
All 25 ranked packets are data clumps. Other scanners have no precision sample.
A true positive means an accepted parameter-object proposal. Overlapping
subset proposals are rejected. This measures task usefulness, not just matching
parameter names. Estimates add class overhead and credit no unverified deletions.

| Rank | Candidate | Preliminary verdict | Reason |
|---:|---|---|---|
| 1 | `data_clump-ad509edf4a` | accept | Connection, identity, and environment form a shared request context. |
| 2 | `data_clump-d0c5dbb7fe` | reject | Clock injection is independent of connection and identity. |
| 3 | `data_clump-464ce3f648` | reject | A version selector is operation data, separate from connection and identity. |
| 4 | `data_clump-8af819cebc` | reject | Environment and clock are separate injected dependencies. |
| 5 | `data_clump-71821049b0` | reject | This overlaps the fuller context at rank 8; keep one proposal. |
| 6 | `data_clump-af47da6ad3` | reject | Connection, rate limiter, and clock have separate lifetimes. |
| 7 | `data_clump-9198f22116` | reject | Identity is request data; limiter and clock are injected services. |
| 8 | `data_clump-ac08a4c427` | accept | The complete execution context travels through the same read and write helpers. |
| 9 | `data_clump-1d3781bb31` | reject | The subset omits the media type; rank 10 gives the complete invocation. |
| 10 | `data_clump-661958eeaf` | accept | The handler signatures share a complete invocation context. |
| 11 | `data_clump-8a0a7c6671` | reject | A page limit is query data, separate from connection and identity. |
| 12 | `data_clump-b18fd7dbcd` | accept | The retrieval helpers pass one connection, key, and identity context. |
| 13 | `data_clump-c3b5ad4ad8` | reject | An existing dependency object and ingestion options are separate concepts. |
| 14 | `data_clump-70dc60006a` | reject | The dependency object is infrastructure; document and compartment ids are operation data. |
| 15 | `data_clump-6ccdec4fb5` | reject | A compartment selector is operation data, separate from request identity. |
| 16 | `data_clump-c751492fc9` | reject | A filename identifies input data; it is not connection context. |
| 17 | `data_clump-4dc7284ff9` | accept | The data access helpers repeatedly need connection, key, and identity together. |
| 18 | `data_clump-87e8969f31` | accept | Dates, compartments, and concept type form one search filter value. |
| 19 | `data_clump-b71dd2fff8` | reject | Filename and content form input data; deps already groups services. |
| 20 | `data_clump-6aa0abe6b4` | reject | The provider has a separate lifetime from request identity. |
| 21 | `data_clump-72d4b92fb2` | reject | An existing service dependency object should remain separate from identity. |
| 22 | `data_clump-a01004cc3e` | reject | This combines connection and dependencies with independent ingestion options. |
| 23 | `data_clump-2d7c720619` | reject | Provider services are separate from the connection and identity context. |
| 24 | `data_clump-9bd880d52c` | reject | The entity selector is operation data; the remaining context overlaps rank 8. |
| 25 | `data_clump-1a0ba98bec` | reject | Raw content is payload data, separate from dependencies and identity. |

### Repo A: source-only standard-library run

The input policy includes `src/**/*.py`. Thresholds keep their defaults.
Optional tool executables were absent from `PATH`. The scan covered 303 files
and found 733 candidates. It took 183.683 s. There were 0 syntax errors.

| Scanner | Candidates | Judged | True positives | Precision | Runtime |
|---|---:|---:|---:|---:|---|
| `dispatch_chain` | 27 | 0 | 0 | N/A | Shared scan: 183.683 s |
| `repeated_dispatch` | 3 | 0 | 0 | N/A | Shared scan: 183.683 s |
| `parallel_functions` | 139 | 0 | 0 | N/A | Shared scan: 183.683 s |
| `data_clump` | 564 | 0 | 0 | N/A | Shared scan: 183.683 s |
| `flag_argument` | 0 | 0 | 0 | N/A | Shared scan: 183.683 s |

Runtime covers the combined scan. Per-scanner time was not instrumented.
Ranking was still in progress at the checkpoint. Packet generation and judging
were not reached. Their runtimes and precision are unmeasured. Zero judged
means no sample. It does not mean that all candidates are false positives.

### Remaining work

Finish the source-only repo A ranking and packet steps. Read its top 25 packets
in full. Complete the repo B packet review before treating its provisional
precision as final. Time the judge and emit steps. Run the markdown emitter
only after final verdicts are ready. Keep the later fixture cases separate
from this calibration ticket. No threshold change is supported yet.
