# ET665.R182 — P15 subprocess allowlist hardening (2026-11-08)

## Achado
A inspeção integral dos executores P15.16 e P15.25B identificou que `cmd(c)` usava `shlex.split()` sobre uma string contendo o destino local. Em Windows, o parser POSIX pode consumir barras invertidas do caminho. Além disso, o contrato aceitava qualquer origem com prefixo `gdrive:` e não fixava o destino local nem a lista completa de argumentos.

## Correção publicada
Nos dois executores:
- `cmd(args)` agora exige uma lista/tupla de argumentos.
- A única chamada permitida é exatamente `["rclone", "copy", REMOTE_NORM, str(DATA), "--progress"]`.
- Origem remota, destino local e flags são comparados integralmente com os valores aprovados.
- `subprocess.run` recebe argv diretamente com `shell=False`; não há parsing de shell nem `shlex.split()`.
- A chamada em `run()` foi convertida para argv, preservando barras invertidas de caminhos Windows.
- Nenhuma transferência, subprocesso, rede, MT5 ou broker foi executado nesta alteração.

## Regressões adicionadas
Arquivo: `mind_trader/tests/security_review/test_et665_r182_p15_rclone_allowlist.py`.
- 2 casos de argv autorizado com subprocesso mockado.
- 8 casos de rejeição de origem, destino, flag adicional e alvo remoto adulterados.
- 2 casos de rejeição de string shell.
- Total: 12 cenários parametrizados; **publicados, NÃO EXECUTADOS**.

## Commits e escopo
- P15.16: `b15d6fb8793a6b0fae05050bceaa29c8f57395c5`.
- P15.25B: `5315952bbfa0698aab8e04846c0441626cf08817`.
- Testes R182: `2b9c7fbfc8105af4208526bd8ecc5f1e1e632600`.
- Branch: `audit/et665-r180-p15-dataset-path-guards-20261108`.

## Verificação pendente
Executar R180 + R182 no Docker offline autorizado. Confirmar os casos de caminho Windows e symlink no host real. Não declarar PASS com base apenas na publicação. A auditoria não prova isolamento global de rede/OS nem segurança de toda a árvore de subprocessos.

`PHASE_B=OPEN | TESTS=NOT_EXECUTED | MAIN=UNCHANGED | PRODUCTION=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0.00`
