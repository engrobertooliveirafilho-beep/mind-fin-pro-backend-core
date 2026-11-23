# R836 — Reconciliação 58/58 (existência e identidade Git)
Data: 2026-11-22. Base: P4.64C histórico Drive, manifesto idêntico em GitHub main (R835).
Foram consultados individualmente os caminhos dos 58 módulos em GitHub main, em lotes; 58 retornaram Git blob SHA e conteúdo. R835 já havia verificado 16; R836 verificou os 42 restantes. A cobertura é de **existência e leitura de fonte**, não de funcionamento.
Buckets: ACTIVE_IN_PIPELINE=10/10, ACTIVE_IN_WHATSAPP_ADAPTER=2/2, ACTIVE_OUTSIDE_PIPELINE=22/22, ORPHANED_OR_UNUSED=24/24.
Anomalia: `app/humanization/social_dataset_builder.py`, `social_memory_provider.py`, `social_observation_layer.py`, `social_pattern_extractor.py` compartilham blob SHA `d6ccc147ced874867a0e6f91338fcc5920555be1` (5080 caracteres retornados). São quatro caminhos para conteúdo idêntico; **não** inferir quatro implementações independentes.
Duas entradas `__init__.py` do pacote eldora/memory e eldora/retrieval compartilham blob SHA `d3f5a12faa99758192ecc4ed3fc22c9249232e86` (2 caracteres).
Exemplos de motores/fontes confirmados: `app/modules/usde_core/scientific_knowledge_graph.py` blob `e91f0eb6333bffd91f146cbbbaf9c0ccd7fbbdc5`; `app/runtime/social_cognition_engine.py` blob `cd5117817e5640ac56ae0d15c980aeb103ea2d12`; `app/eldora/core/persistent_cognitive_graph.py` blob `8e0f2da738371cb0ad80fb258312afc1003227e7`; `app/workers/semantic_ingestion_worker.py` blob `2978f3cd55c2fe9a5a96eeb2768a18090875f59a`.
O manifesto é histórico; a presença de fonte em main não comprova execução, dependências, consumidores, certificação R817 nem E2E.
**Restrições:** nenhuma execução/importação dos 58 módulos; nenhum órfão promovido; main e produção intactas. Próximo passo: auditoria AST de dependências e chamadas e testes isolados dos componentes elegíveis.
