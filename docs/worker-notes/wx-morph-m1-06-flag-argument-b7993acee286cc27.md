# wx-morph-m1-06-flag-argument notes
- Fix author post-check: vulture (fixture unused fns), refurb FURB115, duplicates of candidate_id/_scan/test_ids.
- Plan: reuse dispatch_chain.candidate_id if same hash; add __all__ to fixture; drop duplicate test helper and test; use not-form assert.
- Done: candidate_id reuses dispatch_chain hash; fixture __all__ added; test helper and duplicate id test removed; FURB115 fixed. gate GREEN; flag fixture: 2 candidates (report, run), 0 for forward/once. Not committed (launcher commits).
