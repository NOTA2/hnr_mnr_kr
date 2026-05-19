# Translation Expansion Opportunities

- Last updated: `2026-05-18T18:34:44.301623+00:00`
- Dataset: `confirmed_data/localization_workbench/workbench_dataset.json`
- ROM used for pointer scan: `patched_roms/current_review/current_review_font_ready.gba`

## Reading

- packed_repoint_available: Registry D처럼 청크/entry 재패킹이 가능하므로 원문 byte 슬롯보다 긴 번역을 허용한다.
- direct_repoint_available: 문자열 직접 포인터가 확인되어, 현재 슬롯을 넘으면 새 위치에 쓰고 포인터를 갱신할 수 있다.
- in_place_slack_only: 직접 포인터는 없지만 현재 슬롯에 남은 byte 여유가 있으므로 그 범위 안에서 자연스럽게 늘릴 수 있다.
- fixed_capacity_exact: 직접 포인터가 없고 현재 번역이 슬롯을 정확히 채운다. 더 늘리면 원문 잔류/skipped 위험이 있다.
- too_long_without_pointer: 현재 번역이 슬롯을 넘는데 직접 포인터가 없다. 반드시 줄이거나 별도 구조 분석이 필요하다.

## Source Summary

| Source | Expansion modes |
|---|---|
| ability_texts | `fixed_capacity_exact: 95`, `in_place_slack_only: 318` |
| battle_texts | `fixed_capacity_exact: 63`, `in_place_slack_only: 41` |
| choice_yes_no_texts | `in_place_slack_only: 16` |
| credits_texts | `direct_repoint_available: 10` |
| duplicate_text_slots | `direct_repoint_available: 1`, `fixed_capacity_exact: 8`, `in_place_slack_only: 19` |
| item_texts | `direct_repoint_available: 49` |
| location_texts | `direct_repoint_available: 1`, `fixed_capacity_exact: 2`, `in_place_slack_only: 7` |
| material_texts | `fixed_capacity_exact: 7`, `in_place_slack_only: 37` |
| registry_a_entry12_texts | `fixed_capacity_exact: 4`, `in_place_slack_only: 18` |
| registry_a_entry8_prefixed_texts | `direct_repoint_available: 2`, `fixed_capacity_exact: 5183`, `in_place_slack_only: 4637`, `too_long_without_pointer: 1` |
| registry_a_map_labels | `fixed_capacity_exact: 9`, `in_place_slack_only: 39` |
| registry_d_fc_script_texts | `packed_repoint_available: 244` |
| save_menu_texts | `fixed_capacity_exact: 4`, `in_place_slack_only: 8` |
| startup_intro_texts | `fixed_capacity_exact: 1`, `in_place_slack_only: 3` |
| system_messages | `direct_repoint_available: 9`, `in_place_slack_only: 1` |
| ui_skill_texts | `direct_repoint_available: 25` |

## Examples

### `ability_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D3835` | エド式大砲 | 에드식대포 | 11/11 | 0 |
| `0x3D385E` | エド式巨大砲 | 에드식거대포 | 13/13 | 0 |
| `0x3D3889` | エド式超巨大砲 | 에드식초거대포 | 15/15 | 0 |
| `0x3D38B6` | エド式超絶巨大砲 | 에드식초절거대포 | 17/17 | 0 |
| `0x3D3914` | 鉄拳制裁 | 철권제재 | 9/9 | 0 |
| `0x3D393F` | 鉄拳大制裁 | 철권대제재 | 11/11 | 0 |
| `0x3D396C` | 鉄脚制裁 | 철각제재 | 9/9 | 0 |
| `0x3D3997` | 鉄脚大制裁 | 철각대제재 | 11/11 | 0 |

