## R826 — Source-only capability inventory integration (2026-11-23)

Historical source: P4.72B staging bridge, Git blob 8c20ed03bfe838bfafd94e7fd2eedfe9fc9e5775; R823 reconciliation preserved.
Protected source: app/runtime/capability_recovery_bridge.py on isolated branch engineering/r823-p472b-source-recovery-20261122.
Change: optional source_root allows AST parsing of the five allowlisted module files, reporting declared functions (including async) and classes, without importing or calling them. No opt-in permits active probing.
GitHub published source blob: b04fc26cc66940231d16bc4b425efedce5bd699a.
GitHub published test blob: afb95d5cfc80a127519eb422a6d0ee1a784db186.
Local command: python -B -m unittest discover -s tests -v.
Local results: 8 tests PASS in 0.007s, 0 failures; source used locally was a functionally equivalent independently assembled implementation (blob 9ba323deca8c63516eaa30bf562f059fbfaa7f04), NOT byte-identical to the published source. Published test blob matches local test.
Certification: local isolated behavioral tests PASS; byte-identical GitHub source execution NOT PROVEN. No repository-native integration or E2E certification. Existing R817 protections preserved; main and production untouched.
Next gate: execute published source and test together byte-identically; audit real consumer invocation and module path authority.
PAPER_ONLY=TRUE; REAL_ORDERS=FORBIDDEN; FTMO_REAL=FORBIDDEN; COST=R$0.
