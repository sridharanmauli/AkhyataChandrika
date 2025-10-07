import os
import gzip
import struct
import json

# -----------------------------
# CONFIG: Set your dictionary folder path here
# -----------------------------
DICT_FOLDER = "input"  # e.g., "./sanskrit_dict"
OUTPUT_JSON = "out/parsed_dict.generated.json"

# -----------------------------
# Helper Functions
# -----------------------------

def read_ifo(ifo_path):
    """Read metadata from .ifo file"""
    meta = {}
    with open(ifo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line:
                key, val = line.split("=", 1)
                meta[key.strip()] = val.strip()
    return meta

def read_idx(idx_path):
    """Read .idx file and return {word: (offset, size)}"""
    idx = {}
    with open(idx_path, "rb") as f:
        while True:
            # Read null-terminated word
            word_bytes = bytearray()
            while True:
                b = f.read(1)
                if not b:
                    return idx
                if b == b'\x00':
                    break
                word_bytes += b
            word = word_bytes.decode('utf-8')
            # Read 4 bytes offset + 4 bytes size (big-endian)
            offset_bytes = f.read(4)
            size_bytes = f.read(4)
            if not offset_bytes or not size_bytes:
                break
            offset = struct.unpack('>I', offset_bytes)[0]
            size = struct.unpack('>I', size_bytes)[0]
            idx[word] = (offset, size)

def read_dict(dict_path):
    """Read dict.dz (gzipped) or dict file"""
    if dict_path.endswith(".dz"):
        with gzip.open(dict_path, 'rb') as f:
            data = f.read()
    else:
        with open(dict_path, 'rb') as f:
            data = f.read()
    return data

def read_syn(syn_path):
    """Read synonym mapping: returns {alternate_word: main_word offset info}"""
    syn_map = {}
    if not syn_path or not os.path.exists(syn_path):
        return syn_map
    with open(syn_path, 'rb') as f:
        while True:
            # Read null-terminated synonym word
            word_bytes = bytearray()
            while True:
                b = f.read(1)
                if not b:
                    return syn_map
                if b == b'\x00':
                    break
                word_bytes += b
            if not word_bytes:
                continue
            # Decode using latin1 to avoid decode errors
            syn_word = word_bytes.decode('latin1')

            # Read 4-byte offset + 4-byte size (big-endian)
            offset_bytes = f.read(4)
            size_bytes = f.read(4)
            if not offset_bytes or not size_bytes:
                break
            offset = struct.unpack('>I', offset_bytes)[0]
            size = struct.unpack('>I', size_bytes)[0]

            syn_map[syn_word] = (offset, size)
    return syn_map

def version_key(vstr):
    """
    Convert a version string like '1.1.2' to a tuple of ints for sorting.
    Invalid versions are treated as (0, 0, 0) by default.
    """
    if not isinstance(vstr, str):
        return (0, 0, 0)
    parts = vstr.split(".")
    version_nums = []
    for part in parts:
        try:
            version_nums.append(int(part))
        except ValueError:
            # Non-integer parts are treated as 0
            version_nums.append(0)
    return tuple(version_nums)


# -----------------------------
# Main Processing
# -----------------------------

# Find files
ifo_file = None
idx_file = None
dict_file = None
syn_file = None

for file in os.listdir(DICT_FOLDER):
    if file.endswith(".ifo"):
        ifo_file = os.path.join(DICT_FOLDER, file)
    elif file.endswith(".idx"):
        idx_file = os.path.join(DICT_FOLDER, file)
    elif file.endswith(".dict") or file.endswith(".dict.dz"):
        dict_file = os.path.join(DICT_FOLDER, file)
    elif file.endswith(".syn"):
        syn_file = os.path.join(DICT_FOLDER, file)

if not ifo_file or not idx_file or not dict_file:
    raise Exception("Missing required .ifo, .idx, or .dict(.dz) file in folder!")

# Read files
metadata = read_ifo(ifo_file)
idx = read_idx(idx_file)
dict_data = read_dict(dict_file)
syn_map = read_syn(syn_file)

# Build JSON entries
json_entries = {}

# Main words
for word, (offset, size) in idx.items():
    try:
        meaning = dict_data[offset:offset+size].decode('utf-8')
    except UnicodeDecodeError:
        meaning = dict_data[offset:offset+size].decode('latin1', errors='replace')
    entities = meaning.split('\n')
    
    json_entries[word] = {
        "artha": entities[0],
        "text_number":entities[1],
        "synonyms": entities[2].split(' ')
    }

# Add synonyms
for syn_word, (offset, size) in syn_map.items():
    # Try to find main word by matching offset+size
    main_word = None
    for w, (o, s) in idx.items():
        if o == offset and s == size:
            main_word = w
            break
    if main_word:
        json_entries[syn_word] = {
            "meaning": json_entries[main_word]["meaning"],
            "synonyms": [main_word]
        }


sorted_entries = sorted(
    json_entries.items(),
    key=lambda item: version_key(item[1]["text_number"])
)

# Combine metadata and entries
final_json = {
    "dictionary_name": metadata.get("bookname", "Unknown Dictionary"),
    "version": metadata.get("version", ""),
    "author": metadata.get("author", ""),
    "entries": sorted_entries
}

# Save to JSON file
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(final_json, f, ensure_ascii=False, indent=2)

print(f"✅ Dictionary converted to JSON: {OUTPUT_JSON}")
