# P19P38-C Orphan Module Classification

Status: AUDIT_ONLY_PASS
Generated: 2026-06-22T17:31:45.802419+00:00
Candidate count: 400

## Counts
- ACTIVE_CORE: 12
- CONNECTED_SUPPORT: 82
- DANGEROUS_TO_TOUCH: 21
- LEGACY_REVIEW: 282
- ORPHAN_CANDIDATE: 3

## Critical: Dangerous To Touch
- app/api/whatsapp.py | refs=144 | runtime/router/provider/forensic marker
- app/api/whatsapp.py.bak_p449c_fix2 | refs=2 | runtime/router/provider/forensic marker
- app/eldora/core/audit_ledger.py | refs=2 | runtime/router/provider/forensic marker
- app/eldora/core/distributed_runtime.py | refs=6 | runtime/router/provider/forensic marker
- app/eldora/core/distributed_runtime_state.py | refs=3 | runtime/router/provider/forensic marker
- app/eldora/core/event_bus.py | refs=2 | runtime/router/provider/forensic marker
- app/embedding/provider.py | refs=53 | runtime/router/provider/forensic marker
- app/main.py.bak_p4_46x | refs=1 | runtime/router/provider/forensic marker
- app/p19_real_world_validation/whatsapp_real_traffic_eval.py | refs=2 | runtime/router/provider/forensic marker
- app/retrieval/semantic_provider.py | refs=6 | runtime/router/provider/forensic marker
- app/runtime/cognitive_pipeline.py | refs=15 | runtime/router/provider/forensic marker
- app/runtime/forensic_bootstrap.py | refs=1 | runtime/router/provider/forensic marker
- app/runtime/forensic_trace.py | refs=3 | runtime/router/provider/forensic marker
- app/runtime/whatsapp_final_output_guard.py | refs=6 | runtime/router/provider/forensic marker
- tests/institutional/test_p1901h3_live_risk_forensics.py | refs=0 | runtime/router/provider/forensic marker
- tests/modules/test_p449c_whatsapp_live_hook.py | refs=0 | runtime/router/provider/forensic marker
- tests/test_p19a_whatsapp_real_traffic_eval.py | refs=0 | runtime/router/provider/forensic marker
- tests/test_p19p5_whatsapp_final_guard_only.py | refs=0 | runtime/router/provider/forensic marker
- tests/test_p19p6_whatsapp_followup_expansion.py | refs=0 | runtime/router/provider/forensic marker
- tests/test_p19p9_universal_whatsapp_output_guard.py | refs=0 | runtime/router/provider/forensic marker
- tests/test_p463k_memory_whatsapp_contract.py | refs=0 | runtime/router/provider/forensic marker

## Active Core
- app/companionship/self_reflection_engine.py | refs=1 | matches cognition/runtime core marker
- app/domains/__init__.py | refs=95 | matches cognition/runtime core marker
- app/domains/fitness_runtime.py | refs=3 | matches cognition/runtime core marker
- app/main_core.py | refs=0 | matches cognition/runtime core marker
- app/runtime/automotive_domain_guard.py | refs=1 | matches cognition/runtime core marker
- app/runtime/generic_topic_memory_engine.py | refs=4 | matches cognition/runtime core marker
- app/runtime/memory_adapter.py | refs=4 | matches cognition/runtime core marker
- app/runtime/memory_store.py | refs=10 | matches cognition/runtime core marker
- tests/modules/test_usde_cross_domain_transfer_learning.py | refs=0 | matches cognition/runtime core marker
- tests/test_p19p16_confinement_domain_interceptor.py | refs=0 | matches cognition/runtime core marker
- tests/test_p19p37e_self_reflection_engine.py | refs=0 | matches cognition/runtime core marker
- tests/test_p445m_maintenance_checklist.py | refs=0 | matches cognition/runtime core marker

## Orphan Candidates
- app/runtime/fix11k_probe.py | refs=0 | no references found
- app/runtime/p19_unified_pipeline.py | refs=0 | no references found
- app/runtime/p2161_2220_full_governance_system.py | refs=0 | no references found

## Safety
- No files moved
- No files deleted
- No runtime modified
- Classification only

## Next
P19P38-D COGNITION INTEGRATION MAP