# ET665.R60 — execução de regressões em 2026-11-08

Fonte: PR #6, HEAD `9b40f34ed7f00bb09b7912c58923953aece18beb`.

## Resultado local
- Regressões originais R60: **5/5 PASS** (pytest no ambiente de execução do assistente).
- Correção preparada em cópia local: SHA-256 de mapping obrigatório, size_bytes validado como inteiro não negativo, escrita em staging seguida de rename.
- Suite corrigida: **12/12 PASS** (5 regressões originais, 7 negativas adicionais).
- Ambiente: Python local, arquivos sintéticos CSV, sem Drive, MT5, broker, credentials, rede acessada pelo código. Não é atestação de isolamento de sistema operacional.
- JUnit e fontes preservados no ambiente de execução do assistente; sem declaração de upload das evidências ao GitHub.
- Limites: manifesta autoridade Drive não verificada; hashes originais Git e Drive não reconciliados; R58.1/R58.2/R58.3 permanecem abertos; independente não certificou.

## Gates
`R60_ORIGINAL=5_PASS | HARDENED_LOCAL=12_PASS | R58=OPEN | PHASE_B=OPEN | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | MAIN=UNCHANGED`.
