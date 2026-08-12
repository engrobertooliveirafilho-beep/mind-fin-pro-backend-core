from pathlib import Path

out = Path("reports/P5.6G29_PEDIGREE_RECONCILIATION")
out.mkdir(parents=True, exist_ok=True)

pto = r"""
# PTO — P5.6G30 CONTROLLED PEDIGREE MUTATION EXECUTION

## STATUS DE ENTRADA

P5.6G29 concluído em modo PLAN_ONLY.

Nenhuma mutação foi executada.

## EVIDÊNCIA PRIMÁRIA

Fonte:

http://members.americanbuckingbull.com/bulls.aspx?id=10058008

ABBI Competition Animal Pedigree:

- Animal: Bushwacker
- ABBI#: 10058008
- Sire: REINDEER MO
- Sire ABBI#: 10010628
- Dam: 110
- Dam ABBI#: 10007793

## ESTADO ATUAL DO BANCO

Bushwacker existe:

- official_name: Bushwacker
- registry_number: 13/6
- validation_status: reliable

Pais ABBI não existem:

- REINDEER MO: missing
- 110: missing

Edges atuais conflitantes:

- Whitewater Skoal -> Bushwacker
  - relation: sire
  - validation_status: provisional
  - evidence_source_id: null

- Lady Luck -> Bushwacker
  - relation: dam
  - validation_status: provisional
  - evidence_source_id: null

## DECISÃO

Não promover automaticamente.

Executar somente com aprovação explícita.

## OBJETIVO P5.6G30

Executar mutação controlada para:

1. Criar entidade REINDEER MO.
2. Criar entidade 110.
3. Quarentenar edges provisionais sem fonte:
   - Whitewater Skoal -> Bushwacker
   - Lady Luck -> Bushwacker
4. Criar edges ABBI:
   - REINDEER MO -> Bushwacker / sire
   - 110 -> Bushwacker / dam
5. Gerar snapshot antes/depois.
6. Validar que não há self-parent.
7. Validar que Bushwacker tem no máximo um sire ativo e uma dam ativa.

## PROIBIÇÕES

- Não apagar registros.
- Não alterar fontes antigas.
- Não promover edge sem source.
- Não usar snippets de busca como evidência.
- Não executar se Bushwacker não resolver para ID único confiável.
- Não executar se REINDEER MO ou 110 já existirem duplicados.

## STATUS ESPERADO

P5.6G30_READY_FOR_APPROVAL
"""

(out / "P56G30_CONTROLLED_PEDIGREE_MUTATION_PTO.md").write_text(
    pto.strip(),
    encoding="utf-8"
)

print(pto)
