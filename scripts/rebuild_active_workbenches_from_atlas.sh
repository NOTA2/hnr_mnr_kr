#!/bin/zsh
set -euo pipefail

python3 scripts/build_workbench_from_active_atlas.py \
  analysis/startup_intro_active_workbench \
  confirmed_data/extracted_texts/startup_intro_texts.json \
  --start-code 0xEA40 \
  --report analysis/startup_intro_active_workbench_report.json

echo "rebuilt startup intro active workbench"
