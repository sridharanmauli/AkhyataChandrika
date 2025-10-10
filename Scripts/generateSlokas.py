#!/usr/bin/env python3
import yaml
import json
import sys
import os

TAB_SPACES = 2

# Load JSON mapping
with open("output/mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

# -------------------------
# Custom YAML dumper to preserve strings
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)

def update_nulls_with_mapping(node):
    """
    Recursively update list elements or nulls using mapping.
    Rules:
      1️⃣ If a list has entries [x, y]:
            → keep x as-is, replace y if it's in mapping.
      2️⃣ If key itself is in mapping (and value is None):
            → convert to [mapping[key]].
      3️⃣ If key itself is in mapping (and value is a list but empty):
            → replace list with [mapping[key]].
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                update_nulls_with_mapping(value)
            elif value is None:
                # Example: - वेत्ति:
                if key in mapping:
                    print(f"🔄 Updating '{key}' → {mapping[key]}")
                    node[key] = [mapping[key]]

    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                for k, v in item.items():
                    # Case 1: - अविरस्ति: [आविस्, अस्ति]
                    if isinstance(v, list):
                        new_list = []
                        for elem in v:
                            if elem in mapping:
                                print(f"🔄 Updating '{elem}' → {mapping[elem]}")
                                new_list.append(mapping[elem])
                            else:
                                new_list.append(elem)
                        item[k] = new_list

                    # Case 2: - वेत्ति:
                    elif v is None:
                        if k in mapping:
                            print(f"🔄 Updating '{k}' → {mapping[k]}")
                            item[k] = [mapping[k]]
            else:
                update_nulls_with_mapping(item)

                
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
def yaml_to_json(yaml_file, varga_name=None ):
    # 1️⃣ Load YAML and clean tabs
    data = load_yaml_clean_tabs(yaml_file)

    # 2️⃣ Overwrite YAML in-place
    write_clean_yaml(data, yaml_file)

    update_nulls_with_mapping( data )

    # 2️⃣ Overwrite YAML in-place
    write_clean_yaml(data, yaml_file)

    # print(exclude_lines)
    # 5️⃣ Convert to JSON structure
    shlokas_list = []
    shloka_num = 1
    for shloka_text, verbs_data in data.items():
        
        if varga_name is None:
            shloka_entry = {
                "num": str(shloka_num),
                "text": shloka_text.strip().rstrip(":"),
                "verbs": []
            }
        else:
            shloka_entry = {
                "num": str(shloka_num),
                "text": shloka_text.strip().rstrip(":"),
                "adhikaar": varga_name,
                "verbs": []
            }

        if not verbs_data:
            verbs_data = {}
        # and all(isinstance(e, str) for e in verbs_data)
        if isinstance(verbs_data, list):
            verbs_data = {"": verbs_data}
        # print(type(verbs_data))
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
                    if( len( metaData ) == 1):
                        dhatu_id = metaData[0]
                    elif( len(metaData) == 2):
                        upasagra = metaData[0]
                        dhatu_id = metaData[1]
                verb_block["entries"].append({
                    "form": form,
                    "dhatu_id": dhatu_id,
                    "gati": upasagra
                })

            shloka_entry["verbs"].append(verb_block)

        shlokas_list.append(shloka_entry)
        shloka_num += 1  # only incremented for non-excluded shlokas

    return {"shlokas": shlokas_list}

# -------------------------
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateSlokas.py input/sampleFile.yaml output/testSlokas_Autogenerated.json")
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
