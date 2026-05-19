# Translation Expansion Opportunities

- Last updated: `2026-05-19T16:50:31.790635+00:00`
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
| ability_texts | `fixed_capacity_exact: 76`, `in_place_slack_only: 257`, `too_long_without_pointer: 80` |
| battle_texts | `fixed_capacity_exact: 10`, `in_place_slack_only: 31`, `too_long_without_pointer: 63` |
| choice_yes_no_texts | `in_place_slack_only: 16` |
| credits_texts | `direct_repoint_available: 10` |
| duplicate_text_slots | `direct_repoint_available: 1`, `fixed_capacity_exact: 8`, `in_place_slack_only: 19` |
| inline_event_texts | `fixed_capacity_exact: 2`, `in_place_slack_only: 39` |
| item_texts | `direct_repoint_available: 49` |
| location_texts | `direct_repoint_available: 1`, `in_place_slack_only: 7`, `too_long_without_pointer: 2` |
| material_texts | `fixed_capacity_exact: 9`, `in_place_slack_only: 28`, `too_long_without_pointer: 7` |
| registry_a_entry12_texts | `fixed_capacity_exact: 3`, `in_place_slack_only: 15`, `too_long_without_pointer: 4` |
| registry_a_entry8_prefixed_texts | `direct_repoint_available: 2`, `fixed_capacity_exact: 3061`, `in_place_slack_only: 7354` |
| registry_a_map_labels | `fixed_capacity_exact: 11`, `in_place_slack_only: 28`, `too_long_without_pointer: 9` |
| registry_d_fc_script_texts | `packed_repoint_available: 244` |
| save_menu_texts | `fixed_capacity_exact: 4`, `in_place_slack_only: 8` |
| startup_intro_texts | `fixed_capacity_exact: 3`, `in_place_slack_only: 1` |
| system_messages | `direct_repoint_available: 9`, `in_place_slack_only: 1` |
| ui_skill_texts | `direct_repoint_available: 25` |

## Examples

### `ability_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D3772` | 黄昏の壁 | 황혼 벽 | 8/8 | 0 |
| `0x3D377B` | 敵の足元に壁を　錬成して攻撃 | 발밑에 벽을　　 연성해 공격 | 29/29 | 0 |
| `0x3D3840` | 鋼鉄の大砲を　　錬成して攻撃 | 강철 대포를　　 연성해 공격 | 29/29 | 0 |
| `0x3D39D1` | 敵に鉄巨人の　　攻撃を浴びせる | 철거인이　　　　공격을 퍼붓음 | 31/31 | 0 |
| `0x3D39F8` | 大きな剣を錬成　敵を分断する | 큰 검을 연성해　적을 가른다 | 29/29 | 0 |
| `0x3D3D34` | 槍を錬成して攻撃 | 창을연성해 공격 | 16/16 | 0 |
| `0x3D42EA` | 紺碧の壁 | 감청 벽 | 8/8 | 0 |
| `0x3D43BC` | 錬成した壁を　　殴って攻撃 | 연성한 벽을　　 쳐서 공격 | 27/27 | 0 |

### `ability_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D3799` | 旋律の壁 | 선율벽 | 7/8 | 0 |
| `0x3D37C0` | 虚空の壁 | 허공벽 | 7/8 | 0 |
| `0x3D37C9` | 複数の壁を錬成　敵全体を攻撃 | 여러 벽을 연성해전체 공격 | 27/29 | 0 |
| `0x3D37E7` | 忘却の壁 | 망각벽 | 7/8 | 0 |
| `0x3D380E` | 鎮魂の壁 | 진혼벽 | 7/8 | 0 |
| `0x3D38E5` | エルリックカノン | 엘릭캐논 | 9/16 | 0 |
| `0x3D391D` | 敵に鉄巨人の　　パンチを降らせる | 철거인이　　　　펀치를 꽂음 | 29/33 | 0 |
| `0x3D3975` | 敵に鉄巨人の　　キックを降らせる | 철거인이　　　　킥을 꽂는다 | 29/33 | 0 |

