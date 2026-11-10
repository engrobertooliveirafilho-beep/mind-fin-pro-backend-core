# ET665.R266 — P2387/P2390/P2393/P2394 promotion-authority reconciliation
Date 2026-11-10. NEW original Drive audit discoveries.

P2387 AUDIT_FINAL.txt Drive ID 1GCN1NLCS46bwJjcH4fOTOOhTnOG_qO_1: 230 input signals, 230 valid, 0 invalid, 230 bridge-ready, output mind_de40_mt5_paper_bridge_p2387.csv in simulated mt5_common_files_simulated, no actual terminal, REAL_EXEC_ALLOWED=False. Historical pytest claim only; no current rerun.

P2390 AUDIT_FINAL.txt Drive ID 1aSdgcXr3LJYHaTyazzeZQVSk6gz9oBjg: 230 PAPER signals, PF=1.543464, WR=56.521739%, expectancy=0.104782R, max DD=4.544174R, net=24.099759R; governance P2389 lock, REAL_EXEC_ALLOWED=False. Historical report only.

P2393 EDGE_CLUSTERING_REPAIR AUDIT_FINAL.txt Drive ID 1x9pD339vj-VZYal-mIyls1e3Y4_oxZeV: 1 cluster created, 1 promoted at clustering stage, source edge P2391_8149352397, cluster P2393_CLUSTER_AB78986FAD66, PF=1.715719, WR=59.210526%, expectancy=.139817R, DD=4.158651R, net=21.252145R, PAPER_STACK_MOD=False and REAL_EXEC_ALLOWED=False. Historical input P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342.

P2394 EDGE_SCORING AUDIT_FINAL.txt Drive ID 1eL8POPMM99Iim8KRwSvF_26re-kBygMv: same cluster and source edge, 1 scored, 0 PROMOTED_SCORES, 1 OBSERVED_SCORE, final score=68.391266, samples=152, passed windows=4, PF=1.715719, DD=4.158651R. PAPER_STACK_MOD=False, REAL_EXEC_ALLOWED=False. CRITICAL AUTHORITY RULE: P2393 clustering promotion is intermediate, not runtime promotion; P2394 OBSERVE_SCORE takes precedence and P2397 original code further disallows direct runtime promotion. Do not use historical P2393 promotion to bypass current R262 P2377 fail-closed gate.

Evidence classification: Drive historical audit reports, not independently reproduced raw trades, current CI or certified code paths. Original row-level bridge CSV, P2392 split dates and OHLC still missing. No functional integration or live execution performed.

Attempted native Google Docs Ledger V1 append ET-716 on tab t.0, result HTTP 403 PERMISSION_DENIED; NOT recorded in native document. This GitHub audit preserves the proposed ledger entry only.
MAIN UNCHANGED | PAPER_ONLY | REAL_ORDERS/FTMO_REAL FORBIDDEN | COST R$0 | FASE B OPEN | CERTIFICATION BLOCKED.
