from __future__ import annotations

import argparse
import json
import math
import re
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROM_BASE = 0x08000000
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
SUSPICIOUS_ASCII_SYMBOLS = set("`|{}[]<>^_~\\")
ALLOWED_NONPRINTABLE_TEXT_CHARS = {"\u3000"}


class ToolError(Exception):
    pass


@dataclass
class RomHeader:
    path: str
    size: int
    title: str
    game_code: str
    maker_code: str
    unit_code: int
    device_type: int
    version: int
    complement_check: int


class TableCodec:
    def __init__(self, mapping: Dict[bytes, str]) -> None:
        if not mapping:
            raise ToolError("빈 테이블은 사용할 수 없습니다.")
        self.mapping = mapping
        self.decode_keys = sorted(mapping.keys(), key=len, reverse=True)
        reverse: Dict[str, bytes] = {}
        for key, value in mapping.items():
            reverse.setdefault(value, key)
        self.encode_keys = sorted(reverse.keys(), key=len, reverse=True)
        self.reverse = reverse

    @classmethod
    def from_path(cls, path: Path) -> "TableCodec":
        mapping: Dict[bytes, str] = {}
        for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith(";") or line.startswith("//"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip().replace(" ", "")
            value = value.strip()
            if len(key) % 2 != 0 or not re.fullmatch(r"[0-9A-Fa-f]+", key):
                raise ToolError(f"{path}:{lineno}: 잘못된 테이블 키입니다: {key!r}")
            mapping[bytes.fromhex(key)] = value
        return cls(mapping)

    def decode(self, payload: bytes) -> Tuple[str, int]:
        parts: List[str] = []
        unknown = 0
        i = 0
        while i < len(payload):
            for key in self.decode_keys:
                if payload.startswith(key, i):
                    parts.append(self.mapping[key])
                    i += len(key)
                    break
            else:
                parts.append(f"[{payload[i]:02X}]")
                unknown += 1
                i += 1
        return "".join(parts), unknown

    def encode(self, text: str) -> bytes:
        out = bytearray()
        i = 0
        while i < len(text):
            for token in self.encode_keys:
                if text.startswith(token, i):
                    out.extend(self.reverse[token])
                    i += len(token)
                    break
            else:
                raise ToolError(f"테이블에 없는 문자/토큰입니다: {text[i:i + 8]!r}")
        return bytes(out)


def load_rom(path: Path) -> bytes:
    return path.read_bytes()


def parse_header(path: Path, data: bytes) -> RomHeader:
    if len(data) < 0xC0:
        raise ToolError("ROM 크기가 너무 작아서 GBA 헤더를 읽을 수 없습니다.")
    return RomHeader(
        path=str(path),
        size=len(data),
        title=data[0xA0:0xAC].split(b"\x00", 1)[0].decode("ascii", errors="replace"),
        game_code=data[0xAC:0xB0].decode("ascii", errors="replace"),
        maker_code=data[0xB0:0xB2].decode("ascii", errors="replace"),
        unit_code=data[0xB3],
        device_type=data[0xB4],
        version=data[0xBC],
        complement_check=data[0xBD],
    )


def parse_offset(value: str) -> int:
    raw = int(value, 0)
    if raw >= ROM_BASE:
        return raw - ROM_BASE
    return raw


def parse_hex_byte(value: str) -> int:
    cleaned = value.strip().lower().removeprefix("0x")
    return int(cleaned, 16) & 0xFF


def read_terminators(values: Sequence[str]) -> List[int]:
    if not values:
        return [0x00]
    return [parse_hex_byte(value) for value in values]


def format_offset(offset: int) -> str:
    return f"0x{offset:06X}"


def format_rom_address(offset: int) -> str:
    return f"0x{ROM_BASE + offset:08X}"


def contains_japanese(text: str) -> bool:
    return bool(JAPANESE_RE.search(text))


def is_text_printable(ch: str) -> bool:
    return (ch.isprintable() and ch not in "\x0b\x0c") or ch in ALLOWED_NONPRINTABLE_TEXT_CHARS


def japanese_ratio(text: str) -> float:
    if not text:
        return 0.0
    return sum(1 for ch in text if JAPANESE_RE.match(ch)) / len(text)


def suspicious_symbol_ratio(text: str) -> float:
    if not text:
        return 0.0
    return sum(1 for ch in text if ch in SUSPICIOUS_ASCII_SYMBOLS) / len(text)


def is_plausible_text(
    text: str,
    require_non_ascii: bool,
    require_japanese_text: bool,
    min_japanese_ratio: float,
) -> bool:
    if not text:
        return False
    printable_ratio = sum(is_text_printable(ch) for ch in text) / len(text)
    if printable_ratio < 0.9:
        return False
    if suspicious_symbol_ratio(text) > 0.2:
        return False
    if require_non_ascii and text.isascii():
        return False
    if require_japanese_text and (not contains_japanese(text) or japanese_ratio(text) < min_japanese_ratio):
        return False
    return True


def decode_payload(
    payload: bytes,
    *,
    encoding: Optional[str],
    table: Optional[TableCodec],
    max_unknown_ratio: float,
) -> Tuple[str, int]:
    if table is not None:
        text, unknown = table.decode(payload)
        if payload and (unknown / len(payload)) > max_unknown_ratio:
            raise ToolError("미지 바이트 비율이 너무 높습니다.")
        return text, unknown
    if encoding is None:
        raise ToolError("encoding 또는 table 중 하나는 반드시 필요합니다.")
    return payload.decode(encoding), 0


def encode_text(text: str, *, encoding: Optional[str], table: Optional[TableCodec]) -> bytes:
    if table is not None:
        return table.encode(text)
    if encoding is None:
        raise ToolError("encoding 또는 table 중 하나는 반드시 필요합니다.")
    return text.encode(encoding)


def iter_delimited_chunks(
    data: bytes,
    terminators: Sequence[int],
    *,
    max_bytes: int,
) -> Iterable[Tuple[int, bytes, Optional[int]]]:
    terminator_set = set(terminators)
    start = 0
    for index, byte in enumerate(data):
        if byte in terminator_set:
            length = index - start
            if 0 < length <= max_bytes:
                yield start, data[start:index], byte
            start = index + 1
    if start < len(data):
        length = len(data) - start
        if 0 < length <= max_bytes:
            yield start, data[start:], None


def iter_sliding_terminated_strings(
    data: bytes,
    *,
    start: int,
    end: int,
    terminators: Sequence[int],
    max_bytes: int,
) -> Iterable[Tuple[int, bytes, Optional[int]]]:
    if start < 0 or end > len(data) or start >= end:
        raise ToolError("잘못된 스캔 범위입니다.")
    terminator_set = set(terminators)
    sjis_lead_bytes = set(range(0x81, 0xA0)) | set(range(0xE0, 0xFD))
    for offset in range(start, end):
        if data[offset] in terminator_set or data[offset] in (0x00, 0xFF):
            continue
        if offset > start and data[offset - 1] in sjis_lead_bytes:
            continue
        if offset > start and data[offset - 1] not in terminator_set and data[offset - 1] not in (0x00, 0xFF):
            continue
        stop = min(end, offset + max_bytes + 1)
        found_at: Optional[int] = None
        found_byte: Optional[int] = None
        for index in range(offset, stop):
            b = data[index]
            if b in terminator_set:
                found_at = index
                found_byte = b
                break
        if found_at is None:
            continue
        if found_at == offset:
            continue
        yield offset, data[offset:found_at], found_byte


def extract_range_records(
    data: bytes,
    *,
    start: int,
    end: int,
    terminators: Sequence[int],
    max_bytes: int,
    encoding: Optional[str],
    table: Optional[TableCodec],
    max_unknown_ratio: float,
    min_chars: int,
    require_non_ascii: bool,
    require_japanese_text: bool,
    min_japanese_ratio: float,
) -> List[dict]:
    if start < 0 or end > len(data) or start >= end:
        raise ToolError("잘못된 추출 범위입니다.")
    records = []
    for rel_offset, payload, terminator in iter_delimited_chunks(
        data[start:end],
        terminators,
        max_bytes=max_bytes,
    ):
        try:
            text, unknown = decode_payload(
                payload,
                encoding=encoding,
                table=table,
                max_unknown_ratio=max_unknown_ratio,
            )
        except (UnicodeDecodeError, ToolError):
            continue
        if len(text) < min_chars:
            continue
        if not is_plausible_text(text, require_non_ascii, require_japanese_text, min_japanese_ratio):
            continue
        offset = start + rel_offset
        records.append(
            {
                "offset": offset,
                "rom_address": ROM_BASE + offset,
                "byte_length": len(payload),
                "terminator": None if terminator is None else f"0x{terminator:02X}",
                "unknown_tokens": unknown,
                "text": text,
                "translation": "",
            }
        )
    return records


def decode_fixed_char_count(payload: bytes, *, encoding: str, char_count: int) -> Tuple[str, int]:
    if char_count < 0:
        raise ToolError("문자 수는 0 이상이어야 합니다.")
    if char_count == 0:
        return "", 0

    chars: List[str] = []
    cursor = 0

    while len(chars) < char_count:
        progressed = False
        for end in range(cursor + 1, min(len(payload), cursor + 4) + 1):
            try:
                decoded = payload[cursor:end].decode(encoding)
            except UnicodeDecodeError:
                continue
            if not decoded:
                continue
            decoded_chars = list(decoded)
            if len(chars) + len(decoded_chars) > char_count:
                raise ToolError("헤더 문자 수보다 많이 디코드되었습니다.")
            chars.extend(decoded_chars)
            cursor = end
            progressed = True
            break
        if not progressed:
            raise ToolError("지정된 문자 수만큼 디코드하지 못했습니다.")

    if len(chars) != char_count:
        raise ToolError("헤더 문자 수와 실제 디코드 길이가 맞지 않습니다.")
    return "".join(chars), cursor


def scan_prefixed_text_records(
    data: bytes,
    *,
    start: int,
    end: int,
    prefix: bytes,
    count_size: int,
    count_endian: str,
    encoding: str,
    min_chars: int,
    max_chars: int,
    require_non_ascii: bool,
    require_japanese_text: bool,
    min_japanese_ratio: float,
    limit: Optional[int],
    preview_bytes: int,
) -> List[dict]:
    if start < 0 or end > len(data) or start >= end:
        raise ToolError("잘못된 스캔 범위입니다.")
    if not prefix:
        raise ToolError("prefix는 최소 1바이트 이상이어야 합니다.")
    if count_size not in {1, 2, 4}:
        raise ToolError("count-size는 1, 2, 4 중 하나여야 합니다.")
    if count_endian not in {"little", "big"}:
        raise ToolError("count-endian은 little 또는 big 이어야 합니다.")
    if max_chars < min_chars:
        raise ToolError("max-chars는 min-chars 이상이어야 합니다.")

    records: List[dict] = []
    cursor = start
    header_size = len(prefix) + count_size

    while True:
        offset = data.find(prefix, cursor, end)
        if offset == -1:
            return records
        cursor = offset + 1
        if offset + header_size > end:
            continue

        count_bytes = data[offset + len(prefix):offset + header_size]
        char_count = int.from_bytes(count_bytes, count_endian)
        if char_count < min_chars or char_count > max_chars:
            continue

        text_offset = offset + header_size
        try:
            text, byte_length = decode_fixed_char_count(
                data[text_offset:end],
                encoding=encoding,
                char_count=char_count,
            )
        except ToolError:
            continue

        if not is_plausible_text(text, require_non_ascii, require_japanese_text, min_japanese_ratio):
            continue

        after_start = text_offset + byte_length
        after_end = min(end, after_start + preview_bytes)
        before_start = max(start, offset - preview_bytes)

        records.append(
            {
                "header_offset": offset,
                "header_rom_address": ROM_BASE + offset,
                "offset": text_offset,
                "rom_address": ROM_BASE + text_offset,
                "prefix": " ".join(f"{byte:02X}" for byte in prefix),
                "char_count": char_count,
                "byte_length": byte_length,
                "header_bytes": data[offset:text_offset].hex(" "),
                "before_bytes": data[before_start:offset].hex(" "),
                "after_bytes": data[after_start:after_end].hex(" "),
                "text": text,
                "translation": "",
            }
        )
        if limit is not None and len(records) >= limit:
            return records


def normalize_fc_script_payload(payload: bytes) -> bytes:
    normalized = payload
    while normalized.endswith((b"\x00", b"\x0c", b"\x0d")):
        normalized = normalized[:-1]
    normalized = normalized.replace(b"\x0d\x0c", b"\n")
    normalized = normalized.replace(b"\x0a\x0b", b"\n")
    normalized = normalized.replace(b"\x0d", b"")
    normalized = normalized.replace(b"\x0c", b"")
    normalized = normalized.replace(b"\x0a", b"\n")
    normalized = normalized.replace(b"\x0b", b"")
    return normalized


def find_next_script_stop(data: bytes, *, start: int, end: int, stop_byte: int) -> int:
    sjis_lead_bytes = set(range(0x81, 0xA0)) | set(range(0xE0, 0xFD))
    cursor = start
    while True:
        stop_offset = data.find(bytes([stop_byte]), cursor, end)
        if stop_offset == -1:
            return end
        if stop_offset > start and data[stop_offset - 1] in sjis_lead_bytes:
            cursor = stop_offset + 1
            continue
        return stop_offset


def scan_fc_script_text_records(
    data: bytes,
    *,
    start: int,
    end: int,
    anchor: bytes,
    stop_byte: int,
    encoding: str,
    min_chars: int,
    require_non_ascii: bool,
    require_japanese_text: bool,
    min_japanese_ratio: float,
    limit: Optional[int],
    preview_bytes: int,
) -> List[dict]:
    if start < 0 or end > len(data) or start >= end:
        raise ToolError("잘못된 스캔 범위입니다.")
    if not anchor:
        raise ToolError("anchor는 최소 1바이트 이상이어야 합니다.")

    records: List[dict] = []
    cursor = start

    while True:
        anchor_offset = data.find(anchor, cursor, end)
        if anchor_offset == -1:
            return records
        cursor = anchor_offset + 1
        text_offset = anchor_offset + len(anchor)
        if text_offset >= end:
            continue

        stop_offset = find_next_script_stop(
            data,
            start=text_offset,
            end=end,
            stop_byte=stop_byte,
        )
        if stop_offset <= text_offset:
            continue

        raw_payload = data[text_offset:stop_offset]
        payload = normalize_fc_script_payload(raw_payload)
        if not payload:
            continue

        try:
            text = payload.decode(encoding)
        except UnicodeDecodeError:
            continue

        if len(text) < min_chars:
            continue
        if not is_plausible_text(
            text.replace("\n", ""),
            require_non_ascii,
            require_japanese_text,
            min_japanese_ratio,
        ):
            continue

        before_start = max(start, anchor_offset - preview_bytes)
        after_end = min(end, stop_offset + 1 + preview_bytes)
        records.append(
            {
                "anchor_offset": anchor_offset,
                "anchor_rom_address": ROM_BASE + anchor_offset,
                "offset": text_offset,
                "rom_address": ROM_BASE + text_offset,
                "anchor": " ".join(f"{byte:02X}" for byte in anchor),
                "stop_byte": f"0x{stop_byte:02X}",
                "byte_length": len(payload),
                "raw_byte_length": len(raw_payload),
                "before_bytes": data[before_start:anchor_offset].hex(" "),
                "raw_bytes": raw_payload.hex(" "),
                "after_bytes": data[stop_offset:after_end].hex(" "),
                "text": text,
                "translation": "",
            }
        )
        if limit is not None and len(records) >= limit:
            return records


KEYWORD_TAG_RULES: List[Tuple[str, Tuple[str, ...]]] = [
    ("save_menu", ("セーブ", "記録", "上書き", "旅を記録")),
    ("liore", ("リオール", "コーネロ")),
    ("central", ("セントラル", "中央区画", "北側区画", "西側区画", "南側区画")),
    ("east_city", ("イーストシティ", "東方軍司令部")),
    ("hospital", ("病院", "患者", "退院")),
    ("cat_quest", ("猫", "ネコ")),
    ("bank", ("銀行", "強盗", "お預け入れ")),
    ("military", ("軍", "国家錬金術師", "大総統", "マスタング", "ヒューズ", "ホークアイ")),
    ("elicia", ("エリシア",)),
    ("armor_parts", ("鎧のパーツ", "アルの右腕", "アルの左腕", "アルの右足", "アルの左足")),
    ("reward", ("手に入れた", "証", "素材", "書類", "花束")),
    ("travel_blocked", ("入れない", "閉まってる", "カギが閉まってて")),
    ("shop_npc", ("いらっしゃい", "ありがとうございます", "寄っておくれ")),
    ("battle_dialogue", ("覚悟", "勝負", "相手", "負けたら", "滅ぼす", "裁き")),
    ("tutorial", ("兄さん", "錬成", "手帳", "素材", "カード")),
    ("debug_or_script", ("ぶんきミス", "強制移動")),
]


def load_text_records(path: Path) -> List[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ToolError("입력 JSON은 text record 배열이어야 합니다.")
    records: List[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        if "offset" not in item or "text" not in item:
            continue
        records.append(item)
    if not records:
        raise ToolError("offset/text 필드를 가진 레코드를 찾지 못했습니다.")
    return records


def infer_cluster_tags(texts: Sequence[str]) -> List[str]:
    joined = "\n".join(texts)
    tags: List[str] = []
    for tag, keywords in KEYWORD_TAG_RULES:
        if any(keyword in joined for keyword in keywords):
            tags.append(tag)
    return tags


def choose_primary_tag(tags: Sequence[str]) -> str:
    if not tags:
        return "unclassified"
    priority = [
        "save_menu",
        "liore",
        "central",
        "east_city",
        "hospital",
        "cat_quest",
        "bank",
        "elicia",
        "armor_parts",
        "military",
        "reward",
        "shop_npc",
        "travel_blocked",
        "battle_dialogue",
        "tutorial",
        "debug_or_script",
    ]
    for tag in priority:
        if tag in tags:
            return tag
    return tags[0]


def summarize_text_clusters(
    records: Sequence[dict],
    *,
    gap_threshold: int,
    sample_count: int,
) -> dict:
    sorted_records = sorted(records, key=lambda item: int(item["offset"]))
    clusters: List[List[dict]] = []
    current: List[dict] = []
    previous_offset: Optional[int] = None

    for record in sorted_records:
        offset = int(record["offset"])
        if previous_offset is None or offset - previous_offset <= gap_threshold:
            current.append(record)
        else:
            clusters.append(current)
            current = [record]
        previous_offset = offset
    if current:
        clusters.append(current)

    cluster_summaries = []
    for index, cluster in enumerate(clusters):
        offsets = [int(item["offset"]) for item in cluster]
        texts = [str(item["text"]) for item in cluster]
        tags = infer_cluster_tags(texts)
        unique_samples: List[str] = []
        seen = set()
        for text in texts:
            if text in seen:
                continue
            seen.add(text)
            unique_samples.append(text)
            if len(unique_samples) >= sample_count:
                break
        cluster_summaries.append(
            {
                "cluster_index": index,
                "start_offset": offsets[0],
                "start_rom_address": ROM_BASE + offsets[0],
                "end_offset_exclusive": offsets[-1] + int(cluster[-1].get("byte_length", 0)),
                "record_count": len(cluster),
                "first_text": texts[0],
                "last_text": texts[-1],
                "sample_texts": unique_samples,
                "tags": tags,
                "primary_tag": choose_primary_tag(tags),
            }
        )

    return {
        "gap_threshold": gap_threshold,
        "record_count": len(sorted_records),
        "cluster_count": len(cluster_summaries),
        "clusters": cluster_summaries,
    }


def find_all(data: bytes, needle: bytes) -> List[int]:
    hits: List[int] = []
    cursor = 0
    while True:
        index = data.find(needle, cursor)
        if index == -1:
            return hits
        hits.append(index)
        cursor = index + 1


def find_pointers(data: bytes, target_offset: int, *, aligned_only: bool = True, limit: Optional[int] = None) -> List[int]:
    target_value = ROM_BASE + target_offset
    hits: List[int] = []
    step = 4 if aligned_only else 1
    stop = len(data) - 3
    for offset in range(0, stop, step):
        if struct.unpack_from("<I", data, offset)[0] == target_value:
            hits.append(offset)
            if limit is not None and len(hits) >= limit:
                return hits
    return hits


def parse_u32(value: str) -> int:
    parsed = int(value, 0)
    if parsed < 0 or parsed > 0xFFFFFFFF:
        raise ToolError("32비트 범위를 벗어난 값입니다.")
    return parsed


def find_u32_values(
    data: bytes,
    value: int,
    *,
    aligned_only: bool = False,
    start: int = 0,
    end: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[int]:
    needle = struct.pack("<I", value)
    hits: List[int] = []
    step = 4 if aligned_only else 1
    stop = (len(data) if end is None else min(end, len(data))) - 3
    offset = start
    if aligned_only and offset % 4:
        offset += 4 - (offset % 4)
    for offset in range(offset, stop, step):
        if data[offset:offset + 4] != needle:
            continue
        hits.append(offset)
        if limit is not None and len(hits) >= limit:
            return hits
    return hits


def decode_thumb_ldr_literal(data: bytes, offset: int) -> Optional[Tuple[int, int]]:
    if offset < 0 or offset + 2 > len(data):
        return None
    insn = struct.unpack_from("<H", data, offset)[0]
    if (insn & 0xF800) != 0x4800:
        return None
    register = (insn >> 8) & 0x7
    pc = (offset + 4) & ~0x3
    literal_offset = pc + ((insn & 0xFF) * 4)
    return register, literal_offset


def describe_thumb16(data: bytes, offset: int) -> str:
    if offset < 0 or offset + 2 > len(data):
        return "out-of-range"
    insn = struct.unpack_from("<H", data, offset)[0]
    if (insn & 0xF800) == 0x4800:
        register, literal_offset = decode_thumb_ldr_literal(data, offset) or (0, 0)
        return f"ldr r{register}, [pc] -> {format_offset(literal_offset)}"
    if (insn & 0xF800) == 0x7800:
        return f"ldrb r{insn & 7}, [r{(insn >> 3) & 7}, #{(insn >> 6) & 0x1F}]"
    if (insn & 0xF800) == 0x7000:
        return f"strb r{insn & 7}, [r{(insn >> 3) & 7}, #{(insn >> 6) & 0x1F}]"
    if (insn & 0xF800) == 0x6800:
        return f"ldr r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 4}]"
    if (insn & 0xF800) == 0x6000:
        return f"str r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 4}]"
    if (insn & 0xF800) == 0x8800:
        return f"ldrh r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 2}]"
    if (insn & 0xF800) == 0x8000:
        return f"strh r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 2}]"
    if (insn & 0xF800) == 0x2800:
        return f"cmp r{(insn >> 8) & 7}, #{insn & 0xFF}"
    if (insn & 0xF800) == 0x2000:
        return f"movs r{(insn >> 8) & 7}, #{insn & 0xFF}"
    return f"thumb16 0x{insn:04X}"


THUMB_COND_NAMES = [
    "eq",
    "ne",
    "cs",
    "cc",
    "mi",
    "pl",
    "vs",
    "vc",
    "hi",
    "ls",
    "ge",
    "lt",
    "gt",
    "le",
]


def infer_literal_access(data: bytes, instruction_offset: int, register: int, *, max_instructions: int = 8) -> str:
    for index in range(1, max_instructions + 1):
        offset = instruction_offset + index * 2
        if offset + 2 > len(data):
            break
        insn = struct.unpack_from("<H", data, offset)[0]
        opcode = insn & 0xF800
        base = (insn >> 3) & 7
        if base == register:
            if opcode == 0x7000:
                return "write_byte"
            if opcode == 0x7800:
                return "read_byte"
            if opcode == 0x6000:
                return "write_word"
            if opcode == 0x6800:
                return "read_word"
            if opcode == 0x8000:
                return "write_halfword"
            if opcode == 0x8800:
                return "read_halfword"
        dest = None
        if opcode in {0x4800, 0x2000, 0x2800}:
            dest = (insn >> 8) & 7
        elif opcode in {0x7000, 0x7800, 0x6000, 0x6800, 0x8000, 0x8800}:
            dest = insn & 7
        if dest == register and opcode != 0x2800:
            break
    return "unknown"


def find_thumb_literal_loads(
    data: bytes,
    literal_offsets: Sequence[int],
    *,
    start: int = 0,
    end: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    literal_set = set(literal_offsets)
    stop = len(data) if end is None else min(end, len(data))
    if start < 0 or start >= stop:
        raise ToolError("잘못된 Thumb literal 검색 범위입니다.")

    hits: List[dict] = []
    for offset in range(start, stop - 1, 2):
        decoded = decode_thumb_ldr_literal(data, offset)
        if decoded is None:
            continue
        register, literal_offset = decoded
        if literal_offset not in literal_set:
            continue
        context = []
        for context_offset in range(max(start, offset - 4), min(stop, offset + 18), 2):
            context.append(
                {
                    "offset": context_offset,
                    "rom_address": ROM_BASE + context_offset,
                    "instruction": describe_thumb16(data, context_offset),
                }
            )
        hits.append(
            {
                "instruction_offset": offset,
                "instruction_rom_address": ROM_BASE + offset,
                "literal_offset": literal_offset,
                "literal_rom_address": ROM_BASE + literal_offset,
                "register": f"r{register}",
                "access": infer_literal_access(data, offset, register),
                "context": context,
            }
        )
        if limit is not None and len(hits) >= limit:
            return hits
    return hits


def sign_extend(value: int, bits: int) -> int:
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


def describe_thumb_disasm(data: bytes, offset: int) -> str:
    if offset < 0 or offset + 2 > len(data):
        return "out-of-range"

    insn = struct.unpack_from("<H", data, offset)[0]
    if (insn & 0xF800) == 0x4800:
        register, literal_offset = decode_thumb_ldr_literal(data, offset) or (0, 0)
        literal = ""
        if 0 <= literal_offset <= len(data) - 4:
            value = struct.unpack_from("<I", data, literal_offset)[0]
            literal = f" ; =0x{value:08X} @{format_offset(literal_offset)}"
        return f"ldr r{register}, [pc]{literal}"
    if (insn & 0xF000) == 0xD000 and (insn & 0x0F00) != 0x0F00:
        cond = (insn >> 8) & 0xF
        target = (offset + 4 + sign_extend((insn & 0xFF) << 1, 9)) & 0xFFFFFFFF
        return f"b{THUMB_COND_NAMES[cond]} {format_offset(target)}"
    if (insn & 0xF800) == 0xE000:
        target = (offset + 4 + sign_extend((insn & 0x07FF) << 1, 12)) & 0xFFFFFFFF
        return f"b {format_offset(target)}"
    if (insn & 0xFFC0) == 0x4240:
        return f"negs r{insn & 7}, r{(insn >> 3) & 7}"
    if (insn & 0xFFC0) == 0x4700:
        return f"bx r{(insn >> 3) & 0xF}"
    if (insn & 0xFF87) == 0x4680:
        source = ((insn >> 3) & 0x7) | (((insn >> 7) & 0x1) << 3)
        dest = (insn & 0x7) | (((insn >> 6) & 0x1) << 3)
        return f"mov r{dest}, r{source}"
    if (insn & 0xE000) == 0x0000:
        opcode = (insn >> 11) & 0x3
        names = ["lsls", "lsrs", "asrs"]
        if opcode <= 2:
            amount = (insn >> 6) & 0x1F
            return f"{names[opcode]} r{insn & 7}, r{(insn >> 3) & 7}, #{amount}"
    if (insn & 0xFC00) == 0x1800:
        op = "adds" if ((insn >> 9) & 1) == 0 else "subs"
        return f"{op} r{insn & 7}, r{(insn >> 3) & 7}, r{(insn >> 6) & 7}"
    if (insn & 0xFC00) == 0x1C00:
        op = "adds" if ((insn >> 9) & 1) == 0 else "subs"
        imm = (insn >> 6) & 0x7
        source = (insn >> 3) & 0x7
        dest = insn & 0x7
        if imm == 0 and op == "adds":
            return f"movs r{dest}, r{source}"
        return f"{op} r{dest}, r{source}, #{imm}"
    if (insn & 0xFC00) == 0x4000:
        op = (insn >> 6) & 0xF
        names = {
            0: "ands",
            1: "eors",
            2: "lsls",
            3: "lsrs",
            4: "asrs",
            5: "adcs",
            6: "sbcs",
            7: "rors",
            8: "tst",
            9: "rsbs",
            10: "cmp",
            11: "cmn",
            12: "orrs",
            13: "muls",
            14: "bics",
            15: "mvns",
        }
        return f"{names[op]} r{insn & 7}, r{(insn >> 3) & 7}"
    if (insn & 0xF800) == 0x3000:
        return f"adds r{(insn >> 8) & 7}, #{insn & 0xFF}"
    if (insn & 0xF800) == 0x3800:
        return f"subs r{(insn >> 8) & 7}, #{insn & 0xFF}"
    if (insn & 0xFE00) == 0x5E00:
        return f"ldrsh r{insn & 7}, [r{(insn >> 3) & 7}, r{(insn >> 6) & 7}]"
    if (insn & 0xFE00) == 0x5600:
        return f"ldrsb r{insn & 7}, [r{(insn >> 3) & 7}, r{(insn >> 6) & 7}]"
    if (insn & 0xFE00) == 0x5A00:
        return f"ldrh r{insn & 7}, [r{(insn >> 3) & 7}, r{(insn >> 6) & 7}]"
    if (insn & 0xFE00) == 0x5200:
        return f"strh r{insn & 7}, [r{(insn >> 3) & 7}, r{(insn >> 6) & 7}]"
    if (insn & 0xFE00) == 0x5000:
        op = (insn >> 9) & 0x7
        names = {
            0: "str",
            1: "strh",
            2: "strb",
            3: "ldrsb",
            4: "ldr",
            5: "ldrh",
            6: "ldrb",
            7: "ldrsh",
        }
        return f"{names[op]} r{insn & 7}, [r{(insn >> 3) & 7}, r{(insn >> 6) & 7}]"
    if (insn & 0xF800) == 0x7800:
        return f"ldrb r{insn & 7}, [r{(insn >> 3) & 7}, #{(insn >> 6) & 0x1F}]"
    if (insn & 0xF800) == 0x7000:
        return f"strb r{insn & 7}, [r{(insn >> 3) & 7}, #{(insn >> 6) & 0x1F}]"
    if (insn & 0xF800) == 0x6800:
        return f"ldr r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 4}]"
    if (insn & 0xF800) == 0x6000:
        return f"str r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 4}]"
    if (insn & 0xF800) == 0x8800:
        return f"ldrh r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 2}]"
    if (insn & 0xF800) == 0x8000:
        return f"strh r{insn & 7}, [r{(insn >> 3) & 7}, #{((insn >> 6) & 0x1F) * 2}]"
    if (insn & 0xFE00) == 0xB400:
        return f"push 0x{insn & 0x1FF:03X}"
    if (insn & 0xFE00) == 0xBC00:
        return f"pop 0x{insn & 0x1FF:03X}"
    if (insn & 0xFF80) == 0xB000:
        amount = (insn & 0x7F) * 4
        if insn & 0x80:
            return f"add sp, #{amount}"
        return f"sub sp, #{amount}"
    if (insn & 0xF800) == 0x2800:
        return f"cmp r{(insn >> 8) & 7}, #{insn & 0xFF}"
    if (insn & 0xF800) == 0x2000:
        return f"movs r{(insn >> 8) & 7}, #{insn & 0xFF}"
    return f".hword 0x{insn:04X}"


def decode_thumb_bl_target(data: bytes, offset: int) -> Optional[int]:
    if offset < 0 or offset + 4 > len(data):
        return None
    first = struct.unpack_from("<H", data, offset)[0]
    second = struct.unpack_from("<H", data, offset + 2)[0]
    if (first & 0xF800) != 0xF000 or (second & 0xD000) != 0xD000:
        return None

    s = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm10 = first & 0x03FF
    imm11 = second & 0x07FF
    i1 = 1 if j1 == s else 0
    i2 = 1 if j2 == s else 0
    imm25 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    return (offset + 4 + sign_extend(imm25, 25)) & 0xFFFFFFFF


def find_thumb_bl_callers(
    data: bytes,
    *,
    target_offset: int,
    start: int = 0,
    end: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    stop = len(data) if end is None else min(end, len(data))
    if start < 0 or start >= stop:
        raise ToolError("잘못된 Thumb BL 검색 범위입니다.")

    hits: List[dict] = []
    for offset in range(start, stop - 3, 2):
        target = decode_thumb_bl_target(data, offset)
        if target != target_offset:
            continue
        hits.append(
            {
                "call_offset": offset,
                "call_rom_address": ROM_BASE + offset,
                "target_offset": target_offset,
                "target_rom_address": ROM_BASE + target_offset,
            }
        )
        if limit is not None and len(hits) >= limit:
            return hits
    return hits


def dump_thumb_slice(data: bytes, *, start: int, end: int) -> List[str]:
    if start < 0 or end > len(data) or start >= end:
        raise ToolError("잘못된 Thumb 슬라이스 범위입니다.")
    if start % 2 or end % 2:
        raise ToolError("Thumb 슬라이스 범위는 2바이트 정렬이어야 합니다.")

    lines: List[str] = []
    offset = start
    while offset < end:
        target = decode_thumb_bl_target(data, offset)
        if target is not None:
            first = struct.unpack_from("<H", data, offset)[0]
            second = struct.unpack_from("<H", data, offset + 2)[0]
            lines.append(f"{format_offset(offset)}: {first:04X} {second:04X}  bl {format_offset(target)}")
            offset += 4
            continue
        insn = struct.unpack_from("<H", data, offset)[0]
        lines.append(f"{format_offset(offset)}: {insn:04X}  {describe_thumb_disasm(data, offset)}")
        offset += 2
    return lines


def decompress_lz77(data: bytes, offset: int, *, max_output_size: int) -> Tuple[bytes, int]:
    if offset + 4 > len(data) or data[offset] != 0x10:
        raise ToolError("LZ77 헤더가 아닙니다.")
    output_size = data[offset + 1] | (data[offset + 2] << 8) | (data[offset + 3] << 16)
    if output_size <= 0 or output_size > max_output_size:
        raise ToolError("비정상적인 LZ77 출력 크기입니다.")

    src = offset + 4
    out = bytearray()
    while len(out) < output_size:
        if src >= len(data):
            raise ToolError("LZ77 데이터가 중간에 끝났습니다.")
        flags = data[src]
        src += 1
        for bit in range(8):
            if len(out) >= output_size:
                break
            if flags & (0x80 >> bit):
                if src + 1 >= len(data):
                    raise ToolError("LZ77 백레퍼런스가 잘렸습니다.")
                b1 = data[src]
                b2 = data[src + 1]
                src += 2
                count = (b1 >> 4) + 3
                disp = (((b1 & 0x0F) << 8) | b2) + 1
                if disp > len(out):
                    raise ToolError("LZ77 백레퍼런스 거리가 잘못되었습니다.")
                for _ in range(count):
                    out.append(out[-disp])
                    if len(out) >= output_size:
                        break
            else:
                if src >= len(data):
                    raise ToolError("LZ77 리터럴이 잘렸습니다.")
                out.append(data[src])
                src += 1
    return bytes(out), src - offset


def scan_lz77_blocks(
    data: bytes,
    *,
    max_output_size: int,
    min_compressed_size: int,
    min_decompressed_size: int,
    limit: Optional[int],
) -> List[dict]:
    hits: List[dict] = []
    cursor = 0
    while True:
        index = data.find(b"\x10", cursor)
        if index == -1:
            return hits
        cursor = index + 1
        if index + 4 > len(data):
            continue
        declared = data[index + 1] | (data[index + 2] << 8) | (data[index + 3] << 16)
        if declared <= 0 or declared > max_output_size:
            continue
        try:
            payload, consumed = decompress_lz77(data, index, max_output_size=max_output_size)
        except ToolError:
            continue
        if consumed < min_compressed_size or len(payload) < min_decompressed_size:
            continue
        hits.append(
            {
                "offset": index,
                "rom_address": ROM_BASE + index,
                "compressed_size": consumed,
                "decompressed_size": len(payload),
            }
        )
        if limit is not None and len(hits) >= limit:
            return hits


def align_up(value: int, alignment: int) -> int:
    if alignment <= 1:
        return value
    return (value + alignment - 1) // alignment * alignment


def find_free_space(data: bytes, *, start: int, size: int, fill_byte: int, alignment: int) -> int:
    offset = align_up(start, alignment)
    while offset + size <= len(data):
        if all(byte == fill_byte for byte in data[offset:offset + size]):
            return offset
        offset += alignment
    raise ToolError("요청한 길이만큼의 빈 공간을 찾지 못했습니다.")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_binary(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def write_pgm(path: Path, pixels: bytes, width: int, height: int) -> None:
    header = f"P5\n{width} {height}\n255\n".encode("ascii")
    write_binary(path, header + pixels)


def unpack_chunk_table_entry(raw_first: int, raw_second: int, layout: str) -> Tuple[int, int]:
    if layout == "length-pointer":
        return raw_first, raw_second
    if layout == "pointer-length":
        return raw_second, raw_first
    raise ToolError(f"지원하지 않는 청크 레이아웃입니다: {layout}")


def is_valid_chunk_entry(data_size: int, *, length: int, rom_address: int) -> bool:
    if length <= 0 or length > data_size:
        return False
    if rom_address < ROM_BASE or rom_address >= ROM_BASE + data_size:
        return False
    file_offset = rom_address - ROM_BASE
    return file_offset + length <= data_size


def score_chunk_layout(data: bytes, *, start: int, count: int, layout: str) -> Tuple[int, int]:
    score = 0
    valid_entries = 0
    previous_offset: Optional[int] = None

    for index in range(count):
        table_offset = start + index * 8
        if table_offset + 8 > len(data):
            break
        raw_first, raw_second = struct.unpack_from("<II", data, table_offset)
        length, rom_address = unpack_chunk_table_entry(raw_first, raw_second, layout)
        if not is_valid_chunk_entry(len(data), length=length, rom_address=rom_address):
            continue
        valid_entries += 1
        score += 3
        file_offset = rom_address - ROM_BASE
        if file_offset % 4 == 0:
            score += 1
        if previous_offset is None or file_offset >= previous_offset:
            score += 1
        previous_offset = file_offset

    return score, valid_entries


def resolve_chunk_layout(data: bytes, *, start: int, count: int, layout: str) -> Tuple[str, Dict[str, dict]]:
    if layout != "auto":
        score, valid_entries = score_chunk_layout(data, start=start, count=count, layout=layout)
        return layout, {layout: {"score": score, "valid_entries": valid_entries}}

    candidates = {}
    for candidate in ("length-pointer", "pointer-length"):
        score, valid_entries = score_chunk_layout(data, start=start, count=count, layout=candidate)
        candidates[candidate] = {"score": score, "valid_entries": valid_entries}

    resolved_layout = max(
        candidates.items(),
        key=lambda item: (item[1]["score"], item[1]["valid_entries"]),
    )[0]
    return resolved_layout, candidates


def inspect_chunk_table(
    data: bytes,
    *,
    start: int,
    count: int,
    layout: str,
    stop_on_invalid: bool,
    scan_text: bool,
    terminators: Sequence[int],
    max_bytes: int,
    encoding: Optional[str],
    table: Optional[TableCodec],
    max_unknown_ratio: float,
    min_chars: int,
    require_non_ascii: bool,
    require_japanese_text: bool,
    min_japanese_ratio: float,
) -> dict:
    resolved_layout, auto_scores = resolve_chunk_layout(data, start=start, count=count, layout=layout)
    entries = []
    previous_end_inclusive: Optional[int] = None

    for index in range(count):
        table_offset = start + index * 8
        if table_offset + 8 > len(data):
            raise ToolError("청크 테이블 범위가 ROM 끝을 넘어갑니다.")

        raw_first, raw_second = struct.unpack_from("<II", data, table_offset)
        length, rom_address = unpack_chunk_table_entry(raw_first, raw_second, resolved_layout)
        entry = {
            "index": index,
            "table_offset": table_offset,
            "raw_first_u32": raw_first,
            "raw_second_u32": raw_second,
            "layout": resolved_layout,
            "valid": False,
        }

        if is_valid_chunk_entry(len(data), length=length, rom_address=rom_address):
            file_offset = rom_address - ROM_BASE
            end_exclusive = file_offset + length
            end_inclusive = end_exclusive - 1
            overlap_previous = previous_end_inclusive is not None and file_offset <= previous_end_inclusive
            gap_from_previous = None
            if previous_end_inclusive is not None:
                gap_from_previous = file_offset - (previous_end_inclusive + 1)

            entry.update(
                {
                    "valid": True,
                    "length": length,
                    "rom_address": rom_address,
                    "file_offset": file_offset,
                    "end_offset_exclusive": end_exclusive,
                    "end_offset_inclusive": end_inclusive,
                    "overlap_previous": overlap_previous,
                    "gap_from_previous": gap_from_previous,
                }
            )

            if scan_text:
                records = extract_range_records(
                    data,
                    start=file_offset,
                    end=end_exclusive,
                    terminators=terminators,
                    max_bytes=max_bytes,
                    encoding=encoding,
                    table=table,
                    max_unknown_ratio=max_unknown_ratio,
                    min_chars=min_chars,
                    require_non_ascii=require_non_ascii,
                    require_japanese_text=require_japanese_text,
                    min_japanese_ratio=min_japanese_ratio,
                )
                entry["text_hits"] = len(records)
                entry["first_text"] = records[0]["text"] if records else ""

            previous_end_inclusive = end_inclusive
        else:
            if stop_on_invalid:
                break

        entries.append(entry)

    return {
        "table_offset": start,
        "layout_requested": layout,
        "layout_resolved": resolved_layout,
        "auto_scores": auto_scores,
        "entry_count_requested": count,
        "entries": entries,
    }


def render_4bpp_tiles(data: bytes, *, offset: int, tiles: int, columns: int) -> Tuple[bytes, int, int]:
    width = columns * 8
    rows = math.ceil(tiles / columns)
    height = rows * 8
    image = bytearray(width * height)

    for tile_index in range(tiles):
        tile_offset = offset + tile_index * 32
        tile = data[tile_offset:tile_offset + 32]
        if len(tile) < 32:
            raise ToolError("지정한 타일 수가 ROM 끝을 넘어갑니다.")
        base_x = (tile_index % columns) * 8
        base_y = (tile_index // columns) * 8
        for row in range(8):
            row_data = tile[row * 4:(row + 1) * 4]
            x = base_x
            for byte in row_data:
                low = byte & 0x0F
                high = byte >> 4
                image[(base_y + row) * width + x] = low * 17
                image[(base_y + row) * width + x + 1] = high * 17
                x += 2

    return bytes(image), width, height


def read_fnt_header(data: bytes, *, payload_offset: int) -> Dict[str, int]:
    if payload_offset + 0x10 > len(data):
        raise ToolError("fnt payload 시작이 ROM 범위를 벗어납니다.")
    if data[payload_offset:payload_offset + 4] != b"fnt\x00":
        raise ToolError("지정한 offset 에서 fnt\\0 magic 을 찾지 못했습니다.")
    flags = data[payload_offset + 7]
    stride = struct.unpack_from("<H", data, payload_offset + 8)[0]
    lookup_base = payload_offset + 0x10 + (0x40000 if (flags & 0x80) else 0)
    glyph_base = lookup_base + 0x20000
    return {
        "payload_offset": payload_offset,
        "flags": flags,
        "stride": stride,
        "lookup_base": lookup_base,
        "glyph_base": glyph_base,
    }


def resolve_fnt_glyph_index(
    data: bytes,
    *,
    header: Dict[str, int],
    glyph_index: Optional[int],
    code: Optional[int],
) -> int:
    if glyph_index is not None and code is not None:
        raise ToolError("--glyph-index 와 --code 는 동시에 쓸 수 없습니다.")
    if glyph_index is None and code is None:
        raise ToolError("--glyph-index 또는 --code 중 하나는 필요합니다.")
    if glyph_index is not None:
        return glyph_index
    assert code is not None
    lookup_offset = header["lookup_base"] + code * 2
    if lookup_offset + 2 > len(data):
        raise ToolError("lookup table 범위를 벗어났습니다.")
    return struct.unpack_from("<H", data, lookup_offset)[0]


def render_fnt_glyph(
    data: bytes,
    *,
    glyph_offset: int,
    width: int,
    height: int,
    row_bytes: int,
) -> bytes:
    expected_size = height * row_bytes
    glyph = data[glyph_offset:glyph_offset + expected_size]
    if len(glyph) < expected_size:
        raise ToolError("glyph 데이터가 ROM 끝을 넘어갑니다.")
    pixels = bytearray(width * height)
    for row in range(height):
        row_data = glyph[row * row_bytes:(row + 1) * row_bytes]
        x = 0
        for byte in row_data:
            low = byte & 0x0F
            high = byte >> 4
            if x < width:
                pixels[row * width + x] = low * 17
                x += 1
            if x < width:
                pixels[row * width + x] = high * 17
                x += 1
    return bytes(pixels)


def decode_cp932_code(code: int) -> str:
    payload = bytes([code]) if code <= 0xFF else bytes([(code >> 8) & 0xFF, code & 0xFF])
    try:
        return payload.decode("cp932")
    except UnicodeDecodeError:
        return ""


def encode_cp932_char(ch: str) -> Optional[int]:
    try:
        payload = ch.encode("cp932")
    except UnicodeEncodeError:
        return None
    if len(payload) == 1:
        return payload[0]
    if len(payload) == 2:
        return (payload[0] << 8) | payload[1]
    return None


def iter_text_fields_from_json(path: Path) -> Iterable[str]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ToolError(f"{path}: JSON 배열이 아닙니다.")
    for record in records:
        if isinstance(record, dict):
            text = record.get("text")
            if isinstance(text, str):
                yield text


def cmd_info(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    header = parse_header(rom_path, load_rom(rom_path))
    if args.json_output:
        print(json.dumps(asdict(header), ensure_ascii=False, indent=2))
    else:
        print(f"ROM       : {header.path}")
        print(f"Size      : {header.size} bytes")
        print(f"Title     : {header.title}")
        print(f"Game Code : {header.game_code}")
        print(f"Maker     : {header.maker_code}")
        print(f"Unit Code : {header.unit_code}")
        print(f"Device    : {header.device_type}")
        print(f"Version   : {header.version}")
        print(f"Checksum  : 0x{header.complement_check:02X}")
    return 0


def cmd_scan_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    records = []
    start = parse_offset(args.start) if args.start else 0
    end = parse_offset(args.end) if args.end else len(data)
    terminators = read_terminators(args.terminator)
    if args.sliding and (args.start is None or args.end is None):
        raise ToolError("--sliding 사용 시 --start/--end 범위를 반드시 지정해야 합니다.")

    if args.sliding:
        iterator = iter_sliding_terminated_strings(
            data,
            start=start,
            end=end,
            terminators=terminators,
            max_bytes=args.max_bytes,
        )
    else:
        if start < 0 or end > len(data) or start >= end:
            raise ToolError("잘못된 스캔 범위입니다.")
        iterator = iter_delimited_chunks(data[start:end], terminators, max_bytes=args.max_bytes)

    for rel_offset, payload, terminator in iterator:
        offset = rel_offset if args.sliding else (start + rel_offset)
        try:
            text, unknown = decode_payload(
                payload,
                encoding=args.encoding,
                table=table,
                max_unknown_ratio=args.max_unknown_ratio,
            )
        except (UnicodeDecodeError, ToolError):
            continue
        if len(text) < args.min_chars:
            continue
        if not is_plausible_text(text, args.require_non_ascii, args.require_japanese, args.min_japanese_ratio):
            continue
        records.append(
            {
                "offset": offset,
                "rom_address": ROM_BASE + offset,
                "byte_length": len(payload),
                "terminator": None if terminator is None else f"0x{terminator:02X}",
                "unknown_tokens": unknown,
                "text": text,
            }
        )
        if args.limit and len(records) >= args.limit:
            break

    if args.output:
        write_json(Path(args.output), records)

    for item in records:
        print(
            f"{format_offset(item['offset'])} "
            f"({format_rom_address(item['offset'])}) "
            f"[{item['byte_length']} bytes] "
            f"{item['text']}"
        )
    print(f"hits: {len(records)}")
    return 0


def cmd_scan_prefixed_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    records = scan_prefixed_text_records(
        data,
        start=parse_offset(args.start),
        end=parse_offset(args.end),
        prefix=bytes(parse_hex_byte(part) for part in args.prefix.split()),
        count_size=args.count_size,
        count_endian=args.count_endian,
        encoding=args.encoding,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        require_non_ascii=args.require_non_ascii,
        require_japanese_text=args.require_japanese,
        min_japanese_ratio=args.min_japanese_ratio,
        limit=args.limit,
        preview_bytes=args.preview_bytes,
    )
    if args.output:
        write_json(Path(args.output), records)

    for item in records:
        print(
            f"{format_offset(item['header_offset'])} -> "
            f"{format_offset(item['offset'])} "
            f"[{item['char_count']} chars / {item['byte_length']} bytes] "
            f"{item['text']}"
        )
    print(f"hits: {len(records)}")
    return 0


def cmd_scan_fc_script_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    records = scan_fc_script_text_records(
        data,
        start=parse_offset(args.start),
        end=parse_offset(args.end),
        anchor=bytes(parse_hex_byte(part) for part in args.anchor.split()),
        stop_byte=parse_hex_byte(args.stop_byte),
        encoding=args.encoding,
        min_chars=args.min_chars,
        require_non_ascii=args.require_non_ascii,
        require_japanese_text=args.require_japanese,
        min_japanese_ratio=args.min_japanese_ratio,
        limit=args.limit,
        preview_bytes=args.preview_bytes,
    )
    if args.output:
        write_json(Path(args.output), records)

    for item in records:
        print(
            f"{format_offset(item['anchor_offset'])} -> "
            f"{format_offset(item['offset'])} "
            f"[raw {item['raw_byte_length']} bytes / normalized {item['byte_length']} bytes] "
            f"{item['text']}"
        )
    print(f"hits: {len(records)}")
    return 0


def cmd_summarize_text_clusters(args: argparse.Namespace) -> int:
    records = load_text_records(Path(args.input))
    result = summarize_text_clusters(
        records,
        gap_threshold=args.gap_threshold,
        sample_count=args.sample_count,
    )
    if args.output:
        write_json(Path(args.output), result)

    print(f"records: {result['record_count']}")
    print(f"clusters: {result['cluster_count']}")
    for cluster in result["clusters"][: args.preview]:
        tags = ",".join(cluster["tags"]) if cluster["tags"] else "-"
        print(
            f"[{cluster['cluster_index']:02d}] "
            f"{format_offset(cluster['start_offset'])}..{format_offset(cluster['end_offset_exclusive'])} "
            f"records={cluster['record_count']} tags={tags} "
            f"first={cluster['first_text'][:40]!r}"
        )
    if len(result["clusters"]) > args.preview:
        print(f"... {len(result['clusters']) - args.preview} more")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_extract_range(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    records = extract_range_records(
        data,
        start=parse_offset(args.start),
        end=parse_offset(args.end),
        terminators=read_terminators(args.terminator),
        max_bytes=args.max_bytes,
        encoding=args.encoding,
        table=table,
        max_unknown_ratio=args.max_unknown_ratio,
        min_chars=args.min_chars,
        require_non_ascii=args.require_non_ascii,
        require_japanese_text=args.require_japanese,
        min_japanese_ratio=args.min_japanese_ratio,
    )
    if args.output:
        write_json(Path(args.output), records)
    for item in records[: args.preview]:
        print(
            f"{format_offset(item['offset'])} "
            f"({format_rom_address(item['offset'])}) "
            f"[{item['byte_length']} bytes] "
            f"{item['text']}"
        )
    if len(records) > args.preview:
        print(f"... {len(records) - args.preview} more")
    print(f"hits: {len(records)}")
    return 0


def cmd_search_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    needle = encode_text(args.text, encoding=args.encoding, table=table)
    hits = find_all(data, needle)
    for offset in hits[: args.limit or None]:
        print(f"{format_offset(offset)} ({format_rom_address(offset)})")
        if args.show_pointers:
            pointers = find_pointers(data, offset, aligned_only=not args.unaligned_pointers, limit=args.pointer_limit)
            if pointers:
                joined = ", ".join(f"{format_offset(ptr)}" for ptr in pointers)
                print(f"  pointers: {joined}")
    print(f"hits: {min(len(hits), args.limit) if args.limit else len(hits)} / total {len(hits)}")
    return 0


def cmd_find_pointers(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    target_offset = parse_offset(args.target)
    hits = find_pointers(data, target_offset, aligned_only=not args.unaligned, limit=args.limit)
    for hit in hits:
        print(f"{format_offset(hit)} ({format_rom_address(hit)})")
    print(f"hits: {len(hits)}")
    return 0


def cmd_find_u32_refs(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    value = parse_u32(args.value)
    start = parse_offset(args.start) if args.start else 0
    end = parse_offset(args.end) if args.end else None
    scoped_word_hits = find_u32_values(data, value, aligned_only=args.aligned, start=start, end=end, limit=args.limit)
    literal_loads = find_thumb_literal_loads(
        data,
        scoped_word_hits,
        start=start,
        end=end,
        limit=args.load_limit,
    )
    report = {
        "value": value,
        "value_hex": f"0x{value:08X}",
        "search_start": start,
        "search_start_rom_address": ROM_BASE + start,
        "search_end": end,
        "search_end_rom_address": None if end is None else ROM_BASE + end,
        "word_hits": [
            {
                "offset": offset,
                "rom_address": ROM_BASE + offset,
                "aligned": offset % 4 == 0,
            }
            for offset in scoped_word_hits
        ],
        "thumb_literal_loads": literal_loads,
    }
    if args.output:
        write_json(Path(args.output), report)

    print(f"value: 0x{value:08X}")
    print(f"word hits: {len(scoped_word_hits)}")
    for offset in scoped_word_hits[: args.preview]:
        print(f"  {format_offset(offset)} ({format_rom_address(offset)})")
    if len(scoped_word_hits) > args.preview:
        print(f"  ... {len(scoped_word_hits) - args.preview} more")
    print(f"thumb literal loads: {len(literal_loads)}")
    for item in literal_loads[: args.preview]:
        print(
            f"  {format_offset(item['instruction_offset'])} "
            f"({format_rom_address(item['instruction_offset'])}) "
            f"loads {item['register']} from {format_offset(item['literal_offset'])} "
            f"access={item['access']}"
        )
    if len(literal_loads) > args.preview:
        print(f"  ... {len(literal_loads) - args.preview} more")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_scan_lz77(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    hits = scan_lz77_blocks(
        data,
        max_output_size=args.max_output_size,
        min_compressed_size=args.min_compressed_size,
        min_decompressed_size=args.min_decompressed_size,
        limit=args.limit,
    )
    if args.output:
        write_json(Path(args.output), hits)
    for item in hits:
        print(
            f"{format_offset(item['offset'])} "
            f"({format_rom_address(item['offset'])}) "
            f"compressed={item['compressed_size']} "
            f"decompressed={item['decompressed_size']}"
        )
    print(f"hits: {len(hits)}")
    return 0


def cmd_find_thumb_bl(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    start = parse_offset(args.start) if args.start else 0
    end = parse_offset(args.end) if args.end else None
    target_offset = parse_offset(args.target)
    hits = find_thumb_bl_callers(
        data,
        target_offset=target_offset,
        start=start,
        end=end,
        limit=args.limit,
    )
    if args.output:
        write_json(Path(args.output), hits)

    for item in hits:
        print(
            f"{format_offset(item['call_offset'])} "
            f"({format_rom_address(item['call_offset'])}) "
            f"-> {format_offset(item['target_offset'])} "
            f"({format_rom_address(item['target_offset'])})"
        )
    print(f"hits: {len(hits)}")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_dump_thumb(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    start = parse_offset(args.start)
    end = parse_offset(args.end)
    lines = dump_thumb_slice(data, start=start, end=end)
    text = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)
    print(f"lines: {len(lines)}")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_dump_4bpp(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    pixels, width, height = render_4bpp_tiles(
        data,
        offset=parse_offset(args.offset),
        tiles=args.tiles,
        columns=args.columns,
    )
    output_path = Path(args.output)
    write_pgm(output_path, pixels, width, height)
    print(f"wrote: {output_path} ({width}x{height})")
    return 0


def cmd_dump_fnt_glyph(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    payload_offset = parse_offset(args.payload)
    header = read_fnt_header(data, payload_offset=payload_offset)
    glyph_index = resolve_fnt_glyph_index(
        data,
        header=header,
        glyph_index=args.glyph_index,
        code=parse_offset(args.code) if args.code else None,
    )
    glyph_offset = header["glyph_base"] + glyph_index * header["stride"]
    width = args.width or 12
    height = args.height or 12
    row_bytes = args.row_bytes or max(1, math.ceil(width / 2))
    pixels = render_fnt_glyph(
        data,
        glyph_offset=glyph_offset,
        width=width,
        height=height,
        row_bytes=row_bytes,
    )
    output_path = Path(args.output)
    write_pgm(output_path, pixels, width, height)
    print(
        f"wrote: {output_path} ({width}x{height}) "
        f"payload={format_offset(payload_offset)} "
        f"lookup={format_offset(header['lookup_base'])} "
        f"glyph_base={format_offset(header['glyph_base'])} "
        f"glyph_index=0x{glyph_index:04X} glyph_offset={format_offset(glyph_offset)} "
        f"stride=0x{header['stride']:X} flags=0x{header['flags']:02X}"
    )
    return 0


def cmd_inspect_fnt(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    payload_offset = parse_offset(args.payload)
    header = read_fnt_header(data, payload_offset=payload_offset)
    records: List[Dict[str, object]] = []
    max_glyph_index = 0
    nonzero_count = 0

    for code in range(0x10000):
        lookup_offset = header["lookup_base"] + code * 2
        if lookup_offset + 2 > len(data):
            break
        glyph_index = struct.unpack_from("<H", data, lookup_offset)[0]
        if glyph_index == 0:
            if args.include_zero:
                records.append(
                    {
                        "code": code,
                        "code_hex": f"0x{code:04X}",
                        "text": decode_cp932_code(code),
                        "glyph_index": 0,
                        "glyph_offset": None,
                    }
                )
            continue
        nonzero_count += 1
        max_glyph_index = max(max_glyph_index, glyph_index)
        records.append(
            {
                "code": code,
                "code_hex": f"0x{code:04X}",
                "text": decode_cp932_code(code),
                "glyph_index": glyph_index,
                "glyph_offset": header["glyph_base"] + glyph_index * header["stride"],
            }
        )

    result = {
        "payload_offset": payload_offset,
        "payload_rom_address": ROM_BASE + payload_offset,
        "flags": header["flags"],
        "flags_hex": f"0x{header['flags']:02X}",
        "stride": header["stride"],
        "stride_hex": f"0x{header['stride']:X}",
        "lookup_base": header["lookup_base"],
        "glyph_base": header["glyph_base"],
        "nonzero_count": nonzero_count,
        "max_glyph_index": max_glyph_index,
        "max_glyph_index_hex": f"0x{max_glyph_index:04X}",
        "glyph_end": header["glyph_base"] + (max_glyph_index + 1) * header["stride"],
        "entries": records,
    }
    if args.output:
        write_json(Path(args.output), result)

    print(
        f"payload={format_offset(payload_offset)} "
        f"lookup={format_offset(header['lookup_base'])} "
        f"glyph_base={format_offset(header['glyph_base'])} "
        f"stride=0x{header['stride']:X} flags=0x{header['flags']:02X}"
    )
    print(f"nonzero glyph mappings: {nonzero_count}")
    print(f"max glyph index: 0x{max_glyph_index:04X}")
    preview = records[: args.preview]
    for item in preview:
        text = item["text"] if item["text"] else "<undecodable>"
        glyph_offset = item["glyph_offset"]
        glyph_desc = "None" if glyph_offset is None else format_offset(int(glyph_offset))
        print(
            f"  {item['code_hex']} {text!r} -> "
            f"0x{int(item['glyph_index']):04X} @ {glyph_desc}"
        )
    if len(records) > args.preview:
        print(f"  ... {len(records) - args.preview} more")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_audit_fnt_usage(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    payload_offset = parse_offset(args.payload)
    header = read_fnt_header(data, payload_offset=payload_offset)

    manifest_entries: List[Dict[str, object]] = []
    code_to_entry: Dict[int, Dict[str, object]] = {}
    max_glyph_index = 0

    for code in range(0x10000):
        lookup_offset = header["lookup_base"] + code * 2
        if lookup_offset + 2 > len(data):
            break
        glyph_index = struct.unpack_from("<H", data, lookup_offset)[0]
        if glyph_index == 0:
            continue
        max_glyph_index = max(max_glyph_index, glyph_index)
        entry = {
            "code": code,
            "code_hex": f"0x{code:04X}",
            "text": decode_cp932_code(code),
            "glyph_index": glyph_index,
            "glyph_offset": header["glyph_base"] + glyph_index * header["stride"],
        }
        manifest_entries.append(entry)
        code_to_entry[code] = entry

    counts: Dict[int, int] = {}
    total_chars_scanned = 0
    per_file: List[Dict[str, object]] = []
    for raw_path in args.inputs:
        source_path = Path(raw_path)
        local_counts: Dict[int, int] = {}
        file_total_chars = 0
        for text in iter_text_fields_from_json(source_path):
            for ch in text:
                code = encode_cp932_char(ch)
                if code is None:
                    continue
                file_total_chars += 1
                local_counts[code] = local_counts.get(code, 0) + 1
                counts[code] = counts.get(code, 0) + 1
                total_chars_scanned += 1
        per_file.append(
            {
                "path": str(source_path),
                "char_count": file_total_chars,
                "unique_code_count": len(local_counts),
            }
        )

    unused_mapped_entries = [entry for entry in manifest_entries if counts.get(int(entry["code"]), 0) == 0]
    rare_used_entries = []
    for entry in manifest_entries:
        usage_count = counts.get(int(entry["code"]), 0)
        if 0 < usage_count <= args.rare_threshold:
            item = dict(entry)
            item["usage_count"] = usage_count
            rare_used_entries.append(item)
    rare_used_entries.sort(key=lambda item: (int(item["usage_count"]), int(item["code"])))

    top_used_entries = []
    for code, usage_count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        entry = code_to_entry.get(code)
        if entry is None:
            continue
        item = dict(entry)
        item["usage_count"] = usage_count
        top_used_entries.append(item)
        if len(top_used_entries) >= args.top_used:
            break

    used_mapped_codes = {int(entry["code"]) for entry in manifest_entries if counts.get(int(entry["code"]), 0) > 0}
    unused_code_ranges = []
    range_start: Optional[int] = None
    for code in range(0x20, 0x10000):
        is_free = code not in code_to_entry
        if is_free and range_start is None:
            range_start = code
            continue
        if (not is_free) and range_start is not None:
            if code - range_start >= args.min_free_code_range:
                unused_code_ranges.append(
                    {
                        "start": range_start,
                        "start_hex": f"0x{range_start:04X}",
                        "end": code - 1,
                        "end_hex": f"0x{code - 1:04X}",
                        "length": code - range_start,
                    }
                )
            range_start = None
    if range_start is not None and 0x10000 - range_start >= args.min_free_code_range:
        unused_code_ranges.append(
            {
                "start": range_start,
                "start_hex": f"0x{range_start:04X}",
                "end": 0xFFFF,
                "end_hex": "0xFFFF",
                "length": 0x10000 - range_start,
            }
        )

    used_glyphs = {int(entry["glyph_index"]) for entry in manifest_entries}
    glyph_gaps = []
    gap_start: Optional[int] = None
    for glyph_index in range(1, max_glyph_index + 1):
        is_free = glyph_index not in used_glyphs
        if is_free and gap_start is None:
            gap_start = glyph_index
            continue
        if (not is_free) and gap_start is not None:
            glyph_gaps.append(
                {
                    "start": gap_start,
                    "end": glyph_index - 1,
                    "length": glyph_index - gap_start,
                }
            )
            gap_start = None
    if gap_start is not None:
        glyph_gaps.append(
            {
                "start": gap_start,
                "end": max_glyph_index,
                "length": max_glyph_index + 1 - gap_start,
            }
        )

    payload_length = parse_offset(args.payload_length) if args.payload_length else None
    glyph_end = header["glyph_base"] + (max_glyph_index + 1) * header["stride"]
    tail_free_bytes = None
    if payload_length is not None:
        tail_free_bytes = max(0, payload_offset + payload_length - glyph_end)

    result = {
        "payload_offset": payload_offset,
        "payload_rom_address": ROM_BASE + payload_offset,
        "payload_length": payload_length,
        "payload_length_hex": None if payload_length is None else f"0x{payload_length:X}",
        "flags": header["flags"],
        "flags_hex": f"0x{header['flags']:02X}",
        "stride": header["stride"],
        "stride_hex": f"0x{header['stride']:X}",
        "lookup_base": header["lookup_base"],
        "glyph_base": header["glyph_base"],
        "glyph_end": glyph_end,
        "mapped_code_count": len(manifest_entries),
        "mapped_code_count_used_in_inputs": len(used_mapped_codes),
        "mapped_code_count_unused_in_inputs": len(unused_mapped_entries),
        "max_glyph_index": max_glyph_index,
        "glyph_gap_count": len(glyph_gaps),
        "tail_free_bytes": tail_free_bytes,
        "total_chars_scanned": total_chars_scanned,
        "source_files": per_file,
        "unused_code_ranges": unused_code_ranges,
        "unused_mapped_entries": unused_mapped_entries,
        "rare_used_entries": rare_used_entries,
        "top_used_entries": top_used_entries,
        "glyph_gaps": glyph_gaps,
    }
    if args.output:
        write_json(Path(args.output), result)

    print(
        f"payload={format_offset(payload_offset)} "
        f"lookup={format_offset(header['lookup_base'])} "
        f"glyph_base={format_offset(header['glyph_base'])} "
        f"stride=0x{header['stride']:X} mapped={len(manifest_entries)}"
    )
    print(f"chars scanned: {total_chars_scanned}")
    print(f"mapped codes used in inputs: {len(used_mapped_codes)}")
    print(f"mapped codes unused in inputs: {len(unused_mapped_entries)}")
    print(f"glyph gaps: {len(glyph_gaps)}")
    if tail_free_bytes is not None:
        print(f"tail free bytes: {tail_free_bytes}")
    print("top used preview:")
    for item in top_used_entries[: min(10, len(top_used_entries))]:
        text = item["text"] if item["text"] else "<undecodable>"
        print(
            f"  {item['code_hex']} {text!r} "
            f"count={item['usage_count']} glyph=0x{int(item['glyph_index']):04X}"
        )
    print("unused mapped preview:")
    for item in unused_mapped_entries[: args.unused_preview]:
        text = item["text"] if item["text"] else "<undecodable>"
        print(f"  {item['code_hex']} {text!r} glyph=0x{int(item['glyph_index']):04X}")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_inspect_chunk_table(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    data = load_rom(rom_path)
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    result = inspect_chunk_table(
        data,
        start=parse_offset(args.start),
        count=args.count,
        layout=args.layout,
        stop_on_invalid=args.stop_on_invalid,
        scan_text=args.scan_text,
        terminators=read_terminators(args.terminator),
        max_bytes=args.max_bytes,
        encoding=args.encoding,
        table=table,
        max_unknown_ratio=args.max_unknown_ratio,
        min_chars=args.min_chars,
        require_non_ascii=args.require_non_ascii,
        require_japanese_text=args.require_japanese,
        min_japanese_ratio=args.min_japanese_ratio,
    )
    if args.output:
        write_json(Path(args.output), result)

    requested = result["layout_requested"]
    resolved = result["layout_resolved"]
    if requested == "auto":
        scores = result["auto_scores"]
        summary = ", ".join(
            f"{name} score={values['score']} valid={values['valid_entries']}"
            for name, values in scores.items()
        )
        print(f"layout: auto -> {resolved} ({summary})")
    else:
        print(f"layout: {resolved}")

    valid_entries = 0
    for entry in result["entries"]:
        if not entry["valid"]:
            print(
                f"[{entry['index']:02d}] table={format_offset(entry['table_offset'])} "
                f"raw=0x{entry['raw_first_u32']:08X},0x{entry['raw_second_u32']:08X} invalid"
            )
            continue

        valid_entries += 1
        line = (
            f"[{entry['index']:02d}] table={format_offset(entry['table_offset'])} "
            f"len=0x{entry['length']:X} "
            f"ptr=0x{entry['rom_address']:08X} "
            f"file={format_offset(entry['file_offset'])} "
            f"end={format_offset(entry['end_offset_inclusive'])}"
        )
        gap = entry.get("gap_from_previous")
        if gap is not None:
            if gap < 0:
                line += f" overlap={-gap} bytes"
            else:
                line += f" gap={gap} bytes"
        if args.scan_text:
            line += f" text_hits={entry['text_hits']}"
            if entry["first_text"]:
                line += f" first={entry['first_text']}"
        print(line)

    print(f"valid entries: {valid_entries} / {len(result['entries'])}")
    if args.output:
        print(f"wrote: {args.output}")
    return 0


def cmd_replace_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    output_path = Path(args.output_rom)
    data = bytearray(load_rom(rom_path))
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    payload = bytearray(encode_text(args.text, encoding=args.encoding, table=table))
    if args.terminator:
        payload.extend(parse_hex_byte(value) for value in args.terminator)
    offset = parse_offset(args.offset)
    if len(payload) > args.max_bytes:
        raise ToolError(f"새 문자열 길이 {len(payload)} bytes 가 허용 길이 {args.max_bytes} bytes 를 초과합니다.")
    end = offset + args.max_bytes
    if end > len(data):
        raise ToolError("교체 범위가 ROM 끝을 넘어갑니다.")
    data[offset:offset + len(payload)] = payload
    if len(payload) < args.max_bytes:
        pad = parse_hex_byte(args.pad_byte)
        data[offset + len(payload):end] = bytes([pad]) * (args.max_bytes - len(payload))
    write_binary(output_path, bytes(data))
    print(f"patched: {output_path}")
    print(f"offset : {format_offset(offset)}")
    print(f"bytes  : {len(payload)} / {args.max_bytes}")
    return 0


def cmd_inject_text(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    output_path = Path(args.output_rom)
    data = bytearray(load_rom(rom_path))
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    payload = bytearray(encode_text(args.text, encoding=args.encoding, table=table))
    if args.terminator:
        payload.extend(parse_hex_byte(value) for value in args.terminator)

    if args.destination_offset:
        destination = parse_offset(args.destination_offset)
    else:
        destination = find_free_space(
            data,
            start=parse_offset(args.search_free_space_from),
            size=len(payload),
            fill_byte=parse_hex_byte(args.fill_byte),
            alignment=args.align,
        )

    end = destination + len(payload)
    if end > len(data):
        raise ToolError("주입 위치가 ROM 끝을 넘어갑니다.")
    data[destination:end] = payload

    pointer_offsets = [parse_offset(value) for value in args.pointer]
    pointer_value = ROM_BASE + destination
    for pointer_offset in pointer_offsets:
        if pointer_offset + 4 > len(data):
            raise ToolError(f"포인터 위치가 ROM 끝을 넘어갑니다: {format_offset(pointer_offset)}")
        struct.pack_into("<I", data, pointer_offset, pointer_value)

    write_binary(output_path, bytes(data))
    print(f"patched     : {output_path}")
    print(f"string_at   : {format_offset(destination)} ({format_rom_address(destination)})")
    print(f"pointer_val : 0x{pointer_value:08X}")
    print(f"pointers    : {', '.join(format_offset(ptr) for ptr in pointer_offsets)}")
    return 0


def parse_record_terminator(record: dict, default_values: Sequence[str]) -> bytes:
    terminator_value = record.get("terminator")
    if terminator_value:
        return bytes([parse_hex_byte(terminator_value)])
    return bytes(parse_hex_byte(value) for value in default_values)


def normalize_translation_record(record: dict, *, source_path: Path, source_order: int) -> dict:
    normalized = dict(record)
    normalized.setdefault("translation", "")
    normalized.setdefault("notes", "")
    normalized["source_file"] = source_path.name
    normalized["source_group"] = source_path.stem
    normalized["source_order"] = source_order
    return normalized


def cmd_build_translation_set(args: argparse.Namespace) -> int:
    output_path = Path(args.output)
    merged: List[dict] = []
    seen_keys = set()

    for source_order, raw_path in enumerate(args.inputs):
        source_path = Path(raw_path)
        records = json.loads(source_path.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ToolError(f"{source_path}: JSON 배열이 아닙니다.")

        for record in records:
            if not isinstance(record, dict):
                raise ToolError(f"{source_path}: 배열 원소는 객체여야 합니다.")
            if "offset" not in record or "text" not in record:
                raise ToolError(f"{source_path}: 최소한 offset, text 필드가 필요합니다.")

            normalized = normalize_translation_record(record, source_path=source_path, source_order=source_order)
            dedupe_key = (
                normalized["source_file"],
                int(normalized["offset"]),
            )
            if args.dedupe_text:
                dedupe_key = (normalized["text"],)
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            merged.append(normalized)

    merged.sort(key=lambda item: (int(item.get("source_order", 0)), int(item["offset"])))
    write_json(output_path, merged)

    print(f"written : {output_path}")
    print(f"records : {len(merged)}")
    print(f"sources : {len(args.inputs)}")
    return 0


def cmd_apply_translations(args: argparse.Namespace) -> int:
    rom_path = Path(args.rom)
    translation_path = Path(args.translation_file)
    output_path = Path(args.output_rom)
    table = TableCodec.from_path(Path(args.table)) if args.table else None
    data = bytearray(load_rom(rom_path))
    records = json.loads(translation_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ToolError("번역 파일은 JSON 배열이어야 합니다.")

    report = []
    next_free_search = parse_offset(args.search_free_space_from)

    for record in records:
        translation = record.get("translation", "")
        if not translation:
            continue

        original_offset = int(record["offset"])
        original_byte_length = int(record["byte_length"])
        terminator = parse_record_terminator(record, args.terminator)
        encoded_text = encode_text(translation, encoding=args.encoding, table=table)
        payload = encoded_text + terminator
        original_capacity = original_byte_length + len(terminator)

        if len(payload) <= original_capacity:
            data[original_offset:original_offset + len(payload)] = payload
            if len(payload) < original_capacity:
                pad = parse_hex_byte(args.pad_byte)
                data[original_offset + len(payload):original_offset + original_capacity] = bytes([pad]) * (
                    original_capacity - len(payload)
                )
            report.append(
                {
                    "offset": original_offset,
                    "action": "in_place",
                    "translation": translation,
                    "written_bytes": len(payload),
                }
            )
            continue

        if not args.auto_repoint:
            report.append(
                {
                    "offset": original_offset,
                    "action": "skipped_too_long",
                    "translation": translation,
                    "required_bytes": len(payload),
                    "capacity_bytes": original_capacity,
                }
            )
            continue

        pointers = find_pointers(
            data,
            original_offset,
            aligned_only=not args.unaligned_pointers,
            limit=None,
        )
        if not pointers:
            if args.fail_on_missing_pointers:
                raise ToolError(f"{format_offset(original_offset)} 에 대한 포인터를 찾지 못했습니다.")
            report.append(
                {
                    "offset": original_offset,
                    "action": "skipped_no_pointer",
                    "translation": translation,
                }
            )
            continue

        destination = find_free_space(
            data,
            start=next_free_search,
            size=len(payload),
            fill_byte=parse_hex_byte(args.fill_byte),
            alignment=args.align,
        )
        data[destination:destination + len(payload)] = payload
        pointer_value = ROM_BASE + destination
        for pointer_offset in pointers:
            struct.pack_into("<I", data, pointer_offset, pointer_value)
        next_free_search = destination + len(payload)
        report.append(
            {
                "offset": original_offset,
                "action": "repointed",
                "translation": translation,
                "new_offset": destination,
                "pointer_count": len(pointers),
            }
        )

    write_binary(output_path, bytes(data))
    if args.report:
        write_json(Path(args.report), report)

    changed = sum(1 for item in report if item["action"] in {"in_place", "repointed"})
    print(f"patched: {output_path}")
    print(f"changed: {changed}")
    print(f"report : {args.report or '(not written)'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GBA 한글화 작업용 ROM 조사/패치 툴")
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info", help="GBA ROM 헤더를 출력합니다.")
    info.add_argument("rom")
    info.add_argument("--json-output", action="store_true")
    info.set_defaults(func=cmd_info)

    scan_text = sub.add_parser("scan-text", help="종단 바이트 기준으로 문자열 후보를 스캔합니다.")
    scan_text.add_argument("rom")
    scan_text.add_argument("--encoding", default="cp932")
    scan_text.add_argument("--table")
    scan_text.add_argument("--terminator", action="append", default=[])
    scan_text.add_argument("--min-chars", type=int, default=4)
    scan_text.add_argument("--max-bytes", type=int, default=96)
    scan_text.add_argument("--limit", type=int, default=100)
    scan_text.add_argument("--start", help="스캔 시작 오프셋 (예: 0x700000)")
    scan_text.add_argument("--end", help="스캔 끝 오프셋 (exclusive)")
    scan_text.add_argument("--sliding", action="store_true", help="각 바이트 오프셋에서 종료 바이트까지 슬라이딩 스캔 (범위 필수)")
    scan_text.add_argument("--require-non-ascii", action="store_true", default=True)
    scan_text.add_argument("--require-japanese", action="store_true")
    scan_text.add_argument("--min-japanese-ratio", type=float, default=0.5)
    scan_text.add_argument("--max-unknown-ratio", type=float, default=0.25)
    scan_text.add_argument("--output")
    scan_text.set_defaults(func=cmd_scan_text)

    scan_prefixed_text = sub.add_parser(
        "scan-prefixed-text",
        help="prefix + 문자수 헤더를 가진 command-stream 텍스트를 스캔합니다.",
    )
    scan_prefixed_text.add_argument("rom")
    scan_prefixed_text.add_argument("--start", required=True, help="스캔 시작 오프셋")
    scan_prefixed_text.add_argument("--end", required=True, help="스캔 끝 오프셋 (exclusive)")
    scan_prefixed_text.add_argument("--prefix", default="01 FF", help="헤더 prefix 바이트들 (예: '01 FF')")
    scan_prefixed_text.add_argument("--count-size", type=int, default=2, help="문자수 필드 바이트 길이")
    scan_prefixed_text.add_argument(
        "--count-endian",
        choices=["little", "big"],
        default="little",
        help="문자수 필드 엔디안",
    )
    scan_prefixed_text.add_argument("--encoding", default="cp932")
    scan_prefixed_text.add_argument("--min-chars", type=int, default=4)
    scan_prefixed_text.add_argument("--max-chars", type=int, default=128)
    scan_prefixed_text.add_argument("--limit", type=int)
    scan_prefixed_text.add_argument("--preview-bytes", type=int, default=12)
    scan_prefixed_text.add_argument("--require-non-ascii", action="store_true", default=True)
    scan_prefixed_text.add_argument("--require-japanese", action="store_true")
    scan_prefixed_text.add_argument("--min-japanese-ratio", type=float, default=0.5)
    scan_prefixed_text.add_argument("--output")
    scan_prefixed_text.set_defaults(func=cmd_scan_prefixed_text)

    scan_fc_script = sub.add_parser(
        "scan-fc-script-text",
        help="FC 제어 바이트가 섞인 스크립트 자원에서 FC 00 anchor 뒤 텍스트를 추출합니다.",
    )
    scan_fc_script.add_argument("rom")
    scan_fc_script.add_argument("--start", required=True, help="스캔 시작 오프셋")
    scan_fc_script.add_argument("--end", required=True, help="스캔 끝 오프셋 (exclusive)")
    scan_fc_script.add_argument("--anchor", default="FC 00", help="텍스트 시작 anchor 바이트들")
    scan_fc_script.add_argument("--stop-byte", default="FC", help="다음 command 시작으로 취급할 바이트")
    scan_fc_script.add_argument("--encoding", default="cp932")
    scan_fc_script.add_argument("--min-chars", type=int, default=4)
    scan_fc_script.add_argument("--limit", type=int)
    scan_fc_script.add_argument("--preview-bytes", type=int, default=12)
    scan_fc_script.add_argument("--require-non-ascii", action="store_true", default=True)
    scan_fc_script.add_argument("--require-japanese", action="store_true")
    scan_fc_script.add_argument("--min-japanese-ratio", type=float, default=0.5)
    scan_fc_script.add_argument("--output")
    scan_fc_script.set_defaults(func=cmd_scan_fc_script_text)

    summarize_clusters = sub.add_parser(
        "summarize-text-clusters",
        help="텍스트 레코드 JSON을 offset gap 기준 cluster 로 나누고 샘플/태그 요약을 만듭니다.",
    )
    summarize_clusters.add_argument("input")
    summarize_clusters.add_argument("--gap-threshold", type=lambda value: int(value, 0), default=0x400)
    summarize_clusters.add_argument("--sample-count", type=int, default=3)
    summarize_clusters.add_argument("--preview", type=int, default=20)
    summarize_clusters.add_argument("--output")
    summarize_clusters.set_defaults(func=cmd_summarize_text_clusters)

    extract_range = sub.add_parser("extract-range", help="지정한 ROM 구간에서 문자열을 추출합니다.")
    extract_range.add_argument("rom")
    extract_range.add_argument("start")
    extract_range.add_argument("end")
    extract_range.add_argument("--encoding", default="cp932")
    extract_range.add_argument("--table")
    extract_range.add_argument("--terminator", action="append", default=[])
    extract_range.add_argument("--min-chars", type=int, default=1)
    extract_range.add_argument("--max-bytes", type=int, default=128)
    extract_range.add_argument("--require-non-ascii", action="store_true", default=True)
    extract_range.add_argument("--require-japanese", action="store_true")
    extract_range.add_argument("--min-japanese-ratio", type=float, default=0.5)
    extract_range.add_argument("--max-unknown-ratio", type=float, default=0.25)
    extract_range.add_argument("--preview", type=int, default=20)
    extract_range.add_argument("--output")
    extract_range.set_defaults(func=cmd_extract_range)

    search_text = sub.add_parser("search-text", help="지정한 문자열의 바이트 패턴을 찾습니다.")
    search_text.add_argument("rom")
    search_text.add_argument("text")
    search_text.add_argument("--encoding", default="cp932")
    search_text.add_argument("--table")
    search_text.add_argument("--limit", type=int)
    search_text.add_argument("--show-pointers", action="store_true")
    search_text.add_argument("--pointer-limit", type=int, default=16)
    search_text.add_argument("--unaligned-pointers", action="store_true")
    search_text.set_defaults(func=cmd_search_text)

    find_ptr = sub.add_parser("find-pointers", help="문자열/데이터 오프셋을 가리키는 포인터를 찾습니다.")
    find_ptr.add_argument("rom")
    find_ptr.add_argument("target")
    find_ptr.add_argument("--limit", type=int)
    find_ptr.add_argument("--unaligned", action="store_true")
    find_ptr.set_defaults(func=cmd_find_pointers)

    find_u32_refs = sub.add_parser(
        "find-u32-refs",
        help="특정 32비트 값을 찾고, 그 literal 을 읽는 Thumb LDR 후보를 함께 표시합니다.",
    )
    find_u32_refs.add_argument("rom")
    find_u32_refs.add_argument("value")
    find_u32_refs.add_argument("--start")
    find_u32_refs.add_argument("--end")
    find_u32_refs.add_argument("--aligned", action="store_true", help="4바이트 정렬 위치만 값 검색")
    find_u32_refs.add_argument("--limit", type=int, help="값 검색 결과 제한")
    find_u32_refs.add_argument("--load-limit", type=int, help="Thumb literal load 결과 제한")
    find_u32_refs.add_argument("--preview", type=int, default=20)
    find_u32_refs.add_argument("--output")
    find_u32_refs.set_defaults(func=cmd_find_u32_refs)

    find_thumb_bl = sub.add_parser("find-thumb-bl", help="Thumb BL 호출자가 특정 함수 오프셋을 가리키는지 찾습니다.")
    find_thumb_bl.add_argument("rom")
    find_thumb_bl.add_argument("target")
    find_thumb_bl.add_argument("--start")
    find_thumb_bl.add_argument("--end")
    find_thumb_bl.add_argument("--limit", type=int)
    find_thumb_bl.add_argument("--output")
    find_thumb_bl.set_defaults(func=cmd_find_thumb_bl)

    dump_thumb = sub.add_parser("dump-thumb", help="지정한 ROM 구간을 간단한 Thumb 디스어셈블리 형태로 출력합니다.")
    dump_thumb.add_argument("rom")
    dump_thumb.add_argument("start")
    dump_thumb.add_argument("end")
    dump_thumb.add_argument("--output")
    dump_thumb.set_defaults(func=cmd_dump_thumb)

    scan_lz77 = sub.add_parser("scan-lz77", help="GBA BIOS LZ77 블록을 스캔합니다.")
    scan_lz77.add_argument("rom")
    scan_lz77.add_argument("--limit", type=int, default=100)
    scan_lz77.add_argument("--max-output-size", type=int, default=4 * 1024 * 1024)
    scan_lz77.add_argument("--min-compressed-size", type=int, default=24)
    scan_lz77.add_argument("--min-decompressed-size", type=int, default=32)
    scan_lz77.add_argument("--output")
    scan_lz77.set_defaults(func=cmd_scan_lz77)

    inspect_chunk = sub.add_parser(
        "inspect-chunk-table",
        help="8바이트 리소스/청크 테이블을 길이+포인터 또는 포인터+길이로 해석합니다.",
    )
    inspect_chunk.add_argument("rom")
    inspect_chunk.add_argument("start")
    inspect_chunk.add_argument("--count", type=int, required=True)
    inspect_chunk.add_argument("--layout", choices=["auto", "length-pointer", "pointer-length"], default="auto")
    inspect_chunk.add_argument("--stop-on-invalid", action="store_true")
    inspect_chunk.add_argument("--scan-text", action="store_true")
    inspect_chunk.add_argument("--encoding", default="cp932")
    inspect_chunk.add_argument("--table")
    inspect_chunk.add_argument("--terminator", action="append", default=["00"])
    inspect_chunk.add_argument("--min-chars", type=int, default=4)
    inspect_chunk.add_argument("--max-bytes", type=int, default=128)
    inspect_chunk.add_argument("--require-non-ascii", action="store_true", default=True)
    inspect_chunk.add_argument("--require-japanese", action="store_true")
    inspect_chunk.add_argument("--min-japanese-ratio", type=float, default=0.5)
    inspect_chunk.add_argument("--max-unknown-ratio", type=float, default=0.25)
    inspect_chunk.add_argument("--output")
    inspect_chunk.set_defaults(func=cmd_inspect_chunk_table)

    dump_4bpp = sub.add_parser("dump-4bpp", help="4bpp 타일 데이터를 PGM 이미지로 덤프합니다.")
    dump_4bpp.add_argument("rom")
    dump_4bpp.add_argument("offset")
    dump_4bpp.add_argument("--tiles", type=int, required=True)
    dump_4bpp.add_argument("--columns", type=int, default=16)
    dump_4bpp.add_argument("--output", required=True)
    dump_4bpp.set_defaults(func=cmd_dump_4bpp)

    dump_fnt = sub.add_parser("dump-fnt-glyph", help="공통 fnt payload 에서 glyph 하나를 PGM 으로 덤프합니다.")
    dump_fnt.add_argument("rom")
    dump_fnt.add_argument("payload")
    dump_fnt.add_argument("--glyph-index", type=lambda value: int(value, 0))
    dump_fnt.add_argument("--code", help="lookup table 에 넣을 문자 코드 (예: 0x82A0)")
    dump_fnt.add_argument("--width", type=int)
    dump_fnt.add_argument("--height", type=int)
    dump_fnt.add_argument("--row-bytes", type=int)
    dump_fnt.add_argument("--output", required=True)
    dump_fnt.set_defaults(func=cmd_dump_fnt_glyph)

    inspect_fnt = sub.add_parser("inspect-fnt", help="공통 fnt payload 의 lookup/glyph 매핑 현황을 JSON/텍스트로 출력합니다.")
    inspect_fnt.add_argument("rom")
    inspect_fnt.add_argument("payload")
    inspect_fnt.add_argument("--include-zero", action="store_true")
    inspect_fnt.add_argument("--preview", type=int, default=40)
    inspect_fnt.add_argument("--output")
    inspect_fnt.set_defaults(func=cmd_inspect_fnt)

    audit_fnt = sub.add_parser(
        "audit-fnt-usage",
        help="공통 fnt 매핑이 현재 추출 텍스트에서 얼마나 쓰이는지 집계하고, 재사용 후보를 정리합니다.",
    )
    audit_fnt.add_argument("rom")
    audit_fnt.add_argument("payload")
    audit_fnt.add_argument("inputs", nargs="+")
    audit_fnt.add_argument("--payload-length")
    audit_fnt.add_argument("--rare-threshold", type=int, default=2)
    audit_fnt.add_argument("--top-used", type=int, default=40)
    audit_fnt.add_argument("--unused-preview", type=int, default=40)
    audit_fnt.add_argument("--min-free-code-range", type=int, default=8)
    audit_fnt.add_argument("--output")
    audit_fnt.set_defaults(func=cmd_audit_fnt_usage)

    replace_text = sub.add_parser("replace-text", help="기존 위치에 문자열을 같은 길이 이하로 교체합니다.")
    replace_text.add_argument("rom")
    replace_text.add_argument("output_rom")
    replace_text.add_argument("--offset", required=True)
    replace_text.add_argument("--text", required=True)
    replace_text.add_argument("--encoding", default="cp932")
    replace_text.add_argument("--table")
    replace_text.add_argument("--max-bytes", required=True, type=int)
    replace_text.add_argument("--terminator", action="append", default=[])
    replace_text.add_argument("--pad-byte", default="FF")
    replace_text.set_defaults(func=cmd_replace_text)

    inject_text = sub.add_parser("inject-text", help="자유 공간에 문자열을 넣고 포인터를 새 위치로 갱신합니다.")
    inject_text.add_argument("rom")
    inject_text.add_argument("output_rom")
    inject_text.add_argument("--pointer", action="append", required=True)
    inject_text.add_argument("--text", required=True)
    inject_text.add_argument("--encoding", default="cp932")
    inject_text.add_argument("--table")
    inject_text.add_argument("--terminator", action="append", default=[])
    inject_text.add_argument("--destination-offset")
    inject_text.add_argument("--search-free-space-from", default="0x700000")
    inject_text.add_argument("--fill-byte", default="FF")
    inject_text.add_argument("--align", type=int, default=4)
    inject_text.set_defaults(func=cmd_inject_text)

    build_translation_set = sub.add_parser(
        "build-translation-set",
        help="여러 추출 JSON을 번역 작업용 JSON 한 개로 묶고 translation 필드를 정규화합니다.",
    )
    build_translation_set.add_argument("output")
    build_translation_set.add_argument("inputs", nargs="+")
    build_translation_set.add_argument("--dedupe-text", action="store_true")
    build_translation_set.set_defaults(func=cmd_build_translation_set)

    apply_translations = sub.add_parser("apply-translations", help="번역 JSON 파일을 ROM에 일괄 반영합니다.")
    apply_translations.add_argument("rom")
    apply_translations.add_argument("translation_file")
    apply_translations.add_argument("output_rom")
    apply_translations.add_argument("--encoding", default="cp932")
    apply_translations.add_argument("--table")
    apply_translations.add_argument("--terminator", action="append", default=["00"])
    apply_translations.add_argument("--pad-byte", default="FF")
    apply_translations.add_argument("--no-auto-repoint", action="store_false", dest="auto_repoint")
    apply_translations.add_argument("--search-free-space-from", default="0x700000")
    apply_translations.add_argument("--fill-byte", default="FF")
    apply_translations.add_argument("--align", type=int, default=4)
    apply_translations.add_argument("--unaligned-pointers", action="store_true")
    apply_translations.add_argument("--fail-on-missing-pointers", action="store_true")
    apply_translations.add_argument("--report")
    apply_translations.set_defaults(func=cmd_apply_translations)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ToolError as exc:
        parser.exit(1, f"error: {exc}\n")
