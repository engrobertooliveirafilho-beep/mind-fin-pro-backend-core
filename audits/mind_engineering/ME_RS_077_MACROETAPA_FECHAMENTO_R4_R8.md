# ME-RS-077 — MACROETAPA ÚNICA DE FECHAMENTO R4–R8

**Status:** OPEN / FAIL-CLOSED. **Objetivo:** recuperar, integrar e certificar um pipeline R4→R5→R6→R7→R8 executável, determinístico, seguro e retomável. **Sem custos pagos, sem alterações em produção, sem ordens reais.**

## Base verificada
- R7 original SHA-256 `58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63`; executor corrigido em `code/engineering_pipeline/post_r6.py`.
- Windows ME-RS-074: 7/7 regressões sintéticas PASS, log SHA-256 informado `FF0478E3D5D7061B3241DB68803144D1647F839C217CBCFCAD1CD66ABF2F612D`. Não equivale a integração histórica.
- ZIP ME-RS-067 SHA-256 `b15db9f692e73a20558921a578e5764b324fe53e3e464b6db87a2ef45e39c3b5`; 50/50 candidatos R8 íntegros. A versão `008_local_bridge_v2_integrity_candidate.py` detecta mudança de conteúdo com mesmo tamanho e mtime; teste legado 044 precisava de expectativa corrigida.
- R8 checkpoint histórico 11/32: ainda sem reprodução/autoridade comprovadas.

## Plano fechado, sem microetapas independentes
1. **Autoridade e proveniência:** inventariar executores originais R4–R8, hashes, dependências, checkpoints e políticas; escolher um único caminho de execução, sem criar motor duplicado.
2. **Reparos mínimos:** manter original imutável; corrigir somente bugs reproduzidos em branch isolada; adicionar testes regressivos.
3. **Integração histórica:** executar com dados R4/R5/R6 reais ou fixtures com proveniência explícita; validar invariantes de contagem, linhagem, hashes, autoridade e decisões PENDING.
4. **Crash/restart:** interromper em checkpoints controlados, simular journal parcial/corrompido, reexecutar e provar idempotência, rollback e nenhuma promoção indevida.
5. **Certificação reproduzível:** uma suíte offline única, logs integrais, hashes dos artefatos, commits, matriz de requisitos e relatório final com PASS/FAIL/NOT_RUN; nenhum PASS inferido.
6. **Consolidação:** publicar código, testes e evidências no GitHub; Drive permanece fonte histórica imutável; PR somente pode sair de draft após gates 1–5.

## Regras de encerramento
- **PASS** somente se todos os gates críticos forem executados e evidenciados no mesmo snapshot de commit, sem regressão de segurança.
- **BLOCKED** se faltar fonte original, autoridade, integridade, dados históricos ou ambiente isolado.
- **FAIL** em divergência de linhagem, corrupção não tratada, perda/duplicação, alteração de fonte ou promoção não autorizada.
- Não executar operação financeira real, nem modificar produção ou Drive.
- Evitar novas missões de auditoria atomizadas: consolidar resultados sob este identificador até decisão final.

**Próxima ação concreta:** localizar no pacote R8 o executor e o journal que correspondem ao checkpoint 11/32, recuperar fonte R4/R5 e executar a suíte offline integrada em um único lote.
