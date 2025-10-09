#!/usr/bin/env python3
import yaml
import json
import sys
import os

TAB_SPACES = 2

# Load JSON mapping
with open("mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

# -------------------------
# Custom YAML dumper to preserve strings
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)

def update_nulls_with_mapping(node):
    """Recursively walk the YAML structure and update null verbs if mapping exists."""
    if isinstance(node, dict):
        for k, v in node.items():
            # If the value is a list
            if isinstance(v, list):
                for i, item in enumerate(v):
                    # item is a dict with single key
                    if isinstance(item, dict):
                        for verb, val in item.items():
                            # print(f"Checking verb: {verb} with value: {val}")
                            if val is None or val == []:
                                if verb in mapping:
                                    # print(f"Updating verb '{verb}' with mapping '{mapping[verb]}'")
                                    # Replace null/empty with the mapped number as a list
                                    item[verb] = [mapping[verb]]
                    elif isinstance(item, str):
                        # Optional: handle string items if needed
                        pass
            else:
                # Recurse for nested dicts
                update_nulls_with_mapping(v)
    elif isinstance(node, list):
        for elem in node:
            update_nulls_with_mapping(elem)
# -------------------------
# Custom loader to force all scalars to strings
class ForceStringLoader(yaml.SafeLoader):
    pass

def str_constructor(loader, node):
    return loader.construct_scalar(node)

ForceStringLoader.add_constructor(u'tag:yaml.org,2002:int', str_constructor)
ForceStringLoader.add_constructor(u'tag:yaml.org,2002:float', str_constructor)

# -------------------------
def load_yaml_clean_tabs(yaml_file):
    """Load YAML and replace tabs with spaces."""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    clean_text = raw_text.replace("\t", " " * TAB_SPACES)
    return yaml.load(clean_text, Loader=ForceStringLoader) or {}

def write_clean_yaml(data, yaml_file):
    """Overwrite the YAML file with cleaned data, preserving leading zeros."""
    with open(yaml_file, 'w', encoding='utf-8') as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            indent=2,
            sort_keys=False,
            width=1000,
            Dumper=QuotedDumper
        )

# -------------------------
def yaml_to_json(yaml_file):
    # 1️⃣ Load YAML and clean tabs
    data = load_yaml_clean_tabs(yaml_file)

    # 2️⃣ Overwrite YAML in-place
    write_clean_yaml(data, yaml_file)

    update_nulls_with_mapping( data )

    # 2️⃣ Overwrite YAML in-place
    write_clean_yaml(data, yaml_file)
    exclude_lines = []
    # 4️⃣ Load exclusions
    with open("excludes.yaml", "r", encoding="utf-8") as ef:
        exclude_lines = [line.strip() for line in ef if line.strip()]

    print(exclude_lines)
    # 5️⃣ Convert to JSON structure
    shlokas_list = []
    shloka_num = 1
    for shloka_text, verbs_data in data.items():
        if shloka_text.strip() in exclude_lines:
            shloka_entry = {
            "num": "_",
            "text": shloka_text.strip().rstrip(":"),
            "verbs": []
            }
            shlokas_list.append(shloka_entry)
            continue  # skip increment and skip adding to output

        shloka_entry = {
            "num": shloka_num,
            "text": shloka_text.strip().rstrip(":"),
            "verbs": []
        }

        if not verbs_data:
            verbs_data = {}

        if isinstance(verbs_data, list) and all(isinstance(e, str) for e in verbs_data):
            verbs_data = {"": verbs_data}

        for artha, entries in verbs_data.items():
            verb_block = {"artha": artha, "entries": []}

            if not entries:
                continue
            # If verb_items is a list of single-key dicts, merge into one dict
            if isinstance(entries, list):
                merged_entries = {}
                for item in entries:
                    if isinstance(item, dict):
                        merged_entries.update(item)
                    elif isinstance(item, str):
                        # Handle simple string verbs if needed
                        merged_entries[item] = ""
                entries_dict = merged_entries
            elif isinstance(entries, dict):
                entries_dict = entries
            else:
                entries_dict = {}
            
            for verb, metaData in entries_dict.items():
                form = verb
                dhatu_id, upasagra = "", ""
                if metaData:
                    dhatu_id = metaData[0] if len(metaData) > 0 else ""
                    upasagra = metaData[1] if len(metaData) > 1 else ""
                verb_block["entries"].append({
                    "form": form,
                    "dhatu_id": dhatu_id,
                    "upasagra": upasagra
                })

            shloka_entry["verbs"].append(verb_block)

        shlokas_list.append(shloka_entry)
        shloka_num += 1  # only incremented for non-excluded shlokas

    return {"shlokas": shlokas_list}

# -------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateSlokas.py <input.yaml> <output.json>")
        sys.exit(1)

    input_yaml = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.exists(input_yaml):
        print(f"Error: {input_yaml} does not exist")
        sys.exit(1)

    slokasPerVarga = yaml_to_json(input_yaml)

    with open(output_json, 'w', encoding='utf-8') as out:
        json.dump(slokasPerVarga, out, ensure_ascii=False, indent=4)

    print(f"✅ JSON written to {output_json} and YAML cleaned in-place!")
