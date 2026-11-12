# ET665.R41 — 127004 checkpoint inventory triage (2026-11-12)

## Source
Local original MINDCENTRAL_0098_R4_INVENTORY_CERTIFIED(1).zip: 127004 PARTITIONS/*.json scanned (index metadata only; audit certification BLOCKED). Candidate index exported locally as ET665_R41_CHECKPOINT_TRIAGE.json. Filename matches are not unique implementations or test passes.

## Indexed filename matches
strategy 2894; FTMO 1415; PAPER/broker 758; backtest 669; risk 342; data 119. These categories overlap, contain third-party files and duplicates. Never treat count as a count of engines.

## Four additional Drive originals recovered by exact ID and reviewed
- p2392_edge_walk_forward_validation.py: 1IY_BKJfc_zoPrSmDZWQCWZwNNF88oHWa; SHA256 dffc5e1a1f2b8e6e0bfc639fd4c6f3533d77668d20fa67468a4f8edf9fb83037; 10835 bytes. Candidate for independent fold replay; needs leakage and cost regression before import.
- p2403c_replay_source_validation.py: 1g7JtvbNqYa7bYwzGo5YlGJtz42yP3c1y; SHA256 5c5624deda6a8db0e1c10c7c40782f7e22ad496b77342fbc807cebb135b20a7e; 5854 bytes. Contains 3 hardcoded Windows paths, top-level filesystem operations and assertions; unsafe to import directly.
- ftmo_ruleset.py: 1QTdQbfGqOcBoaWOMyDRN8RsJv0kLGLlR; SHA256 6c632690f53172bc82a79f8687af7c572833cdc6c7a54953178997828b9cf542; 4392 bytes. Config schema candidate only; static default values are not proof of current FTMO rules. Require versioned challenge-specific contract, boundary tests and independently verified terms.
- p2404_correlation_analyzer.py: 1sdjZ11FpRSiR0iaaUtfqt-ueFpZNsdVC; SHA256 410293c96752c6d3509c0708656e8048f185c8a84ca71de74bc96065c445441f; 8504 bytes. Contains 4 hardcoded Windows paths and top-level filesystem operations; unsafe to import directly. Correlation requires synchronized time series and out-of-sample verification.

## Incorporation policy
Use original Drive IDs and hashes as provenance. Do not import originals into execution runtime. Refactor pure functions into isolated research modules only after regression coverage. Never use archived source self-declared CERTIFIED as proof. Keep existing R40 isolated guards and M8/M9 PAPER financial gate intact. Do not promote strategies or enable broker execution.

## State
INDEX_SCAN=127004/127004; FOUR_ADDITIONAL_DRIVE_SOURCES=READ; STATIC_AUDIT=COMPLETE; FOUR_NEW_ENGINES=NOT_INTEGRATED; DOCKER_CERTIFICATION=PENDING; MAIN=INTACT; PAPER_ONLY; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
