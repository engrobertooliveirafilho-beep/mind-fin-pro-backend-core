# ET665.R258 — Pinned regression snapshot correction

Date: 2026-11-09. Draft PR #18.

## Verified defect
R257 execution protocol pinned `50f714ecdde007992696bd6f228895d12a631ccf` (R256), which predates publication of the R257 protocol. That SHA contains the R244–R256 code/tests but not the runbook itself.

## Correction
The R257 runbook now pins `1bdecd9cfa081ac984b8e3da1648544347d9f208`, the GitHub commit that published R257. This is a deliberately frozen execution snapshot; it is not the moving tip of draft PR #18. Operator must check out the exact pinned SHA before running; no branch auto-update and no network pulls.

## Evidence boundary
Runbook corrected and published; Docker regression has NOT been executed. No PASS, CI approval, independent security review or Phase B certification. PR remains draft and unmerged. No production or real orders. FASE_B=0/16; HP19=0/19; COST=R$0.
