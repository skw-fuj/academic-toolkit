#!/usr/bin/env bash
# Thin wrapper so `./install.sh` works on macOS/Linux. All logic lives in tools/install.py.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 (3.9+) is required." >&2; exit 1
fi
exec python3 "$here/tools/install.py" "$@"