### `ability_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D3835` | エド式大砲 | 에드식대포 | 11/10 | 0 |
| `0x3D385E` | エド式巨大砲 | 에드식거대포 | 13/12 | 0 |
| `0x3D3889` | エド式超巨大砲 | 에드식초거대포 | 15/14 | 0 |
| `0x3D38B6` | エド式超絶巨大砲 | 에드식초절거대포 | 17/16 | 0 |
| `0x3D3914` | 鉄拳制裁 | 철권제재 | 9/8 | 0 |
| `0x3D393F` | 鉄拳大制裁 | 철권대제재 | 11/10 | 0 |
| `0x3D396C` | 鉄脚制裁 | 철각제재 | 9/8 | 0 |
| `0x3D3997` | 鉄脚大制裁 | 철각대제재 | 11/10 | 0 |

### `battle_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D203D` | 壁を錬成し　　　相手を攻撃 | 벽을 연성해　　 상대 공격 | 27/27 | 0 |
| `0x3D211F` | 瓦礫をパンチで　錬成し打ち出す | 펀치로 잔해를　 연성해 날린다 | 31/31 | 0 |
| `0x3D2192` | 敵陣に飛び込み　敵全体に雷攻撃 | 적진돌입　　　　전체 번개공격 | 31/31 | 0 |
| `0x3D2202` | クロスダーツ | 크로스 다트 | 12/12 | 0 |
| `0x3D2259` | 仕込みバズーカ | 숨겨둔 바주카 | 14/14 | 0 |
| `0x3D227B` | 豪腕ラリアート | 강완 래리어트 | 14/14 | 0 |
| `0x3D23F4` | ラストリゾート | 라스트 리조트 | 14/14 | 0 |
| `0x3D228D` | 豪腕ラリアート | 강완 래리어트 | 14/14 | 0 |

### `battle_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2062` | 連続で攻撃を　　たたき込む | 연속 공격을　　 퍼붓는다 | 26/27 | 0 |
| `0x3D2081` | 集めた猫たちが　アルのために攻撃 | 고양이들이　　　알을 위해 공격 | 32/33 | 0 |
| `0x3D20C9` | 一点集中で　　　銃を連射する | 한 점 집중해　　총 연사 | 25/29 | 0 |
| `0x3D20E7` | マッハパンチ | 마하 펀치 | 10/12 | 0 |
| `0x3D20F4` | 高速でパンチを　連打する技 | 고속펀치　　　　연속타 | 24/27 | 0 |
| `0x3D2110` | ＡＳ式錬成術１ | ＡＳ연성술 1 | 13/14 | 0 |
| `0x3D213F` | ＡＳ式錬成術２ | ＡＳ연성술 2 | 13/14 | 0 |
| `0x3D214E` | 地面をパンチし　敵の下から攻撃 | 지면을 쳐　　　 아래서 공격 | 29/31 | 0 |

