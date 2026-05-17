#!/bin/zsh
set -euo pipefail

ATLAS="third_party/font_atlases/maruminyahangul_12x12.png"

python3 scripts/import_hangul_syllable_atlas.py \
  --atlas "$ATLAS" \
  --manifest analysis/startup_intro_seed_manifest.json \
  --output-dir analysis/startup_intro_active_workbench \
  --expected-columns 64 \
  --expected-rows 175 \
  --report analysis/startup_intro_active_workbench_report.json

python3 scripts/import_hangul_syllable_atlas.py \
  --atlas "$ATLAS" \
  --manifest analysis/hangul_core_ui_priority48_manifest.json \
  --output-dir analysis/hangul_core_ui_priority48_workbench \
  --expected-columns 64 \
  --expected-rows 175 \
  --report analysis/hangul_core_ui_priority48_workbench_report.json

python3 scripts/import_hangul_syllable_atlas.py \
  --atlas "$ATLAS" \
  --manifest analysis/hangul_core_ui_seed_manifest.json \
  --output-dir analysis/hangul_core_ui_workbench \
  --expected-columns 64 \
  --expected-rows 175 \
  --report analysis/hangul_core_ui_workbench_report.json

echo "rebuilt active atlas workbenches"
