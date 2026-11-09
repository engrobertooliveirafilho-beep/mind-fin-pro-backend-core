# ET665.R245 — Persisted P15.25 fail-closed regression

Date: 2026-11-08. Depends on ET665.R244 / draft PR #18, itself dependent on draft PR #17.

## Authenticated source evidence
- PR #18 was open/draft and unmerged at initial inspection, with HEAD 85c1c9b3a45df97ecd9dfa57d38ea38f60d6d65a.
- main pointed to 1b5916fbdc8c90173061315400abb92f3bbbb13a and was reported protected=false.
- ET665.R244's source-level fix sets P15.25 certification to RESEARCH_ONLY, APPROVED_EDGES=0, and INDEPENDENT_APPROVAL=NOT_PROVEN.
- P15.25B source sets reconstructed rows to RESEARCH_ONLY; P16 edge_revalidation_engine defaults approved=False. Neither claim proves all runtime consumer routes.
- The global recursive GitHub tree response was truncated, so repository-wide coverage cannot be certified.
- R244 negative tests patch Path.write_text and Path.mkdir; therefore they assert returned dictionaries but do not inspect real persisted JSON files.

## New evidence-producing regression
New file: `mind_trader/tests/security_review/test_et665_r245_p1525_artifact_failclosed.py`.

Uses synthetic trades and mock reconstruct(), runs the actual P15.25 report writer inside an isolated temporary working directory, then reads the persisted certification JSON and per-edge reconstruction JSON.

Four cases: profitable 50-trade candidate, no candidates, 19-trade candidate, and a deliberately untrusted upstream record marked approved/certified. Each must stay RESEARCH_ONLY; independent approval and approved edge count must remain negative, and LIVE/REAL_ORDERS forbidden. This is a behavioral artifact regression only for P15.25 and not process/network isolation.

## Certification boundaries and next gate
TESTS_PUBLISHED_NOT_EXECUTED; no CI PASS, Docker execution, independent sign-off, R113 runtime integration, R60 reconciliation, or MT5 isolation claimed.

Run offline with:
```bash
python -m unittest discover -s mind_trader/tests/security_review -p 'test_et665_r245_p1525_artifact_failclosed.py' -v
```
Retain actual stdout/JUnit and SHA-256 evidence from an approved isolated runner before changing certification status. No merge. No production. PAPER/DEMO only; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
