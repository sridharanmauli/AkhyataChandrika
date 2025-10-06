#!/usr/bin/env python3
import json
import os
import re
from typing import Any, Dict, List, Tuple


SPEC_INPUT_PATH = os.path.join(
    os.path.dirname(__file__),  "out", "parsed_dict.generated.json"
)
OUTPUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..","generated")
INVALID_DIR = os.path.join(OUTPUT_ROOT, "invalid")
INVALID_FILE = os.path.join(INVALID_DIR, "invalid.text_numbers.json")
INVALID_YAML_FILE = os.path.join(INVALID_DIR, "invalid.text_numbers.yaml")


TEXT_NUMBER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def ensure_directories(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_text_number(text_number: str) -> Tuple[int, int, int]:
    match = TEXT_NUMBER_RE.match(text_number.strip())
    if not match:
        raise ValueError("malformed text_number")
    x_str, y_str, z_str = match.groups()
    return int(x_str), int(y_str), int(z_str)


def read_input(path: str) -> List[Tuple[str, Dict[str, Any]]]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    # Expecting payload with key "entries": list of [headword, data]
    entries = payload.get("entries", [])
    result: List[Tuple[str, Dict[str, Any]]] = []
    for item in entries:
        if isinstance(item, list) and len(item) == 2 and isinstance(item[1], dict):
            result.append((item[0], item[1]))
    return result


def write_invalid_json(item: Tuple[str, Dict[str, Any]]) -> None:
    ensure_directories(INVALID_DIR)
    with open(INVALID_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False))
        f.write("\n")


def append_invalid_yaml(artha: str, synonyms: List[str]) -> None:
    # Only append if we have a sensible artha and a list of string synonyms
    if not isinstance(artha, str) or not isinstance(synonyms, list):
        return
    if not all(isinstance(s, str) and s.strip() for s in synonyms):
        return
    ensure_directories(INVALID_DIR)
    # Reuse the same YAML block format
    lines: List[str] = [f"{artha}:"]
    for syn in synonyms:
        lines.append(f"  - {syn}:")
    block = "\n".join(lines) + "\n"
    if os.path.exists(INVALID_YAML_FILE) and os.path.getsize(INVALID_YAML_FILE) > 0:
        with open(INVALID_YAML_FILE, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(block)
    else:
        with open(INVALID_YAML_FILE, "w", encoding="utf-8") as f:
            f.write(block)


def append_yaml_block(file_path: str, artha: str, synonyms: List[str]) -> None:
    ensure_directories(os.path.dirname(file_path))
    # Prepare YAML block with required format:
    # artha:\n  - synonym1:\n  - synonym2:\n
    # Normalize lines to avoid trailing spaces; keep exactly two-space indent for list items
    lines: List[str] = [f"{artha}:"]
    for syn in synonyms:
        lines.append(f"  - {syn}:")
    block = "\n".join(lines) + "\n"

    # Append with a separating newline if file already has content
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(block)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(block)


def process() -> None:
    entries = read_input(SPEC_INPUT_PATH)

    for headword, data in entries:
        text_number = data.get("text_number", "")
        artha = data.get("artha", "").strip()
        synonyms = data.get("synonyms", [])

        # Basic validation of required fields
        if not isinstance(text_number, str) or not isinstance(artha, str) or not isinstance(synonyms, list):
            write_invalid_json((headword, data))
            continue

        # Reject non-string synonyms early to avoid broken YAML lines
        if not all(isinstance(s, str) and s.strip() for s in synonyms):
            write_invalid_json((headword, data))
            continue

        try:
            x, y, _z = parse_text_number(text_number)
        except Exception:
            # Log all invalids to JSON, and also append to invalid YAML using the same format
            write_invalid_json((headword, data))
            append_invalid_yaml(artha, synonyms)
            continue

        out_dir = os.path.join(OUTPUT_ROOT, str(x))
        out_file = os.path.join(out_dir, f"{y}.yaml")
        append_yaml_block(out_file, artha, synonyms)


if __name__ == "__main__":
    process()


