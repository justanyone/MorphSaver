# ADR 0007: Host-agnostic: a SKILL.md per role for Claude Code, AGENTS.md for Codex; the host needs only the CLI and markdown

**Status:** Accepted 2026-11-04.
**Decision:** Session instructions are plain markdown: `skills/<role>/SKILL.md` for Claude Code, mirrored in `AGENTS.md` for Codex and any agent that reads it. No API calls, model names or keys in this repository.
**Why:** The owner runs Claude Code, Codex and other agents. The same deterministic files serve all of them.
**Consequences:** When a host grows a richer integration (an MCP tool, a plugin), it wraps the CLI; the CLI stays the contract.
