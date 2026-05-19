# Entry8 Opening Pagination Analysis

## Summary

- JP segment 0x150: `0xB499C`
- JP segment 0x15C: `0xB5A28`
- EN segment 0x150: `0x1EDFBC`
- EN segment 0x15C: `0x1EF104`
- JP opening block length: `0x5D8`
- EN opening block length: `0x690`

## Record Map

| JP offset | JP rel | EN rel | JP cnt | EN cnt | JP gap | EN gap | Text |
|---:|---:|---:|---:|---:|---:|---:|---|
| `0x76B1F8` | `0xF0C` | `0x2AA` | 11 | 10 | 44 | 3146 | 肉体の材料はそろえた。 |
| `0x76B23E` | `0xF52` | `0xF0C` | 10 | 7 | 10 | 2 | 母さんを元に戻そう。 |
| `0x76B260` | `0xF74` | `0xF20` | 9 | 7 | 20 | 2 | 生き返らせるんだ！ |
| `0x76B28A` | `0xF9E` | `0xF34` | 14 | 6 | 6 | 14 | …人体錬成は禁じられてるよ。 |
| `0x76B2B0` | `0xFC4` | `0xF52` | 12 | 1 | 18 | 8 | それに錬金術は等価交換… |
| `0x76B2DE` | `0xFF2` | `0xF60` | 10 | 2 | 48 | 12 | 肉体は交換できても、 |
| `0x76B326` | `0x103A` | `0xF74` | 9 | 9 | 52 | 2 | なにと交換するの？ |
| `0x76B370` | `0x1084` | `0xF8C` | 5 | 6 |  |  | いいから、 |
| `0x76B382` | `0xA` | `0xA` | 4 | 12 | 6 | 50 | 指だせ。 |
| `0x76B394` | `0x1C` | `0x58` | 13 | 2 | 70 | 36 | オレたちの血も必要なんだ。 |
| `0x76B3F8` | `0x80` | `0x84` | 5 | 8 | 36 | 2 | イタッ！！ |
| `0x76B42A` | `0xB2` | `0x9A` | 12 | 10 |  |  | この血で魂の情報はよしっ |

## Notes

- EN does not preserve JP relative positions. The first alchemy line is moved far earlier inside segment `0x150`.
- EN expands the opening block length and redistributes later lines across the rebuilt segment.
- This should be treated as event-script pagination, not as a simple text repoint template.
