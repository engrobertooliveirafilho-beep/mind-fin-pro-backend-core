# R265 — SQLite rollback reproduction

Actual offline run: `python -m unittest -v test_rollback` → **43/43 PASS**, 0.574s. Includes inherited test methods; one new explicit rollback reproduction.

Sequence: snapshot valid empty SQLite ledger; record signed run; overwrite ledger with prior snapshot; replay same signed run accepted as new. Both results return `certified=False`. This demonstrates that R264's fail-closed missing-ledger control does **not** prevent replacement by a valid older database.

Required next mitigation: independent monotonic state/externally anchored checkpoint or trusted append-only record with rollback detection. Do not represent a second replaceable local file as a secure external anchor. HP19 0/19. Main and production untouched.
