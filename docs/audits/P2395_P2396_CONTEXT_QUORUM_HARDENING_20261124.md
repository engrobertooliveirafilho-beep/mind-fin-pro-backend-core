# P2395/P2396 — Context and quorum hardening
Date: 2026-11-24

## Authority and preservation
- Base: main at 1b5916fbdc8c90173061315400abb92f3bbbb13a.
- Work isolated on fix/p2395-p2396-context-quorum-20261124.
- No changes to main, production runtime, P2394 historical inputs, P2397, or P2398 source.
- PAPER_ONLY=true; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN.

## Historical sources recovered
Drive P2395 folder: 1KJydhl4DLbioK2hxhdvFytaZd4Jc6YwB
- p2395_context_router_v2.py: 7,074 bytes, Drive ID 1gjXEFZdn2iXXTely1ducUqA1qOGvA_a-
- test_p2395_context_router_v2.py: 1,510 bytes, Drive ID 1X7JP7G1CBA3fLofvmT-p3uve6TNvmYeE
- runtime_router_candidates.csv: 4,383 bytes, Drive ID 1QEbr__WVpRvbuIuXNcx7nmtOnwKovJ-9
Drive P2396 folder: 15VTjP-iKLY7N_Uod0JSrZhen_-K2Tvhk
- p2396_edge_ensemble.py: 6,266 bytes, Drive ID 1XhdAY-wJIdTJ6-IIMF0guvtYfa4nfEO7
- test_p2396_edge_ensemble.py: 1,544 bytes, Drive ID 1bTgT3N3YIgqhZjNjP2YBx3fBlk-2xTi6
- ensemble_votes.csv: 194 bytes, Drive ID 1hcNU6nAasy3Ep6IrTrOGme1NTlLQ-hVA

## Defects confirmed in original source
- P2395 route(context) ignored the supplied context; for a promoted edge it checked only that the stored key/direction were nonempty.
- P2395 audit claimed runtime_integrated=true although integration_mode was ISOLATED_RUNTIME_MODULE; integration was not proven.
- P2396 counted any allowed PAPER_SIGNAL_CANDIDATE dictionary, without lineage, explicit PAPER safety flags, promotion decision, or unique source-edge identity.
- Historical P2394 score remains 68.391266 / OBSERVE_SCORE.
- Historical P2395 remains OBSERVE_ONLY.
- Historical P2396 remains 1 member / 0 operational / quorum 2 / allowed=false.

## Corrections
- P2395 now validates context type, exact key and direction match, finite score, promotion decision, and source cluster/edge lineage. It emits explicit decision and real_execution_allowed=false fields and exposes as_dict().
- P2396 now requires the P2395 PAPER_ELIGIBLE contract, explicit PAPER_ONLY safety flags, finite score, PROMOTE_SCORE lineage, source cluster/edge identity, and distinct source_edge IDs. Invalid/duplicate members cannot inflate quorum. Invalid quorum types/values fail closed.
- P2396 emits decision/vote PAPER_ELIGIBLE only after quorum and retains real_execution_allowed=false. No broker/order APIs were introduced.

## Regression evidence
- 19/19 new isolated unittest cases PASS, Python unittest, exit 0.
- Includes P2395->P2396 contract composition with synthetic promoted candidates, context mismatch, missing lineage, duplicate IDs, malformed quorum, non-finite score, and real-execution authority rejection.
- This does not change historical P2394's OBSERVE_SCORE or grant the current historical edge eligibility.
- Not an E2E runtime/MT5 certification; no live broker, orders, deployment, or main merge.

## Remaining gates
- Reconcile full historical P2397 and P2398 integration using exact-source checkout.
- Recover and certify independent eligible candidates; current historical ensemble remains 0/1.
- Reconcile HP19 alternatives/R258 and source hashes before dispatch changes.
- E2E certification remains false.
