# Translation Readiness Report

- last_updated: `2026-05-17`

## Worksets

- `translation_workset_startup_font_showcase` (`ready_with_fixed_slot_rules`)
  All records belong to the confirmed startup_intro_fixed_slots family.
  Use exact byte-length slots and append_terminator=false.
- `translation_workset_core_ui` (`ready_with_source_specific_rules`)
  Mixed workset; apply source_group-specific family rules first.
  system_messages/save_menu still have some runtime uncertainty, but record structures are already usable.
- `translation_workset_gameplay_terms` (`ready_conservative`)
  Record structures are objective for item/ui/battle/ability/material families.
  Keep translations concise and preserve 0x0B/padding where present.
- `translation_workset_registry_d_dialogue` (`ready_with_multiline_preservation`)
  Preserve existing explicit newlines.
  Do not invent extra line breaks until runtime page-flow is visually confirmed.
- `registry_a_entry8_clusters_manifest` (`ready_with_singleline_conservatism`)
  Treat records as short counted single-line payloads unless source data explicitly says otherwise.
  Do not insert manual newlines.

## Live Playthrough Still Needed For

- final unseen-string sweep
- visual page-turn confirmation for dialogue runtime
- image-baked text discovery outside canonical extracted sources

## Reading

- Most canonical worksets are translation-ready before live playthrough, as long as source-specific layout rules are followed.
- Live playthrough is now primarily a final QA sweep, not a prerequisite for starting translation on known sources.
- This report exists to separate 'translation can start' from 'runtime/page QA is fully closed'.