### `battle_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2036` | 壁錬成 | 벽연성 | 7/6 | 0 |
| `0x3D2059` | 撃鉄靠掌 | 격철고장 | 9/8 | 0 |
| `0x3D20A3` | 発火 | 발화 | 5/4 | 0 |
| `0x3D20A8` | 手加減なしの　　発火攻撃 | 가차 없이　　　 발화공격 | 26/25 | 0 |
| `0x3D20C2` | 銃連射 | 총연사 | 7/6 | 0 |
| `0x3D216E` | 紫電 | 자전 | 5/4 | 0 |
| `0x3D218D` | 遠雷 | 원뢰 | 5/4 | 0 |
| `0x3D21B2` | 迅雷 | 신뢰 | 5/4 | 0 |

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
| `0x08C3AC` | 　　チーフプロデューサー　　　　　　　　 | 　　치프　프로듀서　　　　　　　　 | 35/40 | 1 |
| `0x08C404` | 　　ゼネラルプロデューサー　　　　　　　 | 　　총괄　프로듀서　　　　　　　 | 33/40 | 1 |
| `0x08C45C` | 　　エグゼクティブプロデューサー　　　　 | 　　책임　프로듀서　　　　 | 27/40 | 1 |
| `0x08C7CC` | 　　ソニー・クリエイティブプロダクツ　　 | 　　소니　크리에이티브　프로덕츠　　 | 37/40 | 1 |
| `0x08C92C` | 　　　　　スクウェア・エニックス　　　　 | 　　　　　스퀘어　에닉스　　　　 | 33/40 | 1 |
| `0x08CA34` | 　　　ペイント　中山　しほ子／ボンズ　　 | 　　　페인트　나카야마　시호코/본즈　　 | 40/40 | 1 |
| `0x08CAB8` | 　　　　　ポール・トゥ・ウィン　　　　　 | 　　　　　폴　투　윈　　　　　 | 31/40 | 1 |
| `0x08CC18` | 　　　 堀口　比呂志／ツーファイブ 　　　 | 　　　　호리구치히로시/투파이브　　　　 | 40/40 | 1 |

### `duplicate_text_slots` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08B80C` | 壁錬成 | 벽연성 | 7/6 | 1 |

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
| `0x6B5D6A` | 01：リオール街 | 01:리올 거리 | 13/14 | 0 |
| `0x6C58B2` | 09：レドンド下水道 | 09:레돈드 하수도 | 17/18 | 0 |
| `0x739630` | 57：--ダイムラー邸③2階 | 57:다이무라③2층 | 17/23 | 0 |
| `0x739E18` | 58：ダイムラー邸④地下 | 58:다이무라④지하 | 18/22 | 0 |
| `0x7A8558` | 体力を５０回復する薬 | 체력 50 회복약 | 14/20 | 0 |
| `0x7A85E4` | 体力を２００回復する薬 | 체력 200 회복약 | 15/22 | 0 |
| `0x7A86BC` | 国家錬金術師の証 | 연금술사 증표 | 13/16 | 0 |
| `0x7A886C` | 幻の機械鎧の素材　５／５ | 오토메일 소재 5/5 | 17/24 | 0 |

### `inline_event_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6D70F6` | 誰がチビだっ！ | 누가꼬맹이래！ | 14/14 | 0 |
| `0x6F7A16` | センズか… | 센즈인가… | 10/10 | 0 |

### `inline_event_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B8D60` | おおーっ！ | 오오－！ | 8/10 | 0 |
| `0x6BA8A2` | 　水をあげる　水をあげない | 　물주기　안주기 | 16/26 | 0 |
| `0x6CF240` | 　丸太をあげる　丸太をあげない | 　통나무주기　안주기 | 20/30 | 0 |
| `0x6D8E38` | 　泊まる　やっぱ泊まらない | 　묵는다　안묵는다 | 18/26 | 0 |
| `0x6DA488` | だーっ！ | 으악！ | 6/8 | 0 |
| `0x6DA496` | なんで脱ぐ必要がある！ | 왜벗어야해！ | 12/22 | 0 |
| `0x6E549E` | 　いつでもオッケー！　ちょっと待ったー！ | 　언제든오케이！　잠깐만！ | 26/40 | 0 |
| `0x6E56AC` | 　いつでもオッケー！　ちょっと待ったー！ | 　언제든오케이！　잠깐만！ | 26/40 | 0 |

