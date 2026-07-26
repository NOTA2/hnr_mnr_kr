---
name: gba-localization-rom-analysis
description: Investigate a GBA ROM conservatively to map headers, pointers, registries, compression, text and image candidates, runtime structures, and experiment evidence without promoting guesses into build rules. Use after bootstrap, when locating resources, when a new source family appears, or when an existing structural assumption fails during apply or gameplay QA.
---

# GBA ROM Analysis

Turn unknown ROM structure into bounded, reproducible hypotheses. Prefer small
probes that can falsify an idea.

## Prepare

1. Run lifecycle `check` and `status`; require `bootstrap` to be ready.
2. Verify the current source ROM hash before using offsets from prior work.
3. Read the current artifact inventory and only the analysis notes relevant to
   the target resource.
4. Read [analysis-evidence.md](references/analysis-evidence.md).
5. Acquire the `rom_analysis` lifecycle claim before writing evidence.

## Analyze

1. Record immutable facts first: ROM size, GBA header fields, likely address
   range, checksums, and existing toolchain.
2. Keep `confirmed`, `strong hypothesis`, `weak hypothesis`, and `rejected`
   findings distinct.
3. For pointer candidates:
   - verify little-endian interpretation;
   - verify alignment and `0x08xxxxxx` ROM range;
   - normalize to file offsets deliberately;
   - search real consumers, not only repeated values.
4. For Thumb literal loads, calculate the PC-relative target from the
   instruction. Do not equate a nearby constant with a proven reference.
5. When disassembling a detached ROM slice, preserve its original ROM address.
   Do not rebase it to zero and then trust literal or branch targets.
6. For tables and script banks, validate complete record spans and overlaps
   before treating pointer-looking values as boundaries.
7. Probe compression and graphics candidates without overwriting the source.
   Record decompressor, expected size, and rejection reason.
8. Keep broad scans as discovery output. Promote only confirmed resources into
   canonical manifests.
9. For every experiment, record command, input hash, output path, observation,
   conclusion, confidence, and next test.

## Avoid Open-Ended Reverse Engineering

Stop investigating a structure when downstream text, font, or image work has a
safe bounded path. Park unrelated engine questions with evidence and a reason.
Do not block localization on fully understanding the game engine.

## Exit Gate

Mark `rom_analysis` as `ready` when:

- domain probes have confirmed or explicitly unknown resource boundaries;
- the artifact inventory identifies candidate text, font, and image regions;
- active conclusions are reproducible from repository scripts or commands;
- rejected assumptions are recorded compactly;
- no source ROM mutation occurred.

Return to `in_progress` when later runtime evidence invalidates a structural
assumption. Release the lifecycle claim after checkpointing the phase.
