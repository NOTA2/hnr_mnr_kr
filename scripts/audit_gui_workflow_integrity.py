#!/usr/bin/env python3
"""Compatibility wrapper for the grouped GUI workflow audit."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


sys.dont_write_bytecode = True

IMPL = Path(__file__).resolve().parent / "audit" / "audit_gui_workflow_integrity.py"


if __name__ == "__main__":
    runpy.run_path(str(IMPL), run_name="__main__")
