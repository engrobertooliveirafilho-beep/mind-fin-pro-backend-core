# ET665.R64 — Descoberta autenticada Drive: P77/P77B (2026-11-08)

## Fontes históricas novas verificadas
- Pasta Drive `P77_DEMO_ORDER_CHECK_ONLY` ID `1jlzXP9shkiAf8kKztlBVcBnI40Zaan3U` contém `p77_order_check_only.py` (ID `1R4cBsUwzEovwGVGDDBVN5qU2oT5wkfp6`), `p77_order_check_report.json` (ID `1qSu6fpY3WVVW_ZbmT-q-KuHX84vAI_s9`) e request JSON.
- Pasta Drive `P77B_DEMO_ORDER_CHECK_FILLING_MODE_FIX` ID `1_YxCasm--7TYTD43ERfC1VNCpqx3IxTw` contém `p77b_filling_check.py` (ID `1XPKtIzdtf_2vNLoD9YegdgxJ3NSt1dbM`) e relatório.
- SHA-256 dos bytes baixados: P77 Python `5f665b80a24cb477c8fb681f271ac885c564dc2e70dd8c63d4803cfab3e06c69`; P77B Python `ce69aa18bfc751ae7d9784441f04fd1acf493a5d45f06440fa894cec37813ef5`; P77 relatório `c1211938d28bc3a44d0936773c357c37bfba6e890fe674bab790b3394ba1f3cc`.

## Inspeção estática, sem executar MT5
- P77 original importa MetaTrader5 e chama `mt5.initialize`, `account_info`, `terminal_info` e `order_check`. Não foi observada chamada `order_send` no arquivo recuperado.
- P77B original importa MetaTrader5 e chama `initialize`, `account_info`, `terminal_info`, `order_check`; não foi observada chamada `order_send` no arquivo recuperado.
- Relatório histórico P77 declara `ACCOUNT_SERVER=MetaQuotes-Demo`, `ACCOUNT_DEMO_VALIDATED=true`, `ORDER_CHECK_EXECUTED=true`, retorno 10030 `Unsupported filling mode`, `ORDER_SENT=false`. Essas são declarações do arquivo histórico, não observações atuais nem certificação de sandbox.
- O campo histórico `NEXT=P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED` não concede autoridade operacional. P78 permanece bloqueado pelo controle posterior ET665.CL.

## Inventário e integração
- Componentes recuperados: P77 original (inspeção estática concluída), P77B original (inspeção estática concluída), P77 relatório (evidência histórica, não teste atual).
- Integração em runtime: **BLOQUEADA** até revisão de autoridade, equivalência e isolamento institucional. Não duplicar executores, não importar MT5 em testes offline.
- R62: `approved` é autodeclarado no JSON e cinco categorias podem apontar ao mesmo arquivo; `evidence_complete` não constitui aprovação de segurança.

`P77_P77B_SOURCE_RECOVERED=TRUE | P77_P79_ISOLATION=NOT_CERTIFIED | PHASE_B=OPEN | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN`.
