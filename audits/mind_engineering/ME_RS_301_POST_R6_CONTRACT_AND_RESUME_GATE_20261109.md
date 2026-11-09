# ME-RS-301 — POST_R6 source contract and isolated completion gate (2026-11-09)

Status: SOURCE_CONTRACT_VERIFIED / LOCAL_FULL_REPLAY_NOT_EXECUTED / R8_BLOCKED.

## Evidence
Authenticated GitHub read of `code/engineering_pipeline/post_r6.py` on draft PR #4 HEAD `d75aa9c7ee62733cc04c62c72a9686374c2b1153`. User-supplied Windows reports R96–R110: 16 PASS, 0 FAIL; 127004 R6 source lines; recovered SQLite 124491 rows; remaining 2513 lines; source SHA256 `39812eeaf59a87a22d998d89e81341cb6197d1306ed91e86257975a4c4621b59`. Original local code SHA256 reported `58e559debb6181b4a34f857572a3fd1c84f1994def82637ad696106aaecd9d63`. These local hashes have not been independently re-read in this GitHub session.

## Verified consume contract
`consume(source, db_path, approval_path=None, limit=1000)`. It validates source binding and SHA256 of prefix bytes, reads complete newline-terminated JSONL rows, validates exact keys `stage,seq,r5_seq,r4_sha256,r5_sha256`, `stage=R6`, strict sequential integers, and 64-hex lineage hashes. `r6_sha256=SHA256(raw JSONL line including newline)`. It writes `records(r6_sha256,seq,r4_sha256,r5_sha256,decision,authority)` and `cursor(source,offset,prefix_sha256,seq)` in one SQLite transaction, using WAL. `approval_path=None` creates an empty approval map; new rows are PENDING with NULL authority; no automatic promotion. Explicit approval manifests are validated and lineage mismatches rejected. The patched PR #4 version also rejects late-approval lineage mismatches. `limit=2513` is a bounded one-shot consume call; `main()` is not appropriate for this isolated replay because it loops unless `--once` is specified.

## Safe replay criteria
1. Verify source and original code SHA256 and exact GitHub source equivalence before execution.
2. Create a fresh SQLite backup from the recovered database; never operate on the original or recovered copy.
3. Confirm 124491 rows, exact prefix cursor, integrity_check and full historical record mapping.
4. Execute one bounded call with `approval_path=None, limit=2513` against the fresh copy only, after verifying module side effects and isolation.
5. Require result processed=2513, promoted=0, total=127004, pending=127004, approved=0; verify all 127004 rows against raw JSONL bytes and lineage fields; require final cursor offset=file size and prefix hash=full source SHA256; require repeat call processed=0.
6. Verify original source and database unchanged. WAL/SHM are transient; do not use SHM hash as proof of data mutation.
7. If any check fails, BLOCKED; do not activate R8, real orders, FTMO real or production.

## Separate certification boundaries
R96–R110 certifies only the 124491-row isolated recovered copy, not the remaining 2513 rows. ME-RS-074's seven synthetic tests are user-executed, not independently reproduced CI. ME-RS-076 R8 archive tests do not certify original R8 checkpoint/journal or R6→R7→R8 integration. PR #4 stays draft, no merge. Cost R$0.
