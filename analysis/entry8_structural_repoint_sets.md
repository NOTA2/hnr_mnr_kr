# Entry8 Structural Repoint Sets

| set | offsets | description |
|---|---:|---|
| `safe_tail_baseline` | 60 | Previously working conservative tail-safe offset set. |
| `structural_early` | 1763 | All variable offsets in unprotected segments below 0x100. |
| `structural_late` | 725 | All variable offsets in unprotected segments from 0x100 upward. |
| `structural_all_unprotected` | 2488 | All variable offsets except protected opening segments. |

## Segment Counts

| table | variable | tail-safe | bucket |
|---:|---:|---:|---|
| `0x20` | 72 | 0 | `early` |
| `0x24` | 36 | 0 | `early` |
| `0x28` | 7 | 0 | `early` |
| `0x2C` | 15 | 1 | `early` |
| `0x30` | 42 | 0 | `early` |
| `0x38` | 25 | 2 | `early` |
| `0x3C` | 9 | 0 | `early` |
| `0x40` | 19 | 0 | `early` |
| `0x44` | 18 | 0 | `early` |
| `0x48` | 16 | 1 | `early` |
| `0x4C` | 31 | 0 | `early` |
| `0x50` | 25 | 0 | `early` |
| `0x54` | 61 | 1 | `early` |
| `0x58` | 4 | 0 | `early` |
| `0x5C` | 23 | 0 | `early` |
| `0x60` | 14 | 5 | `early` |
| `0x64` | 16 | 0 | `early` |
| `0x68` | 44 | 0 | `early` |
| `0x6C` | 15 | 0 | `early` |
| `0x70` | 99 | 0 | `early` |
| `0x74` | 35 | 3 | `early` |
| `0x78` | 94 | 1 | `early` |
| `0x7C` | 16 | 0 | `early` |
| `0x80` | 2 | 0 | `early` |
| `0x84` | 4 | 0 | `early` |
| `0x88` | 1 | 0 | `early` |
| `0x8C` | 2 | 0 | `early` |
| `0x90` | 1 | 0 | `early` |
| `0x94` | 44 | 0 | `early` |
| `0x98` | 10 | 0 | `early` |
| `0x9C` | 50 | 3 | `early` |
| `0xA0` | 4 | 0 | `early` |
| `0xA4` | 10 | 2 | `early` |
| `0xA8` | 4 | 0 | `early` |
| `0xAC` | 6 | 0 | `early` |
| `0xB4` | 24 | 0 | `early` |
| `0xB8` | 4 | 0 | `early` |
| `0xBC` | 40 | 0 | `early` |
| `0xC0` | 27 | 0 | `early` |
| `0xC4` | 30 | 1 | `early` |
| `0xC8` | 352 | 8 | `early` |
| `0xCC` | 34 | 0 | `early` |
| `0xD0` | 18 | 0 | `early` |
| `0xD4` | 67 | 0 | `early` |
| `0xD8` | 42 | 0 | `early` |
| `0xDC` | 38 | 0 | `early` |
| `0xE8` | 27 | 0 | `early` |
| `0xEC` | 26 | 0 | `early` |
| `0xF0` | 56 | 5 | `early` |
| `0xF4` | 77 | 2 | `early` |
| `0xF8` | 26 | 2 | `early` |
| `0xFC` | 1 | 0 | `early` |
| `0x104` | 4 | 0 | `late` |
| `0x108` | 29 | 0 | `late` |
| `0x10C` | 13 | 0 | `late` |
| `0x110` | 46 | 3 | `late` |
| `0x114` | 42 | 0 | `late` |
| `0x118` | 16 | 0 | `late` |
| `0x11C` | 123 | 7 | `late` |
| `0x120` | 36 | 1 | `late` |
| `0x124` | 41 | 0 | `late` |
| `0x128` | 34 | 0 | `late` |
| `0x12C` | 18 | 0 | `late` |
| `0x130` | 114 | 0 | `late` |
| `0x134` | 64 | 0 | `late` |
| `0x138` | 8 | 0 | `late` |
| `0x13C` | 7 | 4 | `late` |
| `0x140` | 5 | 0 | `late` |
| `0x144` | 4 | 0 | `late` |
| `0x148` | 1 | 1 | `late` |
| `0x14C` | 4 | 0 | `late` |
| `0x160` | 60 | 0 | `late` |
| `0x168` | 56 | 7 | `late` |
