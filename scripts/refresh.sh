#!/usr/bin/env bash
# Refresh the OpenCity database: fetch the sources that are due, then write CSV exports.
#
#   scripts/refresh.sh                 # sources whose refresh interval has elapsed (what cron runs)
#   scripts/refresh.sh --all           # every enabled source now
#   scripts/refresh.sh -s smc_swm      # one source (repeatable)
#   scripts/refresh.sh --force         # ignore intervals and re-download already-seen documents
#   scripts/refresh.sh --no-export     # skip writing data/export/*.csv
#
# Safe to run from cron: only one refresh runs at a time (flock), output goes to
# data/logs/refresh-YYYY-MM-DD.log, and the exit code is non-zero if any source failed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${OPENCITY_DATA_DIR:-$ROOT/data}"
PY="${PYTHON:-python3}"
LOG_DIR="$DATA_DIR/logs"

usage() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; }

mode=(--due)
extra=()
do_export=1
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) mode=() ;;
    --due) mode=(--due) ;;
    -s|--source) [[ $# -ge 2 ]] || { echo "missing source id after $1" >&2; exit 2; }
                 extra+=(--source "$2"); mode=(); shift ;;
    --force) extra+=(--force) ;;
    --no-export) do_export=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
  shift
done

# --- preflight ---------------------------------------------------------------
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
  || { echo "python 3.9+ required (set PYTHON=...)" >&2; exit 2; }
command -v pdftotext >/dev/null || echo "warning: pdftotext not found (apt install poppler-utils); PDF sources will fail" >&2

mkdir -p "$LOG_DIR"
log="$LOG_DIR/refresh-$(date +%Y-%m-%d).log"

# --- one refresh at a time ---------------------------------------------------
exec 9>"$DATA_DIR/.refresh.lock"
if ! flock -n 9; then
  echo "$(date -Iseconds) another refresh is still running; skipping" >>"$log"
  exit 0
fi

# Show output on a terminal; stay quiet (log only) under cron.
if [[ -t 1 ]]; then out() { tee -a "$log"; }; else out() { cat >>"$log"; }; fi

cd "$ROOT/pipeline"
set +e
{
  echo "=== $(date -Iseconds) refresh ${mode[*]:-all} ${extra[*]:-}"
  "$PY" -m opencity refresh "${mode[@]}" "${extra[@]}" 2>&1
} | out
status=${PIPESTATUS[0]}

if [[ $do_export -eq 1 ]]; then
  "$PY" -m opencity export 2>&1 | out
  [[ ${PIPESTATUS[0]} -eq 0 ]] || status=1
fi
set -e

find "$LOG_DIR" -name 'refresh-*.log' -mtime +60 -delete 2>/dev/null || true

if [[ $status -ne 0 ]]; then
  echo "refresh finished with errors (exit $status); see $log" >&2
fi
exit "$status"
