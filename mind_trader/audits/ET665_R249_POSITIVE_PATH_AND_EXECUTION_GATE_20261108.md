# ET665.R249 — Positive-path regression and execution gate

Date: 2026-11-08. Scope: P15.25, draft PR #18.

## Change
The R247/R248 containment suite had only negative cases, which could pass if the loader rejected every input. Added a positive control using a real temporary `data/normalized/synthetic.csv` containing two close prices (101, 102). It asserts the approved relative path is readable and returns numeric close values.

## Verification boundary
The GitHub branch contains the updated test; no GitHub Actions run, local unittest result, Docker offline isolation, JUnit or SHA-256 test evidence is claimed. An attempted unauthenticated raw GitHub download from the execution container failed due to network access; do not infer that tests ran.

## Next gate
Run R244–R249 under approved offline isolation, capture stdout/JUnit, container image digest, exact commit SHA and SHA-256 of evidence. Then assess R113 integration, MT5 process/network isolation and R60 reconciliation. Keep draft; no merge; no production; no real orders. FASE_B=0/16 | HP19=0/19 | COST=R$0.
