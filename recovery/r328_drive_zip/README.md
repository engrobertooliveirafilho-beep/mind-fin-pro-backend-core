# R328 — Recuperação do inventário ZIP no Drive (PAPER_ONLY)

**Fonte de verdade:** Drive, somente leitura. **Destino de evidências:** GitHub, após auditoria explícita. Não envia ordens nem expõe credenciais.

## Uso local no Windows (rclone previamente autenticado)
```powershell
python recovery/r328_drive_zip/recovery_pipeline.py --inventory "D:\MIND_TEMP\inventario.zip" --member "PARTITION_METADATA.csv" --remote "gdrive:MIND" --output "D:\MIND_TEMP\R328_RECOVERY" --limit 20
python -m pytest -q recovery/r328_drive_zip/test_recovery_pipeline.py
```

O inventário CSV precisa ter `path` ou `remote_path` (caminho relativo ao remote), e opcionalmente `sha256` com hash histórico independente. Se o ZIP contiver mais de um CSV, indique `--member`. **Não presumir** que `PARTITION_METADATA.csv` possui SHA ou que o caminho indicado corresponde ao prefixo remoto. Verificar o esquema e autoridade antes de execução em massa.

Cada linha recuperada gera evento persistente em `recovery_ledger.jsonl` (com flush+fsync), SHA calculado e estado `verified`, `unverified`, `failed` ou `skipped`. Sem SHA independente, nunca recebe `verified`. Falhas e divergências não são promovidas. Arquivos são baixados para staging e movidos atomicamente após checagem. O `report.json` resume a tentativa, não comprova publicação remota.

**Critério de fechamento:** (1) inventário e ZIP identificados, (2) cardinalidade integral reconciliada, (3) hashes independentes conferidos, (4) artefatos e ledger enviados a uma branch GitHub sem segredos ou dados excessivos, (5) commit SHA, leitura de retorno e CI registrados no Ledger Mestre. Este commit contém somente **o motor e seus testes**, não o ZIP recuperado, nem prova de conclusão do acervo.

**Limites:** `--limit` restringe a recuperação; execução interrompida requer reconciliação de ledger antes de retomar; este motor não faz publicação Git automática, pois a publicação exige gate separado. R$0,00; fail-closed.
