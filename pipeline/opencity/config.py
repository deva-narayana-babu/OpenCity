"""Paths and politeness settings. Everything can be overridden with environment variables."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get('OPENCITY_DATA_DIR', REPO_ROOT / 'data'))
DB_PATH = Path(os.environ.get('OPENCITY_DB', DATA_DIR / 'opencity.db'))
RAW_DIR_NAME = 'raw'          # raw snapshots live in DATA_DIR/raw (content-addressed, gzipped)
EXPORT_DIR = Path(os.environ.get('OPENCITY_EXPORT_DIR', DATA_DIR / 'export'))

TZ = ZoneInfo('Asia/Kolkata')

# Identify ourselves honestly. Set OPENCITY_CONTACT to a team email or URL.
CONTACT = os.environ.get('OPENCITY_CONTACT', 'https://github.com/QbitCloud/OpenCity')
USER_AGENT = os.environ.get(
    'OPENCITY_USER_AGENT',
    f'Mozilla/5.0 (compatible; OpenCityBot/0.1; +{CONTACT}; student civic-data project)')

HOST_MIN_DELAY = float(os.environ.get('OPENCITY_HOST_DELAY', '2.0'))   # seconds between requests to one host
TIMEOUT = float(os.environ.get('OPENCITY_TIMEOUT', '60'))
RETRIES = int(os.environ.get('OPENCITY_RETRIES', '3'))
DUE_SLACK_HOURS = 0.25        # run a source slightly early so an hourly cron does not skip a cycle


def now() -> datetime:
    return datetime.now(TZ)


def now_iso() -> str:
    return now().isoformat(timespec='seconds')
