#!/usr/bin/env python3
import yaml
import json
import sys
import os

TAB_SPACES = 2

# Load SopasargaMappings (contains all verb forms with upasarga and dhatu information)
with open("output/SopasargaMappings.json", "r", encoding="utf-8") as f:
    sopasarga_mapping = json.load(f)

# -------------------------
# Custom YAML dumper to preserve strings
class QuotedDumper(yaml.SafeDumper):
    pass

def quoted_str_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(str, quoted_str_representer, Dumper=QuotedDumper)

def update_nulls_with_mapping(node):
    """
    Recursively update list elements or nulls using sopasarga_mapping.
    The sopasarga_mapping contains all verb forms with their upasarga and dhatu information.
    For verbs without upasarga, the upasarga field will be empty string.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                update_nulls_with_mapping(value)
            elif value is None:
                # Check sopasarga_mapping for verb forms
                if key in sopasarga_mapping:
                    # Get all possible combinations from sopasarga mapping
                    combinations = sopasarga_mapping[key]
                    if len(combinations) == 1:
                        # Single combination - use it directly
                        combo = combinations[0]
                        if combo['upasarga']:
                            print(f"🔄 Updating '{key}' → [{combo['upasarga']}, {combo['dhatuNumber']}]")
                            node[key] = [combo['upasarga'], combo['dhatuNumber']]
                        else:
                            print(f"🔄 Updating '{key}' → [{combo['dhatuNumber']}]")
                            node[key] = [combo['dhatuNumber']]
                    else:
                        # Multiple combinations - use dhatu_ids separated by comma
                        dhatu_ids = ', '.join([c['dhatuNumber'] for c in combinations])
                        upasarga = combinations[0]['upasarga']  # All should have same upasarga
                        if upasarga:
                            print(f"🔄 Updating '{key}' → [{upasarga}, {dhatu_ids}]")
                            node[key] = [upasarga, dhatu_ids]
                        else:
                            print(f"🔄 Updating '{key}' → [{dhatu_ids}]")
                            node[key] = [dhatu_ids]

    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                for k, v in item.items():
                    # Case: - वेत्ति:
                    if v is None:
                        # Check sopasarga_mapping
                        if k in sopasarga_mapping:
                            combinations = sopasarga_mapping[k]
                            if len(combinations) == 1:
                                combo = combinations[0]
                                if combo['upasarga']:
                                    print(f"🔄 Updating '{k}' → [{combo['upasarga']}, {combo['dhatuNumber']}]")
                                    item[k] = [combo['upasarga'], combo['dhatuNumber']]
                                else:
                                    print(f"🔄 Updating '{k}' → [{combo['dhatuNumber']}]")
                                    item[k] = [combo['dhatuNumber']]
                            else:
                                dhatu_ids = ', '.join([c['dhatuNumber'] for c in combinations])
                                upasarga = combinations[0]['upasarga']
                                if upasarga:
                                    print(f"🔄 Updating '{k}' → [{upasarga}, {dhatu_ids}]")
                                    item[k] = [upasarga, dhatu_ids]
                                else:
                                    print(f"🔄 Updating '{k}' → [{dhatu_ids}]")
                                    item[k] = [dhatu_ids]
                    elif isinstance(v, (dict, list)):
                        update_nulls_with_mapping(v)
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
def fix_yaml_indentation_in_memory(raw_text):
    """
    Fix YAML indentation issue where artha categories are not properly nested under shloka text.

    The issue: YAML files may have structure like:
      "shloka text...॥": null
      artha:           ← should be indented by 2!
      - verb1:         ← should be indented by 4!
        - dhatu_id
      - verb2:
        - dhatu_id

    Also handles nested verb structures:
      artha:
      - parent_verb:
        - child_verb1:
        - child_verb2:

    This function:
    1. Removes " null" from shloka lines that have ": null"
    2. Indents artha lines by 2 spaces (to be children of shloka)
    3. Indents verb list items and their children appropriately
    4. Flattens nested verb structures into the same artha category

    Returns fixed text.
    """
    lines = raw_text.split('\n')
    fixed_lines = []
    indented_count = 0
    removed_null_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)

        # Check if this is a shloka line (ends with ॥":)
        if line.strip().endswith('॥": null') or line.strip().endswith('॥":'):
            # Remove " null" if present to allow artha children
            if line.strip().endswith('॥": null'):
                line = line.replace(': null', ':')
                removed_null_count += 1
            fixed_lines.append(line)
            i += 1
        # Check if this is an artha line that should be indented:
        # - No leading spaces (column 0)
        # - Not a list item (doesn't start with -)
        # - Ends with a colon (is a key)
        # - Not a shloka line
        elif (leading_spaces == 0 and
              not stripped.startswith('-') and
              stripped.endswith(':') and
              not stripped.endswith('॥":')):
            # Indent artha by 2 spaces (under shloka)
            fixed_lines.append('  ' + line)
            indented_count += 1
            i += 1
        # Check if this is a parent verb at column 0 with nested child verbs
        elif leading_spaces == 0 and stripped.startswith('-') and stripped.endswith(':'):
            # Check if next line is a nested child verb (indent 2, starts with -, ends with :)
            # vs a dhatu_id (indent 2, starts with -, does NOT end with :)
            if (i + 1 < len(lines) and
                lines[i + 1].lstrip().startswith('-') and
                len(lines[i + 1]) - len(lines[i + 1].lstrip()) == 2 and
                lines[i + 1].rstrip().endswith(':')):
                # This is a nested verb structure - flatten it
                # Add the parent verb as a regular verb
                fixed_lines.append('    ' + line)
                indented_count += 1
                i += 1

                # Add all child verbs as siblings (not nested) by removing one level of indentation
                while (i < len(lines) and
                       lines[i].lstrip().startswith('-') and
                       len(lines[i]) - len(lines[i].lstrip()) == 2 and
                       lines[i].rstrip().endswith(':')):
                    # Child verb at indent 2 - make it indent 0, then add 4 spaces
                    # Remove 2 spaces of indentation, then add 4
                    child_verb = lines[i][2:]  # Remove first 2 spaces
                    fixed_lines.append('    ' + child_verb)
                    indented_count += 1
                    i += 1
            else:
                # Regular verb at column 0 without nested child verbs (may have dhatu_ids as children)
                fixed_lines.append('    ' + line)
                indented_count += 1
                i += 1
        # Check if this is a verb list item at column 0 (no children)
        elif leading_spaces == 0 and stripped.startswith('-'):
            # Indent verb list items by 4 spaces (2 + 2, under artha)
            fixed_lines.append('    ' + line)
            indented_count += 1
            i += 1
        # Check if this is a dhatu_id list item already indented by 2
        elif leading_spaces == 2 and stripped.startswith('-'):
            # This is already at indent 2, needs to be at indent 6 (4 + 2)
            fixed_lines.append('    ' + line)
            indented_count += 1
            i += 1
        else:
            fixed_lines.append(line)
            i += 1

    if indented_count > 0:
        print(f"🔧 Fixed {indented_count} indentation issue(s) in YAML")
    if removed_null_count > 0:
        print(f"🔧 Removed {removed_null_count} 'null' value(s) from shloka lines")

    return '\n'.join(fixed_lines)

def load_yaml_clean_tabs(yaml_file):
    """Load YAML and replace tabs with spaces."""
    with open(yaml_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # Replace tabs with spaces
    clean_text = raw_text.replace("\t", " " * TAB_SPACES)

    # Fix indentation issues where artha categories are not properly nested under shloka text
    clean_text = fix_yaml_indentation_in_memory(clean_text)

    try:
        return yaml.load(clean_text, Loader=ForceStringLoader) or {}
    except yaml.YAMLError as e:
        print(f"\n❌ YAML parsing error in file: {yaml_file}")
        print(f"Error: {e}")
        raise

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
def yaml_to_json(yaml_file, varga_name=None, prevCnt=0 ):
    # 1️⃣ Load YAML and clean tabs
    data = load_yaml_clean_tabs(yaml_file)

    # NOTE: Do NOT rewrite YAML files! The files contain duplicate keys (multiple arthis with same name)
    # which is valid in YAML but gets lost when converted to Python dict and back.
    # The update_nulls_with_mapping() function is disabled for now to prevent data loss.

    # update_nulls_with_mapping( data )

    # Detect if this is a Nanartha Varga file
    is_nanartha = 'नानार्थवर्गः' in yaml_file or 'nanartha' in yaml_file.lower()

    # print(exclude_lines)
    # 5️⃣ Convert to JSON structure
    shlokas_list = []
    shloka_num = prevCnt + 1
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

        # Special handling for Nanartha Varga: interchange form and artha
        if is_nanartha:
            # In Nanartha Varga:
            # Original structure: भवति: [सत्तायाम्:, ...]
            # We need to treat: form=भवति, artha=सत्तायाम्
            # So each "artha" key becomes a "form", and each entry becomes an "artha"
            for form_text, artha_list in verbs_data.items():
                if not artha_list:
                    continue

                # artha_list should be a list of dicts like [{'सत्तायाम्': None}, ...]
                if isinstance(artha_list, list):
                    for artha_item in artha_list:
                        if isinstance(artha_item, dict):
                            for artha_text, metadata in artha_item.items():
                                # Create a verb block for each artha
                                verb_block = {"artha": artha_text, "entries": []}

                                # Now we need to split the form_text to extract upasarga and dhatu
                                form = form_text
                                dhatu_id, upasagra = "Not Found", ""

                                # Try to look up in sopasarga_mapping
                                if form in sopasarga_mapping:
                                    combinations = sopasarga_mapping[form]
                                    if len(combinations) == 1:
                                        # Single combination
                                        combo = combinations[0]
                                        upasagra = combo['upasarga']
                                        dhatu_id = combo['dhatuNumber']
                                    else:
                                        # Multiple dhatu IDs with same upasarga
                                        upasagra = combinations[0]['upasarga']
                                        dhatu_ids = [c['dhatuNumber'] for c in combinations]
                                        dhatu_id = ", ".join(dhatu_ids) + " (More than one)"
                                else:
                                    dhatu_id = "Not Found"

                                verb_block["entries"].append({
                                    "form": form,
                                    "dhatu_id": dhatu_id,
                                    "gati": upasagra
                                })

                                shloka_entry["verbs"].append(verb_block)
        else:
            # Normal processing for non-Nanartha Varga
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
                    dhatu_id, upasagra = "Not Found", ""

                    # Normalize metaData to a list
                    if not metaData or metaData == "":
                        data_list = []
                    elif isinstance(metaData, list):
                        data_list = metaData
                    elif isinstance(metaData, str):
                        data_list = [metaData]
                    else:
                        data_list = []

                    # Filter out empty strings and None values
                    valid_data = [item for item in data_list if item and isinstance(item, str) and item.strip()]

                    if len(valid_data) == 0:
                        # No valid data - check sopasarga_mapping
                        if verb in sopasarga_mapping:
                            combinations = sopasarga_mapping[verb]
                            if len(combinations) == 1:
                                # Single combination
                                combo = combinations[0]
                                upasagra = combo['upasarga']
                                dhatu_id = combo['dhatuNumber']
                            else:
                                # Multiple dhatu IDs with same upasarga
                                upasagra = combinations[0]['upasarga']  # All should have same upasarga
                                dhatu_ids = [c['dhatuNumber'] for c in combinations]
                                dhatu_id = ", ".join(dhatu_ids) + " (More than one)"
                        else:
                            dhatu_id = "Not Found"
                    elif len(valid_data) == 1:
                        # Single item - could be dhatu_id or gati
                        item = valid_data[0].strip()
                        # Check if it looks like a dhatu_id (format: XX.XXXX or contains comma-separated IDs)
                        if ',' in item:
                            # Multiple dhatu_ids separated by comma
                            dhatu_id = item + " (More than one)"
                        elif '.' in item and any(c.isdigit() for c in item):
                            dhatu_id = item
                        else:
                            # It's probably a gati (upasarga) without dhatu_id
                            upasagra = item
                            dhatu_id = "Not Found"
                    elif len(valid_data) == 2:
                        # Two items - first is gati, second is dhatu_id
                        upasagra = valid_data[0].strip()
                        second_item = valid_data[1].strip()
                        # Check if second item has comma-separated dhatu_ids
                        if ',' in second_item:
                            dhatu_id = second_item + " (More than one)"
                        else:
                            dhatu_id = second_item
                    else:
                        # More than 2 items - check if multiple dhatu_ids
                        # First item might be gati, rest are dhatu_ids
                        possible_gati = valid_data[0].strip()
                        dhatu_ids = []

                        # Check if first item is a gati (not a dhatu_id)
                        if '.' not in possible_gati or not any(c.isdigit() for c in possible_gati):
                            upasagra = possible_gati
                            dhatu_ids = [item.strip() for item in valid_data[1:]]
                        else:
                            dhatu_ids = [item.strip() for item in valid_data]

                        # Handle multiple dhatu_ids
                        if len(dhatu_ids) > 1:
                            dhatu_id = ", ".join(dhatu_ids) + " (More than one)"
                        elif len(dhatu_ids) == 1:
                            dhatu_id = dhatu_ids[0]
                        else:
                            dhatu_id = "Not Found"

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