### `item_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08AED8` | 古城の最上階に咲いていた花 | 고성 최상층에 핀 꽃 | 20/26 | 1 |
| `0x08AEF4` | 花束 | 꽃다발 | 7/4 | 1 |
| `0x08AEFC` | 東方軍司令部で受け取った書類 | 동방군 사령부에서 받은 서류 | 28/28 | 1 |
| `0x08AF1C` | 書類③ | 서류③ | 7/6 | 1 |
| `0x08AF24` | 東方軍司令部へ届ける書類 | 동방군 사령부에 전달할 서류 | 28/24 | 1 |
| `0x08AF40` | 書類② | 서류② | 7/6 | 1 |
| `0x08AF48` | ブラッドレイ大総統に届ける書類 | 브래드레이 대총통에게 전달할 서류 | 34/30 | 1 |
| `0x08AF68` | 書類① | 서류① | 7/6 | 1 |

### `location_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x18425C` | セントラルシティ | 센트럴 시티 | 12/16 | 4 |

### `location_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x184288` | ヴィヴァス | 비바스 | 7/10 | 0 |
| `0x1842B4` | リオール | 리올 | 5/8 | 0 |
| `0x1842E0` | ソリン | 솔링 | 5/6 | 0 |
| `0x184338` | オルヘンティノス城 | 올헨티노스 성 | 14/18 | 0 |
| `0x184364` | イーストシティ | 이스트 시티 | 12/14 | 0 |
| `0x184390` | レドンド | 레돈드 | 7/8 | 0 |
| `0x1843BC` | リゼンブール | 리젠블 | 7/12 | 0 |

### `location_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x18430C` | ダイムラー邸 | 다이무라저택 | 13/12 | 0 |
| `0x1843E8` | クルス遺跡 | 크루스유적 | 11/10 | 0 |

### `material_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2EB6` | チタン　　　　　軽くて硬い金属 | 티타늄　　　　　가볍고 단단함 | 31/31 | 0 |
| `0x3D2F7A` | 青銅　　　　　　銅よりも硬い | 청동　　　　　　단단한 합금 | 29/29 | 0 |
| `0x3D3040` | 小石　　　　　　普通の石 | 자갈　　　　　　보통 돌 | 25/25 | 0 |
| `0x3D305A` | サファイア　　　青くて硬い宝石 | 사파이어　　　　푸르고 단단함 | 31/31 | 0 |
| `0x3D309A` | 水晶　　　　　　六角柱状の結晶 | 수정　　　　　　육각기둥 결정 | 31/31 | 0 |
| `0x3D325E` | 花　　　　　　　美しく弱い植物 | 꽃　　　　　　　아름답고 약함 | 31/31 | 0 |
| `0x3D327E` | 黒曜石　　　　　火山岩の一種 | 흑요석　　　　　화산암 일종 | 29/29 | 0 |
| `0x3D33C2` | 錬成できません　質量が７以上 | 연성 불가　　　 질량 7 이상 | 29/29 | 0 |

### `material_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2E94` | 錬成できません　質量価値が０以下 | 연성 불가　　　 질량값 0 이하 | 31/33 | 0 |
| `0x3D2ED6` | 鋼　　　　　　　錬度の高い鋼鉄 | 강철　　　　　　제련도 높음 | 29/31 | 0 |
| `0x3D2EF6` | クロム　　　　　耐食性に優れる | 크롬　　　　　　내식성 우수 | 29/31 | 0 |
| `0x3D2F16` | 銅　　　　　　　通電性の高い金属 | 구리　　　　　　전도성 높음 | 29/33 | 0 |
| `0x3D2F38` | 銀　　　　　　　熱伝導性が高い | 은　　　　　　　열전도 높음 | 29/31 | 0 |
| `0x3D2FBA` | 金　　　　　　　黄金色に輝く金属 | 금　　　　　　　황금빛 금속 | 29/33 | 0 |
| `0x3D2FDC` | プラチナ　　　　耐久、硬度とも○ | 플래티나　　　　내구 경도 우수 | 32/33 | 0 |
| `0x3D2FFE` | アメジスト　　　語源は酔わない | 자수정　　　　　취하지 않음 | 29/31 | 0 |

