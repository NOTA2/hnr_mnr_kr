# Entry8 Segment Capability Map

- Entry8 offset: `0x6B594C`
- Entry8 length: `776444` bytes
- Segment count: `77`
- Capability counts: `{'active_repoint': 18, 'active_repoint_overlay': 2, 'candidate_structural': 53, 'protected': 2, 'unknown_or_unused': 2}`
- Apply action counts: `{'entry8_boundary_crossing_in_place_length_preserved': 21, 'entry8_in_place_length_preserved': 6189, 'entry8_overlay_in_place_length_preserved': 16, 'entry8_segment0_in_place_length_preserved': 241, 'entry8_segment_repointed': 3913}`

## Meaning

- `active_repoint`: 현재 빌드에서 segment repoint가 실제 사용됨.
- `active_repoint_overlay`: segment repoint와 원위치 overlay가 함께 필요했던 구간.
- `candidate_tail_safe`: 다음 확장 실험 우선 후보.
- `candidate_structural`: 후보는 있으나 tail-safe 검증은 부족한 구간.
- `fixed_or_overlay`: 현재는 원위치 고정/overlay 중심.
- `protected`: 보호 세그먼트. 기본적으로 확장 금지.

## Next Candidate Segments

| segment | capability | variable | tail-safe | u16 warnings | records | samples |
|---:|---|---:|---:|---:|---:|---|
| `0x90` | `candidate_structural` | 1 | 0 | 1 | 12 | お、お兄さん！<br>いいところに来た！<br>ワインもってないですか？<br>ワインですよ！ |
| `0x104` | `candidate_structural` | 4 | 0 | 3 | 30 | 58：ダイムラー邸④地下<br>大佐！この部屋！？<br>うむ！<br>うひょー、 |
| `0xFC` | `candidate_structural` | 1 | 0 | 8 | 14 | このカードじゃダメだ。<br>金属の２－４を作らないと…<br>必要なのは<br>金属の２－４のカードだね |
| `0x44` | `candidate_structural` | 18 | 0 | 26 | 53 | 自然の６－３のカードが必要だ<br>兄さん、置いてかないでね<br>わーってるよ！<br>どこか渡れるところを探そう |
| `0x88` | `candidate_structural` | 1 | 0 | 27 | 19 | ケガをした時のために<br>薬草はいかがでしょう？<br>とても高価な薬草だけど<br>うちの病院ならお買い得よ？ |
| `0x28` | `candidate_structural` | 7 | 0 | 44 | 40 | これがリオライトか？<br>リオライト、ゲットだぜ！<br>よし、<br>ウィンリィのところに戻るか |
| `0xBC` | `candidate_structural` | 40 | 0 | 47 | 166 | いらっしゃい。<br>泊まっていくかい？<br>一泊、２００センズだよ。<br>　泊まる　やっぱ泊まらない |
| `0xB8` | `candidate_structural` | 4 | 0 | 58 | 22 | 買わないかい？<br>暗黒の１－７、レベル５だ！<br>ダークマターだぞ！<br>１５００００センズだ。 |
| `0x84` | `candidate_structural` | 4 | 0 | 72 | 42 | さっき上でドカーンって<br>大きな音がしたんだ！<br>なんだったんだろう？<br>おじいちゃんの |
| `0xE8` | `candidate_structural` | 27 | 0 | 85 | 152 | この部屋、誰かいるみたいだね<br>どうする、兄さん？<br>よし、いくか！<br>さっきと同じ、金属の４－６だ |
| `0x5C` | `candidate_structural` | 23 | 0 | 86 | 114 | いらっしゃい。<br>泊まっていくかい？<br>一泊、２００センズだよ。<br>　泊まる　やっぱ泊まらない |
| `0x8C` | `candidate_structural` | 2 | 0 | 91 | 9 | 早く退院したいのぉ。<br>孫と遊べるように<br>なりたいのぉ<br>孫が毎日来てくれるんです。 |
| `0x40` | `candidate_structural` | 19 | 0 | 97 | 61 | 09：レドンド下水道<br>あなたが銀行強盗さんですね？<br>盗んだものを返してください<br>あ、すみません。 |
| `0xB4` | `candidate_structural` | 24 | 0 | 98 | 123 | ここがイーストシティね。<br>初めての街って、<br>ワクワクしますね<br>オレは大佐をどうやって |
| `0x3C` | `candidate_structural` | 9 | 0 | 143 | 26 | そうなんだ<br>これでこの街にも平和が<br>戻ります。<br>ありがとうございます |
| `0x144` | `candidate_structural` | 4 | 0 | 204 | 15 | きっとこの上じゃないかな？<br>どうする、兄さん？<br>錬成でハシゴを作れば<br>上にのぼれそうだな |
| `0x20` | `candidate_structural` | 72 | 0 | 208 | 251 | 01：リオール街<br>医者になりたいんだけど、<br>どうやったらなれるのかな？<br>は、 |
| `0xA0` | `candidate_structural` | 4 | 0 | 236 | 24 | 法で禁じられている錬成とは？<br>　花を錬成する事　黄金を錬成する事<br>またまた正解です！<br>すごいじゃないですか！ |
| `0xA8` | `candidate_structural` | 4 | 0 | 237 | 24 | よっ！<br>兄ちゃん、兄ちゃん<br>ウラモノのすごいのがあるぜ！<br>買わないかい？ |
| `0x58` | `candidate_structural` | 4 | 0 | 243 | 11 | 猫ですね♪<br>ああ、猫だな<br>旅は道連れ＄<br>猫だよ～♪ |

