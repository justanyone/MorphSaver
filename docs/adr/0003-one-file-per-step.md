# ADR 0003: One JSON file per pipeline step; every step resumable; schema versioned

**Status:** Accepted 2026-11-04.
**Decision:** `scan` writes `candidates.json`, `rank` writes `ranked.json`, the judge writes `verdicts.json`, `emit` writes `tasks/`. Each file carries `schema`; a reader refuses an unknown version. Candidate ids are stable hashes of (file, function, discriminator), never line numbers.
**Why:** Sessions stop and resume; a judge may run hours after a scan; a host may run steps on different machines. Stable ids let a re-run match earlier verdicts and let an emitter avoid duplicate tasks.
**Consequences:** A schema change bumps `SCHEMA_VERSION` and gets a migration note. The same input must give byte-identical `candidates.json` and `ranked.json` (tested).
