#!/usr/bin/env bash
set -Eeuo pipefail
# R187: operator-invoked only. No image pull, package install, external network, or credentials.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
IMAGE="et665-pytest-offline:py312"
EVIDENCE="${ET665_EVIDENCE_DIR:-$(dirname "$ROOT")/et665-r187-evidence}"
EXPECTED_HEAD="${ET665_EXPECTED_HEAD:-}"
EXPECTED_IMAGE_ID="${ET665_EXPECTED_IMAGE_ID:-}"
if [[ ! "$EVIDENCE" = /* ]]; then echo "BLOCKED: evidence path must be absolute" >&2; exit 31; fi
if [[ -z "$EXPECTED_HEAD" || ! "$EXPECTED_HEAD" =~ ^[0-9a-f]{40}$ ]]; then echo "BLOCKED: ET665_EXPECTED_HEAD must be a verified 40-character commit SHA" >&2; exit 32; fi
if [[ ! "$EXPECTED_IMAGE_ID" =~ ^sha256:[0-9a-f]{64}$ ]]; then echo "BLOCKED: ET665_EXPECTED_IMAGE_ID must be an independently approved sha256 image ID" >&2; exit 43; fi
# Resolve parent paths before containment checks; reject symlinked evidence targets.
if [[ -L "$EVIDENCE" ]]; then echo "BLOCKED: symlinked evidence target" >&2; exit 27; fi
EVIDENCE_PARENT="$(cd "$(dirname "$EVIDENCE")" && pwd -P)" || { echo "BLOCKED: evidence parent missing" >&2; exit 28; }
EVIDENCE="$EVIDENCE_PARENT/$(basename "$EVIDENCE")"
# Evidence must be outside the read-only source mount to avoid nested writable mounts.
case "$EVIDENCE/" in "$ROOT/"*) echo "BLOCKED: evidence directory must be outside repository" >&2; exit 24;; esac
if [[ -e "$EVIDENCE" || -L "$EVIDENCE" ]]; then echo "BLOCKED: evidence directory already exists; use a fresh path" >&2; exit 25; fi
# Prevent an unexpected Docker daemon/context from silently selecting a remote host.
if [[ -n "${DOCKER_HOST:-}" || -n "${DOCKER_CONTEXT:-}" ]]; then echo "BLOCKED: explicit Docker remote/context override is not allowed" >&2; exit 34; fi
if [[ "$(id -u)" == "0" ]]; then echo "BLOCKED: host execution as root prohibited" >&2; exit 35; fi
if ! command -v docker >/dev/null 2>&1; then echo "BLOCKED: Docker unavailable" >&2; exit 20; fi
if [[ "$(docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null)" != "unix:///var/run/docker.sock" ]]; then echo "BLOCKED: Docker endpoint not approved local Unix socket" >&2; exit 36; fi
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then echo "BLOCKED: prebuilt local image $IMAGE unavailable; no pull attempted" >&2; exit 21; fi
if ! command -v sha256sum >/dev/null 2>&1; then echo "BLOCKED: sha256sum unavailable" >&2; exit 22; fi
if ! command -v python3 >/dev/null 2>&1; then echo "BLOCKED: python3 unavailable for JUnit validation" >&2; exit 38; fi
if ! command -v timeout >/dev/null 2>&1; then echo "BLOCKED: timeout unavailable for bounded test execution" >&2; exit 45; fi
# Validate immutable checkout BEFORE creating evidence output.
HEAD_ACTUAL="$(git -C "$ROOT" rev-parse --verify HEAD)" || { echo "BLOCKED: checkout HEAD unavailable" >&2; exit 26; }
if [[ "$HEAD_ACTUAL" != "$EXPECTED_HEAD" ]]; then echo "BLOCKED: checkout commit differs from ET665_EXPECTED_HEAD" >&2; exit 33; fi
if [[ -n "$(git -C "$ROOT" status --porcelain)" ]]; then echo "BLOCKED: checkout has tracked or untracked changes" >&2; exit 30; fi
# Ignored Python modules could still shadow imported code; fail closed on ignored .py files.
if [[ -n "$(git -C "$ROOT" ls-files --others --ignored --exclude-standard -- '*.py')" ]]; then echo "BLOCKED: ignored Python files in checkout" >&2; exit 37; fi
IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$IMAGE")" || { echo "BLOCKED: cannot resolve local image ID" >&2; exit 41; }
if [[ ! "$IMAGE_ID" =~ ^sha256:[0-9a-f]{64}$ ]]; then echo "BLOCKED: invalid local image ID" >&2; exit 42; fi
if [[ "$IMAGE_ID" != "$EXPECTED_IMAGE_ID" ]]; then echo "BLOCKED: local image ID differs from independently approved ET665_EXPECTED_IMAGE_ID" >&2; exit 44; fi
FILES=(
  mind_trader/tests/security_review/test_et665_r180_p15_dataset_path_guards.py
  mind_trader/tests/security_review/test_et665_r182_p15_rclone_allowlist.py
  mind_trader/tests/security_review/test_et665_r183_p15_pipeline_rclone_allowlist.py
  mind_trader/tests/security_review/test_et665_r184_mt5_status_truth.py
  mind_trader/tests/security_review/test_et665_r186_dependency_gates.py
  mind_trader/tests/security_review/test_et665_r196_junit_identity_gate.py
)
for f in "${FILES[@]}"; do
  if [[ ! -f "$ROOT/$f" ]]; then echo "BLOCKED: missing $f" >&2; exit 23; fi
done
(umask 077; mkdir "$EVIDENCE") || { echo "BLOCKED: cannot create fresh evidence directory" >&2; exit 29; }
chmod 700 "$EVIDENCE"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$EVIDENCE/started_utc.txt"
echo "$HEAD_ACTUAL" > "$EVIDENCE/commit.txt"
printf '%s\n' "$IMAGE_ID" > "$EVIDENCE/image_id.txt"
( cd "$ROOT" && sha256sum "${FILES[@]}" ) > "$EVIDENCE/test_sources.sha256"
# Do not pass secrets or the host network. Repo is read-only; only evidence output is writable.
set +e
timeout --signal=TERM --kill-after=15s 15m docker run --rm --pull=never --network=none --read-only --cap-drop=ALL \
  --security-opt=no-new-privileges --pids-limit=128 --memory=512m --cpus=1 \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,noexec,nosuid,size=128m \
  -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  -v "$ROOT:/workspace:ro" -v "$EVIDENCE:/evidence:rw" -w /workspace \
  --entrypoint python "$IMAGE_ID" -m pytest -q -p no:cacheprovider \
  --junitxml=/evidence/junit.xml "${FILES[@]}" > "$EVIDENCE/pytest.stdout.log" 2> "$EVIDENCE/pytest.stderr.log"
status=$?
set -e
# Exit code zero is insufficient: require a nonempty, well-formed JUnit result.
if [[ "$status" -eq 0 ]]; then
  if [[ ! -s "$EVIDENCE/junit.xml" ]]; then
    echo "BLOCKED: Docker returned success without JUnit evidence" >&2
    status=39
  elif ! python3 - "$EVIDENCE/junit.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
try:
    root = ET.parse(sys.argv[1]).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall(".//testsuite"))
    tests = sum(int(x.get("tests", "0")) for x in suites)
    failures = sum(int(x.get("failures", "0")) for x in suites)
    errors = sum(int(x.get("errors", "0")) for x in suites)
    skipped = sum(int(x.get("skipped", "0")) for x in suites)
    cases = root.findall(".//testcase")
    if root.tag not in ("testsuites", "testsuite") or not suites or tests < 1:
        raise ValueError("missing or empty JUnit suites")
    if tests != len(cases) or failures or errors or skipped:
        raise ValueError("JUnit counts inconsistent or nonpassing/skipped tests")
    expected = {
        "test_et665_r180_p15_dataset_path_guards",
        "test_et665_r182_p15_rclone_allowlist",
        "test_et665_r183_p15_pipeline_rclone_allowlist",
        "test_et665_r184_mt5_status_truth",
        "test_et665_r186_dependency_gates",
        "test_et665_r196_junit_identity_gate",
    }
    observed = {part for c in cases for part in (c.get("classname") or "").split(".")}
    if not expected.issubset(observed):
        raise ValueError("JUnit missing one or more exact regression module classnames")
    if any(c.find("failure") is not None or c.find("error") is not None or c.find("skipped") is not None for c in cases):
        raise ValueError("JUnit contains failed or skipped testcase")
except (ET.ParseError, OSError, ValueError, TypeError) as exc:
    print("BLOCKED: invalid or nonpassing JUnit evidence:", exc, file=sys.stderr)
    sys.exit(1)
PY
  then
    status=40
  fi
fi
printf '%s\n' "$status" > "$EVIDENCE/exit_code.txt"
date -u +'%Y-%m-%dT%H:%M:%SZ' > "$EVIDENCE/finished_utc.txt"
( cd "$EVIDENCE" && find . -maxdepth 1 -type f ! -name evidence.sha256 -print0 | sort -z | xargs -0 -r sha256sum ) > "$EVIDENCE/evidence.sha256"
if [[ "$status" -ne 0 ]]; then echo "R187 NOT CERTIFIED: pytest/docker exit $status"; exit "$status"; fi
echo "R187 TESTS COMPLETED: review JUnit, isolation settings and independent evidence before certification."
