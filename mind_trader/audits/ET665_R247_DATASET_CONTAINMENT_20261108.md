# ET665.R247 — P15.25 dataset containment

Date: 2026-11-08. Parent R246. Isolated draft PR #18.

## Confirmed source issue
P15.25 `load_dataset(name)` previously combined untrusted `edge["dataset"]` with three allowed directory names using `Path(root)/name`, then opened the first existing path. Absolute paths, `..` and symlinks could escape those directories. This is a source-level path containment issue; exploitation was not demonstrated.

## Correction
The loader now rejects empty, non-string and absolute references, resolves each candidate, and checks `target.is_relative_to(root.resolve())` before opening. This also rejects symlink escapes. The change is limited to the P15.25 research dataset loader; other loaders remain unaudited.

## Tests
Added `test_et665_r247_dataset_containment.py` with four offline scenarios: absolute path, parent traversal, non-string reference and symlink escape. **TESTS PUBLISHED, NOT EXECUTED**. Symlink scenario skips where symlink creation is unsupported.

## Certification
No Docker execution, CI PASS, JUnit/SHA-256 evidence, independent review, downstream consumer proof, MT5 isolation, R113 or R60 reconciliation. Fase B 0/16, HP19 0/19. PR remains draft, no merge, production unchanged. REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