## Segment Table

| segment | capability | size | records | actions | variable | tail-safe | delta | sources |
|---:|---|---:|---:|---|---:|---:|---:|---|
| `0x20` | `candidate_structural` | 20404 | 251 | entry8_segment0_in_place_length_preserved:241 | 72 | 0 | 0 | duplicate_text_slots:1, inline_event_texts:2, registry_a_entry8_prefixed_texts:248 |
| `0x24` | `candidate_structural` | 13360 | 133 | entry8_in_place_length_preserved:133 | 36 | 0 | 0 | registry_a_entry8_prefixed_texts:133 |
| `0x28` | `candidate_structural` | 4748 | 40 | entry8_in_place_length_preserved:39 | 7 | 0 | 0 | registry_a_entry8_prefixed_texts:39, registry_a_map_labels:1 |
| `0x2C` | `active_repoint` | 4328 | 57 | entry8_segment_repointed:57 | 15 | 1 | 0 | registry_a_entry8_prefixed_texts:57 |
| `0x30` | `candidate_structural` | 13876 | 131 | entry8_in_place_length_preserved:130 | 42 | 0 | 0 | registry_a_entry8_prefixed_texts:130, registry_a_map_labels:1 |
| `0x38` | `active_repoint` | 5520 | 78 | entry8_segment_repointed:77 | 25 | 2 | 0 | registry_a_entry8_prefixed_texts:77, registry_a_map_labels:1 |
| `0x3C` | `candidate_structural` | 2092 | 26 | entry8_in_place_length_preserved:25 | 9 | 0 | 0 | registry_a_entry8_prefixed_texts:25, registry_a_map_labels:1 |
| `0x40` | `candidate_structural` | 10216 | 61 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:57, entry8_overlay_in_place_length_preserved:1 | 19 | 0 | 0 | choice_yes_no_texts:1, duplicate_text_slots:1, registry_a_entry8_prefixed_texts:59 |
| `0x44` | `candidate_structural` | 7856 | 53 | entry8_in_place_length_preserved:52 | 18 | 0 | 0 | registry_a_entry8_prefixed_texts:52, registry_a_map_labels:1 |
| `0x48` | `active_repoint` | 5368 | 88 | entry8_segment_repointed:86 | 16 | 1 | 0 | registry_a_entry8_prefixed_texts:87, registry_a_map_labels:1 |
| `0x4C` | `candidate_structural` | 16352 | 165 | entry8_in_place_length_preserved:163, entry8_overlay_in_place_length_preserved:1 | 31 | 0 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:164 |
| `0x50` | `candidate_structural` | 17512 | 144 | entry8_in_place_length_preserved:142 | 25 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:142, registry_a_map_labels:1 |
| `0x54` | `active_repoint` | 19432 | 304 | entry8_segment_repointed:302 | 61 | 1 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:302, registry_a_map_labels:1 |
| `0x58` | `candidate_structural` | 3220 | 11 | entry8_in_place_length_preserved:10 | 4 | 0 | 0 | registry_a_entry8_prefixed_texts:10, registry_a_map_labels:1 |
| `0x5C` | `candidate_structural` | 6696 | 114 | entry8_in_place_length_preserved:110 | 23 | 0 | 0 | inline_event_texts:3, registry_a_entry8_prefixed_texts:110, registry_a_map_labels:1 |
| `0x60` | `active_repoint` | 7268 | 106 | entry8_segment_repointed:105 | 14 | 5 | -4 | registry_a_entry8_prefixed_texts:105, registry_a_map_labels:1 |
| `0x64` | `candidate_structural` | 8488 | 62 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:60 | 16 | 0 | 0 | registry_a_entry8_prefixed_texts:61, registry_a_map_labels:1 |
| `0x68` | `candidate_structural` | 12712 | 168 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:166 | 44 | 0 | 0 | registry_a_entry8_prefixed_texts:167, registry_a_map_labels:1 |
| `0x6C` | `candidate_structural` | 6288 | 96 | entry8_in_place_length_preserved:95 | 15 | 0 | 0 | registry_a_entry8_prefixed_texts:95, registry_a_map_labels:1 |
| `0x70` | `candidate_structural` | 30088 | 591 | entry8_in_place_length_preserved:585 | 99 | 0 | 0 | inline_event_texts:5, registry_a_entry8_prefixed_texts:586 |
| `0x74` | `active_repoint` | 9552 | 148 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_segment_repointed:146 | 35 | 3 | -8 | registry_a_entry8_prefixed_texts:147, registry_a_map_labels:1 |
| `0x78` | `active_repoint` | 15536 | 376 | entry8_segment_repointed:367 | 94 | 1 | 0 | registry_a_entry8_prefixed_texts:375, registry_a_map_labels:1 |
| `0x7C` | `candidate_structural` | 10996 | 103 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:101 | 16 | 0 | 0 | registry_a_entry8_prefixed_texts:102, registry_a_map_labels:1 |
| `0x80` | `candidate_structural` | 4028 | 23 | entry8_in_place_length_preserved:21 | 2 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:21 |
| `0x84` | `candidate_structural` | 4904 | 42 | entry8_in_place_length_preserved:41 | 4 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:41 |
| `0x88` | `candidate_structural` | 2280 | 19 | entry8_in_place_length_preserved:18 | 1 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:18 |
| `0x8C` | `candidate_structural` | 2636 | 9 | entry8_in_place_length_preserved:9 | 2 | 0 | 0 | registry_a_entry8_prefixed_texts:9 |
| `0x90` | `candidate_structural` | 4920 | 12 | entry8_in_place_length_preserved:9 | 1 | 0 | 0 | inline_event_texts:3, registry_a_entry8_prefixed_texts:9 |
| `0x94` | `candidate_structural` | 20300 | 311 | entry8_in_place_length_preserved:308 | 44 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:308, registry_a_map_labels:1 |
| `0x98` | `candidate_structural` | 5932 | 54 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:50 | 10 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:51, registry_a_map_labels:1 |
| `0x9C` | `active_repoint` | 7904 | 155 | entry8_segment_repointed:152 | 50 | 3 | -8 | inline_event_texts:2, registry_a_entry8_prefixed_texts:152, registry_a_map_labels:1 |
| `0xA0` | `candidate_structural` | 2860 | 24 | entry8_in_place_length_preserved:22 | 4 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:22, registry_a_map_labels:1 |
| `0xA4` | `active_repoint` | 10444 | 60 | entry8_segment_repointed:59 | 10 | 2 | -10 | registry_a_entry8_prefixed_texts:59, registry_a_map_labels:1 |
| `0xA8` | `candidate_structural` | 2316 | 24 | entry8_in_place_length_preserved:21 | 4 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:21, registry_a_map_labels:1 |
| `0xAC` | `candidate_structural` | 5464 | 24 | entry8_in_place_length_preserved:20 | 6 | 0 | 0 | registry_a_entry8_prefixed_texts:20, startup_intro_texts:4 |
| `0xB0` | `unknown_or_unused` | 8480 | 0 | - | 0 | 0 | 0 | - |
| `0xB4` | `candidate_structural` | 14860 | 123 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:121 | 24 | 0 | 0 | registry_a_entry8_prefixed_texts:123 |
| `0xB8` | `candidate_structural` | 2920 | 22 | entry8_in_place_length_preserved:19 | 4 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:19, registry_a_map_labels:1 |
| `0xBC` | `candidate_structural` | 8140 | 166 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:161 | 40 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:164, registry_a_map_labels:1 |
| `0xC0` | `candidate_structural` | 10416 | 127 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:125 | 27 | 0 | 0 | registry_a_entry8_prefixed_texts:126, registry_a_map_labels:1 |
| `0xC4` | `active_repoint` | 8888 | 125 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_segment_repointed:122 | 30 | 1 | -4 | registry_a_entry8_prefixed_texts:124, registry_a_map_labels:1 |
| `0xC8` | `active_repoint` | 40192 | 896 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_segment_repointed:878 | 352 | 8 | 0 | registry_a_entry8_prefixed_texts:895, registry_a_map_labels:1 |
| `0xCC` | `candidate_structural` | 8304 | 126 | entry8_in_place_length_preserved:125 | 34 | 0 | 0 | registry_a_entry8_prefixed_texts:125, registry_a_map_labels:1 |
| `0xD0` | `candidate_structural` | 9276 | 62 | entry8_in_place_length_preserved:61 | 18 | 0 | 0 | registry_a_entry8_prefixed_texts:61, registry_a_map_labels:1 |
| `0xD4` | `candidate_structural` | 20396 | 319 | entry8_in_place_length_preserved:317 | 67 | 0 | 0 | registry_a_entry8_prefixed_texts:318, registry_a_map_labels:1 |
| `0xD8` | `candidate_structural` | 14364 | 174 | entry8_in_place_length_preserved:170 | 42 | 0 | 0 | inline_event_texts:2, registry_a_entry8_prefixed_texts:171, registry_a_map_labels:1 |
| `0xDC` | `candidate_structural` | 11460 | 185 | entry8_in_place_length_preserved:181, entry8_overlay_in_place_length_preserved:1 | 38 | 0 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:183, registry_a_map_labels:1 |
| `0xE8` | `candidate_structural` | 12428 | 152 | entry8_in_place_length_preserved:150, entry8_overlay_in_place_length_preserved:1 | 27 | 0 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:150, registry_a_map_labels:1 |
| `0xEC` | `candidate_structural` | 10408 | 148 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:143 | 26 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:146, registry_a_map_labels:1 |
| `0xF0` | `active_repoint` | 11552 | 155 | entry8_segment_repointed:154 | 56 | 5 | -18 | registry_a_entry8_prefixed_texts:154, registry_a_map_labels:1 |
| `0xF4` | `active_repoint` | 11232 | 190 | entry8_segment_repointed:188 | 77 | 2 | -8 | registry_a_entry8_prefixed_texts:190 |
| `0xF8` | `active_repoint_overlay` | 7584 | 88 | entry8_overlay_in_place_length_preserved:1, entry8_segment_repointed:86 | 26 | 2 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:86, registry_a_map_labels:1 |
| `0xFC` | `candidate_structural` | 2024 | 14 | entry8_in_place_length_preserved:13 | 1 | 0 | 0 | registry_a_entry8_prefixed_texts:13, registry_a_map_labels:1 |
| `0x100` | `unknown_or_unused` | 2024 | 1 | - | 0 | 0 | 0 | duplicate_text_slots:1 |
| `0x104` | `candidate_structural` | 4732 | 30 | entry8_in_place_length_preserved:29 | 4 | 0 | 0 | duplicate_text_slots:1, registry_a_entry8_prefixed_texts:29 |
| `0x108` | `candidate_structural` | 16568 | 181 | entry8_in_place_length_preserved:180 | 29 | 0 | 0 | registry_a_entry8_prefixed_texts:180, registry_a_map_labels:1 |
| `0x10C` | `candidate_structural` | 4316 | 55 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:53 | 13 | 0 | 0 | registry_a_entry8_prefixed_texts:54, registry_a_map_labels:1 |
| `0x110` | `active_repoint` | 11812 | 239 | entry8_segment_repointed:235 | 46 | 3 | -10 | inline_event_texts:3, registry_a_entry8_prefixed_texts:235, registry_a_map_labels:1 |
| `0x114` | `candidate_structural` | 16332 | 203 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:201 | 42 | 0 | 0 | registry_a_entry8_prefixed_texts:202, registry_a_map_labels:1 |
| `0x118` | `candidate_structural` | 9884 | 55 | entry8_in_place_length_preserved:54 | 16 | 0 | 0 | registry_a_entry8_prefixed_texts:54, registry_a_map_labels:1 |
| `0x11C` | `active_repoint` | 21008 | 458 | entry8_segment_repointed:457 | 123 | 7 | -6 | registry_a_entry8_prefixed_texts:457, registry_a_map_labels:1 |
| `0x120` | `active_repoint` | 12840 | 143 | entry8_segment_repointed:142 | 36 | 1 | -2 | registry_a_entry8_prefixed_texts:143 |
| `0x124` | `candidate_structural` | 11640 | 148 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:147 | 41 | 0 | 0 | registry_a_entry8_prefixed_texts:148 |
| `0x128` | `candidate_structural` | 11880 | 173 | entry8_in_place_length_preserved:169, entry8_overlay_in_place_length_preserved:1 | 34 | 0 | 0 | choice_yes_no_texts:1, inline_event_texts:1, registry_a_entry8_prefixed_texts:171 |
| `0x12C` | `candidate_structural` | 10104 | 86 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:85 | 18 | 0 | 0 | registry_a_entry8_prefixed_texts:86 |
| `0x130` | `candidate_structural` | 24424 | 513 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:510, entry8_overlay_in_place_length_preserved:2 | 114 | 0 | 0 | choice_yes_no_texts:2, registry_a_entry8_prefixed_texts:511 |
| `0x134` | `candidate_structural` | 16476 | 316 | entry8_in_place_length_preserved:313 | 64 | 0 | 0 | inline_event_texts:1, registry_a_entry8_prefixed_texts:314, registry_a_map_labels:1 |
| `0x138` | `candidate_structural` | 4584 | 14 | entry8_in_place_length_preserved:14 | 8 | 0 | 0 | registry_a_entry8_prefixed_texts:14 |
| `0x13C` | `active_repoint` | 4676 | 20 | entry8_segment_repointed:20 | 7 | 4 | 0 | registry_a_entry8_prefixed_texts:20 |
| `0x140` | `candidate_structural` | 4676 | 12 | entry8_in_place_length_preserved:12 | 5 | 0 | 0 | registry_a_entry8_prefixed_texts:12 |
| `0x144` | `candidate_structural` | 3472 | 15 | entry8_in_place_length_preserved:13, entry8_overlay_in_place_length_preserved:1 | 4 | 0 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:13, registry_a_map_labels:1 |
| `0x148` | `active_repoint` | 4788 | 8 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_segment_repointed:7 | 1 | 1 | 0 | registry_a_entry8_prefixed_texts:8 |
| `0x14C` | `candidate_structural` | 4684 | 20 | entry8_in_place_length_preserved:20 | 4 | 0 | 0 | registry_a_entry8_prefixed_texts:20 |
| `0x150` | `protected` | 4236 | 20 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:19 | 6 | 1 | 0 | registry_a_entry8_prefixed_texts:20 |
| `0x15C` | `protected` | 6792 | 148 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:147 | 37 | 3 | 0 | registry_a_entry8_prefixed_texts:148 |
| `0x160` | `candidate_structural` | 12540 | 255 | entry8_boundary_crossing_in_place_length_preserved:1, entry8_in_place_length_preserved:250, entry8_overlay_in_place_length_preserved:1 | 60 | 0 | 0 | choice_yes_no_texts:1, registry_a_entry8_prefixed_texts:253, registry_a_map_labels:1 |
| `0x168` | `active_repoint_overlay` | 13136 | 292 | entry8_overlay_in_place_length_preserved:6, entry8_segment_repointed:273 | 56 | 7 | -12 | choice_yes_no_texts:6, registry_a_entry8_prefixed_texts:273, registry_a_map_labels:1, save_menu_texts:12 |
