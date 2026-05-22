# User Supplied SS4/SS5 ROM Location Trace

Input states are mGBA PNG-backed savestates (`gbAs` chunk), freshly extracted into `runtime_user_captures/user_supplied_latest_ss45`.

## Confirmed Runtime Placement

- `錬成手帳`: BG1, char base `0x06004000`, screen base block `24`, palette bank `1`, visible tile rect `[14,2,7,4]`.
- `入れ替え / 必殺技`: same BG1 setup, visible tile rect `[14,2,7,6]`.
- Crops: `confirmed_data/image_inventory/rom_location_traces/user_supplied_latest_ss45/assets/bg1_label_crops_contact.png`.

## ROM Search Result

- Full phrase CP932 search: no hits for `錬成手帳`, `入れ替え`, `必殺技`.
- Runtime label tile bytes: no exact ROM hits.
- Runtime label tile hashes against extracted LZ77/RLE/raw image candidates: zero matches.
- Fresh savestate tile-to-ROM match reports also have no matching image block for these labels.

## Corrected ROM-Side Location Found

The earlier `fnt` renderer hypothesis was too broad for this target. These SUB menu labels are loaded as `Registry B` compressed graphics resources, not as normal text and not as the existing LZ77 label images.

The loader is `0x068DF8(dest, id)`. It indexes the `Registry B` mirror table at `0x08183D50`, checks whether the resource begins with `ZP`, and routes `ZP01` payloads through the decoder at `0x0690C4`. Decoded graphics are copied to VRAM.

Relevant call sites:

- `0x065396..0x0653A8`: loads `Registry B` entry `0x10` to `0x06004000`.
- `0x065400..0x065412`: loads `Registry B` entry `0x11` to `0x06004000`.
- `0x0658C4..0x0658DC`: loads `Registry B` entry `0x12` to `0x06004000`.
- `0x0658F6..0x0658FC`: loads `Registry B` entry `0x13` to `0x06008000` for the same nearby screen flow.

Confirmed `Registry B` entries:

| entry | table offset | ROM pointer | file offset | compressed size | header | output size | VRAM |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| `0x10` | `0x00183DD0` | `0x087CE608` | `0x007CE608` | `0x027F` | `ZP01` | `0x0D00` | `0x06004000` |
| `0x11` | `0x00183DD8` | `0x087CE888` | `0x007CE888` | `0x0419` | `ZP01` | `0x1500` | `0x06004000` |
| `0x12` | `0x00183DE0` | `0x087CECA4` | `0x007CECA4` | `0x031C` | `ZP01` | `0x19E0` | `0x06004000` |
| `0x13` | `0x00183DE8` | `0x087CEFC0` | `0x007CEFC0` | `0x030A` | `ZP01` | `0x0FA0` | `0x06008000` |

So the localization path is to add `ZP01`/`Registry B` image replacement support, or to validate a safe repoint strategy for these entries. The existing LZ77 label replacement path is not the right target for this set.
