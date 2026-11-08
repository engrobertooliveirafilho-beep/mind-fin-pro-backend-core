# ET665.R60 — revisão de fonte e bloqueios (2026-11-08)

Fonte verificada diretamente: commit 016a7ee67889694a11d22ef7be3106226bfad9f0, arquivos `mind_trader/security/et665_r60_drive_git_reconciliation.py` e `mind_trader/tests/security_review/test_et665_r60_drive_git_reconciliation.py`.

## Confirmado por inspeção
- Comparador offline, CSV explícitos, SHA-256 exigidos para os dois manifestos; não acessa Drive nem broker.
- Saída diferencia MATCH, DRIVE_ONLY, GIT_ONLY e CONTENT_MISMATCH e não certifica equivalência semântica ou autoridade integral do Drive.
- Cinco testes de regressão existentes cobrem match, divergência de hash, caminhos sem mapeamento, mapeamento explícito e duplicidade de caminho.

## Pendências e riscos
- Testes ainda não executados nesta intervenção; não declarar CURRENT_PASS.
- CSV de mapeamento opcional não tem SHA-256 esperado, portanto sua integridade/proveniência não está fixada pelo contrato CLI.
- `size_bytes` é comparado como texto, sem validação de inteiro não negativo; normalização/validação do schema requer regressão adicional.
- O programa cria o diretório de saída antes de gravar os dois relatórios; falha de escrita pode deixar artefatos parciais. Executar em workspace descartável, sem segredos e sem rede.
- A equivalência entre manifestos fornecidos não prova completude do Drive nem funcionamento do runtime. Não promover para certificação global.

## Próximo gate
Executar os cinco testes existentes em sandbox offline; recuperar os manifestos R59/Drive e seus hashes; validar cobertura, proveniência e mapeamentos; só então avançar R58 (isolamento SO e revisão de segurança).

`PHASE_B=OPEN | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | NO_MERGE`
