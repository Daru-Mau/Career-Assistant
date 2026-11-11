#!/usr/bin/env bash
# Daily jobs pipeline entry point. Phase 0 runs guards and a no-op scan.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"

if [[ -n "${JOBS_DISABLED:-}" && "${JOBS_DISABLED}" != "0" ]]; then
  echo "jobs pipeline disabled via JOBS_DISABLED" >&2
  exit 3
fi

if [[ -f "$REPO/STOP" ]]; then
  echo "jobs pipeline disabled: STOP file present" >&2
  exit 3
fi

PYTHON="${PYTHON:-python3}"
exec timeout --signal=TERM 1800 "$PYTHON" -m scripts.jobs.cli scan "$@"