### `ability_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D3772` | 黄昏の壁 | 황혼 벽 | 8/9 | 0 |
| `0x3D377B` | 敵の足元に壁を　錬成して攻撃 | 발밑에 벽을　　 연성해 공격 | 29/30 | 0 |
| `0x3D3799` | 旋律の壁 | 선율벽 | 7/9 | 0 |
| `0x3D37C0` | 虚空の壁 | 허공벽 | 7/9 | 0 |
| `0x3D37C9` | 複数の壁を錬成　敵全体を攻撃 | 여러 벽을 연성해전체 공격 | 27/30 | 0 |
| `0x3D37E7` | 忘却の壁 | 망각벽 | 7/9 | 0 |
| `0x3D380E` | 鎮魂の壁 | 진혼벽 | 7/9 | 0 |
| `0x3D3840` | 鋼鉄の大砲を　　錬成して攻撃 | 강철 대포를　　 연성해 공격 | 29/30 | 0 |

### `battle_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2036` | 壁錬成 | 벽연성 | 7/7 | 0 |
| `0x3D2059` | 撃鉄靠掌 | 격철고장 | 9/9 | 0 |
| `0x3D20A3` | 発火 | 발화 | 5/5 | 0 |
| `0x3D20A8` | 手加減なしの　　発火攻撃 | 가차 없이　　　 발화공격 | 26/26 | 0 |
| `0x3D20C2` | 銃連射 | 총연사 | 7/7 | 0 |
| `0x3D216E` | 紫電 | 자전 | 5/5 | 0 |
| `0x3D218D` | 遠雷 | 원뢰 | 5/5 | 0 |
| `0x3D21B2` | 迅雷 | 신뢰 | 5/5 | 0 |

### `battle_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D203D` | 壁を錬成し　　　相手を攻撃 | 벽을 연성해　　 상대 공격 | 27/28 | 0 |
| `0x3D2062` | 連続で攻撃を　　たたき込む | 연속 공격을　　 퍼붓는다 | 26/28 | 0 |
| `0x3D2081` | 集めた猫たちが　アルのために攻撃 | 고양이들이　　　알을 위해 공격 | 32/34 | 0 |
| `0x3D20C9` | 一点集中で　　　銃を連射する | 한 점 집중해　　총 연사 | 25/30 | 0 |
| `0x3D20E7` | マッハパンチ | 마하 펀치 | 10/13 | 0 |
| `0x3D20F4` | 高速でパンチを　連打する技 | 고속펀치　　　　연속타 | 24/28 | 0 |
| `0x3D2110` | ＡＳ式錬成術１ | ＡＳ연성술 1 | 13/15 | 0 |
| `0x3D211F` | 瓦礫をパンチで　錬成し打ち出す | 펀치로 잔해를　 연성해 날린다 | 31/32 | 0 |

### `choice_yes_no_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6C7AEC` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x6CECCE` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x72B80E` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x72BB12` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x7389B8` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x754468` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x759B9E` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |
| `0x75EF3E` | 　はい　いいえ | 　예　아니요 | 12/14 | 0 |

### `credits_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08C3AC` | 　　チーフプロデューサー　　　　　　　　 |   チーフプロデューサー         | 31/41 | 1 |
| `0x08C404` | 　　ゼネラルプロデューサー　　　　　　　 |   ゼネラルプロデューサー        | 32/41 | 1 |
| `0x08C45C` | 　　エグゼクティブプロデューサー　　　　 |   エグゼクティブプロデューサー     | 35/41 | 1 |
| `0x08C7CC` | 　　ソニー・クリエイティブプロダクツ　　 |   ソニー・クリエイティブプロダクツ   | 37/41 | 1 |
| `0x08C92C` | 　　　　　スクウェア・エニックス　　　　 |      スクウェア・エニックス     | 32/41 | 1 |
| `0x08CA34` | 　　　ペイント　中山　しほ子／ボンズ　　 |    ペイント 中山 しほ子/ボンズ   | 33/41 | 1 |
| `0x08CAB8` | 　　　　　ポール・トゥ・ウィン　　　　　 |      ポール・トゥ・ウィン      | 31/41 | 1 |
| `0x08CC18` | 　　　 堀口　比呂志／ツーファイブ 　　　 |     堀口 比呂志/ツーファイブ     | 33/41 | 1 |

### `duplicate_text_slots` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08B80C` | 壁錬成 | 벽연성 | 7/7 | 1 |

