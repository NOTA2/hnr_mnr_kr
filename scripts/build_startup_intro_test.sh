#!/bin/zsh
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <source-rom> <output-dir>" >&2
  exit 1
fi

SOURCE_ROM="$1"
OUTPUT_DIR="$2"
ALLOW_BLANK_GLYPHS="${ALLOW_BLANK_GLYPHS:-0}"

mkdir -p "$OUTPUT_DIR"

BASE_ROM="$OUTPUT_DIR/font_expand_base.gba"
STARTUP_FONT_ROM="$OUTPUT_DIR/hnr_font_startup_active.gba"
STARTUP_INTRO_ROM="$OUTPUT_DIR/hnr_startup_intro_test.gba"
ACTIVE_WORKBENCH="analysis/startup_intro_active_workbench"

if [[ "$ALLOW_BLANK_GLYPHS" != "1" ]]; then
  python3 -m gba_kor_tool audit-pgm-glyph-set \
    "$ACTIVE_WORKBENCH/prepared_manifest.json" \
    --fail-on-blank \
    --allowed-values 0,34 \
    --fail-on-disallowed \
    --output "$OUTPUT_DIR/startup_intro_active_glyph_audit.json"
fi

python3 -m gba_kor_tool relocate-chunk \
  "$SOURCE_ROM" \
  "$BASE_ROM" \
  --table 0x17C2F4 \
  --index 0 \
  --layout pointer-length \
  --new-length 0x42000 \
  --destination-offset 0x800000 \
  --mirror-table 0x1823A0 \
  --report "$OUTPUT_DIR/font_expand_base_report.json"

python3 -m gba_kor_tool append-fnt-glyph-set \
  "$BASE_ROM" \
  "$STARTUP_FONT_ROM" \
  0x800000 \
  --payload-length 0x42000 \
  --manifest "$ACTIVE_WORKBENCH/prepared_manifest.json" \
  --report "$OUTPUT_DIR/startup_intro_active_font_append_report.json"

python3 -m gba_kor_tool apply-translations \
  "$STARTUP_FONT_ROM" \
  analysis/startup_intro_texts.json \
  "$STARTUP_INTRO_ROM" \
  --table "$ACTIVE_WORKBENCH/prepared.tbl" \
  --encoding cp932 \
  --report "$OUTPUT_DIR/startup_intro_apply_report.json"

echo "built: $STARTUP_INTRO_ROM"
