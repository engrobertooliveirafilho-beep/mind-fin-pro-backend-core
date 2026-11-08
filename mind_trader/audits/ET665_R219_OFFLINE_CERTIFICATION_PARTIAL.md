# ET665.R219 — Certificação parcial das regressões offline

Data: 2026-11-08
Estado: REGRESSOES_OFFLINE_PASS / FASE_B_ABERTA
Origem: execução local Docker Desktop R217 e auditoria R218
Commit-fonte: f8a60e23d565561aa291298681081a7901d34e46
Imagem Docker: sha256:2455245dce8b8d25adcf19d1bb193dc5381040cdd6d5c180537f78028ce18921
Evidências locais: D:\MIND_TEMP\SYSTEM_TEMP\ET665_OFFLINE_TEST_WORKSPACE\ET665_R217_EVIDENCE_20261108_134300_678

## Resultado
- Testes: 67/67 PASS
- Suítes: 6/6
- Falhas: 0
- Erros: 0
- Ignorados: 0
- Exit code: 0
- Integridade: manifestos SHA-256 de fontes e evidências verificados

## Distribuição
- mind_trader.tests.security_review.test_et665_r180_p15_dataset_path_guards: 24 PASS
- mind_trader.tests.security_review.test_et665_r182_p15_rclone_allowlist: 12 PASS
- mind_trader.tests.security_review.test_et665_r183_p15_pipeline_rclone_allowlist: 12 PASS
- mind_trader.tests.security_review.test_et665_r184_mt5_status_truth: 4 PASS
- mind_trader.tests.security_review.test_et665_r186_dependency_gates: 6 PASS
- mind_trader.tests.security_review.test_et665_r196_junit_identity_gate.GateTests: 9 PASS

## Controles da execução
- Docker offline, sem rede
- Sistema de arquivos raiz somente leitura
- Capacidades Linux removidas e no-new-privileges
- Limites de processos, CPU e memória
- Diretório temporário tmpfs
- Código-fonte montado somente leitura
- Evidências gravadas em volume separado

## Limites da certificação
- Testes estruturais e regressões offline aprovados
- Não comprova isolamento operacional integral de MT5
- Não comprova ausência de rotas alternativas não testadas
- Não comprova conformidade FTMO
- R60: reconciliação Drive/GitHub pendente
- HP19: 19 executores recuperados, 0 certificados
- Evidências locais ainda não publicadas no GitHub

## Decisão
REGRESSOES_OFFLINE=PASS
FASE_B=ABERTA
MERGE=PROIBIDO
MAIN=INALTERADA
PRODUCAO=INTACTA
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
CUSTO=R