### `duplicate_text_slots` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8550` | 回復薬１ | 회복약 1 | 8/8 | 0 |
| `0x7A85DC` | 回復薬３ | 회복약 3 | 8/8 | 0 |
| `0x7A86B4` | 銀時計 | 은시계 | 6/6 | 0 |
| `0x7A86F4` | 猫 | 냥 | 2/2 | 0 |
| `0x7A8BB8` | マスタング大佐　汚名返上の証 | 머스탱 대령 오명 회복의 증표 | 28/28 | 0 |
| `0x7A8D94` | 書類① | 서류① | 6/6 | 0 |
| `0x7A8DE4` | 書類② | 서류② | 6/6 | 0 |
| `0x7A8E2C` | 書類③ | 서류③ | 6/6 | 0 |

### `duplicate_text_slots` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B5D6A` | 01：リオール街 | 01:리올 거리 | 13/15 | 0 |
| `0x6C58B2` | 09：レドンド下水道 | 09:레돈드 하수도 | 17/19 | 0 |
| `0x739630` | 57：--ダイムラー邸③2階 | 57:다이무라③2층 | 17/24 | 0 |
| `0x739E18` | 58：ダイムラー邸④地下 | 58:다이무라④지하 | 18/23 | 0 |
| `0x7A8558` | 体力を５０回復する薬 | 체력 50 회복약 | 14/20 | 0 |
| `0x7A85E4` | 体力を２００回復する薬 | 체력 200 회복약 | 15/22 | 0 |
| `0x7A86BC` | 国家錬金術師の証 | 연금술사 증표 | 13/16 | 0 |
| `0x7A886C` | 幻の機械鎧の素材　５／５ | 오토메일 소재 5/5 | 17/24 | 0 |

### `item_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08AED8` | 古城の最上階に咲いていた花 | 고성 최상층에 핀 꽃 | 20/27 | 1 |
| `0x08AEF4` | 花束 | 꽃다발 | 7/5 | 1 |
| `0x08AEFC` | 東方軍司令部で受け取った書類 | 동방군 사령부에서 받은 서류 | 28/29 | 1 |
| `0x08AF1C` | 書類③ | 서류③ | 7/7 | 1 |
| `0x08AF24` | 東方軍司令部へ届ける書類 | 동방군 사령부에 전달할 서류 | 28/25 | 1 |
| `0x08AF40` | 書類② | 서류② | 7/7 | 1 |
| `0x08AF48` | ブラッドレイ大総統に届ける書類 | 브래드레이 대총통에게 전달할 서류 | 34/31 | 1 |
| `0x08AF68` | 書類① | 서류① | 7/7 | 1 |

### `location_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x18425C` | セントラルシティ | 센트럴 시티 | 12/17 | 4 |

### `location_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x18430C` | ダイムラー邸 | 다이무라저택 | 13/13 | 0 |
| `0x1843E8` | クルス遺跡 | 크루스유적 | 11/11 | 0 |

### `location_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x184288` | ヴィヴァス | 비바스 | 7/11 | 0 |
| `0x1842B4` | リオール | 리올 | 5/9 | 0 |
| `0x1842E0` | ソリン | 솔링 | 5/7 | 0 |
| `0x184338` | オルヘンティノス城 | 올헨티노스 성 | 14/19 | 0 |
| `0x184364` | イーストシティ | 이스트 시티 | 12/15 | 0 |
| `0x184390` | レドンド | 레돈드 | 7/9 | 0 |
| `0x1843BC` | リゼンブール | 리젠블 | 7/13 | 0 |

### `material_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2F58` | 鉛　　　　　　　加工し易い重金属 | 납　　　　　　　가공 쉬운 중금속 | 34/34 | 0 |
| `0x3D2F98` | 鉄　　　　　　　非常に堅固な金属 | 철　　　　　　　매우 견고한 금속 | 34/34 | 0 |
| `0x3D3154` | 粘土　　　　　　粘りけのある土 | 점토　　　　　　끈기가 있는 흙 | 32/32 | 0 |
| `0x3D31B8` | ワイン　　　　　ぶどうの醸造酒 | 와인　　　　　　포도로 빚은 술 | 32/32 | 0 |
| `0x3D331E` | ダークジュエル　怪しく光る宝石 | 다크 주얼　　　 수상한 빛 보석 | 32/32 | 0 |
| `0x3D333E` | ダークストーン　高密度の黒い石 | 다크스톤　　　　고밀도 검은 돌 | 32/32 | 0 |
| `0x3D3380` | ダークマター　　光を吸収する塊 | 다크 매터　　　 빛 흡수 덩어리 | 32/32 | 0 |

