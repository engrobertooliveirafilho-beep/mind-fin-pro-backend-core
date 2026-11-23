# R53 — P2392 original walk-forward recovery (2026-11-23)

## Original evidence read from Drive (READ ONLY)
Folder P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342: 1IeBcoWOcJbDUoyfVtSgw3ug_5gJF9nna
summary.json: 11kEakj1qQxW7p4YjF1G2Wy7Gr4TVf_za
AUDIT_FINAL.txt: 1_OrwdhcasEGGk34u3iam6wcQhV9jx1r_
de40_edge_promoted.csv: 1vg5rjtYsDrR_A_vPcKzd5Tr1VSiBSqjC
Additional original CSVs: de40_edge_walkforward_detail.csv, de40_edge_stability.csv, de40_edge_rejected.csv, de40_edge_observed.csv, de40_edge_walkforward_results.csv.

## Reconciled original state
P2392 historical complete: 40 candidates, 5 walk-forward windows, 1 PROMOTED, 1 OBSERVED, 38 REJECTED.
Criteria: PF>=1.5, WR>=45%, expectancy>0, samples>=30, passed_windows>=4.
Promoted P2391_8149352397: US_AFTERNOON|LIQUIDITY_SWEEP_REVERSAL_DOWN|LIQUIDITY_REVERSAL_ENTRY|DISTRIBUTION->BALANCE; BUY_PAPER; 152 samples, 90 wins, 62 losses, 4 windows passed, PF 1.715719, expectancy 0.139817 R, max DD 4.158651 R, net 21.252145 R.
Original audit says no retraining during test; pytest passed historically; governance P2389 preserved; PAPER stack unchanged; no real orders.
Next original step P2393_EDGE_CLUSTERING. Do not rerun P2392 or re-promote strategy without original source data, independent chronology and cost verification.

## Certification scope
Certified here: original files retrieved and cross-checked against summary/audit/CSV; GitHub ledger published and read back.
Not certified: execution of original code now, source-dataset hashes, end-to-end integration, realistic market fills, independent out-of-sample verification, future profitability.
PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0
