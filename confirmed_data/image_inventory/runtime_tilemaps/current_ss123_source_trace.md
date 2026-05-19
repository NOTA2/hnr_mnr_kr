# Current SS1/SS2/SS3 Tilemap Source Trace

Current ss1/ss2/ss3 tilemap source trace. Tilemap PNGs are analysis maps; actionable replacements require ROM source blocks or text renderer sources.

## no_entry8_latest_ss1 BG0

- visible: `エド式… / 錬成 / つかう / すてる / もどる`
- assessment: Tied to RLE UI/popup fragments. `0x003AF23C` strongly matches this screen's `錬成 / つかう / すてる / もどる` popup body. `0x003ABB9C` is the clearer `OK? / はい / いいえ` confirmation popup candidate when rendered as a readable 8-column RLE layout.
- next: Treat `0x003AF23C` as the actionable candidate for `연성/사용/버리기/돌아가기`, and `0x003ABB9C` as the actionable candidate for `예/아니요`.
- graphics matches:
  - `rle` `0x003AF23C` shared=47 item=`image:rle_ui_fragment:003AF23C`
  - `rle` `0x003ABB9C` shared=10 item=`image:rle_ui_fragment:003ABB9C`

## no_entry8_latest_ss2 BG1

- visible: `錬成手帳`
- assessment: No raw tilemap or extracted LZ77/RLE/raw graphics block match. This strongly suggests runtime font/text rendering or generated tiles.
- next: Find the encoded source string/menu table for 錬成手帳; do not treat this as an image replacement yet.

## no_entry8_latest_ss3 BG0

- visible: `card list numbers / ????? / lower description area`
- assessment: Mostly runtime text/list rendering, with a small overlap against an RLE card-list UI fragment.
- next: Keep RLE fragment for UI frame investigation; list text should be handled as text/font-rendered data.
- graphics matches:
  - `rle` `0x003A3540` shared=13 item=`image:rle_ui_fragment:003A3540`

## no_entry8_latest_ss3 BG1

- visible: `card list frame / BACK / NEXT / side labels`
- assessment: Best actionable image/tilemap candidate among current ss1-3. Both raw tilemap spans and RLE graphics sources are visible.
- next: Patch/rebuild against RLE graphics blocks and, if layout changes are needed, raw tilemap spans around 0x003A40C5/0x003AB70C.
- raw tilemap hits:
  - `0x003A40C5` (0-15)
  - `0x003A417A` (320-335)
  - `0x003A4211` (352-367)
  - `0x003A424E` (416-431)
  - `0x003AB70C` (640-648)
- graphics matches:
  - `rle` `0x003A7C3C` shared=165 item=`image:rle_ui_fragment:003A7C3C`
  - `rle` `0x003A8894` shared=150 item=`image:rle_ui_fragment:003A8894`
  - `rle` `0x003AA4C0` shared=127 item=`image:rle_ui_fragment:003AA4C0`
  - `rle` `0x003A9624` shared=126 item=`image:rle_ui_fragment:003A9624`
  - `rle` `0x003A6E24` shared=123 item=`image:rle_ui_fragment:003A6E24`

## no_entry8_latest_ss2 BG0

- visible: `party frame/background panel`
- assessment: Raw tilemap source exists, but this layer is mostly frame/background, not the 錬成手帳 text itself.
- next: Useful for UI layout patching if panel geometry changes; not a direct text replacement target.
- raw tilemap hits:
  - `0x007CA438` (whole screenblock)
