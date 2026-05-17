#!/bin/zsh
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 <source-rom> <translation-json> <output-dir> [slug]" >&2
  exit 1
fi

SOURCE_ROM="$1"
TRANSLATION_JSON="$2"
OUTPUT_DIR="$3"
SLUG="${4:-$(basename "$TRANSLATION_JSON" .json)}"

WORKBENCH_DIR="analysis/generated_workbenches/${SLUG}"
mkdir -p "$OUTPUT_DIR"

python3 scripts/build_workbench_from_active_atlas.py \
  "$WORKBENCH_DIR" \
  "$TRANSLATION_JSON"

python3 -m gba_kor_tool audit-pgm-glyph-set \
  "$WORKBENCH_DIR/prepared_manifest.json" \
  --allowed-values 0,123,255 \
  --fail-on-disallowed \
  --fail-on-blank \
  --output "$OUTPUT_DIR/${SLUG}_glyph_audit.json"

python3 -m gba_kor_tool relocate-chunk \
  "$SOURCE_ROM" \
  "$OUTPUT_DIR/${SLUG}_font_expand_base.gba" \
  --table 0x17C2F4 \
  --index 0 \
  --layout pointer-length \
  --new-length 0x42000 \
  --destination-offset 0x800000 \
  --mirror-table 0x1823A0 \
  --report "$OUTPUT_DIR/${SLUG}_font_expand_base_report.json"

python3 -m gba_kor_tool append-fnt-glyph-set \
  "$OUTPUT_DIR/${SLUG}_font_expand_base.gba" \
  "$OUTPUT_DIR/${SLUG}_font_ready.gba" \
  0x800000 \
  --payload-length 0x42000 \
  --manifest "$WORKBENCH_DIR/prepared_manifest.json" \
  --report "$OUTPUT_DIR/${SLUG}_font_append_report.json"

python3 -m gba_kor_tool apply-translations \
  "$OUTPUT_DIR/${SLUG}_font_ready.gba" \
  "$TRANSLATION_JSON" \
  "$OUTPUT_DIR/${SLUG}_translated.gba" \
  --table "$WORKBENCH_DIR/prepared.tbl" \
  --encoding cp932 \
  --report "$OUTPUT_DIR/${SLUG}_apply_report.json"

echo "built: $OUTPUT_DIR/${SLUG}_translated.gba"