### `material_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2E94` | 錬成できません　質量価値が０以下 | 연성 불가　　　 질량값 0 이하 | 31/34 | 0 |
| `0x3D2EB6` | チタン　　　　　軽くて硬い金属 | 티타늄　　　　　가볍고 단단함 | 31/32 | 0 |
| `0x3D2ED6` | 鋼　　　　　　　錬度の高い鋼鉄 | 강철　　　　　　제련도 높음 | 29/32 | 0 |
| `0x3D2EF6` | クロム　　　　　耐食性に優れる | 크롬　　　　　　내식성 우수 | 29/32 | 0 |
| `0x3D2F16` | 銅　　　　　　　通電性の高い金属 | 구리　　　　　　전도성 높음 | 29/34 | 0 |
| `0x3D2F38` | 銀　　　　　　　熱伝導性が高い | 은　　　　　　　열전도 높음 | 29/32 | 0 |
| `0x3D2F7A` | 青銅　　　　　　銅よりも硬い | 청동　　　　　　단단한 합금 | 29/30 | 0 |
| `0x3D2FBA` | 金　　　　　　　黄金色に輝く金属 | 금　　　　　　　황금빛 금속 | 29/34 | 0 |

### `registry_a_entry12_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8730` | リオライト | 리오라이트 | 11/11 | 0 |
| `0x7A873C` | 幻の機械鎧の素材　１／５ | 환상의 오토메일 소재 1/5 | 25/25 | 0 |
| `0x7A87D4` | 幻の機械鎧の素材　３／５ | 환상의 오토메일 소재 3/5 | 25/25 | 0 |
| `0x7A8AB4` | エリシアちゃん誘拐事件解決の証 | 엘리시아 납치 사건 해결의 증표 | 31/31 | 0 |

### `registry_a_entry12_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8594` | 回復薬２体力を１００回復する薬 | 회복약 2체력 100 회복 | 23/31 | 0 |
| `0x7A8624` | 回復薬４体力を３００回復する薬 | 회복약 4체력 300 회복 | 23/31 | 0 |
| `0x7A866C` | 回復薬５体力を５００回復する薬 | 회복약 5체력 500 회복 | 23/31 | 0 |
| `0x7A877C` | ヴィリジウム幻の機械鎧の素材　２／５ | 비리지움환상의 오토메일 소재 2/5 | 34/40 | 0 |
| `0x7A8814` | ソリタリウム幻の機械鎧の素材　４／５ | 솔리타리움환상의 오토메일 소재 4/5 | 36/40 | 0 |
| `0x7A8E78` | 花束古城の最上階に咲いていた花 | 꽃다발고성 최상층 꽃 | 22/31 | 0 |
| `0x7A86F8` | アルが拾った猫 | 알이 주운 냥 | 13/15 | 0 |
| `0x7A87C8` | レドニウム | 레도니움 | 9/11 | 0 |

### `registry_a_entry8_prefixed_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6DFFB0` | ビックリしました | ビックリしました | 17/17 | 1 |
| `0x6F086E` | 知っているかね？ | 知っているかね? | 16/17 | 1 |

### `registry_a_entry8_prefixed_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B7B2E` | 腹へったぁ… | 腹へったぁ… | 13/13 | 0 |
| `0x6B7B44` | のど渇いたぁ… | のど渇いたぁ… | 15/15 | 0 |
| `0x6B7B8E` | 街に着いたからね | 街に着いたからね | 17/17 | 0 |
| `0x6B7BBA` | 食いものぉぉぉ… | 食いものぉぉぉ… | 17/17 | 0 |
| `0x6B7BD4` | みずぅぅ… | みずぅぅ… | 11/11 | 0 |
| `0x6B7C4A` | 今日はにぎやかね | 今日はにぎやかね | 17/17 | 0 |
| `0x6B7CD6` | 見慣れない方ですね。 | 見慣れない方ですね。 | 21/21 | 0 |
| `0x6B7D20` | ある物を探して | ある物を探して | 15/15 | 0 |

