---
name: gba-localization-release
description: Verify, package, and close a GBA localization release with patch round-trip checks, source and output hashes, QA scope, known issues, asset licenses, safe cleanup, Git checkpoints, and reusable retrospective capture. Use for release candidates, BPS or UPS patch creation, final artifact cleanup, handoff documentation, post-project review, or extracting new lessons into the GBA localization skill suite.
---

# GBA Localization Release

Package a patch, never a copyrighted ROM. Treat cleanup and retrospective
capture as release engineering, not an afterthought.

## Prepare

1. Require `images` and `build_qa` to be ready; require the intended candidate
   build to be identified by hash.
2. Run lifecycle `check` and all project audits.
3. Read [release-cleanup-contract.md](references/release-cleanup-contract.md).
4. Freeze canonical data for the candidate and create a Git checkpoint.
5. Acquire the `release` lifecycle claim before packaging or cleanup.

## Verify The Candidate

1. Rebuild from the documented source ROM hash.
2. Compare the output hash with the candidate under test.
3. Run the release QA matrix and classify every unresolved issue.
4. Confirm fonts and image assets have compatible licenses and attribution.
5. Confirm no ROM, save, savestate, emulator state, or user-specific path is
   tracked or included.

## Create And Test The Patch

1. Create the chosen BPS, UPS, or other approved patch from the clean source to
   the candidate.
2. Apply the patch to a fresh verified source copy.
3. Require the round-trip output SHA-256 to equal the candidate hash.
4. Record patch path, size, checksum, tool and version, source hash, output hash,
   Git revision, and creation command.

## Package

Include:

- patch;
- patch checksum;
- expected source ROM identity and checksum;
- patching instructions;
- target-language and version information;
- QA scope and known issues;
- font and asset licenses or notices;
- project revision or release tag.

Do not include local debugging artifacts merely because they helped produce the
release. Prefer a platform-independent patch format and document patching tools
for Windows and macOS; do not make the release depend on a developer-only GUI.

## Clean Safely

1. Inventory candidates before deletion or untracking.
2. Read nearby documentation and search exact active references.
3. Classify each candidate as keep, keep with caution, retrospective keep,
   untrack, delete, or unknown.
4. Preserve symptom, cause, failed assumption, and replacement rule before
   removing confusing evidence.
5. Refresh GUI/image manifests before pruning uploads or generated assets.
6. Remove one recoverable family per Git checkpoint.
7. Leave ignored temporary output alone until final cleanup unless it consumes
   material space or blocks validation.

## Capture The Retrospective

Update project failure modes and decisions from repository evidence and user
notes. Do not copy raw chat logs, machine paths, ROM content, or game-specific
offsets into the generic skill suite. Promote only a generalized rule with a
clear trigger and prevention gate.

## Exit Gate

Mark `release` as `complete` only when patch round-trip verification passes, the
package contains no ROM, documentation is sufficient on another machine,
cleanup decisions are recoverable, and the retrospective has captured remaining
reusable lessons. Release the lifecycle claim only after the final checkpoint.