### `material_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x3D2F58` | 鉛　　　　　　　加工し易い重金属 | 납　　　　　　　가공 쉬운 중금속 | 34/33 | 0 |
| `0x3D2F98` | 鉄　　　　　　　非常に堅固な金属 | 철　　　　　　　매우 견고한 금속 | 34/33 | 0 |
| `0x3D3154` | 粘土　　　　　　粘りけのある土 | 점토　　　　　　끈기가 있는 흙 | 32/31 | 0 |
| `0x3D31B8` | ワイン　　　　　ぶどうの醸造酒 | 와인　　　　　　포도로 빚은 술 | 32/31 | 0 |
| `0x3D331E` | ダークジュエル　怪しく光る宝石 | 다크 주얼　　　 수상한 빛 보석 | 32/31 | 0 |
| `0x3D333E` | ダークストーン　高密度の黒い石 | 다크스톤　　　　고밀도 검은 돌 | 32/31 | 0 |
| `0x3D3380` | ダークマター　　光を吸収する塊 | 다크 매터　　　 빛 흡수 덩어리 | 32/31 | 0 |

### `registry_a_entry12_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8B60` | マスタング大佐　ああ無能！の証 | 머스탱 대령 아아 무능!의 증표 | 30/30 | 0 |
| `0x7A8C54` | アルの右腕 | 알 오른팔 | 10/10 | 0 |
| `0x7A8CF4` | アルの右足 | 알 오른발 | 10/10 | 0 |

### `registry_a_entry12_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8594` | 回復薬２体力を１００回復する薬 | 회복약 2체력 100 회복 | 23/30 | 0 |
| `0x7A8624` | 回復薬４体力を３００回復する薬 | 회복약 4체력 300 회복 | 23/30 | 0 |
| `0x7A866C` | 回復薬５体力を５００回復する薬 | 회복약 5체력 500 회복 | 23/30 | 0 |
| `0x7A877C` | ヴィリジウム幻の機械鎧の素材　２／５ | 비리지움환상의 오토메일 소재 2/5 | 34/39 | 0 |
| `0x7A8814` | ソリタリウム幻の機械鎧の素材　４／５ | 솔리타리움환상의 오토메일 소재 4/5 | 36/39 | 0 |
| `0x7A8E78` | 花束古城の最上階に咲いていた花 | 꽃다발고성 최상층 꽃 | 22/30 | 0 |
| `0x7A86F8` | アルが拾った猫 | 알이 주운 냥 | 13/14 | 0 |
| `0x7A87C8` | レドニウム | 레도니움 | 9/10 | 0 |

### `registry_a_entry12_texts` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7A8730` | リオライト | 리오라이트 | 11/10 | 0 |
| `0x7A873C` | 幻の機械鎧の素材　１／５ | 환상의 오토메일 소재 1/5 | 25/24 | 0 |
| `0x7A87D4` | 幻の機械鎧の素材　３／５ | 환상의 오토메일 소재 3/5 | 25/24 | 0 |
| `0x7A8AB4` | エリシアちゃん誘拐事件解決の証 | 엘리시아 납치 사건 해결의 증표 | 31/30 | 0 |

### `registry_a_entry8_prefixed_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6DFFB0` | ビックリしました | 놀랐습니다 | 10/16 | 1 |
| `0x6F086E` | 知っているかね？ | 알고　있나？ | 12/16 | 1 |

### `registry_a_entry8_prefixed_texts` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B7B22` | は、 | 하、 | 4/4 | 0 |
| `0x6B7B8E` | 街に着いたからね | 마을에　도착했어 | 16/16 | 0 |
| `0x6B7C3C` | あら、 | 어머、 | 6/6 | 0 |
| `0x6B7C4A` | 今日はにぎやかね | 오늘은　북적이네 | 16/16 | 0 |
| `0x6B7CF4` | 旅の方ですか？ | 여행자신가요？ | 14/14 | 0 |
| `0x6B7D12` | ああ、 | 그래、 | 6/6 | 0 |
| `0x6B7D20` | ある物を探して | 찾는게　있어서 | 14/14 | 0 |
| `0x6B7D6A` | 錬金術師の | 연금술사인 | 10/10 | 0 |

