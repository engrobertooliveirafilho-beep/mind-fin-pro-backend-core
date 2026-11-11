# ET665.R347 — Bloqueio de integridade do pacote local (2026-11-11)

Auditoria independente do arquivo ET665_R347_RUNTIME_EVIDENCE.zip disponibilizado no ambiente.

Reexecução: 4/4 testes unittest PASS, 0 falhas. Escopo sintético/estrutural.

Comparação Git blob SHA-1 (hash-object --stdin) entre arquivos do pacote e blobs publicados na branch:
| Caminho | GitHub blob | ZIP blob | Resultado |
|---|---|---|---|
| mind_trader/scripts/et665_r341_s20_s21_causal_gate.py | 2022b8b4d0b57bda7ce91557faf3c0118824b34c | 747c6575944fe9a80e4734382aeadcd2821e66ec | MISMATCH |
| mind_trader/scripts/et665_r347_real_component_e2e.py | 6de1cc19718df772c62f0f3fc311e828683838a1 | 9ed5e261cc2828bc6d6eed9c6a8f4b90f28c7056 | MISMATCH |
| mind_trader/tests/test_et665_r347_real_component_e2e.py | de9713f378b887bb4dfa7485469b7e9a5e93afd0 | a9fe32cd16c2d1f4bd2dd69dc7b49352ac8b89fa | MISMATCH |

No claim of malicious alteration: could be reproduction/line-ending differences. Nevertheless exact code provenance is NOT certified. R347 must remain open until checkout of exact GitHub blobs and runtime execution with independently captured log and input hash. Historical S20/S21 data absent; 16/16 and HP19 19/19 remain 0 certified.

No new fronts; PAPER_ONLY; main intact; real orders forbidden; R$0.
