# ELDORA TRADER — P9.4 source-provenance remediation

Date: 2026-11-25  
Branch: `engineering/eldora-p9-failclosed-remediation-20261125`  
Scope: P9.4 DNA extraction only; original Drive artifacts remain read-only.

## Reconciliation

The original GitHub P9.4 implementation used a built-in sample research string whenever `run()` received no source. It therefore emitted DNA/genome candidates without an actual research input. The original source identifier hashed only the first 500 characters, and DNA IDs used only the first 200 characters, allowing different full documents with a shared prefix to collide.

## Correction

- Removed the implicit sample source; `run()` without an explicit source now writes an empty, blocked manifest (`P9.4_BLOCKED_SOURCE_REQUIRED`).
- Explicit source input is validated against supported source types and title constraints.
- Source identity and candidate IDs are SHA-256 derived from the full source content, source type, and candidate identity.
- Every DNA and genome candidate carries the same source hash; mismatched provenance is rejected.
- Extraction is explicitly labeled `BOUNDED_KEYWORD_TAGGING`, not semantic understanding.
- Candidates remain unvalidated; edge, causality, promotion, and export readiness remain false.

## Verification

Isolated Python 3.13.5 test run: **8 passed, 0 failed**. JUnit and SHA-256 evidence are stored under `mind_trader/evidence/p9/`. The local source/test files were run in an isolated sandbox; GitHub readback verified the published files. No repository-wide suite or CI workflow was executed.

## Boundary

This validates source-required behavior, provenance identity, and fail-closed candidate handling. It does not establish semantic extraction quality, backtest validity, edge, FTMO readiness, or production integration.

`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=INTACTA`