### `registry_a_entry8_prefixed_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6B7A36` | 医者になりたいんだけど、 | 의사가　되고　싶은데、 | 22/24 | 0 |
| `0x6B7A54` | どうやったらなれるのかな？ | 어떻게　해야　될까？ | 20/26 | 0 |
| `0x6B7B2E` | 腹へったぁ… | 배고파… | 8/12 | 0 |
| `0x6B7B44` | のど渇いたぁ… | 목말라… | 8/14 | 0 |
| `0x6B7B6E` | はいはい、もう心配ないよ。 | 그래그래、걱정하지　마。 | 24/26 | 0 |
| `0x6B7BBA` | 食いものぉぉぉ… | 먹을　거어어… | 14/16 | 0 |
| `0x6B7BD4` | みずぅぅ… | 무우울… | 8/10 | 0 |
| `0x6B7BFA` | ははは、兄さんってば | 하하하、형도　참 | 16/20 | 0 |

### `registry_a_map_labels` / `fixed_capacity_exact`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6C5088` | 08：金庫室 | 08:금고실 | 10/10 | 0 |
| `0x6E1A64` | 20：軍法会議所 | 20:군법회의소 | 14/14 | 0 |
| `0x6EA87C` | 22：大総統府 | 22:대총통부 | 12/12 | 0 |
| `0x6FCE0C` | 31：図書館 | 31:도서관 | 10/10 | 0 |
| `0x70B1A0` | 39：宿屋イースト１F | 39:이스트 여관 1Ｆ | 19/19 | 0 |
| `0x70BD08` | 40：宿屋イースト２F | 40:이스트 여관 2Ｆ | 19/19 | 0 |
| `0x71E5AC` | 45：練兵場 | 45:연병장 | 10/10 | 0 |
| `0x7291B0` | 48：軍刑務所① | 48:군형무소① | 14/14 | 0 |

### `registry_a_map_labels` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6BE150` | 03：教会内廊下 | 03:교회 복도 | 13/14 | 0 |
| `0x6C04C4` | 05：レドンド | 05:레돈도 | 10/12 | 0 |
| `0x6C3AF8` | 07：銀行内 | 07:은행 | 8/10 | 0 |
| `0x6C9F4C` | 11：村長の家 | 11:촌장 집 | 11/12 | 0 |
| `0x6CF424` | 13：ヴィヴァス | 13:비바스 | 10/14 | 0 |
| `0x6D388C` | 14：セントラル中央 | 14:센트럴 중앙 | 15/18 | 0 |
| `0x6D8474` | 15：宿屋セントラル | 15:센트럴 여관 | 15/18 | 0 |
| `0x6D9108` | 16：宿屋セントラル２F | 16:센트럴 여관 2Ｆ | 19/21 | 0 |

### `registry_a_map_labels` / `too_long_without_pointer`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x6C809C` | 10：ソリン村 | 10:소린 마을 | 13/12 | 0 |
| `0x6DE8BC` | 19：中央軍司令部 | 19:중앙군 사령부 | 17/16 | 0 |
| `0x6FE538` | 32：図書館分館 | 32:도서관 분관 | 15/14 | 0 |
| `0x710584` | 42：東方軍司令部 | 42:동방군 사령부 | 17/16 | 0 |
| `0x74304C` | 62：クルス遺跡① | 62:크루스 유적① | 17/16 | 0 |
| `0x747018` | 63：クルス遺跡② | 63:크루스 유적② | 17/16 | 0 |
| `0x7496B4` | 64：クルス遺跡③ | 64:크루스 유적③ | 17/16 | 0 |
| `0x75FDAC` | 70：列車内① | 70:열차 안① | 13/12 | 0 |

