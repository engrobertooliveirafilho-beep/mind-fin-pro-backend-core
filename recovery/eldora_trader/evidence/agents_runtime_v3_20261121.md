# Agents runtime V3 — offline certification scope

Drive originals inspected: `sec.sentinel` (`1B4RdoylWbUMmpUmk1JGzylu0Yh-gtaEW`), `sec.gatekeeper` (`15--U6Liy5Jr7kR2ktsBMlD7SswZBKR8P`), `dev.test_guardian_agent` (`10Uu_8GhAd_Fido4fZMMkx1BDjPRERvho`), `domain.economics_finance_markets` (`1NWZNHcOxAvhVvS3RFNDvhWQeG4KLqdFx`), `core.safety_compliance_hub` (`1uH27Ze9FOz1xg05jqidLKiCDy7drj3X2`). All five originals implement `run_dry` as `status=not_implemented`, `mode=stub`. V3 rejects these responses.

Actual offline run: `python -m unittest -v test_agents_runtime_v3`; **16 PASS / 0 FAIL**, 0.001s, local Python. Loader doubles used; no original agent functionality or E2E certified.

SHA-256: code `0c447c419ef1e4b07f1fc80df46cd03b29a2986116adeefc801d1bf2dc4aafd8`; tests `9f4030fcb90bdca7b05f508db3d81053f03069ee75d931ce291a5d332b5e7b51`; log `ceed990b4f444e344acae6406e6ef4b9229c5180b47707fe0336e1e7d7561289`.

Git blob read-back: code `64da23e0ded37a583a08bb81ab91c8b164f7ecfe`; tests `9b27ae937ef043c5496285b84c6ddee6ac2b94e3`. Both equal local `git hash-object`.

`MAIN=INTACTA | PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | COST=R$0 | E2E_CERTIFIED=FALSE`.
