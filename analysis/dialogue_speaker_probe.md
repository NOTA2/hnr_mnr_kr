# Dialogue Speaker Probe

This probe does not assign speaker IDs. It captures objective per-record control gaps around representative dialogue lines so portrait/speaker state tracing can continue without relying on guesswork.

## Liore early arrival hunger/thirst exchange

- Status: `speaker_not_objectively_identified_yet`
- Consecutive records with only short repetitive control gaps are candidate same-turn / same-active-speaker lines.
- Larger control-gap changes between adjacent records are candidate speaker/portrait/state transitions, but not proven speaker IDs yet.

### `腹へったぁ…`

- Index: `2`
- Header: `0x6b7b2a`
- Text offset: `0x6b7b2e`
- Control gap length: `188`
- Control gap: `0d ff 07 ff 00 00 22 ff 00 00 00 00 00 00 00 00 00 00 00 00 00 00 a0 0b 00 00 ff ff ff ff 00 80 ff 01 00 00 00 00 00 04 00 00 00 00 00 00 02 80 04 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 28 ff 00 70 22 26 4e ff 01 01 ff ff 00 00 2b ff 01 80 01 00 05 ff 0a 00 2b ff 02 80 02 00 23 ff 10 1b 82 00 68 00 90 01 90 01 92 01 00 00 24 ff 00 03 1a ff 06 14 00 00 05 ff 14 00 4b ff 10 22 08 60 00 c8 98 ff d8 ff 50 ff 01 00 00 00 1b ff 02 00 00 00 06 ff 80 80 05 00 07 ff 00 80 08 ff 06 00 01 ff 02 00 82 cd 81 41 05 ff 0a 00`
- Header prefix: `01 ff 06 00`

### `のど渇いたぁ…`

- Index: `3`
- Header: `0x6b7b40`
- Text offset: `0x6b7b44`
- Control gap length: `6`
- Control gap: `04 ff 05 ff 0a 00`
- Header prefix: `01 ff 07 00`

### `はいはい、もう心配ないよ。`

- Index: `4`
- Header: `0x6b7b6a`
- Text offset: `0x6b7b6e`
- Control gap length: `24`
- Control gap: `10 ff 01 00 0d ff 1b ff 0b 80 00 00 06 ff 40 00 05 00 02 ff 08 ff 04 00`
- Header prefix: `01 ff 0d 00`

### `街に着いたからね`

- Index: `5`
- Header: `0x6b7b8a`
- Text offset: `0x6b7b8e`
- Control gap length: `2`
- Control gap: `04 ff`
- Header prefix: `01 ff 08 00`

## Tutorial blood exchange scene

- Status: `speaker_not_objectively_identified_yet`
- Consecutive records with only short repetitive control gaps are candidate same-turn / same-active-speaker lines.
- Larger control-gap changes between adjacent records are candidate speaker/portrait/state transitions, but not proven speaker IDs yet.

### `なにと交換するの？`

- Index: `9162`
- Header: `0x76b322`
- Text offset: `0x76b326`
- Control gap length: `48`
- Control gap: `04 ff 01 ff 03 00 90 b8 90 5f 82 cd 10 ff 81 00 08 ff 0c 00 01 ff 03 00 81 63 81 63 81 63 05 ff 0a 00 10 ff 80 00 04 ff 05 ff 0a 00 08 ff 06 00`
- Header prefix: `01 ff 09 00`

### `いいから、`

- Index: `9163`
- Header: `0x76b36c`
- Text offset: `0x76b370`
- Control gap length: `52`
- Control gap: `10 ff 81 00 05 ff 46 00 02 ff 2b ff 33 00 36 00 10 ff 00 00 06 ff 80 0c 05 00 10 ff 01 00 08 ff 0c 00 01 ff 03 00 81 63 81 63 81 63 10 ff 00 00 08 ff 05 00`
- Header prefix: `01 ff 05 00`

### `指だせ。`

- Index: `9164`
- Header: `0x76b37e`
- Text offset: `0x76b382`
- Control gap length: `4`
- Control gap: `05 ff 0a 00`
- Header prefix: `01 ff 04 00`

### `オレたちの血も必要なんだ。`

- Index: `9165`
- Header: `0x76b390`
- Text offset: `0x76b394`
- Control gap length: `6`
- Control gap: `04 ff 05 ff 0a 00`
- Header prefix: `01 ff 0d 00`

### `イタッ！！`

- Index: `9166`
- Header: `0x76b3f4`
- Text offset: `0x76b3f8`
- Control gap length: `70`
- Control gap: `04 ff 08 ff 04 00 05 ff 14 00 01 ff 03 00 90 d8 82 e9 82 bc 10 ff 01 00 05 ff 46 00 07 ff 00 00 05 ff 1e 00 2b ff 69 00 36 00 2b ff 69 00 37 00 05 ff 1e 00 10 ff 80 00 06 ff 40 0c 05 00 07 ff 00 80 08 ff 03 00`
- Header prefix: `01 ff 05 00`

### `この血で魂の情報はよしっ`

- Index: `9167`
- Header: `0x76b426`
- Text offset: `0x76b42a`
- Control gap length: `36`
- Control gap: `10 ff 81 00 05 ff 3c 00 02 ff 2b ff 66 00 36 00 2b ff 66 00 37 00 10 ff 00 00 06 ff 80 00 05 00 08 ff 05 00`
- Header prefix: `01 ff 0c 00`

