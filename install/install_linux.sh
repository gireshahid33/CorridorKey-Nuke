#!/usr/bin/env bash
# CorridorKey 2.0 for Nuke - Linux installer.
# Usage: ./install_linux.sh [--backend ~/CorridorKey2.0] [--nuke-dir ~/.nuke]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
for v in python3.12 python3.13 python3.11 python3.10 python3; do
  if command -v "$v" >/dev/null 2>&1; then exec "$v" "$HERE/install_backend.py" "$@"; fi
done
echo "Python 3.10 - 3.13 was not found." >&2
exit 1
