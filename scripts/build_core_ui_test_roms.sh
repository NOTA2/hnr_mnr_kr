#!/bin/zsh
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <source-rom> <output-dir>" >&2
  exit 1
fi

SOURCE_ROM="$1"
OUTPUT_DIR="$2"

mkdir -p "$OUTPUT_DIR"

BASE_ROM="$OUTPUT_DIR/font_expand_base.gba"
PRIORITY48_FONT_ROM="$OUTPUT_DIR/hnr_font_core_ui_priority48_font.gba"
FULL80_FONT_ROM="$OUTPUT_DIR/hnr_font_core_ui_full80_font.gba"
PRIORITY48_BASIC_ROM="$OUTPUT_DIR/hnr_core_ui_priority48_text_test.gba"
PRIORITY48_COMPACT_ROM="$OUTPUT_DIR/hnr_core_ui_priority48_compact_text_test.gba"
FULL80_BASIC_ROM="$OUTPUT_DIR/hnr_core_ui_full80_text_test.gba"
FULL80_COMPACT_ROM="$OUTPUT_DIR/hnr_core_ui_full80_compact_text_test.gba"

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
  "$PRIORITY48_FONT_ROM" \
  0x800000 \
  --payload-length 0x42000 \
  --manifest analysis/hangul_core_ui_priority48_workbench/prepared_manifest.json \
  --report "$OUTPUT_DIR/core_ui_priority48_font_append_report.json"

python3 -m gba_kor_tool append-fnt-glyph-set \
  "$BASE_ROM" \
  "$FULL80_FONT_ROM" \
  0x800000 \
  --payload-length 0x42000 \
  --manifest analysis/hangul_core_ui_workbench/prepared_manifest.json \
  --report "$OUTPUT_DIR/core_ui_full80_font_append_report.json"

python3 -m gba_kor_tool apply-translations \
  "$PRIORITY48_FONT_ROM" \
  analysis/core_ui_priority48_coverable_translations.json \
  "$PRIORITY48_BASIC_ROM" \
  --table analysis/hangul_core_ui_priority48_workbench/prepared.tbl \
  --encoding cp932 \
  --report "$OUTPUT_DIR/core_ui_priority48_apply_report.json"

python3 -m gba_kor_tool apply-translations \
  "$PRIORITY48_FONT_ROM" \
  analysis/core_ui_priority48_compact_test_translations.json \
  "$PRIORITY48_COMPACT_ROM" \
  --table analysis/hangul_core_ui_priority48_workbench/prepared.tbl \
  --encoding cp932 \
  --report "$OUTPUT_DIR/core_ui_priority48_compact_apply_report.json"

python3 -m gba_kor_tool apply-translations \
  "$FULL80_FONT_ROM" \
  analysis/core_ui_full80_coverable_translations.json \
  "$FULL80_BASIC_ROM" \
  --table analysis/hangul_core_ui_workbench/prepared.tbl \
  --encoding cp932 \
  --report "$OUTPUT_DIR/core_ui_full80_apply_report.json"

python3 -m gba_kor_tool apply-translations \
  "$FULL80_FONT_ROM" \
  analysis/core_ui_full80_compact_test_translations.json \
  "$FULL80_COMPACT_ROM" \
  --table analysis/hangul_core_ui_workbench/prepared.tbl \
  --encoding cp932 \
  --report "$OUTPUT_DIR/core_ui_full80_compact_apply_report.json"

echo "built: $OUTPUT_DIR"