### `registry_d_fc_script_texts` / `packed_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x7F301F` | さぁ相手になってやるぜ！ | 자 상대가 되어 줘! | 19/24 | 0 |
| `0x7F3049` | 兄さん、どうやって戦うの？ | 형, 어떻게 싸우는 거야? | 24/26 | 0 |
| `0x7F3075` | 錬成であっさり終わらせる！ | 연성으로 시원하게 끝낸다! | 26/26 | 0 |
| `0x7F30C0` | このコマンドで錬成だ！ | 이 커맨드로 연성이야! | 22/22 | 0 |
| `0x7F30E8` | 素材や技を作るんだね | 소재나 기술을 만드는 거구나 | 28/20 | 0 |
| `0x7F310E` | そう、説明が表示されるから\nムズかしいことじゃないさ\nとりあえず見とけ | 그래, 설명이 표시되니까\n어려운 건 아니야\n일단 보고 있어 | 56/68 | 0 |
| `0x7F31CA` | これが素材錬成だ | 이게 소재 연성이야 | 19/16 | 0 |
| `0x7F31EC` | これで自分が欲しい素材を\n作っていくんだね？ | 이렇게 원하는 소재를\n만들어 가는 거구나? | 41/43 | 0 |

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
| `0x703D7E` | １９１０年　２月 | １９１０년　２월 | 16/16 | 0 |
| `0x703DAC` | 　兄１１歳　　弟１０歳 | 　형１１세　동생１０세 | 22/22 | 0 |

### `startup_intro_texts` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x703D94` | 　　リゼンブール村 | 　　리젠블　마을 | 16/18 | 0 |

### `system_messages` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x088558` | 通信中・・・ | 통신중・・・ | 13/12 | 1 |
| `0x088568` | 通信エラー！\nケーブルを確認してください | 통신 오류!\n케이블을 확인해 주세요 | 34/39 | 1 |
| `0x088594` | 通信エラー！\nデータ転送できませんでした | 통신 오류!\n데이터를 전송 실패 | 30/39 | 1 |
| `0x0885C0` | 接続数オーバー！\n接続数を１台にしてください | 접속 수 초과!\n접속 수를 1대로 맞춰 주세요 | 42/43 | 1 |
| `0x0774FC` | をストックしました |  보관했습니다 | 14/18 | 2 |
| `0x088538` | 通信錬成開始？\nはい　いいえ | 통신 시작할까?\n 예   아니요 | 28/27 | 1 |
| `0x088D3C` | 全滅しました・・・ | 전멸했습니다・・・ | 19/18 | 2 |
| `0x088D58` | 逃げだした・・・ | 도망쳤습니다・・・ | 19/16 | 2 |

### `system_messages` / `in_place_slack_only`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x0768ED` | 持っていません　 | 없습니다  | 10/16 | 0 |

### `ui_skill_texts` / `direct_repoint_available`

| Offset | Original | Current | Payload/Capacity | Pointers |
|---|---|---|---:|---:|
| `0x08B608` | 敵に命中した瞬間傷口から分解する | 명중 순간 상처를 분해 | 22/32 | 1 |
| `0x08B62C` | クロスダーツ | 크로스 다트 | 12/12 | 1 |
| `0x08B63C` | 相手の治癒力を高めて回復させる | 대상의 치유력을 높여 회복 | 26/30 | 1 |
| `0x08B65C` | 治癒錬成 | 치유 연성 | 10/8 | 1 |
| `0x08B668` | 目にもとまらぬ超高速の抜刀術 | 눈으로 좇기 힘든 초고속 발도술 | 31/28 | 1 |
| `0x08B688` | 迅雷 | 신뢰 | 5/4 | 1 |
| `0x08B690` | 敵陣に飛び込み敵全体に雷攻撃 | 적진에 뛰어들어 적 전체를 번개로 공격 | 38/28 | 1 |
| `0x08B6B0` | 遠雷 | 원뢰 | 5/4 | 1 |
