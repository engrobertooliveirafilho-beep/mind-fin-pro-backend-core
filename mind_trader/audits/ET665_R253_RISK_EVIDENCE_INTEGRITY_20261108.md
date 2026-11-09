# ET665.R253 — Risk evidence integrity

Date: 2026-11-08. Draft PR #18, P15.25 research engine.

## Verified source finding
Before this change, `risk_of_ruin([])` returned `risk_proxy=LOW` and `profit_factor=99` despite zero observed trades. The same function did not explicitly reject nonfinite trade returns. This is a misleading research-risk classification, not proof of actual trading risk.

## Patch
Empty observations now produce `risk_proxy=UNKNOWN` and `profit_factor=null`. Non-numeric, boolean and nonfinite trade returns raise `ValueError`. Finite observations retain the existing proxy calculation. The proxy remains heuristic and must not be treated as independently certified risk of ruin.

## Regression coverage
Three offline test methods published: zero-trade UNKNOWN, malformed/nonfinite rejection, finite positive control. **NOT EXECUTED**. No CI/Docker/JUnit or independent review evidence. No merge, no production, no real orders. FASE_B=0/16 | HP19=0/19 | COST=R$0.
