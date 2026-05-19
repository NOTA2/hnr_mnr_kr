# Entry8 Boundary-Crossing Structure Analysis

## Summary

- Boundary-crossing records: 21
- Applied by length-preserved in-place patch: 21
- Records whose starting inferred segment is also repointed: 4

## Root Cause

The previous segment-end heuristic sorted every pointer-looking value in Entry8 table range 0x20..0x16C and treated the next value as the segment end. Some of those values point into counted text payloads, so they are not safe hard boundaries.

## Implemented Fix

For boundary-crossing counted records that fit their original payload length, patch the original Entry8 bytes and the patched source blob used for relocation, then extend relocated segment copy through the text tail when needed. No variable-length expansion is performed for these records.

## Records

- `0x6C7C68` crosses `8` bytes past inferred end `0x12330`; start segment repointed: `False`; '自然の６－３のカードが必要だ' -> '자연\u3000６－３\u3000카드가\u3000필요해'
- `0x6DE496` crosses `20` bytes past inferred end `0x28B50`; start segment repointed: `False`; 'あれこれ言う人って、結局、' -> '이래저래말하는사람은결국、'
- `0x6E163E` crosses `16` bytes past inferred end `0x2BCF8`; start segment repointed: `False`; 'ここは中央軍司令部です' -> '중앙군사령부입니다\u3000\u3000'
- `0x6EC99E` crosses `8` bytes past inferred end `0x37060`; start segment repointed: `True`; '今、決めてもらいたい。' -> '지금\u3000결정해\u3000줘。\u3000\u3000'
- `0x6F313C` crosses `4` bytes past inferred end `0x3D804`; start segment repointed: `False`; '石の７－１、レベル５だ！' -> '돌\u3000７－１\u3000레벨５다！\u3000'
- `0x6FE100` crosses `4` bytes past inferred end `0x487CC`; start segment repointed: `False`; '金属のカードの質量を５以上、' -> '금속\u3000카드\u3000질량\u3000５\u3000이상、'
- `0x70AD7E` crosses `14` bytes past inferred end `0x55434`; start segment repointed: `False`; '買っていくかい？' -> '사\u3000갈래？\u3000\u3000\u3000'
- `0x70D8AE` crosses `8` bytes past inferred end `0x57F68`; start segment repointed: `False`; 'ハーッハッハ！' -> '하하하！\u3000\u3000\u3000'
- `0x710164` crosses `28` bytes past inferred end `0x5A818`; start segment repointed: `False`; 'こりゃ大変なことになってんな' -> '이거\u3000큰일이\u3000벌어졌네\u3000\u3000\u3000'
- `0x71240E` crosses `10` bytes past inferred end `0x5CAD0`; start segment repointed: `True`; 'ひとつ事件が解決すると、' -> '사건하나해결되면\u3000\u3000\u3000\u3000'
- `0x71C116` crosses `4` bytes past inferred end `0x667D0`; start segment repointed: `True`; '今回は私と' -> '나와\u3000\u3000\u3000'
- `0x731378` crosses `4` bytes past inferred end `0x7BA3C`; start segment repointed: `False`; '冷たいって言われた…' -> '차갑다는말을들었다。'
- `0x73FDFE` crosses `4` bytes past inferred end `0x8A4BC`; start segment repointed: `False`; 'そろそろ行くね' -> '슬슬\u3000갈게\u3000\u3000'
- `0x746BE4` crosses `4` bytes past inferred end `0x912AC`; start segment repointed: `False`; '大佐、真面目に戦ってる？' -> '대령、진지하게싸우고있어'
- `0x754442` crosses `12` bytes past inferred end `0x9EAF8`; start segment repointed: `False`; '準備はいいか？' -> '준비됐나？\u3000\u3000'
- `0x759A26` crosses `26` bytes past inferred end `0xA40D8`; start segment repointed: `False`; 'それでマーティンス中佐を' -> '그래서\u3000마틴스\u3000중령을\u3000'
- `0x75F97A` crosses `8` bytes past inferred end `0xAA040`; start segment repointed: `False`; 'やってる時じゃないですよ！' -> '굴\u3000때가\u3000아니에요！\u3000\u3000\u3000'
- `0x769094` crosses `18` bytes past inferred end `0xB3750`; start segment repointed: `True`; 'まだこんなことやってんの？' -> '아직\u3000이런\u3000짓\u3000해？\u3000\u3000\u3000'
- `0x76B370` crosses `6` bytes past inferred end `0xB5A28`; start segment repointed: `False`; 'いいから、' -> '됐으니까、'
- `0x76CDE2` crosses `2` bytes past inferred end `0xB74B0`; start segment repointed: `False`; '一人で行かせていいのかよ！？' -> '혼자\u3000가게\u3000둬도\u3000돼！？\u3000\u3000'
- `0x76FEEE` crosses `18` bytes past inferred end `0xBA5AC`; start segment repointed: `False`; 'そう…あの背中にある十字架に' -> '그래…저\u3000등에\u3000진\u3000십자가에'
