#!/usr/bin/env bash
# Update the database and data/export/. Output is also saved in data/logs/.
#   scripts/refresh.sh               only the sources that are due (what cron runs)
#   scripts/refresh.sh smc_swm       refresh the named sources now
set -euo pipefail
cd "$(dirname "$0")/../pipeline"
mkdir -p ../data/logs
exec 9>../data/.refresh.lock
flock -n 9 || { echo "a refresh is already running"; exit 0; }
python3 -m opencity refresh "$@" 2>&1 | tee -a "../data/logs/refresh-$(date +%F).log"
