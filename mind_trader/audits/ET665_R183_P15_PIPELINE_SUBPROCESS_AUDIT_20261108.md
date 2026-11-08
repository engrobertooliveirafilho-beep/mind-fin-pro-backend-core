# ET665.R183 — P15 pipeline subprocess audit (2026-11-08)

## Scope and method
Read-only inspection of source files from the isolated review branch. The repository's recursive Git tree response reported 52,479 entries and `truncated=true`; therefore it is not a complete repository inventory. The focused review covered the P15/P16 engines listed below, not every dependency or route.

## Newly identified CM.2 pattern
Two additional P15 engines retained the earlier permissive `shlex.split()` command wrapper:
- `app/p153_p155_profit_market_data_pipeline/engine.py`: copied `REMOTE_RAW` into `RAW`.
- `app/p156_p1510_real_edge_research_runtime/engine.py`: copied `REMOTE_NORM` into `DATA`.

Both accepted any `gdrive:` source and did not pin the exact local destination or complete argv. Their command strings also passed Windows paths through POSIX-style `shlex.split()`.

## Remediation published
Both wrappers now:
- accept only list/tuple argv;
- allow only the exact `rclone copy <declared remote> <declared local target> --progress` argument sequence;
- reject altered source, target, extra flags, remote destination, and shell-string inputs;
- call `subprocess.run(argv, shell=False, capture_output=True, text=True, check=True)`.

Call sites were changed to pass argv directly. No Rclone transfer, subprocess, network request, MT5 connection, broker interaction, Drive write, or production action was performed.

## Regression suite
Added `tests/security_review/test_et665_r183_p15_pipeline_rclone_allowlist.py`.
- 2 accepted-command cases with mocked subprocess.
- 8 mutated-command rejection cases.
- 2 shell-string rejection cases.
- 12 parametrized scenarios total; **published, NOT EXECUTED**.

## Evidence
- P153–P155 engine commit: `d06377a8a7323e7e0f4fadce8df5ae601d084105`.
- P156–P1510 engine commit: `d8df11a59ee4c1d0cd08296203e360660fc1c811`.
- R183 test commit: `75142a5e23c5631b2e74a9fa65ddf14e7b45212d`.
- Branch: `audit/et665-r180-p15-dataset-path-guards-20261108`.

## Remaining limits
This is a targeted source audit, not proof of complete P15/P16 subprocess or network coverage. The full recursive tree was truncated. Other P15/P16 dependencies and scripts remain to be enumerated and classified. The new tests and prior R180/R182 suites require execution in the user's approved offline Docker environment.

`PHASE_B=OPEN | TESTS=NOT_EXECUTED | INVENTORY=PARTIAL | MAIN=UNCHANGED | PRODUCTION=UNCHANGED | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0.00`
