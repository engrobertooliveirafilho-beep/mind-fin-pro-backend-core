# STEP455 — execução real canônica e correção HTTP

2026-11-21 — Origem Drive: `1l7kOqe6zH_vnRiM_X8Zd5zNl3oIgVdGt`. Caminho original recuperado `app/embeddings/vector_index_step455/engine.py`.

**Teste offline executado**: `python -m unittest discover -s tests -v` → **8/8 PASS**, 0 falhas, 0.015 s. Log SHA-256 `7fd4ef8e3254d990379bacd4bce2f4543e2f7988091ad6fde85cc33f76b3cead`.

**Integridade byte-identical (git hash-object local = GitHub):**
- Motor: `543e136a856f7a3a54c6d07201b5c83e59037e4c`
- Testes: `acb608407fe1c65a7ecc09a1f34f8aed69c1c0cb`

Correção funcional: o limite de 4096 shards antes lançava `ValueError` em endpoint FastAPI (potencial HTTP 500). Agora lança `HTTPException(status_code=422)` para entrada excedente. A suite verifica a semântica do status. Motor não cria índice nem executa operações de mercado; apenas planeja.

**Certificação:** suíte unitária real de fonte canônico aprovado; **não** certifica rota HTTP E2E, integração com serviços, Trader S20/S21, ou broker PAPER.

`MAIN=INTACTA | PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
