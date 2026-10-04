#!/usr/bin/env bash
# Small helpers around the OpenCity database (no sqlite3 CLI needed).
#
#   scripts/db.sh status                       # freshness/health of every source
#   scripts/db.sh sources                      # list adapters
#   scripts/db.sh query "SELECT ..." [--csv]   # read-only SQL
#   scripts/db.sh latest <metric_id> [n]       # latest values of one metric
#   scripts/db.sh metrics [module]             # metric catalogue
#   scripts/db.sh errors [n]                   # recent failed fetches
#   scripts/db.sh export                       # rewrite data/export/*.csv
#   scripts/db.sh reparse [-s source]          # rebuild from archived raw snapshots (no network)
#   scripts/db.sh init                         # create/migrate the database
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
oc() { (cd "$ROOT/pipeline" && "$PY" -m opencity "$@"); }

cmd="${1:-status}"; shift || true
case "$cmd" in
  status|sources|export|init|reparse) oc "$cmd" "$@" ;;
  query) oc query "$@" ;;
  latest)
    metric="${1:?metric id required}"; n="${2:-20}"
    [[ "$metric" =~ ^[a-z0-9_.]+$ ]] || { echo "bad metric id" >&2; exit 2; }
    [[ "$n" =~ ^[0-9]+$ ]] || { echo "bad row count" >&2; exit 2; }
    oc query "SELECT geo_level, geo_code, period_start, period_end, dims, value, value_text, status, retrieved_at
              FROM v_observation WHERE metric_id = '$metric'
              ORDER BY period_end DESC, geo_code, dims LIMIT $n" ;;
  metrics)
    if [[ $# -gt 0 ]]; then
      [[ "$1" =~ ^[a-z_]+$ ]] || { echo "bad module name" >&2; exit 2; }
      oc query "SELECT metric_id, unit, source_id, label FROM metric WHERE module = '$1' ORDER BY metric_id"
    else
      oc query "SELECT module, metric_id, unit, source_id FROM metric ORDER BY module, metric_id"
    fi ;;
  errors)
    n="${1:-20}"; [[ "$n" =~ ^[0-9]+$ ]] || { echo "bad row count" >&2; exit 2; }
    oc query "SELECT fetched_at, source_id, status, http_status, substr(error, 1, 120) AS error, url
              FROM fetch WHERE status NOT IN ('ok','unchanged','not_modified','skipped','pending')
              ORDER BY fetch_id DESC LIMIT $n" ;;
  -h|--help|help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//' ;;
  *) echo "unknown command: $cmd (see --help)" >&2; exit 2 ;;
esac
