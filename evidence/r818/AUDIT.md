# R818 — Isolated regression import correction
Date: 2026-11-22.

R817 original file and test were read back from GitHub. R817 test used `from app.runtime import capability_recovery_bridge as m`, which can trigger package initialization. R818 changes only the test import mechanism to `importlib.util.spec_from_file_location` using the explicit original source path. The runtime source and MAIN are unchanged.

Local Python unittest: **12/12 PASS**, executed against a manually reconstructed, behaviorally equivalent R817 module and equivalent tests. This is not byte-identical GitHub-source execution. Original published test file was updated and read back; repo-native integrated execution remains pending.

HP19 historical 19/19 stub recovery, R809 engines and R811–R817 safety changes were not reworked. No agent functional certification, no E2E, no deployment.

`R818_LOCAL_REPRO=12/12_PASS | REPO_NATIVE_TEST=PENDING | MAIN=INTACT | COST=R$0`
