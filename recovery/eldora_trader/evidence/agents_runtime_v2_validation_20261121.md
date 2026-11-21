# Agent runtime V2 — verified offline regression

Drive originals: `app/meta/agents_unified_runtime.py` (`1IsM5-lotyUzmYQg8Ibvsy7VFz1xkr2E-`), `tests/test_agents_unified.py` (`1_gnMumMCQ-gSDhJsfeylzom2PznR_Asd`), `app/agents/sec_sentinel.py` (`1B4RdoylWbUMmpUmk1JGzylu0Yh-gtaEW`). Original dispatcher overwrites imported `run_dry` repeatedly; original agent IDs use dotted names and recovered `sec.sentinel` returns `not_implemented`/`stub`.

Local offline command: `python -m unittest -v test_agents_runtime_v2`. Result: **14 PASS, 0 FAIL**. Test loader uses doubles; no claim of original agent functional certification.

Local SHA256 code: `c8c6e94ca9d68ae3b36d6b50521a70dbc62b4bf617ebf85b1c596629130cd0d8`; tests: `bd8da932de8474045748f74c273b2c7677d866b1bc3f32151f64bb20913989f0`; log: `902f1cfc33d81e4b482c0fdf4aec3b230780b3564f2ab405699846d61488bbd3`.

GitHub blobs read back and matched local `git hash-object`: code `b9048fff4f0159bd46c3b224a9a85ee57eaa99d3`, tests `804280a9d16a28c5478ffa37b2a70c63c3530960`.

Scope: five allowlisted dotted IDs, strict identity validation and stub rejection. Other historical agents not yet recovered or certified. No main merge, production changes, real orders or cost. `E2E_CERTIFIED=FALSE`.
