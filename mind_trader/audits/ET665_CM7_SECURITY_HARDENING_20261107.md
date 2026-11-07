# ET665.CM.7 — Correções adicionais e validação pendente

Revisão identificou e corrigiu dois riscos no stager: resolução prematura de links simbólicos na origem e possível alteração de arquivos entre cálculo do hash e cópia. A implementação agora rejeita raiz simbólica e grava os bytes previamente inspecionados. Adicionados sete testes comportamentais, além dos oito estruturais já publicados: **15 testes CM7 preparados, não executados**.

Validação sugerida: pytest isolado dos dois módulos CM7 com JUnit e hash, sem rclone, MT5, Drive ou suíte histórica. A importação de `mind_trader.security` deve ser testada com PYTHONPATH na raiz do repositório.

Acesso direto ao terminal Windows não disponível neste ambiente. O conector GitHub permite edição e leitura; nenhum runner de testes foi executado nesta etapa. GitHub Actions pode implicar consumo de minutos/custos e não foi acionado sem confirmação de gratuidade. 

PHASE_B=OPEN
CM7_TESTS=PENDING
REAL_ORDERS=FORBIDDEN
FTMO_REAL=FORBIDDEN
