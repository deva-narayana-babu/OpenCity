#!/usr/bin/env bash
# Schedule scripts/refresh.sh to run every hour. Each run only fetches the sources
# that are due (their own interval: 2 h for monsoon rainfall, daily prices, weekly pages...).
#
#   scripts/install-schedule.sh             # add an hourly crontab entry for this user
#   scripts/install-schedule.sh --systemd   # use a systemd user timer instead
#   scripts/install-schedule.sh --remove    # remove both
#   scripts/install-schedule.sh --print     # only print what would be installed
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REFRESH="$ROOT/scripts/refresh.sh"
TAG="# opencity-refresh"
MINUTE="${OPENCITY_CRON_MINUTE:-17}"     # off the hour, to spread load on government servers
CRON_LINE="$MINUTE * * * * $REFRESH --due $TAG"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"

service_unit() { cat <<EOF
[Unit]
Description=OpenCity data refresh (sources that are due)

[Service]
Type=oneshot
ExecStart=$REFRESH --due
Nice=10
EOF
}
timer_unit() { cat <<EOF
[Unit]
Description=Run OpenCity data refresh hourly

[Timer]
OnCalendar=*-*-* *:$MINUTE:00
Persistent=true
RandomizedDelaySec=120

[Install]
WantedBy=timers.target
EOF
}

case "${1:-}" in
  --print)
    echo "crontab line:"; echo "  $CRON_LINE"; echo
    echo "systemd units ($UNIT_DIR):"; service_unit; echo; timer_unit ;;
  --systemd)
    mkdir -p "$UNIT_DIR"
    service_unit >"$UNIT_DIR/opencity-refresh.service"
    timer_unit >"$UNIT_DIR/opencity-refresh.timer"
    systemctl --user daemon-reload
    systemctl --user enable --now opencity-refresh.timer
    echo "installed systemd user timer; check with: systemctl --user list-timers opencity-refresh.timer"
    echo "note: to run while logged out, enable lingering: loginctl enable-linger $USER" ;;
  --remove)
    (crontab -l 2>/dev/null | grep -v -F "$TAG" | crontab -) || true
    if systemctl --user list-unit-files opencity-refresh.timer >/dev/null 2>&1; then
      systemctl --user disable --now opencity-refresh.timer 2>/dev/null || true
      rm -f "$UNIT_DIR/opencity-refresh.service" "$UNIT_DIR/opencity-refresh.timer"
      systemctl --user daemon-reload || true
    fi
    echo "removed OpenCity schedule (cron and systemd)" ;;
  ""|--cron)
    chmod +x "$REFRESH"
    current="$(crontab -l 2>/dev/null || true)"
    if grep -q -F "$TAG" <<<"$current"; then
      echo "already installed:"; grep -F "$TAG" <<<"$current"
    else
      printf '%s\n%s\n' "$current" "$CRON_LINE" | sed '/^$/d' | crontab -
      echo "installed: $CRON_LINE"
    fi ;;
  -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//' ;;
  *) echo "unknown option: $1 (see --help)" >&2; exit 2 ;;
esac
