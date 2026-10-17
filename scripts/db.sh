#!/usr/bin/env bash
# Show how fresh each source in the database is (last success, rows, latest period, errors).
cd "$(dirname "$0")/../pipeline" && exec python3 -m opencity status
