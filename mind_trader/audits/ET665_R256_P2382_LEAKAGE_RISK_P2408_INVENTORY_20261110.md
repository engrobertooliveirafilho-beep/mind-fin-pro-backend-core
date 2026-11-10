# ET665.R256 — NEW Drive findings / P2381-P2382-P2408 risk audit
Date: 2026-11-10. SOURCE: original Drive historical logs, NOT executed original runtime.

P2381 run_p2381.log Drive 1z12joSqGu9qmPMYr-oN_7xylvS4zOLNv:
500 analyzed, 254 losses, 254 loss memory nodes, 5 loss clusters, 227 patched replay candidates; 6 family/timeframe rules blocked, 9 quarantined. Layers: LOSS_MEMORY_GRAPH, LOSS_CLUSTER_ENGINE, CONTEXT/SESSION/REGIME/FOOTPRINT/LIFECYCLE_BLACKLIST, PLAYBOOK_DECAY_ENGINE.

P2382 run_p2382.log Drive 1KaKAHMorTB7DV3VQoIFb6B01VSdOooTd:
baseline PF 0.832504, expectancy -0.083805R, DD 61.28919R; 227 replayed, 224 wins, 0 losses, reported win_rate 0.986784, PF 999.0 (sentinel value), DD 0, 224 promoted rows, 0 promoted groups, 8 observed groups. 224/227 = 98.6784%, but 224 wins + 0 losses leaves 3 outcomes unspecified. Cannot treat these as independently verified trades. Extremely favorable post-loss-patch results are a leakage/selection bias warning; require original row-level CSV, pre-registered time-split, non-overlapping walk-forward, cost/slippage and adverse path replay, and source hash audit. FAIL-CLOSED: no strategy promotion.

P2408 AUDIT_FINAL.txt Drive 1YVTyTAho_Zik7JCKniVTpnpAEbV3goIm:
9 ensemble members, 3 dispatch tests, 1 PAPER candidate, runtime promotion false, real execution false. Historical audit does not prove current executable integration.

Ledger V1 ID 1WYqMJ-wzqmDWTaRzwJGFk4Hj4b7MuBNR7m0F9ct99mI read successfully (726 paragraphs, through ET-704), but append ET-707 attempted using actual document tab t.0 and failed HTTP 403 PERMISSION_DENIED. This report is a pending ledger entry, not successful Google Docs write.

Original P2379 executor/CSVs and P2386B row data still absent in scoped search. No end-to-end offline replay performed. PAPER_ONLY, REAL_ORDERS=FORBIDDEN, FTMO_REAL=FORBIDDEN, MAIN untouched, cost R$0.00, certification blocked.
