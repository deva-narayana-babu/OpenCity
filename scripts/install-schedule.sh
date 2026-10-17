#!/usr/bin/env bash
# Run scripts/refresh.sh every hour with cron. Running it again just replaces the entry.
# To remove it: crontab -e, then delete the line ending in "# opencity".
set -euo pipefail
line="17 * * * * $(cd "$(dirname "$0")" && pwd)/refresh.sh >/dev/null 2>&1  # opencity"
(crontab -l 2>/dev/null | grep -v '# opencity$' || true; echo "$line") | crontab -
echo "installed: $line"
