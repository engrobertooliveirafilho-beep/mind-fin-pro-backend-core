# ET665.R60 — revalidação exata dos blobs GitHub (2026-11-08)

Branch: `audit/et665-r59-full-git-blob-inventory-20261108`
Commit contendo os três arquivos: `3b5665bd967cecc4d0a57ed2c8c188716c1a29dc`

Hashes Git blob verificados no runtime local contra os blobs lidos pelo conector GitHub:
- `mind_trader/security/et665_r60_drive_git_reconciliation.py`: `40f9960773303160f837fafe645811bcc723c779`
- `mind_trader/tests/security_review/test_et665_r60_drive_git_reconciliation.py`: `f6e91b3599f5ce1e238787bcce87eb379f39b3f8`
- `mind_trader/tests/security_review/test_et665_r60_hardening.py`: `d6758a2445573dbb77a9e7ab653de85cfc0baaed`

Comando: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider --junitxml=R60_GITHUB_EXACT_JUNIT_20261108.xml test_et665_r60*.py`

Resultado: **12 passed**; JUnit: tests=12, errors=0, failures=0.
JUnit SHA-256: `eeffd739dc4057c68d836216a2134f405c4aad7611d01f605efdb8592c1970c0`.

Escopo: CSV sintéticos locais; não houve acesso a Drive, corretora ou MT5. Esta execução não atesta sandbox de SO, origem dos manifestos, equivalência histórica ou revisão independente. JUnit gerado localmente; não anexado ao GitHub nesta publicação.

`R60_TESTS=12_PASS | DRIVE_GIT_EQUIVALENCE=NOT_CHECKED | R58=OPEN | PHASE_B=OPEN | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN`
