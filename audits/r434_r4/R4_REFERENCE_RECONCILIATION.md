# R434 — R4 mass-conversion certification gate

Source: local R401 audit of PARTITIONS ZIP and R401_SOURCE_RECOVERY_QUEUE.csv, queue SHA256 ed4d5af07f4a628f21fd36619f8d386b4f8b382142fbe0fa572258016646f552.

- 277405 R4 inventory records (historical R401 inventory).
- 4345 name-based engine candidate references, each with Drive ID; **not** 4345 working engines.
- 1128 distinct path labels; 334 singleton labels; 794 repeated labels; 3217 additional references sharing a label.
- Largest collision: engine.py occurs 349 times. Labels are insufficient to deduplicate; distinct paths may still be the same bytes, and identical names may represent different code.
- R4 ZIP is inventory metadata, not source bytes. SHA256, dependencies, runtime, predecessor, GitHub commit and tests must be verified per source.
- Historical MIND memory agent was recovered in R429, but its 3 archived copies are equivalent; R431 identified preexisting work and duplication.
- The anti-rework CI from R433 remains staging-only and not proven required by branch protection.
- No mass conversion, mass tests or certification claimed. Fail-closed; zero paid services; PAPER_ONLY; no live orders.

Mandatory sequence: (1) reconcile each reference with GitHub existing code and historical lineage; (2) fetch missing source from authoritative Drive path; (3) compute SHA256 and dependency graph; (4) test original in isolation without stubs; (5) integrate only validated nonduplicate modules with regression tests and evidence; (6) record ledger and commit. Do not count reference rows as engines.

Certification: R4_ALL_MOTORS_FUNCTIONAL=FALSE; R4_GLOBAL_COVERAGE=UNKNOWN.
