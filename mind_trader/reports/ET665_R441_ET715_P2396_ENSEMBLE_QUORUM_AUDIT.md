# ET665.R441 / ET-715 — New P2396 original runtime vulnerability

Original source recovered from Google Drive file ID `1XhdAY-wJIdTJ6-IIMF0guvtYfa4nfEO7`, SHA256 `f78e8d647b96c6e3636e4de62b9d2e0cd40d71606e0b49af7f0ab7a540a0a3be`.

Executed the **actual embedded P2396EdgeEnsemble** Python class offline, without executing the Windows generator or connecting to a broker. **5/5 diagnostic assertions PASS**. The original incorrectly returns `allowed=True, PAPER_CONSENSUS_CANDIDATE` for (1) duplicate edge vote counted twice, (2) opposite BUY/SELL directions, (3) zero quorum with zero votes. Single-vote quorum=2 and OBSERVE_ONLY are correctly rejected.

Implemented local `et665_r441_p2396_guard.py` and `test_et665_r441_p2396_guard.py` as research-only safety wrapper; **8/8 unittest PASS**, including valid fixture, duplicates, opposite directions, zero quorum, missing direction, missing ID, observe-only, real execution prohibited. These are structural tests with fixtures, not independent strategy votes or empirical E2E proof. No production or main modification.

Evidence: `ET665_R441_P2396_EVIDENCE.json`, original probe `et665_r441_p2396_probe.py`.

Gate must be placed before P2396 and before P2408; real evidence lineage gate R439 still required. Do not certify original P2396 or historical ensemble results. Canonical Google Docs ledger update attempted separately.

`PHASE_B=0/16 | HP19=0/19 | E2E=FALSE | PAPER_ONLY | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | R$0`