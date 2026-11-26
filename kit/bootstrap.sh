#!/usr/bin/env bash
# Read-only preview unless --apply is explicitly supplied. No network or home writes.
set -eu
KIT=$(cd -- "$(dirname -- "$0")" && pwd -P)
command -v python3 >/dev/null 2>&1 || { echo "BLOCKED: python3 not found. Install Python 3.9+ first." >&2; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info>=(3,9) else 1)' || { echo "BLOCKED: Python 3.9+ required." >&2; exit 1; }
exec python3 -I -B "$KIT/tools/install_entry.py" "$@"
