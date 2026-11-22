# ET665 — Agent and step provenance reconciliation (2026-11-21)

## Authority
- Google Drive: `capability_code_map.txt` (file id `1uOzlFbkFOBizIgECN2sXyvINJZENNh5B`), historical path/line index, **not** executable source or certification.
- GitHub branch `engineering/et665-realdna-reconciliation-20261121`: `app/agents/agent_registry.py` blob `7ce6d28c37019eb7c254057f3de7880c6ecb8772`; `app/runtime/execution_governor_runtime.py` blob `f0038e24528189a774a33c6bcef19247ecae5c87`.
- Drive audit `P2081_2090_AUDIT.md` (file id `1oWQwpzBIYmuDjJc6pK1KOPu84fPFXQX5`) reports historical PASS, not equivalent to the revised GitHub source.

## Recovered capabilities
- Registry declares 14 named agents: TutorAgent, PlannerAgent, ResearchAgent, MemoryAgent, AudioAgent, SummarizerAgent, RetrievalAgent, CodeAgent, MotivationAgent, WorkflowAgent, SemanticSearchAgent, VoiceAgent, VisionAgent, MasterOrchestratorAgent.
- Execution governor default steps: `retrieve_context`, `rank_memory`, `decide_next_action`, `execute`, `record_evidence`.
- Execution governor has PostgreSQL plan/checkpoint/event schema; this is **not** proof of a running orchestrator.
- Registry references external model providers. Do not invoke any provider or paid API under `COST=R$0`.
- The recovered registry/governor are generic NEURA components. Their connection to P2081–P2110 Trader is **unproven**; do not silently wire them to trading or mark them certified.

## Functional blockers
1. P2067 historical allocation residual `0.085857` has no independently verified declared reserve. P2085/P2086 must fail closed.
2. P2087 durable checkpoint can be persisted and hash-checked, but actual process rehydration remains unverified.
3. P2101 scheduler, P2104 recovery, P2105 restart are simulations, not operational execution.
4. GitHub Actions workflow runs queried for commit `16a3066b5f4c4c11a30c54c9f89ae484fd7d01e8`: zero runs returned. No new regression PASS or E2E certification can be claimed.

## Gates
`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | MAIN=INTACTA | COST=R$0 | E2E_CERTIFIED=FALSE`
