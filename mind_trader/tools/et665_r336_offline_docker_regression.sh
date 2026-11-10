#!/usr/bin/env bash
# ET665.R336 — offline Docker regression; run only from a checked-out repository.
set -Eeuo pipefail
umask 077
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
EVIDENCE="${1:-${TMPDIR:-/tmp}/et665_r336_evidence}"
mkdir -p "$EVIDENCE"
EVIDENCE="$(cd "$EVIDENCE" && pwd -P)"
IMAGE="python:3.11"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "FAIL_CLOSED: cached Docker image python:3.11 missing; no pull attempted" >&2
  exit 20
fi
git rev-parse HEAD > "$EVIDENCE/commit.txt"
git status --porcelain > "$EVIDENCE/worktree_status.txt"
if [ -s "$EVIDENCE/worktree_status.txt" ]; then
  echo "FAIL_CLOSED: worktree is not clean" >&2
  exit 21
fi
sha256sum mind_trader/app/p1519_p1525_institutional_research_certification/engine.py \
  mind_trader/tests/security_review/test_et665_r332_causal_fill_gate.py \
  mind_trader/tests/security_review/test_et665_r334_synthetic_reconstruction_e2e.py \
  > "$EVIDENCE/source_sha256.txt"
set +e
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 128 --memory 256m --cpus 1 \
  --tmpfs /tmp:rw,noexec,nosuid,size=32m \
  --mount "type=bind,src=$ROOT,dst=/work,readonly" \
  --workdir /work "$IMAGE" \
  python -B -m unittest -v \
  mind_trader/tests/security_review/test_et665_r332_causal_fill_gate.py \
  mind_trader/tests/security_review/test_et665_r334_synthetic_reconstruction_e2e.py \
  > "$EVIDENCE/unittest.log" 2>&1
STATUS=$?
set -e
printf '%s\n' "$STATUS" > "$EVIDENCE/exit_code.txt"
sha256sum "$EVIDENCE"/*.txt "$EVIDENCE"/*.log > "$EVIDENCE/evidence_sha256.txt"
cat "$EVIDENCE/unittest.log"
if [ "$STATUS" -ne 0 ]; then
  echo "R336=FAIL_CLOSED; no certification granted"
  exit "$STATUS"
fi
echo "R336=2_TEST_MODULES_PASS; not HP19 or Phase B certification"
