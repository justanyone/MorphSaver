# ADR 0008: Emitters are plugins; no host-project text in the core

**Status:** Accepted 2026-11-04.
**Decision:** `morphsaver/emit/<name>.py` modules expose `NAME` and `emit(candidates, out_dir, meta)`. A plugin for a build factory reads its service address, token file and project id from `MORPHSAVER_TASK_API`, `MORPHSAVER_TASK_TOKEN_FILE` and `MORPHSAVER_TASK_PROJECT`. No host name, URL, account or deployment fact is written in this repository.
**Why:** The repository is public and general. The owner's factories are one consumer among others.
**Consequences:** Host-specific policy files and glue live in the host's own repository. The core test suite never needs network.
