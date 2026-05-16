#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: zsh scripts/build_all_startup_fonts.sh <cutoff_percent> [output_folder]" >&2
  exit 1
fi

cutoff_percent="$1"
shift || true

cmd=(python3 scripts/build_startup_font_compare.py "$cutoff_percent")
if [[ $# -eq 1 ]]; then
  cmd+=(--output-folder "$1")
fi

"${cmd[@]}"
