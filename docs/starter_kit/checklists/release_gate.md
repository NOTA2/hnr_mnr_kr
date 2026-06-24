# Release Gate

Use this checklist before publishing a GBA localization patch.

## Patch Safety

- Do not include copyrighted ROM files.
- Track patch files only under the approved release directory.
- Record the expected source ROM checksum.
- Record the patched output checksum.
- Verify the patch applies cleanly from the expected source ROM.

## Release Contents

A release bundle should include:

- patch file;
- checksum file or checksum section;
- patching instructions;
- supported source ROM identification;
- known issues;
- QA scope;
- license notices for bundled fonts or assets;
- no saves, savestates, emulator cache, screenshots, or raw ROM.

## Final Audits

Run:

```bash
git ls-files '*.gba' '*.sav' '*.ss' '*.sgm' '*.srm' '*.state'
git status --short --branch
```

Then verify the release patch from a clean source ROM in a local ignored output
directory.
