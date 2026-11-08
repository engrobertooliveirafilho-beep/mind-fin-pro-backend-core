#!/usr/bin/env bash
set -Eeuo pipefail
# R187: operator-invoked only. No image pull, package install, external network, or credentials.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
IMAGE="et665-pytest-offline:py312"
EVIDENCE="${ET665_EVIDENCE_DIR:-$(dirname "$ROOT")/et665-r187-evidence}"
EXPECTED_HEAD="${ET665_EXPECTED_HEAD:-}"
if [[ ! "$EVIDENCE" = /* ]]; then echo "BLOCKED: evidence path must be absolute" >&2; exit 31; fi
if [[ -z "$EXPECTED_HEAD" || ! "$EXPECTED_HEAD" =~ ^[0-9a-f]{40}$ ]]; then echo "BLOCKED: ET665_EXPECTED_HEAD must be a verified 40-character commit SHA" >&2; exit 32; fi
# Resolve parent paths before containment checks; reject symlinked evidence targets.
if [[ -L "$EVIDENCE" ]]; then echo "BLOCKED: symlinked evidence target" >&2; exit 27; fi
EVIDENCE_PARENT="$(cd "$(dirname "$EVIDENCE")" && pwd -P)" || { echo "BLOCKED: evidence parent missing" >&2; exit 28; }
EVIDENCE="$EVIDENCE_PARENT/$(basename "$EVIDENCE")"
# Evidence must be outside the read-only source mount to avoid nested writable mounts.
case "$EVIDENCE/" in "$ROOT/"*) echo "BLOCKED: evidence directory must be outside repository" >&2; exit 24;; esac
if [[ -e "$EVIDENCE" || -L "$EVIDENCE" ]]; then echo "BLOCKED: evidence directory already exists; use a fresh path" >&2; exit 25; fi
# Prevent an unexpected Docker daemon/context from silently selecting a remote host.
if [[ -n "${DOCKER_HOST:-}" || -n "${DOCKER_CONTEXT:-}" ]]; then echo "BLOCKED: explicit Docker remote/context override is not allowed" >&2; exit 34; fi
if ! command -v docker >/dev/null 2>&1; then echo "BLOCKED: Docker unavailable" >&2; exit 20; fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then echo "BLOCKED: prebuilt local image $IMAGE unavailable; no pull attempted" >&2; exit 21; fi
if ! command -v sha256sum >/dev/null 2>&1; then echo "BLOCKED: sha256sum unavailable" >&2; exit 22; fi
(umask 077; mkdir "$EVIDENCE") || { echo "BLOCKED: cannot create fresh evidence directory" >&2; exit 29; }
chmod 700 "$EVIDENCE"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$EVIDENCE/started_utc.txt"
if ! git -C "$ROOT" rev-parse --verify HEAD > "$EVIDENCE/commit.txt"; then echo "BLOCKED: checkout HEAD unavailable" >&2; exit 26; fi
if [[ "$(cat "$EVIDENCE/commit.txt")" != "$EXPECTED_HEAD" ]]; then echo "BLOCKED: checkout commit differs from ET665_EXPECTED_HEAD" >&2; exit 33; fi
if [[ -n "$(git -C "$ROOT" status --porcelain --untracked-files=no)" ]]; then echo "BLOCKED: tracked source checkout is dirty" >&2; exit 30; fi
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
( cd "$EVIDENCE" && find . -maxdepth 1 -type f ! -name evidence.sha256 -print0 | sort -z | xargs -0 -r sha256sum ) > "$EVIDENCE/evidence.sha256"
if [[ "$status" -ne 0 ]]; then echo "R187 NOT CERTIFIED: pytest/docker exit $status"; exit "$status"; fi
echo "R187 TESTS COMPLETED: review JUnit, isolation settings and independent evidence before certification."
