# ET-664 — Fase A: inventário local e limitações

Data: 2026-11-05. Branch isolada, sem alteração em main.

## Evidência local
- Arquivo de origem: ELDORA TRADER(3).zip
- SHA-256: 4e96276cd9915532956217572b0cb1dfe17a08b662f35ab5ad4dc7a0f8c75ce7
- Entradas de arquivo processadas recursivamente: 199
- Arquivos ZIP aninhados: 5
- Entradas com SHA-256 calculado: 199
- Entradas rejeitadas/ignoradas: 0
- Testes unitários do inventariador: 3/3 PASS (hash, ZIP aninhado, path traversal)

## Limites de certificação
Esta evidência confirma apenas os bytes do pacote recebido, não os hashes esperados dos originais no Drive, nem a autoridade canônica do código. Não foram certificados os requisitos 01–08 integralmente. Não houve alteração de motores de trading nem execução de ordens.

## Pendências Fase A
1. Reconciliação integral de 382 requisitos com código/testes.
2. Inventário GitHub não truncado de todas as branches relevantes.
3. Confronto do Drive histórico por ID e SHA-256.
4. Recuperação dos executores e dependências originais.
5. Testes originais em ambiente isolado.

Estado: FASE_A=PARCIAL; PROVENIENCIA_LOCAL=PASS; GATE_A=BLOCKED.
