# Post-QA Release Snapshot

Date: 2026-06-11 KST

The user completed first-pass QA and created the first patch release bundle.
This snapshot records the file situation before further cleanup.

## Git Status Summary

Working tree summary at snapshot time:

- Modified tracked paths: `235`
- Untracked paths shown by Git: `12`
- Main changed areas:
  - `confirmed_data/`: text, font, image inventory, workbench state, translation workspace
  - `scripts/`: build, audit, normalization, BPS/release helper work
  - `docs/`: active task, workbench docs, translation agent docs
  - `gba_kor_tool/`: CLI and translation normalization
  - `tools/localization_workbench.html`
  - `releases/`

This is no longer a cleanup-only dirty tree. Treat it as a new release baseline
that needs preservation before more deletion work.

## Release Bundle

New release folder:

- `releases/hnr_mnr_ko_v0.1.0/`
- `releases/hnr_mnr_ko_v0.1.0.zip`
- `releases/hnr_mnr_ko_v0.1.0.zip.sha256`

Release files:

- `README_ko.md`
- `NOTICE.txt`
- `LICENSES/Galmuri_OFL_1.1.txt`
- `checksums.sha256`
- `hnr_mnr_ko_v0.1.0.bps`

Sizes:

- BPS patch: `643K`
- zip bundle: `189K`

Verification:

- Source ROM SHA256:
  `49df5e9e128302733fb1465104153923a4a5c0ef36efd8b77a0006bbc0a629d8`
- Expected patched ROM SHA256:
  `c22a2922f25fcf7b10d435f161fe22cd2cd24894e64b2a08818c4ef72cdd2f6d`
- Patch SHA256:
  `5be01d727e734ff2a9a93704a956c25f4bd6ef06fd966c1f329af61a0db55036`
- Zip SHA256:
  `35978862dc0ad1895ca5839f3186745dd84ee3265ccbe9a64137764fe6e6fbd7`

`scripts/create_bps_patch.py verify` passes when the target is
`patched_roms/current_review/hnr_localization_review.gba`.

## Ignore Policy Update

`.gba`, `.sav`, `.ips`, `.ups`, and `.bps` remain ignored globally.

Exception added:

- `!releases/**/*.bps`

Reason: release BPS patches are distributable project artifacts and should not be
silently omitted by `git add releases/`.

ROM files remain ignored. The release bundle must not include original or patched
`.gba` files.

## Local ROM Notes

Current active patched ROM:

- `patched_roms/current_review/hnr_localization_review.gba`
- SHA256:
  `c22a2922f25fcf7b10d435f161fe22cd2cd24894e64b2a08818c4ef72cdd2f6d`

Root `hnr_localization_review.gba` exists locally but has the same SHA256 as the
clean source ROM. It is not the release target and is a misleading local cleanup
candidate.

Do not delete local ROMs in the same batch as release/source preservation.

## Uploaded Image Notes

New untracked uploaded replacement files:

- `title_240x160_transparent.png`: active GUI JSON reference count `0`
- `title_960x640_transparent (1).png`: active GUI JSON reference count `2`
- `workspace-file (2) (1).png`: active GUI JSON reference count `1`

Decision:

- keep the two actively referenced uploads;
- treat `title_240x160_transparent.png` as a local cleanup candidate only after
  another reference check.

## Next Safe Order

1. Commit the release-support plumbing and verified release artifacts.
2. Review the 235 modified tracked paths as the first-pass QA baseline.
3. Commit the QA baseline in logical batches, not mixed with local deletion.
4. Only after the baseline is preserved, resume cleanup candidates such as stale
   local ROMs and unreferenced uploaded images.
