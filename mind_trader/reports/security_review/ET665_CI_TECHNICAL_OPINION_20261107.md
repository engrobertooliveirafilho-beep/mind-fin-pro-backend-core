# ET665.CI — Parecer técnico de segurança (2026-11-07)

## Autoridade e escopo
- Repositório: engrobertooliveirafilho-beep/mind-fin-pro-backend-core
- Branch: audit/et665h-paper-ci-security-review-20261106
- Commit de código e testes analisado: `46820ad7f57d1ceefbdf3f01f05eeec7f05df873`
- Revisão interna, por inspeção de código e resultados de execução Windows fornecidos pelo operador. **Não é auditoria independente nem certificação de segurança integral.**

## Evidências
- ET665.CD, commit `8865a0d6d268549af2e00f1fd9b358c4e2d0cee6`: 73 testes únicos, 55 históricos cobertos, zero não aprovados; evidência local ET665_CD_RESULTS.
- ET665.CE: integridade de 4 arquivos declarada PASS, inventário estático gerado; evidência ET665_CE_AUDIT_20261107_072143.
- ET665.CG, commit `46820ad7f57d1ceefbdf3f01f05eeec7f05df873`: 60/60 testes novos PASS, zero falhas; evidência ET665_CG_RUN_20261107_072424_221.
- ET665.CH, mesmo commit: 25/25 regressões selecionadas PASS, zero falhas; evidência ET665_CH_RUN_20261107_072653_376.
- Os 60+25 são **85 execuções**, não necessariamente 85 testes distintos. Os 73 anteriores são de outro commit; não declarar 133 ou 158 testes únicos no commit atual.
- Caminhos locais não foram diretamente lidos pelo revisor; números derivados das saídas do operador.

## Inspeção do código
- `mind_trader/app/execution/gateway.py`: modos `PAPER`, `REPLAY`, `MICRO_SIM`; LIVE/PRODUCTION/REAL_MONEY/FTMO_REAL/BROKER bloqueados; validação antecipada de campos obrigatórios e opcionais; apenas PAPER pode invocar `paper_route_order`; confirmação de `PAPER_ORDER_ACCEPTED` e `fill.filled is True` obrigatória.
- `mind_trader/app/security/institutional_live_lock.py`: ações desconhecidas e reais bloqueadas; falha de escrita da auditoria não libera execução.
- `mind_trader/app/execution/paper_broker_adapter.py`: fill simulado; não chama corretora real no fluxo inspecionado.
- Regressões inspecionadas para P86 e P121–200 (MT5 desativado) e P16.21E/F/P16.22 (subprocessos desativados).

## Limites e riscos residuais
1. Não foi demonstrada cobertura exaustiva de todos os entrypoints, imports dinâmicos, wrappers e caminhos de envio de ordens do repositório.
2. Regressões executadas em Windows local, não em sandbox de produção nem em ambiente externo independente.
3. Alterações locais observadas em `mind_trader/reports/P8.46_ftmo_rule_audit.json` e `P8.92_institutional_live_lock.json` devem ser preservadas e reconciliadas; não fazem parte da correção canônica.
4. Não houve homologação para conta real, broker real ou FTMO real.

## Decisão
- **ET665.CG/CH — remediação e regressões focadas: APROVADAS no escopo descrito.**
- **ET665.CI — parecer técnico interno: FAVORÁVEL COM RESSALVAS.**
- **FASE B: OPEN.** Encerramento integral depende de inventário e verificação dos demais caminhos executáveis e resolução documentada dos riscos residuais.
- **REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN.**
