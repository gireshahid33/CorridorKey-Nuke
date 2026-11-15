#!/usr/bin/env bash
# CorridorKey 2.0 for Nuke - Linux installer.
# Installs a private Miniforge (conda) into <backend>/_conda if it is missing, then runs install_backend.py
# with that Python - so the machine does not need a particular Python, git or ffmpeg.
# Usage: ./install_linux.sh [--backend ~/CorridorKey2.0] [--nuke-dir ~/.nuke]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$HOME/CorridorKey2.0"
ARGS=("$@")
for ((i = 0; i < ${#ARGS[@]}; i++)); do
  if [ "${ARGS[i]}" = "--backend" ] && [ $((i + 1)) -lt ${#ARGS[@]} ]; then BACKEND="${ARGS[i+1]}"; fi
done
# conda can't be installed into a path with spaces: then use ~/.corridorkey_conda (matches install_backend.py)
case "$BACKEND" in *" "*) CONDA="$HOME/.corridorkey_conda" ;; *) CONDA="$BACKEND/_conda" ;; esac
if [ ! -x "$CONDA/bin/python" ]; then
  echo; echo "=== Miniforge (private conda for CorridorKey) -> $CONDA"
  mkdir -p "$BACKEND"
  TMP="$(mktemp -d)"
  URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"
  echo "  downloading $URL"
  if command -v curl >/dev/null 2>&1; then curl -fsSL -o "$TMP/miniforge.sh" "$URL"; else wget -qO "$TMP/miniforge.sh" "$URL"; fi
  bash "$TMP/miniforge.sh" -b -p "$CONDA"
  rm -rf "$TMP"
fi
exec "$CONDA/bin/python" -s "$HERE/install_backend.py" "$@"
