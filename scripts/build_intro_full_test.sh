#!/bin/zsh
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <source-rom> [output-dir]" >&2
  exit 1
fi

SOURCE_ROM="$1"
OUTPUT_DIR="${2:-patched_roms/intro_full_active}"

zsh scripts/build_translated_rom_with_active_atlas.sh \
  "$SOURCE_ROM" \
  confirmed_data/translation_worksets/translation_workset_intro_full_test.json \
  "$OUTPUT_DIR" \
  intro_full_active
