# ET665.BQ — Semantic review of eight flagged route occurrences

Date: 2026-11-06. Inspected exact commit `ba4b58df2c20e3b6c84bb412338da775f2ce580c` by GitHub authenticated file retrieval. Read-only inspection; no modules imported or executed. This is **not** a security approval.

| Path | GitHub blob SHA | Finding | Disposition |
|---|---|---|---|
| `mind_trader/app/execution/gateway.py` | `08471b07d3a41149c8c320f4f6f055b31af339c6` | PAPER route invokes `paper_route_order`; accepts only `PAPER_ORDER_ACCEPTED` plus `fill.filled is True`. No direct live broker call observed. `write_execution_ledger` mutates the supplied event and persists it, and unknown/unhashable `mode` values may throw before a safe ledger response. | Review dependency reachability and malformed input; do not certify on textual review. |
| `mind_trader/app/p16_autonomous_research_runtime/engine.py` | `7863e8f8623d87299707e71e00f4cd9807832ca5` | Local JSON and statistical research; no subprocess/network/MT5 call observed. | PROCESS heuristic false positive. |
| `mind_trader/app/p1621e_real_video_fetch_loop/engine.py` | `8851afc4acd48046b0acd7643e38013cf2e658fe` | `subprocess.run(["yt-dlp",...,url],timeout=120)` contacts external video sources; no input allowlist, returncode check or network gate. | EXTERNAL_PROCESS_REVIEW_REQUIRED. |
| `mind_trader/app/p1621f_transcript_download_strategy_extraction/engine.py` | `fc84a77c23c0a9dec6f65838967d3b359b38d2be` | `yt-dlp` subprocess with externally supplied URL, 120-second timeout; status `FETCH_ATTEMPTED` without checking returncode; output uses command stdout/stderr rather than verified transcript. | EXTERNAL_PROCESS_REVIEW_REQUIRED; transcript-evidence integrity issue. |
| `mind_trader/app/p1622_autonomous_daily_research_cron/engine.py` | `e5fff75a657cf48169901d6fb80ddbdac38fbec4` | `subprocess.run(["python","-m",module],timeout=900)` executes eight modules including video fetchers. No execution-environment isolation or external-access gate. | EXTERNAL_PROCESS_REVIEW_REQUIRED. |
| `mind_trader/app/p22_38x_ftmo_robust_research_expansion/engine.py` | `815273b71ec3d84a70c4681731fbd0c212429e9c` | Local dataset/research hypothesis enumeration, no subprocess/network/MT5 calls observed. | PROCESS heuristic false positive. |
| `mind_trader/app/p11_evidence_promotion_gate/engine.py` | `fe84aab0d23bbd4b84fcbb00c54a684d11755a48` | Two flagged occurrences, both local evidence/causality evaluation. Output explicitly sets live/broker/FTMO_REAL allowed false; upstream evaluator dependencies not inspected here. | PROCESS heuristic false positives; dependency review pending. |

## Security gates
- Do not run video fetch/transcript/cron components until independent sandbox and dependency review. No claim of broker order transmission in these files.
- The inventory's `PROCESS` classifier is overinclusive; distinguish actual subprocess calls from ordinary functions.
- The P121–P200 MT5 access finding was remediated separately by fail-closed patch in `ba4b58df...`; offline 52/52 PASS was reported by the operator for that commit.
- No tests executed during ET665.BQ. No `main` merge. `PHASE_B=OPEN`, `SECURITY_APPROVAL=NOT_GRANTED`, `REAL_ORDERS=FORBIDDEN`.
