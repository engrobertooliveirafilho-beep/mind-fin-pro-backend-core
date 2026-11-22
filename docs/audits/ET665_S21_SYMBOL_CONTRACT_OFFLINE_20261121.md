# ET665 — S21 symbol lineage offline regression

## Authority recovered from Google Drive
- `TRADER_S21_R13_R2D_R6_R5_R2_R1_FINAL_REPORT.txt`, Drive id `1v-kYhMR-ferb9dI-JfbvhUgl47vVYti8`: canonical writer resolved but symbol incapable; S20 symbol absent; S21 not certified.
- Original historical factory SHA256 `3E4A66308FDF69BEEC2A1DE3309C68A14F8AD285787CD63EAF56A0FB237B7C42`. This historical SHA is NOT a hash of the current patched GitHub factory.

## Executed offline regression
2026-11-21. Original contract content read from GitHub isolated branch, copied into a local Python file, and tested with pytest.
`python -m pytest -q` → **15 passed in 0.06s**.
- source SHA256 `2ea1f3d1a7dd2cfd6ae3f73b42fd06b3be2e5250afb3daf9401ed562e522917d`
- test SHA256 `a015d40ccf95fefbc49a16da384e95494c1e6ab520b1b4ab5806c816d839b08f`
- log SHA256 `1bcc44011bf78a58bc505eb612ef283786f7b4e7ea8747b915963e5b06958e4c`
- Local artifacts `/mnt/data/et665_s21_validation/`.
- Tests cover valid replay→dispatch→writer, replay invalid symbols, dispatch conflict, writer invalid symbols, writer conflict.

## Certification boundary
This tests the isolated source copied from GitHub; it does NOT test the original canonical writer, institutional factory, full S20 replay, realized outcome ledger, or S21 E2E. Do not change historical S20 ledger or claim certification.
`PAPER_ONLY=TRUE | REAL_ORDERS=FORBIDDEN | E2E_CERTIFIED=FALSE | COST=R$0`
