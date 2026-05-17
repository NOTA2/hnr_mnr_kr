#!/bin/zsh
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 <atlas-png> <output-slug> [expected-columns]" >&2
  exit 1
fi

ATLAS_PATH="$1"
OUTPUT_SLUG="$2"
EXPECTED_COLUMNS="${3:-64}"

WORKBENCH_DIR="analysis/startup_intro_${OUTPUT_SLUG}_workbench"
WORKBENCH_REPORT="analysis/startup_intro_${OUTPUT_SLUG}_workbench_report.json"
OUTPUT_DIR="patched_roms/font_compare/${OUTPUT_SLUG}"
PROFILE_JSON="$OUTPUT_DIR/${OUTPUT_SLUG}_profile.json"

mkdir -p "$OUTPUT_DIR"

cat > "$PROFILE_JSON" <<EOF
{
  "label": "$OUTPUT_SLUG",
  "source_png": "$ATLAS_PATH",
  "tile_width": 12,
  "tile_height": 12,
  "columns": $EXPECTED_COLUMNS,
  "rows": 175,
  "character_order": "unicode_hangul_syllables"
}
EOF

python3 scripts/build_workbench_from_active_atlas.py \
  "$WORKBENCH_DIR" \
  confirmed_data/extracted_texts/startup_intro_texts.json \
  --start-code 0xEA40 \
  --profile "$PROFILE_JSON" \
  --report "$WORKBENCH_REPORT"

python3 -m gba_kor_tool audit-pgm-glyph-set \
  "$WORKBENCH_DIR/prepared_manifest.json" \
  --allowed-values 0,34 \
  --fail-on-disallowed \
  --fail-on-blank \
  --output "$OUTPUT_DIR/glyph_audit.json"

python3 -m gba_kor_tool relocate-chunk \
  "Hagane no Renkinjutsushi - Meisou no Rondo (Japan).gba" \
  "$OUTPUT_DIR/font_expand_base.gba" \
  --table 0x17C2F4 \
  --index 0 \
  --layout pointer-length \
  --new-length 0x42000 \
  --destination-offset 0x800000 \
  --mirror-table 0x1823A0 \
  --report "$OUTPUT_DIR/font_expand_base_report.json"

python3 -m gba_kor_tool append-fnt-glyph-set \
  "$OUTPUT_DIR/font_expand_base.gba" \
  "$OUTPUT_DIR/hnr_font_${OUTPUT_SLUG}.gba" \
  0x800000 \
  --payload-length 0x42000 \
  --manifest "$WORKBENCH_DIR/prepared_manifest.json" \
  --report "$OUTPUT_DIR/font_append_report.json"

python3 -m gba_kor_tool apply-translations \
  "/Users/user/test/$OUTPUT_DIR/hnr_font_${OUTPUT_SLUG}.gba" \
  "/Users/user/test/confirmed_data/extracted_texts/startup_intro_texts.json" \
  "/Users/user/test/$OUTPUT_DIR/hnr_startup_intro_${OUTPUT_SLUG}.gba" \
  --table "/Users/user/test/$WORKBENCH_DIR/prepared.tbl" \
  --encoding cp932 \
  --report "/Users/user/test/$OUTPUT_DIR/startup_intro_apply_report.json"

echo "built: /Users/user/test/$OUTPUT_DIR/hnr_startup_intro_${OUTPUT_SLUG}.gba"
