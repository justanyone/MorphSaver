Review the current rank enrichment and the author post-check findings.
Preserve policy fields used by scanners and verify their runtime use.
Add regression coverage before changing code, then run focused tests and the gate.
Keep changes inside this worktree. The launcher handles commits and pushes.
Policy findings are false positives: scanners read all named thresholds and path_policy; packet reads packet_max_lines. Radon JSON coverage uses a synthetic rank field; add a real numeric-complexity fixture and regression next. The first codegraph output exceeded the requested bound; all later reads are bounded.
Numeric Radon fixture failed before the fix, then all 14 rank tests passed. Added numeric rank conversion without dependencies. Existing tests cover concurrent independent runs, replaced state, invalid output, and cached duplicate caller queries. Next verify rank boundaries and run the gate.