### `registry_a_entry8_prefixed_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B7A36` | 医者になりたいんだけど、 | 医者になりたいんだけど, | 24/25 | 0 |
| `0x6B7A54` | どうやったらなれるのかな？ | どうやったらなれるのかな? | 26/27 | 0 |
| `0x6B7B6E` | はいはい、もう心配ないよ。 | はいはい,もう心配ないよ。 | 26/27 | 0 |
| `0x6B7BFA` | ははは、兄さんってば | ははは,兄さんってば | 20/21 | 0 |
| `0x6B7CF4` | 旅の方ですか？ | 旅の方ですか? | 14/15 | 0 |
| `0x6B7E10` | エドワード・エルリック！ | エドワード・エルリック! | 24/25 | 0 |
| `0x6B7E38` | あなた方は兄弟なの？ | あなた方は兄弟なの? | 20/21 | 0 |
| `0x6B7E5A` | いいわねぇ、家族がいるって。 | いいわねぇ,家族がいるって。 | 28/29 | 0 |

### `registry_a_entry8_prefixed_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x71D5CE` | 「キメラ」(合成獣 | 「キメラ」（合成獣 | 20/19 | 0 |

### `registry_a_map_labels` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6C809C` | 10：ソリン村 | 10:소린 마을 | 13/13 | 0 |
| `0x6DE8BC` | 19：中央軍司令部 | 19:중앙군 사령부 | 17/17 | 0 |
| `0x6FE538` | 32：図書館分館 | 32:도서관 분관 | 15/15 | 0 |
| `0x710584` | 42：東方軍司令部 | 42:동방군 사령부 | 17/17 | 0 |
| `0x74304C` | 62：クルス遺跡① | 62:크루스 유적① | 17/17 | 0 |
| `0x747018` | 63：クルス遺跡② | 63:크루스 유적② | 17/17 | 0 |
| `0x7496B4` | 64：クルス遺跡③ | 64:크루스 유적③ | 17/17 | 0 |
| `0x75FDAC` | 70：列車内① | 70:열차 안① | 13/13 | 0 |

### `registry_a_map_labels` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6BE150` | 03：教会内廊下 | 03:교회 복도 | 13/15 | 0 |
| `0x6C04C4` | 05：レドンド | 05:레돈도 | 10/13 | 0 |
| `0x6C3AF8` | 07：銀行内 | 07:은행 | 8/11 | 0 |
| `0x6C5088` | 08：金庫室 | 08:금고실 | 10/11 | 0 |
| `0x6C9F4C` | 11：村長の家 | 11:촌장 집 | 11/13 | 0 |
| `0x6CF424` | 13：ヴィヴァス | 13:비바스 | 10/15 | 0 |
| `0x6D388C` | 14：セントラル中央 | 14:센트럴 중앙 | 15/19 | 0 |
| `0x6D8474` | 15：宿屋セントラル | 15:센트럴 여관 | 15/19 | 0 |

### `registry_d_fc_script_texts` / `packed_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7F301F` | さぁ相手になってやるぜ！ | 자 상대가 되어 줘! | 19/25 | 0 |
| `0x7F3049` | 兄さん、どうやって戦うの？ | 형, 어떻게 싸우는 거야? | 24/27 | 0 |
| `0x7F3075` | 錬成であっさり終わらせる！ | 연성으로 시원하게 끝낸다! | 26/27 | 0 |
| `0x7F30C0` | このコマンドで錬成だ！ | 이 커맨드로 연성이야! | 22/23 | 0 |
| `0x7F30E8` | 素材や技を作るんだね | 소재나 기술을 만드는 거구나 | 28/21 | 0 |
| `0x7F310E` | そう、説明が表示されるから\nムズかしいことじゃないさ\nとりあえず見とけ | 그래, 설명이 표시되니까\n어려운 건 아니야\n일단 보고 있어 | 56/69 | 0 |
| `0x7F31CA` | これが素材錬成だ | 이게 소재 연성이야 | 19/17 | 0 |
| `0x7F31EC` | これで自分が欲しい素材を\n作っていくんだね？ | 이렇게 원하는 소재를\n만들어 가는 거구나? | 41/44 | 0 |

