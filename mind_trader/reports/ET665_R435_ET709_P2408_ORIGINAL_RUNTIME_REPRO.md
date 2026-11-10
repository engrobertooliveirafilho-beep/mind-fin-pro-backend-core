# ET665.R435 / ET-709 — Original P2408 runtime unsafe approval reproduced

2026-11-10. Google Docs canonical ledger `1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI` update attempted: **403 PERMISSION_DENIED**. This is staged evidence, NOT canonical ledger insertion.

New primary source: `P2408_PAPER_RUNTIME_INTEGRATION_GATED`, Google Drive file ID `1derXWI4c8Xp5jjkOb3BMfJLVjgxLFvJV`. SHA-256 of original script: `a7ba89d971e947d54a83d6d7aabd9d45661ed10260f49442e3161b951624cc92`. Historical summary: 9 members, 3 dispatch tests, 1 paper candidate, real_execution_allowed=false. This historical certification string is **not independent behavioral certification**.

**Original runtime execution in isolated local Python:** extracted the original embedded `P2408PaperRuntimeIntegrationGated` class via Python AST, compiled and invoked `dispatch` without running the Windows top-level generator, touching a broker, or sending orders. Three members BUY_PAPER, each weight 0.3; quorum 3; confidence 0.62. Original returned `allowed=True` in all three cases: full BUY context; context with missing direction; SELL_PAPER context against all BUY_PAPER members. Two negative controls incorrectly approved. Cause: matching accepts 2 of 4 context fields and ignores individual emitted directional signals. This is **real reproduced functional failure**.

Local evidence: `ET665_R435_P2408_REPRO.json`, `et665_r435_p2408_repro.py`. R434's isolated fail-closed consensus gate is a candidate corrective component but is not wired into the recovered P2408 runtime.

**Next:** integrate fail-closed R434 gate before P2408 dispatch on isolated branch, require independently generated timestamped votes, rerun original negative controls, validate no network or live broker route, then verify P2409 downstream. Do not promote strategy or certify Phase B/HP19 without E2E proof.

`P2408_CERTIFIED=FALSE | PHASE_B=0/16 | HP19=0/19 | E2E_CERTIFIED=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`
