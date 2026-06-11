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
PYTHON_BIN="${PYTHON:-python3}"

WORKBENCH_DIR="analysis/generated_workbenches/${SLUG}"
mkdir -p "$OUTPUT_DIR"

"$PYTHON_BIN" scripts/build_workbench_from_active_atlas.py \
  "$WORKBENCH_DIR" \
  "$TRANSLATION_JSON"

"$PYTHON_BIN" -m gba_kor_tool audit-pgm-glyph-set \
  "$WORKBENCH_DIR/prepared_manifest.json" \
  --allowed-values 0,17,34 \
  --fail-on-disallowed \
  --fail-on-blank \
  --output "$OUTPUT_DIR/${SLUG}_glyph_audit.json"

PAYLOAD_LENGTH=$("$PYTHON_BIN" - "$WORKBENCH_DIR/prepared_manifest.json" <<'PY'
import json
import math
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
glyph_count = len(json.loads(manifest.read_text()))
old_length = 0x3DDE8
stride = 0x48
minimum = 0x42000
margin = 0x2000
needed = old_length + glyph_count * stride + margin
aligned = (needed + 0xFFF) & ~0xFFF
print(hex(max(minimum, aligned)))
PY
)

echo "payload_length: ${PAYLOAD_LENGTH}"

"$PYTHON_BIN" -m gba_kor_tool relocate-chunk \
  "$SOURCE_ROM" \
  "$OUTPUT_DIR/${SLUG}_font_expand_base.gba" \
  --table 0x17C2F4 \
  --index 0 \
  --layout pointer-length \
  --new-length "$PAYLOAD_LENGTH" \
  --destination-offset 0x800000 \
  --mirror-table 0x1823A0 \
  --report "$OUTPUT_DIR/${SLUG}_font_expand_base_report.json"

"$PYTHON_BIN" -m gba_kor_tool append-fnt-glyph-set \
  "$OUTPUT_DIR/${SLUG}_font_expand_base.gba" \
  "$OUTPUT_DIR/${SLUG}_font_ready.gba" \
  0x800000 \
  --payload-length "$PAYLOAD_LENGTH" \
  --manifest "$WORKBENCH_DIR/prepared_manifest.json" \
  --report "$OUTPUT_DIR/${SLUG}_font_append_report.json"

"$PYTHON_BIN" -m gba_kor_tool apply-translations \
  "$OUTPUT_DIR/${SLUG}_font_ready.gba" \
  "$TRANSLATION_JSON" \
  "$OUTPUT_DIR/${SLUG}_translated.gba" \
  --table "$WORKBENCH_DIR/prepared.tbl" \
  --encoding cp932 \
  --report "$OUTPUT_DIR/${SLUG}_apply_report.json"

echo "built: $OUTPUT_DIR/${SLUG}_translated.gba"
