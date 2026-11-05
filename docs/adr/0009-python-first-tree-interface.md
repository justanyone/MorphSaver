# ADR 0009: Python `ast` in v1 behind a parse-tree scanner interface

**Status:** Accepted 2026-11-04 (owner interview).
**Decision:** v1 scans Python with the standard `ast` module only. A scanner is `scan(tree, rel_path, policy)`; the tree type is per language. Other languages come later through tree-sitter, one ticket per language, without changing rank, packet or emit.
**Why:** Both calibration repositories are Python-dominant. `ast` is exact and dependency-free. Tree-sitter adds a dependency per grammar.
**Consequences:** Candidate and Site records carry no Python-specific fields. Language is a property of the file, selected by extension in the policy include globs.
