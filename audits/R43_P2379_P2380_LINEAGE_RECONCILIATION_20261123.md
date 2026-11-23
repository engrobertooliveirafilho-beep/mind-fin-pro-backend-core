# ELDORA TRADER — R43 | Auditoria de linhagem e reconciliação (2026-11-23)

## Proveniência
- GitHub: mind-fin-pro-backend-core, commit 26e0d445145f3d359649b30e4b2fc9c470e1bb9d
- Fonte exata: app/runtime/p2379_p2380_event_time_lineage_gate.py
- Blob SHA: bf3fc2ea607e8c770c32cb8806c1bba601f5f523
- Drive: run_p2379.log (ID 1WPdM8DeU-n_Vi3sN-oA1G2KrwjdKYF1P); run_p2380.log (ID 1ep7b9s-bZmtpPWzc3cK0nsPoJh6QgcLJ)

## Reconciliação sem retrabalho
- P2379: 699 playbooks, 164 contextos, 53 sequências; 916 sinais, 505 ready, 411 observe-only; 500 linhas no bus. Certificação histórica declarada, não E2E independente.
- P2380: 500 sinais avaliados; 243 wins, 254 losses; expectancy -0.083805 R; profit factor 0.832504; 0 promoted, 1 observed, 49 demoted. PnL proxy PAPER, não PnL real.
- Preservar R37/R38, S20 e P2383/P2384; S21 permanece bloqueado.

## Defeitos identificados por inspeção estática do código exato
1. int(signal["event_index"]) e int(signal["entry_index"]) aceitam float fracionário (1.9 -> 1), bool e strings com sinal, sem garantir índice canônico.
2. SHA256_RE valida apenas o formato hexadecimal, sem recomputar hashes contra bytes reais de dataset e linha.
3. resolve_next_bar_entry compara timestamps e índices, mas não valida símbolo, timeframe, integridade dos candles nem ordenação da série completa.
4. validate_event_bound_signal permite entry_index > event_index + 1; a restrição imediata só existe no resolver. Contrato de validação isolado não deve ser tratado como prova de next-bar.
5. Não há custos, slippage, comissões, posições simultâneas ou encerramento de posições nesse arquivo.

## Gate de correção
- Implementar wrapper fail-closed com índice inteiro estrito (excluir bool), recomputação SHA-256 a partir de bytes canônicos e conferência de símbolo/timeframe por candle.
- Exigir dados e timestamps de origem verificáveis, timezone normalizado e entry_index = event_index + 1 no ponto de emissão.
- Executar testes negativos e regressão contra checkout exato antes de integrar P2380.
- Nenhum edge promovido, nenhuma ordem real autorizada.

## Estado de certificação
READBACK_SOURCE=PASS
STATIC_AUDIT=COMPLETE
NEW_RUNTIME_TESTS=NOT_EXECUTED
INTEGRATION=NOT_CERTIFIED
E2E_CERTIFIED=FALSE
PAPER_ONLY=TRUE
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
MAIN=INTACT
COST=R$0
