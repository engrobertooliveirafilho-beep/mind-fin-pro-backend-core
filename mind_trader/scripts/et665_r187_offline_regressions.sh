#!/usr/bin/env bash
set -Eeuo pipefail
# R187: operator-invoked only. No image pull, package install, external network, or credentials.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
IMAGE="et665-pytest-offline:py312"
EVIDENCE="${ROOT}/.et665-r187-evidence"
if ! command -v docker >/dev/null 2>&1; then echo "BLOCKED: Docker unavailable" >&2; exit 20; fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then echo "BLOCKED: prebuilt local image $IMAGE unavailable; no pull attempted" >&2; exit 21; fi
if ! command -v sha256sum >/dev/null 2>&1; then echo "BLOCKED: sha256sum unavailable" >&2; exit 22; fi
mkdir -p "$EVIDENCE"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$EVIDENCE/started_utc.txt"
git -C "$ROOT" rev-parse HEAD > "$EVIDENCE/commit.txt"
docker image inspect --format '{{.Id}}' "$IMAGE" > "$EVIDENCE/image_id.txt"
FILES=(
  mind_trader/tests/security_review/test_et665_r180_p15_dataset_path_guards.py
  mind_trader/tests/security_review/test_et665_r182_p15_rclone_allowlist.py
  mind_trader/tests/security_review/test_et665_r183_p15_pipeline_rclone_allowlist.py
  mind_trader/tests/security_review/test_et665_r184_mt5_status_truth.py
  mind_trader/tests/security_review/test_et665_r186_dependency_gates.py
)
for f in "${FILES[@]}"; do
  if [[ ! -f "$ROOT/$f" ]]; then echo "BLOCKED: missing $f" >&2; exit 23; fi
done
( cd "$ROOT" && sha256sum "${FILES[@]}" ) > "$EVIDENCE/test_sources.sha256"
# Do not pass secrets or the host network. Repo is read-only; only evidence output is writable.
set +e
docker run --rm --pull=never --network=none --read-only --cap-drop=ALL \
  --security-opt=no-new-privileges --pids-limit=128 --memory=512m --cpus=1 \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=128m \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  -v "$ROOT:/workspace:ro" -v "$EVIDENCE:/evidence:rw" -w /workspace \
  "$IMAGE" python -m pytest -q -p no:cacheprovider \
  --junitxml=/evidence/junit.xml "${FILES[@]}" > "$EVIDENCE/pytest.stdout.log" 2> "$EVIDENCE/pytest.stderr.log"
status=$?
set -e
printf '%s\n' "$status" > "$EVIDENCE/exit_code.txt"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$EVIDENCE/finished_utc.txt"
( cd "$EVIDENCE" && sha256sum *.txt *.log *.xml 2>/dev/null || true ) > "$EVIDENCE/evidence.sha256"
if [[ "$status" -ne 0 ]]; then echo "R187 NOT CERTIFIED: pytest/docker exit $status"; exit "$status"; fi
echo "R187 TESTS COMPLETED: review JUnit, isolation settings and independent evidence before certification."
