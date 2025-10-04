#!/usr/bin/env python3
import yaml
import json
import sys
import os

# Load the JSON mapping into a Python dictionary
with open("mapping.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

def yaml_to_json(yaml_file):
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    shlokas_list = []
    shloka_num = 1
    if data is None:
        data = {}
    for shloka_text, verbs_data in data.items():
        shloka_entry = {
            "num": shloka_num,
            "text": shloka_text.strip().rstrip(":"),
            "verbs": []
        }

        # Handle None or missing verbs
        if not verbs_data:
            verbs_data = {}

        # If verbs_data is a list (only forms), wrap in dummy artha key
        if isinstance(verbs_data, list):
            verbs_data = {"": verbs_data}

        for artha, entries in verbs_data.items():
            verb_block = {"artha": artha, "entries": []}

            if not entries:
                entries = []

            # Iterate over entries
            for e in entries:
                # Convert to string if it's not
                entry_str = str(e).strip()

                # Split by '-' to get form, dhatu_id, upasagra
                parts = [p.strip() for p in entry_str.split('-')]

                form = parts[0] if len(parts) > 0 else ""
                dhatu_id = parts[1] if len(parts) > 1 else ""
                upasagra = parts[2] if len(parts) > 2 else ""

                if dhatu_id == "":
                    dhatu_id = mapping.get(form, "")
                    if dhatu_id == "":
                        upasagra = "check Upasarga" 

                verb_block["entries"].append({
                    "form": form,
                    "dhatu_id": dhatu_id,
                    "upasagra": upasagra
                })

            shloka_entry["verbs"].append(verb_block)

        shlokas_list.append(shloka_entry)
        shloka_num += 1

    final_json = {"shlokas": shlokas_list}

    return final_json

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 generateYaml.py <input.yaml> <output.json>")
        sys.exit(1)

    input_yaml = sys.argv[1]
    output_json = sys.argv[2]

    if not os.path.exists(input_yaml):
        print(f"Error: {input_yaml} does not exist")
        sys.exit(1)

    slokasPerVarga = yaml_to_json(input_yaml)

    with open(output_json, 'w', encoding='utf-8') as out:
      json.dump(slokasPerVarga, out, ensure_ascii=False, indent=4)

    print(f"✅ JSON written to {output_json}")
