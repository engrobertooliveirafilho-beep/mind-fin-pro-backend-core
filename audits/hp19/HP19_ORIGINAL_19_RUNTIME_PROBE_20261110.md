# HP19 ORIGINAL SOURCE CONTRACT PROBE — 2026-11-10

Drive folder 126_GsCSmQq3uHkLT2_2M8Wdka6H0PWO4; 19 original agent_*.py files recovered to isolated local workspace. Historical comparison folder 1cyW1OjaSbHHZTnUDxTevBYD5WuDKwEm7 was not rehashed in this run.

Groups: cog=4, core=3, perf=5, sec=7. All 19 have a pydantic AgentInput/AgentOutput contract and class run(input) method. Local offline probe (Python, pydantic 2.13.5): syntax 19/19 PASS, run 19/19 PASS; 19/19 return generic status='success', analysis={'input_received':True}, telemetry={'latency_ms':1.3}. No specialized functionality proven; HP19 functional=0/19. The source declares capabilities analyze/execute/respond, not actual implementation.

Important divergence: these 19 use class run(AgentInput) and IDs like agent_sec_sentinel, while historical 52 app.agents modules use run_dry(payload) and dotted IDs. Existing fail-closed dispatcher on this branch cannot directly execute HP19 classes without an explicitly tested adapter and authority mapping. DO NOT auto-adapt or activate; no duplicate motors.

Probe is isolated local import+run of original files, not sandboxed OS-level network/process containment, not GitHub checkout CI, not production integration. SHA256 and full per-file outputs stored in local probe artifact; not published as hashes in this report. No real orders, no deployment, no main merge.

Next: validate 19 class contracts vs canonical HP19 registry, prove exact mapping and source hashes, design adapter fail-closed and run negative/integration tests offline.
