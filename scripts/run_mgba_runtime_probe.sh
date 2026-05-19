#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROM="${1:-"$ROOT/patched_roms/current_review/hnr_localization_review.gba"}"
SAVESTATE="${2:-}"

find_mgba() {
  if [[ -n "${MGBA_BIN:-}" && -x "$MGBA_BIN" ]]; then
    printf '%s\n' "$MGBA_BIN"
    return 0
  fi

  for candidate in \
    "/Applications/mGBA.app/Contents/MacOS/mGBA" \
    "$HOME/Applications/mGBA.app/Contents/MacOS/mGBA"
  do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  find "$HOME/Downloads" "$ROOT" -maxdepth 6 -path "*/mGBA.app/Contents/MacOS/mGBA" -type f -perm +111 -print -quit 2>/dev/null
}

MGBA="$(find_mgba)"
if [[ -z "$MGBA" ]]; then
  echo "mGBA executable not found. Set MGBA_BIN=/path/to/mGBA.app/Contents/MacOS/mGBA" >&2
  exit 1
fi

if [[ ! -f "$ROM" ]]; then
  echo "ROM not found: $ROM" >&2
  exit 1
fi

args=("$MGBA")
if [[ -n "$SAVESTATE" ]]; then
  if [[ ! -f "$SAVESTATE" ]]; then
    echo "savestate not found: $SAVESTATE" >&2
    exit 1
  fi
  args+=("--savestate" "$SAVESTATE")
fi
args+=("$ROM")

echo "mGBA: $MGBA"
echo "ROM : $ROM"
if [[ -n "$SAVESTATE" ]]; then
  echo "state: $SAVESTATE"
fi
exec "${args[@]}"