### `save_menu_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x772E4A` | 今はアルがいないから | 지금은　알이　없어서 | 20/20 | 0 |
| `0x772F5C` | セーブ完了！ | 저장　완료！ | 12/12 | 0 |
| `0x773106` | 前のデータに上書きするぞ？ | 이전　데이터에　덮을까요？ | 26/26 | 0 |
| `0x77318E` | セーブ完了！ | 저장　완료！ | 12/12 | 0 |

### `save_menu_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x772E64` | セーブはできないぞ | 저장　불가 | 10/18 | 0 |
| `0x772E96` | これまでの旅を記録する？ | 여정을　기록할까요？ | 20/24 | 0 |
| `0x772EE2` | 前の記録に上書きしてもいい？ | 이전　기록에　덮어쓸까요？ | 26/28 | 0 |
| `0x772F3A` | セーブ中だよ | 저장　중… | 10/12 | 0 |
| `0x772F7A` | このままゲームを続けるの？ | 이대로　계속할까요？ | 20/26 | 0 |
| `0x7730B0` | 今までの旅をセーブするか？ | 여정을　저장할까요？ | 20/26 | 0 |
| `0x773164` | セーブ中だ… | 저장　중… | 10/12 | 0 |
| `0x7731B4` | このまま旅を続けるか？ | 이대로　계속할까요？ | 20/22 | 0 |

### `startup_intro_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x703D70` | 大陸暦 | 대륙력 | 6/6 | 0 |

### `startup_intro_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x703D7E` | １９１０年　２月 | 1910년　2월 | 11/16 | 0 |
| `0x703D94` | 　　リゼンブール村 | 　　리젠블　마을 | 16/18 | 0 |
| `0x703DAC` | 　兄１１歳　　弟１０歳 | 　형11세　동생10세 | 18/22 | 0 |

### `system_messages` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x088558` | 通信中・・・ | 통신 중… | 10/13 | 1 |
| `0x088568` | 通信エラー！\nケーブルを確認してください | 통신 오류!\n케이블을 확인해 주세요 | 34/40 | 1 |
| `0x088594` | 通信エラー！\nデータ転送できませんでした | 통신 오류!\n데이터를 전송하지 못했습니다 | 40/40 | 1 |
| `0x0885C0` | 接続数オーバー！\n接続数を１台にしてください | 접속 수 초과!\n접속 수를 1대로 맞춰 주세요 | 42/44 | 1 |
| `0x0774FC` | をストックしました |  보관했습니다 | 14/19 | 2 |
| `0x088538` | 通信錬成開始？\nはい　いいえ | 통신 연성을 시작할까요?\n예 아니요 | 34/28 | 1 |
| `0x088D3C` | 全滅しました・・・ | 전멸했습니다… | 15/19 | 2 |
| `0x088D58` | 逃げだした・・・ | 도망쳤습니다… | 15/17 | 2 |

### `system_messages` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x0768ED` | 持っていません　 | 없습니다 | 9/17 | 0 |

### `ui_skill_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08B608` | 敵に命中した瞬間傷口から分解する | 명중 순간 상처를 분해 | 22/33 | 1 |
| `0x08B62C` | クロスダーツ | 크로스 다트 | 12/13 | 1 |
| `0x08B63C` | 相手の治癒力を高めて回復させる | 대상의 치유력을 높여 회복 | 26/31 | 1 |
| `0x08B65C` | 治癒錬成 | 치유 연성 | 10/9 | 1 |
| `0x08B668` | 目にもとまらぬ超高速の抜刀術 | 눈으로 좇기 힘든 초고속 발도술 | 31/29 | 1 |
| `0x08B688` | 迅雷 | 신뢰 | 5/5 | 1 |
| `0x08B690` | 敵陣に飛び込み敵全体に雷攻撃 | 적진에 뛰어들어 적 전체를 번개로 공격 | 38/29 | 1 |
| `0x08B6B0` | 遠雷 | 원뢰 | 5/5 | 1 |
