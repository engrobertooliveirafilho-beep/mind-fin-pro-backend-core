# ET665.R437 / ET-711 — Original P2408 integrated with R434 gate

2026-11-10. Original generator `p2408_paper_runtime_integration_gated.py` retrieved from Drive file ID `1derXWI4c8Xp5jjkOb3BMfJLVjgxLFvJV`. Local source SHA256 `326947c34fc77399219a76c56f11ea21ae530700a7db99143e02c8f81e238a46`.

**Executed actual original embedded runtime class** by extracting its source constant via AST (no Windows top-level generator execution), with `et665_r434_context_consensus_gate.decide` pre-dispatch and explicit post-dispatch PAPER lock.

7/7 local behavioral cases PASS:
- valid three BUY votes => PAPER candidate
- missing direction => rejected (original incorrectly approved)
- SELL context vs three BUY votes => rejected (original incorrectly approved)
- no votes => rejected (original incorrectly approved)
- duplicate votes => rejected (original incorrectly approved)
- stale vote => rejected (original incorrectly approved)
- NaN weight => rejected (original incorrectly approved)

Evidence file: `ET665_R437_ORIGINAL_P2408_INTEGRATION.json`, SHA256 `09d48fc706ad5736a0cae746b43ec752f9c7547a1925678d2cc7c5a814e283f9`; replay script `et665_r437_original_integration.py`, SHA256 `d13ed0306ff273ff8c0d923ed5fd73d7b31230392a4a2376dac0be7b6718e95b`. These are sandbox artifacts; not deployed.

**Important limitation:** votes were fixtures, not independent strategy-emitted signed evidence. Therefore neither P2408's complete E2E path nor 19 HP19 agents are certified. Real orders remain forbidden. The isolated R436 adapter is published but not integrated into historical runtime.

`PHASE_B_CERTIFIED=0/16 | HP19_CERTIFIED=0/19 | E2E_CERTIFIED=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`
